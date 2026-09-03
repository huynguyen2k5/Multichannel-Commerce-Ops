from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.shared.time import utc_now


class Channel(SQLModel, table=True):
    __tablename__ = "channels"
    __table_args__ = (UniqueConstraint("code", name="uq_channels_code"),)

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(min_length=1, max_length=32, index=True)
    name: str = Field(min_length=1, max_length=100)
    platform_type: str = Field(min_length=1, max_length=32)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
