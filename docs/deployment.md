# Containerization & Infrastructure Architecture

## Overview

The Multichannel Commerce Operations (MCO) platform is fully containerized across all tiers. Each tier can run as an independent OCI container image or orchestrated locally via Docker Compose.

---

## Container Packaging

### 1. Backend Service (`backend/Dockerfile`)
- **Runtime**: `python:3.12-slim`
- **Security**: Runs under an unprivileged system user (`app`) with drop-in non-root permissions.
- **Healthcheck**: Probes `GET /health` with automatic retries and exponential start period.
- **Port**: `8000`

Required environment variables:
```text
MCO_ENVIRONMENT=production
MCO_LOG_LEVEL=INFO
MCO_DATABASE_URL=postgresql+asyncpg://...-pooler.../...
MCO_MIGRATION_DATABASE_URL=postgresql+psycopg://...direct.../...
MCO_CORS_ORIGINS=http://localhost:5173,https://your-domain.com
```

### 2. Frontend Dashboard (`frontend/Dockerfile`)
- **Multi-Stage Build**:
  - *Builder*: `node:22-alpine` compiling React 19 + TypeScript + Vite with `pnpm`.
  - *Runtime*: `nginx:1.27-alpine` serving static bundle with Gzip compression, asset caching, and SPA fallback routing.
- **Reverse Proxy**: `frontend/nginx.conf` proxies `/api/` directly to `http://backend:8000/api/` and provides `/health` routing.
- **Port**: `80` (mapped to `5173` in Docker Compose)

### 3. Database Layer (PostgreSQL / Neon)
- **Local Engine**: `postgres:16-alpine` with persistent volume `mco_postgres_data`.
- **Production Engine**: Neon Serverless Postgres via `neon link` and connection pooling (`NullPool` with asyncpg).
- **Schema Management**: Alembic migrations execute `alembic upgrade head` before backend traffic is routed.
- **Seed Catalog**: `python -m app.scripts.seed_demo` bootstraps initial channels and product master data.

### 4. Workflow Automation (`n8n`)
- **Image**: `docker.n8n.io/n8nio/n8n:2.38.2`
- **Port**: `5678`
- **Security**: Encrypted state with `N8N_ENCRYPTION_KEY`.

---

## Orchestration with Docker Compose

Run the complete multi-container stack from the repository root:

```bash
# Start all services in the background
docker compose up -d

# Check service health and logs
docker compose ps
docker compose logs -f

# Teardown stack and preserve volumes
docker compose down
```
