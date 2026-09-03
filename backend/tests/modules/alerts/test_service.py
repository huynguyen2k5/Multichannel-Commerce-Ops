from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.models import AlertType
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.service import AlertService
from app.modules.products.models import Product


async def test_low_stock_alert_is_deduplicated_while_active(session: AsyncSession) -> None:
    product = Product(
        sku="CAP-WHT",
        name="White Cap",
        cost_price=Decimal("180000.00"),
        current_stock=2,
        reorder_threshold=2,
    )
    repository = AlertRepository(session)
    service = AlertService(session, repository)

    first = await service.create_low_stock(product)
    second = await service.create_low_stock(product)

    assert first is not None and second is not None
    assert first.id == second.id
    assert first.type is AlertType.LOW_STOCK


async def test_resolved_low_stock_can_open_again(session: AsyncSession) -> None:
    product = Product(
        sku="TEE-BLK-M",
        name="Black Tee",
        cost_price=Decimal("150000.00"),
        current_stock=1,
        reorder_threshold=2,
    )
    service = AlertService(session, AlertRepository(session))

    first = await service.create_low_stock(product)
    assert first is not None and first.id is not None
    await service.resolve(first.id)
    second = await service.create_low_stock(product)

    assert second is not None
    assert second.id != first.id
