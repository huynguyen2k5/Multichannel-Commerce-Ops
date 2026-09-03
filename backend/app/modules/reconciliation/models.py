from datetime import datetime
from enum import StrEnum
from typing import Any, ClassVar

from sqlalchemy import JSON, Column, Index
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.shared.time import Timestamptz, utc_now


class ReconciliationStatus(StrEnum):
    SUCCESS = "success"
    MISMATCH = "mismatch"
    FAILED = "failed"


class ReconciliationLog(SQLModel, table=True):
    __tablename__: ClassVar[Any] = "reconciliation_logs"
    __table_args__ = (Index("ix_reconciliation_logs_started_at", "started_at"),)

    id: int | None = Field(default=None, primary_key=True)
    source_system: str = Field(min_length=1, max_length=64, index=True)
    status: ReconciliationStatus = Field(
        sa_column=Column(
            SAEnum(ReconciliationStatus, native_enum=False, length=16),
            nullable=False,
        )
    )
    records_checked: int = Field(default=0, ge=0, nullable=False)
    mismatches_found: int = Field(default=0, ge=0, nullable=False)
    detail_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    started_at: datetime = Field(default_factory=utc_now, sa_type=Timestamptz)
    completed_at: datetime = Field(default_factory=utc_now, sa_type=Timestamptz)
