from datetime import UTC, datetime

from sqlalchemy import DateTime


class Timestamptz(DateTime):
    """SQLAlchemy timezone-aware DateTime column type for PostgreSQL timestamptz."""

    def __init__(self) -> None:
        super().__init__(timezone=True)


def utc_now() -> datetime:
    return datetime.now(UTC)
