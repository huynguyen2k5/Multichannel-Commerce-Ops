from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.channels.models import Channel
from app.modules.orders.models import Order, OrderItem
from app.modules.orders.repository import OrderRepository
from app.modules.products.models import Product


async def test_order_repository_persists_cost_snapshot(session: AsyncSession) -> None:
    channel = Channel(code="shopee", name="Shopee", platform_type="marketplace")
    product = Product(
        sku="TEE-BLK-M",
        name="Black Tee M",
        cost_price=Decimal("150000.00"),
        current_stock=10,
        reorder_threshold=2,
    )
    session.add_all([channel, product])
    await session.flush()
    assert channel.id is not None
    assert product.id is not None

    repository = OrderRepository(session)
    order = await repository.create(
        Order(
            channel_id=channel.id,
            external_order_id="SP-10001",
            order_date=datetime(2026, 9, 1, tzinfo=UTC),
            total_amount=Decimal("250000.00"),
        )
    )
    assert order.id is not None
    await repository.add_items(
        [
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=1,
                unit_price=Decimal("250000.00"),
                unit_cost=product.cost_price,
            )
        ]
    )

    items = await repository.get_items(order.id)
    assert items[0].unit_cost == Decimal("150000.00")
