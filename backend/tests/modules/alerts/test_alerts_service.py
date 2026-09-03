from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.models import AlertType
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.schemas import LowStockAlertRequest
from app.modules.alerts.service import AlertService


async def test_low_stock_alert_is_deduplicated_while_active(session: AsyncSession) -> None:
    request = LowStockAlertRequest(
        sku="CAP-WHT",
        current_stock=2,
        reorder_threshold=2,
    )
    repository = AlertRepository(session)
    service = AlertService(session, repository)

    async with session.begin():
        first = await service.create_low_stock(request)
        second = await service.create_low_stock(request)

    assert first is not None and second is not None
    assert first.id == second.id
    assert first.type is AlertType.LOW_STOCK


async def test_resolved_low_stock_can_open_again(session: AsyncSession) -> None:
    request = LowStockAlertRequest(
        sku="TEE-BLK-M",
        current_stock=1,
        reorder_threshold=2,
    )
    service = AlertService(session, AlertRepository(session))

    async with session.begin():
        first = await service.create_low_stock(request)
    assert first is not None and first.id is not None

    resolved = await service.resolve(first.id)
    assert resolved.resolved is True
    assert session.in_transaction() is False

    async with session.begin():
        second = await service.create_low_stock(request)

    assert second is not None
    assert second.id != first.id


async def test_mark_notified_commits_delivery_state(session: AsyncSession) -> None:
    request = LowStockAlertRequest(
        sku="BAG-BLK",
        current_stock=1,
        reorder_threshold=2,
    )
    service = AlertService(session, AlertRepository(session))

    async with session.begin():
        alert = await service.create_low_stock(request)
    assert alert is not None and alert.id is not None

    notified = await service.mark_notified(alert.id)

    assert notified.notified_at is not None
    assert session.in_transaction() is False


async def test_alert_repository_list_all(session: AsyncSession) -> None:
    repository = AlertRepository(session)
    alerts = await repository.list_all()
    assert isinstance(alerts, list)
