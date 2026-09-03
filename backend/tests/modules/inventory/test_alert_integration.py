from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.service import AlertService
from app.modules.inventory.service import InventoryService
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository


async def test_stock_crossing_threshold_creates_one_active_alert(session: AsyncSession) -> None:
    product = Product(
        sku="CAP-WHT",
        name="White Cap",
        cost_price=Decimal("180000.00"),
        current_stock=4,
        reorder_threshold=2,
    )
    session.add(product)
    await session.commit()
    assert product.id is not None

    alerts = AlertService(session, AlertRepository(session))
    inventory = InventoryService(session, ProductRepository(session), alert_service=alerts)

    async with session.begin():
        await inventory.consume(product.id, 2)
    async with session.begin():
        await inventory.consume(product.id, 1)

    active = await AlertRepository(session).list(resolved=False)
    assert len(active) == 1
    assert active[0].dedup_key == "low_stock:CAP-WHT"
