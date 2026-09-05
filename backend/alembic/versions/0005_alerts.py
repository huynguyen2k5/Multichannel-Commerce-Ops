"""create operational alerts

Revision ID: 0005_alerts
Revises: 0004_ledger
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_alerts"
down_revision: str | None = "0004_ledger"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "LOW_STOCK",
                "RECONCILIATION_MISMATCH",
                "SYNC_FAILURE",
                name="alerttype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum("INFO", "WARNING", "CRITICAL", name="alertseverity", native_enum=False),
            nullable=False,
        ),
        sa.Column("dedup_key", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"], unique=False)
    op.create_index("ix_alerts_resolved", "alerts", ["resolved"], unique=False)
    op.create_index(
        "uq_alerts_active_dedup_key",
        "alerts",
        ["dedup_key"],
        unique=True,
        postgresql_where=sa.text("resolved = false"),
        sqlite_where=sa.text("resolved = 0"),
    )


def downgrade() -> None:
    op.drop_index("uq_alerts_active_dedup_key", table_name="alerts")
    op.drop_index("ix_alerts_resolved", table_name="alerts")
    op.drop_index("ix_alerts_created_at", table_name="alerts")
    op.drop_table("alerts")
