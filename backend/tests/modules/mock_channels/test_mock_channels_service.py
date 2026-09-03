import pytest

from app.modules.mock_channels.service import MockChannelService
from app.shared.errors import NotFoundError


def test_mock_feed_is_deterministic() -> None:
    service = MockChannelService()

    first = service.get_order_feed("shopee")
    second = service.get_order_feed("shopee")

    assert first == second
    assert first.orders[0].external_order_id == "SP-10001"


def test_mock_feed_rejects_unknown_channel() -> None:
    with pytest.raises(NotFoundError):
        MockChannelService().get_order_feed("amazon")
