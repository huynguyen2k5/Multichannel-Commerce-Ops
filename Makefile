.PHONY: \
	backend-install backend-lint backend-typecheck backend-test backend-compile \
	frontend-install frontend-lint frontend-test frontend-build \
	artifacts boundaries migrate seed check

backend-install:
	cd backend && python3 -m pip install -e '.[dev]'

backend-lint:
	cd backend && ruff check app tests

backend-typecheck:
	cd backend && mypy app

backend-test:
	cd backend && pytest

backend-compile:
	cd backend && python3 -m compileall -q app tests alembic

frontend-install:
	pnpm install --frozen-lockfile

frontend-lint:
	pnpm --filter mco-frontend lint

frontend-test:
	pnpm --filter mco-frontend test

frontend-build:
	pnpm --filter mco-frontend build

boundaries:
	python3 scripts/check_module_boundaries.py

artifacts:
	python3 scripts/validate_artifacts.py

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python3 -m app.scripts.seed_demo

check: boundaries backend-lint backend-typecheck backend-test backend-compile frontend-lint frontend-test frontend-build artifacts
