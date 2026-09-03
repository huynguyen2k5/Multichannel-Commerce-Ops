from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.channels.models import Channel
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import OrderImportRequest, OrderImportStatus
from app.modules.orders.service import OrderService
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService


async def _service(session: AsyncSession) -> OrderService:
    return OrderService(
        session,
        OrderRepository(session),
        ChannelService(ChannelRepository(session)),
        ProductService(ProductRepository(session)),
    )


async def test_same_order_import_is_a_no_op_on_retry(session: AsyncSession) -> None:
    session.add(Channel(code="shopee", name="Shopee", platform_type="marketplace"))
    session.add(
        Product(
            sku="TEE-BLK-M",
            name="Black Tee M",
            cost_price=Decimal("150000.00"),
            current_stock=10,
            reorder_threshold=2,
        )
    )
    await session.commit()

    payload = OrderImportRequest(
        channel="shopee",
        external_order_id="SP-10001",
        order_date=datetime(2026, 9, 1, tzinfo=UTC),
        total_amount=Decimal("500000.00"),
        items=[{"sku": "TEE-BLK-M", "quantity": 2, "unit_price": "250000.00"}],
    )
    service = await _service(session)

    first = await service.import_order(payload)
    second = await service.import_order(payload)

    assert first.status is OrderImportStatus.IMPORTED
    assert second.status is OrderImportStatus.DUPLICATE
    assert first.order_id == second.order_id
