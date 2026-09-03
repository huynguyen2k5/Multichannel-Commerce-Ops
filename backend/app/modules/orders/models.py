from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, Column, Index, Numeric, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from app.shared.time import utc_now


class OrderStatus(StrEnum):
    PAID = "paid"


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint(
            "channel_id",
            "external_order_id",
            name="uq_orders_channel_external_order_id",
        ),
        CheckConstraint("total_amount >= 0", name="ck_orders_total_nonnegative"),
        Index("ix_orders_order_date", "order_date"),
    )

    id: int | None = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channels.id", index=True, nullable=False)
    external_order_id: str = Field(min_length=1, max_length=100)
    order_date: datetime = Field(nullable=False)
    status: OrderStatus = Field(
        default=OrderStatus.PAID,
        sa_column=Column(SAEnum(OrderStatus, native_enum=False, length=16), nullable=False),
    )
    total_amount: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))
    source_updated_at: datetime | None = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_items_price_nonnegative"),
        CheckConstraint("unit_cost >= 0", name="ck_order_items_cost_nonnegative"),
        Index("ix_order_items_order_id", "order_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", nullable=False)
    product_id: int = Field(foreign_key="products.id", index=True, nullable=False)
    quantity: int = Field(nullable=False)
    unit_price: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))
    unit_cost: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))
