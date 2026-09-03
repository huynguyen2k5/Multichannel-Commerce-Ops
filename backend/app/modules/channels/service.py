from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.channels.models import Channel
from app.modules.channels.repository import ChannelRepository
from app.shared.errors import NotFoundError


class ChannelService:
    def __init__(self, repository: ChannelRepository) -> None:
        self._repository = repository

    async def get_by_code(self, code: str) -> Channel:
        channel = await self._repository.get_by_code(code)
        if channel is None:
            raise NotFoundError(
                "CHANNEL_NOT_FOUND",
                f"Commerce channel '{code}' does not exist",
                details={"channel": code},
            )
        return channel


def get_channel_service(session: AsyncSession = Depends(get_session)) -> ChannelService:
    return ChannelService(ChannelRepository(session))
