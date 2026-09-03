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
