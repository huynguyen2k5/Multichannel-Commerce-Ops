# Deployment notes

## Backend: Railway

Use `backend/railway.toml` as Config-as-Code. The Docker image runs as a non-root user and exposes `/ready` for deployment health. Railway executes `alembic upgrade head` before the new application revision is released.

Required backend variables:

```text
MCO_ENVIRONMENT=production
MCO_LOG_LEVEL=INFO
MCO_DATABASE_URL=postgresql+asyncpg://...-pooler.../...
MCO_MIGRATION_DATABASE_URL=postgresql+psycopg://...direct.../...
MCO_CORS_ORIGINS=https://<cloudflare-pages-domain>
```

Run `python -m app.scripts.seed_demo` once for the portfolio demo database. The seed is idempotent, but it is deliberately not part of every production release.

## Frontend: Cloudflare Pages

Build configuration:

```text
Root directory: frontend
Build command: pnpm run build
Output directory: dist
```

Set `VITE_API_BASE_URL` to the Railway API `/api/v1` origin. For the deterministic portfolio dataset, keep `VITE_DEMO_REPORT_DATE=2026-09-01` (or deliberately change both fixtures and demo date together). `frontend/public/_redirects` provides SPA history fallback and is copied into Vite output.

## n8n

Import the JSON files under `n8n/workflows/`, configure the environment variables documented in `README.md`, inspect credentials, and enable workflows only after test executions pass.

Do not publish the local n8n compose instance directly to the Internet. Use a secured n8n deployment and keep its encryption key stable and secret.
