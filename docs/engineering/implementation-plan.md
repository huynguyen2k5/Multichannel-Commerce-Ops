# MCO implementation map

This document is the task/branch map for MCO V1. It prevents large “implement a module” changes and gives agents a bounded unit of work.

## Dependency order

```text
repository foundation
  -> FastAPI/error/logging/database
  -> channels + products
  -> deterministic mock sources
  -> order persistence + import contract + idempotency
  -> inventory
  -> ledger
  -> transaction-integrity tests
  -> reports
  -> n8n order sync
  -> alerts + Telegram delivery
  -> reconciliation + reconciliation schedule
  -> React foundation + typed API layer
  -> dashboard/pages
  -> CI + deployment + runbook
```

## Completed scopes

| Capability | Branch | Representative commits |
|---|---|---|
| Repository foundation | `chore/repo-foundation` | repo structure, scope docs |
| FastAPI foundation | `feat/backend-foundation` | app, config, health |
| Error contract | `feat/error-contract` | request ID, error envelope, structured logging |
| Database foundation | `feat/database-foundation` | async session, Alembic direct URL |
| Channels | `feat/channels-catalog` | model, repository, service, migration, tests |
| Products | `feat/products-catalog` | constraints, repository, migration, tests |
| Mock sources | `feat/mock-channel-apis` | deterministic feeds and endpoint tests |
| Order persistence | `feat/orders-persistence` | Order/OrderItem and uniqueness |
| Import contract | `feat/orders-import-contract` | typed request/response validation |
| Idempotent import | `feat/orders-idempotent-import` | duplicate no-op and race handling |
| Inventory | `feat/inventory-consumption` | atomic conditional stock update |
| Order/inventory | `feat/orders-inventory-integration` | transaction integration and rollback tests |
| Ledger | `feat/ledger-sale-entries` | revenue/COGS entries and constraints |
| Order/ledger | `feat/orders-ledger-integration` | ledger in import transaction |
| Atomicity | `test/orders-transaction-integrity` | injected failure rollback coverage |
| Order queries | `feat/orders-query` | list/detail endpoints |
| Daily reporting | `feat/reports-daily-performance` | read-only aggregate report |
| Low-stock alerts | `feat/alerts-low-stock` | persistence, active dedupe, APIs |
| Alert integration | `feat/inventory-low-stock-alerts` | threshold alert within stock transaction |
| Reconciliation | `feat/reconciliation-engine` | source/order/ledger comparison and alerts |
| Demo bootstrap | `feat/demo-seed` | idempotent catalog seed |
| Operability | `feat/operability-baseline` | readiness and request telemetry |
| Automation | `feat/automation-workflows` | order, reconciliation, Telegram workflows |
| Frontend foundation | `feat/frontend-foundation` | React/Vite/Tailwind shell |
| Typed frontend data | `feat/frontend-api-integration` | Zod + TanStack Query hooks |
| Dashboard | `feat/dashboard-operations` | KPIs, channel charts, status cards |
| Operational pages | `feat/frontend-*-page` | orders, inventory, alerts, reconciliation |
| Frontend tests | `test/frontend-baseline` | component/format baseline |
| CI | `ci/quality-gates` | backend/frontend/migration gates |
| Deployment | `build/deployment-baseline` | Docker, Railway, Cloudflare, compose |
| Alert delivery fix | `fix/alert-delivery-persistence` | committed mutation + post-send marker |
| Critical-path test | `test/core-commerce-pipeline` | import -> report -> reconcile integration |

## Scope rule for future tasks

Every coding prompt should specify `IN SCOPE`, `OUT OF SCOPE`, acceptance criteria, expected tests, and expected commit(s). For example:

```text
Branch: feat/reports-product-performance

IN SCOPE
- read-only product performance query
- typed response schema
- endpoint and tests

OUT OF SCOPE
- Power BI
- order mutation
- inventory mutation
- schema changes unless query evidence requires one
- unrelated refactors
```

Do not create abstractions for hypothetical future modules. Add a boundary only when a current use case needs it.
