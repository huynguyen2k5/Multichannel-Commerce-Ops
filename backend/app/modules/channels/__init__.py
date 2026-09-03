"""Sales channel configurations and lookup."""

from app.modules.channels.models import Channel
from app.modules.channels.service import ChannelService, get_channel_service

__all__ = [
    "Channel",
    "ChannelService",
    "get_channel_service",
]
