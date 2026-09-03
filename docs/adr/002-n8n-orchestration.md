# ADR-002: n8n owns scheduling; FastAPI owns business rules

- Status: Accepted
- Date: 2026-09-03

## Context

The project demonstrates workflow automation and needs scheduled source synchronization, reconciliation, and Telegram delivery. Running both n8n cron and an application scheduler would create two owners for timing and retry behavior.

## Decision

n8n owns schedules, transport normalization, and external integration calls. FastAPI owns validation, idempotency, inventory, accounting calculations, reconciliation decisions, alert deduplication, and database transactions.

## Consequences

Workflow JSON stays thin and replaceable. Business behavior remains testable in Python without running n8n. APScheduler is not part of V1 runtime.
