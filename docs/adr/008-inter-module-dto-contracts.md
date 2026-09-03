# ADR-008: Inter-Module DTO Contract Decoupling

- Status: Accepted
- Date: 2026-09-03
- Extends: ADR-001, ADR-004

## Context

Previously, inter-module service invocations passed SQLAlchemy/SQLModel ORM entities directly across module boundaries:
- `OrderService` passed `Order` and `list[OrderItem]` ORM instances to `LedgerService.record_sale()`.
- `InventoryService` passed `Product` ORM entity to `AlertService.create_low_stock()`.

Passing full ORM models across bounded contexts introduces hidden coupling:
1. The receiving module becomes coupled to the internal database schema and column definitions of the caller.
2. ORM session-attached state can produce detached instance errors or accidental session flushing.
3. Unit tests require mocking entire database entity trees instead of plain data transfer objects.

## Decision

1. **Focused DTO Schemas for Cross-Module Operations**:
   Modules must define and accept explicit, minimal Pydantic DTOs for inter-module contracts:
   - `OrderSaleRecord` and `SaleItemRecord` in `app.modules.ledger.schemas` for ledger posting.
   - `LowStockAlertRequest` in `app.modules.alerts.schemas` for operational inventory alerts.
2. **Caller Adapts to Callee Contract**:
   The caller service extracts the necessary fields from its internal entities and constructs the callee's DTO.
3. **Preservation of Transactional Boundary**:
   The caller passes its active `AsyncSession` to dependent services (or dependency providers). The complete operation (e.g. order creation, inventory decrement, and financial ledger recording) participates in a single ACID transaction boundary while remaining decoupled at the domain contract layer.

## Consequences

- Domain boundaries communicate via explicit, typed, serializable contracts.
- Modules can be tested cleanly with lightweight DTOs.
- Internal schema migrations in one module do not ripple into foreign modules.
