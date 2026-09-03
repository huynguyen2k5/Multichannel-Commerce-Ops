# Engineering references and rationale

Last reviewed: 2026-09-03.

These sources informed implementation choices; repository requirements and tests remain the source of truth for MCO behavior.

## Backend structure and lifecycle

- FastAPI, **Bigger Applications - Multiple Files**: https://fastapi.tiangolo.com/tutorial/bigger-applications/
  - Supports composing domain routers with `APIRouter` instead of one giant application file.
- SQLAlchemy, **Asyncio extension**: https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html
  - `AsyncSession` is mutable transaction state and should not be shared across concurrent tasks. MCO provides one request-scoped session and makes the application service own critical transaction boundaries.
- SQLAlchemy, **PostgreSQL asyncpg + PgBouncer guidance**: https://docs.sqlalchemy.org/en/21/dialects/postgresql.html
  - For Neon `-pooler` URLs, MCO lets PgBouncer own connection pooling (`NullPool` in SQLAlchemy) and uses unique asyncpg prepared-statement names. Direct/local PostgreSQL keeps SQLAlchemy's normal pool.

## Reliability and idempotency

- Stripe Engineering, **Designing robust and predictable APIs with idempotency**: https://stripe.com/blog/idempotency
  - Retries are normal in distributed workflows; mutations need a stable identity and server-side no-op behavior. MCO uses `(channel_id, external_order_id)` plus a database uniqueness constraint rather than relying only on an application pre-check.

## PostgreSQL / Neon connection strategy

- Neon, **Improving the developer experience for Prisma users**: https://neon.com/blog/prisma-dx-improvements
- Neon, **A branch-first dev loop for Neon**: https://neon.com/blog/branch-first-dev-loop
  - Neon exposes pooled and unpooled/direct URLs. MCO deliberately keeps `MCO_DATABASE_URL` and `MCO_MIGRATION_DATABASE_URL` separate. The direct migration URL is a conservative portability choice for Alembic/schema operations, not a claim that current Neon PgBouncer cannot run migrations.

## Frontend server state

- TanStack Query, **Overview**: https://tanstack.com/query/latest/docs/framework/react/overview
  - Remote data has caching, staleness, refetch, and mutation concerns distinct from client-only UI state. MCO therefore uses TanStack Query instead of manually synchronizing fetch state through global React state.

## Deployment

- Railway, **Pre-Deploy Command**: https://docs.railway.com/deployments/pre-deploy-command
  - Alembic runs before a Railway release so a deployment is blocked if migration fails.
- Cloudflare Pages, **Redirects**: https://developers.cloudflare.com/pages/configuration/redirects/
  - The Vite SPA keeps `_redirects` in `public/` so Pages copies it into the build output.

## n8n security

- n8n security advisory **GHSA-6xcw-7xm6-48c6**: https://github.com/n8n-io/n8n/security/advisories/GHSA-6xcw-7xm6-48c6
  - The local integration stack pins n8n `2.38.2` and sets the `vm` expression engine instead of tracking `latest`. Version pins must be reviewed deliberately as new advisories/releases appear.

## What was intentionally not adopted

MCO does not add Kafka, CQRS, event sourcing, a generic repository framework, a service mesh, Redis, or a workflow/domain-event abstraction. None is required to satisfy current reliability, ownership, scale, or deployment constraints.
