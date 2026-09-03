# Contributing to MCO

MCO follows trunk-based development with short-lived, single-scope branches. All code lands on `main` through reviewed pull requests that pass all quality gates.

---

## 1. Branch Strategy

Use lowercase kebab-case with a descriptive prefix:

| Prefix | Use Case | Example |
| :--- | :--- | :--- |
| `feat/` | New functionality or API capability | `feat/order-idempotent-import` |
| `fix/` | Bug fixes or test repairs | `fix/inventory-oversell-check` |
| `refactor/` | Structural improvements without behavioral change | `refactor/public-facades` |
| `test/` | Adding or updating tests | `test/postgres-critical-path` |
| `docs/` | Architecture records and guides | `docs/architecture-hardening` |
| `ci/` | Continuous integration and tooling | `ci/module-boundary-linter` |

Keep branches short-lived and single-scoped. Do not bundle unrelated frontend, backend, and infrastructure changes into one PR.

---

## 2. Commit Standards

We enforce **Conventional Commits**:

```text
<type>(<scope>): <short description>
```

- **Types**: `feat`, `fix`, `refactor`, `test`, `docs`, `ci`, `chore`, `perf`.
- **Scopes**: Module name (`orders`, `inventory`, `ledger`, `alerts`, `reports`, `reconciliation`, `channels`, `products`) or layer (`arch`, `frontend`, `infra`).

Examples:
```text
feat(inventory): enforce atomic conditional stock decrement
fix(frontend): enable vitest globals in test runner
refactor(ledger): decouple order sale recording DTO contract
test(integration): verify commerce pipeline on postgres
docs(adr): document module boundary and encapsulation rules
```

---

## 3. Modular Monolith Architecture Rules

### Adding a New Module
When introducing a new bounded context under `backend/app/modules/<module>/`:
1. **Public Facade**: Define explicit `__all__` in `__init__.py`.
2. **Encapsulate Repositories**: **Never** export `*Repository` classes in `__all__`. Repositories are private module-internal persistence adapters.
3. **Expose Public Surface**: Export only public services, DTO schemas, domain models, and FastAPI routers.
4. **Automated Verification**: Must pass `python scripts/check_module_boundaries.py`.

### Inter-Module Communication
1. **No Cross-Module Repository Imports**: A module must never import another module's repository.
   - *Exception*: `reports/repository.py` is the only permitted cross-domain reader for optimized read-model SQL aggregations (ADR-001).
2. **Services as Entry Points**: Always communicate across modules through the target module's public `Service`.
3. **DTO Contracts**: Pass lightweight Pydantic DTOs across boundaries (e.g. `OrderSaleRecord`, `LowStockAlertRequest`), never foreign ORM entities (ADR-008).
4. **Transaction Integrity**: Pass the active `AsyncSession` to dependency providers so multi-module operations share the single ACID transaction boundary.

---

## 4. Definition of Done & Quality Gates

Before submitting a pull request, verify locally that all checks succeed:

```bash
make check
```

The pull request quality checklist:
- [ ] `python scripts/check_module_boundaries.py` passes with 0 violations.
- [ ] `ruff check app tests` passes with 0 errors.
- [ ] `mypy app` passes in strict mode with 0 errors.
- [ ] `pytest` passes 100% of unit and integration tests.
- [ ] `pnpm run lint` and `pnpm run test` pass in `frontend/`.
- [ ] `pnpm run build` generates production bundle cleanly.
- [ ] PR title adheres to Conventional Commit format.
- [ ] Relevant ADRs added in `docs/adr/` for structural changes.
