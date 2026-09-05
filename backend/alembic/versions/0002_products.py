"""create products catalog

Revision ID: 0002_products
Revises: 0001_channels
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_products"
down_revision: str | None = "0001_channels"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("cost_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("current_stock", sa.Integer(), nullable=False),
        sa.Column("reorder_threshold", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("cost_price >= 0", name="ck_products_cost_nonnegative"),
        sa.CheckConstraint("current_stock >= 0", name="ck_products_stock_nonnegative"),
        sa.CheckConstraint("reorder_threshold >= 0", name="ck_products_threshold_nonnegative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku", name="uq_products_sku"),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_table("products")
