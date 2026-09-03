import json
from pathlib import Path

from app.modules.mock_channels.schemas import MockOrderFeed
from app.shared.errors import NotFoundError

_DATA_DIR = Path(__file__).parent / "data"
_SUPPORTED_CHANNELS = frozenset({"shopee", "tiktok", "website"})


class MockChannelService:
    def get_order_feed(self, channel: str) -> MockOrderFeed:
        if channel not in _SUPPORTED_CHANNELS:
            raise NotFoundError(
                "MOCK_CHANNEL_NOT_FOUND",
                f"Mock channel '{channel}' is not supported",
                details={"channel": channel},
            )
        path = _DATA_DIR / f"{channel}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        return MockOrderFeed.model_validate(payload)
