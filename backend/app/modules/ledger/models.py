from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, Column, Numeric, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.shared.time import utc_now


class LedgerEntryType(StrEnum):
    REVENUE = "revenue"
    COGS = "cogs"


class LedgerEntry(SQLModel, table=True):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        UniqueConstraint("order_id", "entry_type", name="uq_ledger_order_entry_type"),
        CheckConstraint("amount >= 0", name="ck_ledger_amount_nonnegative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True, nullable=False)
    entry_type: LedgerEntryType = Field(
        sa_column=Column(
            SAEnum(LedgerEntryType, native_enum=False, length=16),
            nullable=False,
        )
    )
    amount: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
