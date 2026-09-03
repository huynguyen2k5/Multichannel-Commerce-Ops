# ADR-007: Modular Monolith Boundary & Encapsulation Rules

- Status: Accepted
- Date: 2026-09-03
- Extends: ADR-001

## Context

While ADR-001 established a modular monolith architecture for MCO, several inter-module boundaries previously leaked persistence details:
1. Services in one module directly imported and invoked repositories of other modules (e.g., `ReconciliationService` orchestrating `OrderRepository` and `LedgerRepository`).
2. Routers composed multiple foreign repositories directly inline.
3. Lack of automated boundary checks risked architectural erosion over time.

## Decision

1. **Services as Single Entry Points**:
   A module must only interact with another module via that module's public service facade. Direct repository-to-repository or service-to-foreign-repository communication is strictly forbidden.
2. **Internal Repository Privacy**:
   Repositories are private persistence adapters belonging exclusively to their containing module. Repositories must never be exported from module `__all__` facades or imported across module boundaries.
3. **Reporting Read-Model Exception (ADR-001 Preserved)**:
   The `reports` module maintains an explicit architectural exception. To produce high-performance, single-query cross-domain aggregates without distributed N+1 query amplification, `ReportsRepository` may execute cross-domain read-only SQL queries joining `orders`, `channels`, and `ledger_entries`.
4. **Machine Enforcement via AST Linter**:
   An AST-based boundary validation script (`scripts/check_module_boundaries.py`) is wired into CI (`.github/workflows/ci.yml`) and local verification (`make check`). Any illegal cross-module internal or repository import fails the build.

## Consequences

- Architectural boundaries remain clean and decoupled.
- Module implementations can refactor their internal schemas, queries, or tables without breaking other bounded contexts.
- Quality gates reject architectural regressions automatically.
