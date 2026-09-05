"""create channels catalog

Revision ID: 0001_channels
Revises:
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_channels"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("platform_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_channels_code"),
    )
    op.create_index("ix_channels_code", "channels", ["code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_channels_code", table_name="channels")
    op.drop_table("channels")
