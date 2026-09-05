"""create operational ledger

Revision ID: 0004_ledger
Revises: 0003_orders
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_ledger"
down_revision: str | None = "0003_orders"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column(
            "entry_type",
            sa.Enum("REVENUE", "COGS", name="ledgerentrytype", native_enum=False),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount >= 0", name="ck_ledger_amount_nonnegative"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", "entry_type", name="uq_ledger_order_entry_type"),
    )
    op.create_index("ix_ledger_entries_order_id", "ledger_entries", ["order_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ledger_entries_order_id", table_name="ledger_entries")
    op.drop_table("ledger_entries")
