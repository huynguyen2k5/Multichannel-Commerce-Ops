from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.shared.time import Timestamptz, utc_now


class Product(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_products_sku"),
        CheckConstraint("cost_price >= 0", name="ck_products_cost_nonnegative"),
        CheckConstraint("current_stock >= 0", name="ck_products_stock_nonnegative"),
        CheckConstraint("reorder_threshold >= 0", name="ck_products_threshold_nonnegative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    sku: str = Field(min_length=1, max_length=64, index=True)
    name: str = Field(min_length=1, max_length=200)
    cost_price: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))
    current_stock: int = Field(default=0, nullable=False)
    reorder_threshold: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=utc_now, sa_type=Timestamptz)
    updated_at: datetime = Field(default_factory=utc_now, sa_type=Timestamptz)
