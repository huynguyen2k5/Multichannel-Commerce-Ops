from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Enum as SAEnum, Index, Text, text
from sqlmodel import Field, SQLModel

from app.shared.time import utc_now


class AlertType(str, Enum):
    LOW_STOCK = "low_stock"
    RECONCILIATION_MISMATCH = "reconciliation_mismatch"
    SYNC_FAILURE = "sync_failure"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"
    __table_args__ = (
        Index(
            "uq_alerts_active_dedup_key",
            "dedup_key",
            unique=True,
            postgresql_where=text("resolved = false"),
            sqlite_where=text("resolved = 0"),
        ),
        Index("ix_alerts_created_at", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    type: AlertType = Field(
        sa_column=Column(SAEnum(AlertType, native_enum=False, length=40), nullable=False)
    )
    severity: AlertSeverity = Field(
        sa_column=Column(SAEnum(AlertSeverity, native_enum=False, length=16), nullable=False)
    )
    dedup_key: str = Field(min_length=1, max_length=200, nullable=False)
    message: str = Field(sa_column=Column(Text, nullable=False))
    resolved: bool = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    resolved_at: datetime | None = Field(default=None, nullable=True)
    notified_at: datetime | None = Field(default=None, nullable=True)
