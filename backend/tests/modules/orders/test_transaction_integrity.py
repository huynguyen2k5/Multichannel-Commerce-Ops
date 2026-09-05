from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.channels.models import Channel
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.inventory.service import InventoryService
from app.modules.ledger.repository import LedgerRepository
from app.modules.ledger.schemas import OrderSaleRecord
from app.modules.ledger.service import LedgerService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import OrderImportItem, OrderImportRequest
from app.modules.orders.service import OrderService
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService


class FailingLedgerService(LedgerService):
    async def record_sale(self, record: OrderSaleRecord) -> None:
        raise RuntimeError("simulated ledger failure")


async def test_ledger_failure_rolls_back_order_items_and_inventory(session: AsyncSession) -> None:
    channel = Channel(code="shopee", name="Shopee", platform_type="marketplace")
    product = Product(
        sku="TEE-BLK-M",
        name="Black Tee M",
        cost_price=Decimal("150000.00"),
        current_stock=10,
        reorder_threshold=2,
    )
    session.add_all([channel, product])
    await session.commit()

    product_repository = ProductRepository(session)
    order_repository = OrderRepository(session)
    service = OrderService(
        session=session,
        repository=order_repository,
        channel_service=ChannelService(ChannelRepository(session)),
        product_service=ProductService(product_repository),
        inventory_service=InventoryService(session, ProductService(product_repository)),
        ledger_service=FailingLedgerService(LedgerRepository(session)),
    )
    payload = OrderImportRequest(
        channel="shopee",
        external_order_id="SP-ROLLBACK",
        order_date=datetime(2026, 9, 1, tzinfo=UTC),
        total_amount=Decimal("500000.00"),
        items=[OrderImportItem(sku="TEE-BLK-M", quantity=2, unit_price=Decimal("250000.00"))],
    )

    with pytest.raises(RuntimeError, match="simulated ledger failure"):
        await service.import_order(payload)

    stored_channel = await ChannelRepository(session).get_by_code("shopee")
    assert stored_channel is not None and stored_channel.id is not None
    assert await order_repository.get_by_identity(stored_channel.id, "SP-ROLLBACK") is None

    stored_product = await product_repository.get_by_sku("TEE-BLK-M")
    assert stored_product is not None
    assert stored_product.current_stock == 10
