# ADR-005: Use React + Vite + Tailwind CSS for the operations UI

- Status: Accepted
- Date: 2026-09-03

## Context

MCO already has FastAPI as its business/API backend. The UI is an authenticated-style internal SPA concept rather than a public SEO-oriented website. Adding a second web server/BFF through Next.js would not serve a current requirement.

## Decision

Use React + Vite + Tailwind CSS. TanStack Query owns remote server state, Zod validates runtime API responses, and Recharts renders the small set of operational charts.

## Consequences

Frontend/backend boundaries remain explicit. The frontend never connects directly to PostgreSQL and does not calculate authoritative revenue/COGS/profit rules.
