from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.channels.models import Channel


class ChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_code(self, code: str) -> Channel | None:
        result = await self._session.execute(select(Channel).where(Channel.code == code))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Channel]:
        result = await self._session.execute(select(Channel).order_by(Channel.code))
        return list(result.scalars().all())
