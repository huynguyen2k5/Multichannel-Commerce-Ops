# ADR-003: Make source order import idempotent by business identity

- Status: Accepted
- Date: 2026-09-03

## Context

Scheduled automation and network failures create legitimate retries. Reprocessing a successful order would otherwise double-decrease stock and double-create accounting entries.

## Decision

The canonical source identity is `(channel_id, external_order_id)` and is protected by a database unique constraint. The service performs a fast duplicate lookup, but the database remains the final authority for concurrent requests. A uniqueness race is translated into the existing imported order rather than a second side effect.

## Consequences

n8n can safely retry imports. Duplicate requests return a successful no-op response. The ledger also enforces one entry per `(order_id, entry_type)` as a second integrity boundary.
