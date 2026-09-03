# MCO operations runbook

This runbook is for the V1 demo environment and the intended Neon/Railway/Cloudflare/n8n topology.

## 1. Local bootstrap

### Full integration stack

```bash
cd infra
cp .env.example .env
# Set a long random N8N_ENCRYPTION_KEY in .env
docker compose up --build
```

Compose waits through `PostgreSQL -> migration -> seed -> backend health -> n8n`.

### Frontend

```bash
cd frontend
cp .env.example .env
pnpm install
pnpm run dev
```

### Direct backend development

```bash
cd backend
cp .env.example .env
python -m venv .venv
# activate the virtualenv
python -m pip install -e '.[dev]'
alembic upgrade head
python -m app.scripts.seed_demo
uvicorn app.main:app --reload
```

## 2. Health checks

- `GET /health`: process is alive.
- `GET /ready`: API can reach PostgreSQL.
- FastAPI OpenAPI: `/docs`.

If `/health` is OK but `/ready` is 503, check database URL, Neon state/network access, credentials, and migration/dependency status before restarting the application.

## 3. Order sync diagnosis

1. Open the n8n execution for `MCO - Multichannel Order Sync`.
2. Identify the first failed node: source fetch, normalization, or import.
3. Capture the MCO `X-Request-ID` from the failed API response when available.
4. Find the same request ID in backend structured logs.
5. Classify the failure:
   - 4xx validation/business error: fix source/catalog/stock data; do not retry indefinitely.
   - transient network/5xx: retry is acceptable because order import is idempotent.
6. Re-run the workflow after the cause is fixed.

Do not manually insert orders or ledger rows to “repair” a sync.

## 4. Reconciliation diagnosis

1. Open Dashboard -> Reconciliation or call `GET /api/v1/reconciliations`.
2. Inspect mismatch code and `external_order_id`.
3. Compare the deterministic source feed with local order and ledger data.
4. Correct the upstream/import defect rather than editing reconciliation history.
5. Re-run reconciliation and verify a successful new log.
6. Resolve the old operational alert only after the discrepancy is understood.

## 5. Alert notification diagnosis

The Telegram workflow uses at-least-once delivery semantics:

1. `GET /api/v1/alerts/pending-notifications` shows alerts not yet marked delivered.
2. n8n sends Telegram.
3. Only after success, n8n calls `PATCH /api/v1/alerts/{id}/notified`.

If Telegram accepted a message but its response was lost, a later execution may deliver a duplicate because Telegram `sendMessage` is not an MCO-idempotent endpoint. The workflow intentionally avoids blind immediate retries for that call.

## 6. Database migrations

Create a new Alembic revision for schema changes; never rewrite an applied production revision.

Railway uses `alembic upgrade head` as a pre-deploy command. A failed migration blocks the release.

For Neon, configure:

- `MCO_DATABASE_URL`: runtime async URL (pooled endpoint preferred for application traffic);
- `MCO_MIGRATION_DATABASE_URL`: direct/unpooled psycopg URL used by Alembic.

## 7. Deployment verification

After deployment:

1. `/health` returns 200.
2. `/ready` returns 200.
3. one mock source endpoint returns deterministic data;
4. an order-sync execution returns imported/duplicate rather than 5xx;
5. dashboard daily report loads;
6. reconciliation can complete;
7. no secrets appear in application or workflow logs.

## 8. Rollback

Application rollback: roll Railway back to the previous known-good deployment only if the database schema remains backward compatible.

Database rollback: prefer a forward corrective migration. Alembic `downgrade` is for controlled cases where the migration is proven reversible and no newer data depends on the changed schema.

Never drop/truncate production data to make an application rollback easier.

## 9. Production hardening before real data

V1 intentionally omits end-user auth/RBAC. Before real operational use:

- place API/n8n behind appropriate authentication and network policy;
- use least-privilege database credentials;
- store Telegram and database secrets in deployment secret stores;
- configure backups/retention and audit requirements;
- add service-level monitoring appropriate to the deployment;
- replace mock channels with authenticated vendor integrations and their rate-limit/retry rules.
