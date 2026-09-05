from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.channels.models import Channel
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.inventory.service import InventoryService
from app.modules.ledger.repository import LedgerRepository
from app.modules.ledger.service import LedgerService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderImportItem,
    OrderImportRequest,
    OrderImportStatus,
)
from app.modules.orders.service import OrderService
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService


async def _service(session: AsyncSession) -> OrderService:
    product_repo = ProductRepository(session)
    product_service = ProductService(product_repo)
    return OrderService(
        session,
        OrderRepository(session),
        ChannelService(ChannelRepository(session)),
        product_service,
        InventoryService(session, product_service),
        LedgerService(LedgerRepository(session)),
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
        items=[OrderImportItem(sku="TEE-BLK-M", quantity=2, unit_price=Decimal("250000.00"))],
    )
    service = await _service(session)

    first = await service.import_order(payload)
    second = await service.import_order(payload)

    assert first.status is OrderImportStatus.IMPORTED
    assert second.status is OrderImportStatus.DUPLICATE
    assert first.order_id == second.order_id

    product = await ProductRepository(session).get_by_sku("TEE-BLK-M")
    assert product is not None
    assert product.current_stock == 8

    entries = await LedgerRepository(session).get_for_order(first.order_id)
    assert len(entries) == 2


async def test_insufficient_stock_rolls_back_order(session: AsyncSession) -> None:
    session.add(Channel(code="shopee", name="Shopee", platform_type="marketplace"))
    session.add(
        Product(
            sku="TEE-BLK-M",
            name="Black Tee M",
            cost_price=Decimal("150000.00"),
            current_stock=1,
            reorder_threshold=2,
        )
    )
    await session.commit()

    payload = OrderImportRequest(
        channel="shopee",
        external_order_id="SP-OUT-OF-STOCK",
        order_date=datetime(2026, 9, 1, tzinfo=UTC),
        total_amount=Decimal("500000.00"),
        items=[OrderImportItem(sku="TEE-BLK-M", quantity=2, unit_price=Decimal("250000.00"))],
    )
    service = await _service(session)

    from app.shared.errors import BusinessRuleError

    try:
        await service.import_order(payload)
    except BusinessRuleError as exc:
        assert exc.code == "INSUFFICIENT_STOCK"
    else:
        raise AssertionError("expected insufficient stock failure")

    channel = await ChannelRepository(session).get_by_code("shopee")
    assert channel is not None and channel.id is not None
    assert await OrderRepository(session).get_by_identity(channel.id, "SP-OUT-OF-STOCK") is None
