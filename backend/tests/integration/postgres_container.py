"""PostgreSQL container and connection management for integration testing.

Supports:
1. Direct connection via MCO_TEST_POSTGRES_URL if provided (e.g. in CI or local Postgres).
2. Ephemeral Docker container via testcontainers-python.
3. Graceful skip if Docker daemon is unreachable and no external Postgres URL is set.
"""

from __future__ import annotations

import contextlib
import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

# Import all models to ensure metadata is populated
import app.models  # noqa: F401


def is_docker_available() -> bool:
    """Check if docker daemon is running and reachable."""
    try:
        import docker  # type: ignore[import-untyped]

        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def get_postgres_sync_url() -> str | None:
    """Retrieve external postgres sync URL if configured."""
    return os.getenv("MCO_TEST_POSTGRES_URL") or os.getenv("MCO_MIGRATION_DATABASE_URL")


class PostgresTestEnvironment:
    def __init__(self) -> None:
        self._container: Any = None
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def start(self) -> None:
        external_url = get_postgres_sync_url()
        if external_url:
            async_url = external_url.replace(
                "postgresql+psycopg://", "postgresql+asyncpg://"
            ).replace("postgresql://", "postgresql+asyncpg://")
        elif is_docker_available():
            try:
                from testcontainers.postgres import PostgresContainer

                self._container = PostgresContainer("postgres:16-alpine")
                self._container.start()
                conn_url = self._container.get_connection_url()
                async_url = conn_url.replace(
                    "postgresql+psycopg2://", "postgresql+asyncpg://"
                ).replace("postgresql://", "postgresql+asyncpg://")
            except Exception as exc:
                pytest.skip(f"Could not start Postgres testcontainer: {exc}")
        else:
            pytest.skip(
                "Docker daemon is not running and MCO_TEST_POSTGRES_URL is not set. "
                "Skipping PostgreSQL integration tests."
            )

        self._engine = create_async_engine(async_url, echo=False)
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_schema(self) -> None:
        if self._engine is None:
            raise RuntimeError("Postgres engine not initialized")
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise RuntimeError("Postgres session factory not initialized")
        async with self._session_factory() as session:
            yield session

    async def stop(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
        if self._container is not None:
            with contextlib.suppress(Exception):
                self._container.stop()
