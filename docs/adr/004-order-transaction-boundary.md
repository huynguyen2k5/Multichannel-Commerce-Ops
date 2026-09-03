# ADR-004: Order import owns one ACID transaction

- Status: Accepted
- Date: 2026-09-03

## Context

A paid order creates several state changes that are only valid together: normalized order/items, stock consumption, revenue, COGS, and possible low-stock alert creation.

## Decision

`OrderService.import_order()` owns one SQLAlchemy `AsyncSession.begin()` transaction. Inventory, ledger, repository, and alert sub-operations share that session and flush into the same transaction; they do not commit independently.

Inventory consumption is an atomic conditional SQL update (`current_stock >= quantity`) so concurrent consumers cannot both pass an application-side check and oversell the same units.

## Consequences

Any failure before commit rolls back the complete operation. Integration tests inject a downstream ledger failure and verify order and inventory rollback.
