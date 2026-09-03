"""create reconciliation logs

Revision ID: 0006_reconciliation
Revises: 0005_alerts
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0006_reconciliation"
down_revision: str | None = "0005_alerts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reconciliation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_system", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum("SUCCESS", "MISMATCH", "FAILED", name="reconciliationstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("records_checked", sa.Integer(), nullable=False),
        sa.Column("mismatches_found", sa.Integer(), nullable=False),
        sa.Column("detail_json", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("records_checked >= 0", name="ck_reconciliation_records_nonnegative"),
        sa.CheckConstraint("mismatches_found >= 0", name="ck_reconciliation_mismatches_nonnegative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_reconciliation_logs_source_system",
        "reconciliation_logs",
        ["source_system"],
        unique=False,
    )
    op.create_index(
        "ix_reconciliation_logs_started_at",
        "reconciliation_logs",
        ["started_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_reconciliation_logs_started_at", table_name="reconciliation_logs")
    op.drop_index("ix_reconciliation_logs_source_system", table_name="reconciliation_logs")
    op.drop_table("reconciliation_logs")
