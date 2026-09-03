# ADR-009: Public Facade Pattern & Machine-Enforced Boundary Linter

- Status: Accepted
- Date: 2026-09-03
- Extends: ADR-001, ADR-007

## Context

In Python modular monoliths, standard `import` statements allow any file to import any symbol from any package unless conventions are strictly defined and machine-enforced. Without explicit facades, consumers inadvertently couple to internal classes, private helpers, or persistence layers.

## Decision

1. **Explicit Module Facade (`__all__`)**:
   Every bounded context in `backend/app/modules/<module>/__init__.py` must declare an explicit `__all__` defining its narrow public surface.
2. **Export Rules**:
   - MUST export: Public services, public schemas/DTOs, public FastAPI router, and public domain models (where external consumption is required).
   - MUST NOT export: Any class ending with `Repository` or module-internal persistence helpers.
3. **AST-Based Linter**:
   The script `scripts/check_module_boundaries.py` walks the abstract syntax tree of all Python files in `app/modules/`. It enforces:
   - Rule 1: No cross-module repository imports (except `reports`).
   - Rule 2: Services cannot reach into another module's repository.
   - Rule 3: Cross-module imports must only target public module facades or whitelisted submodules (`schemas`, `service`, `models`, `router`).
4. **Testing Surface Verification**:
   Architectural tests in `backend/tests/architecture/test_boundaries.py` and `backend/tests/test_module_facades.py` assert that all facades define `__all__`, hide repositories, and maintain 0 violations across the codebase.

## Consequences

- Clear, documented, and enforced API contracts for each module.
- Accidental architectural drift is caught by the compiler/test runner before code merges.
