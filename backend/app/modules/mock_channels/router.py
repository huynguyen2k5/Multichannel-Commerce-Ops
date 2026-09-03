from fastapi import APIRouter

from app.modules.mock_channels.schemas import MockOrderFeed
from app.modules.mock_channels.service import MockChannelService

router = APIRouter(prefix="/mock/v1", tags=["mock channels"])
_service = MockChannelService()


@router.get("/{channel}/orders", response_model=MockOrderFeed)
async def get_mock_orders(channel: str) -> MockOrderFeed:
    return _service.get_order_feed(channel)
