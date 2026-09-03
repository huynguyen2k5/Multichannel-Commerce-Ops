import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.channels.models import Channel
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.shared.errors import NotFoundError


async def test_channel_lookup_returns_matching_channel(session: AsyncSession) -> None:
    session.add(Channel(code="shopee", name="Shopee", platform_type="marketplace"))
    await session.commit()

    service = ChannelService(ChannelRepository(session))
    channel = await service.get_by_code("shopee")

    assert channel.name == "Shopee"


async def test_channel_lookup_rejects_unknown_channel(session: AsyncSession) -> None:
    service = ChannelService(ChannelRepository(session))

    with pytest.raises(NotFoundError) as error:
        await service.get_by_code("unknown")

    assert error.value.code == "CHANNEL_NOT_FOUND"
