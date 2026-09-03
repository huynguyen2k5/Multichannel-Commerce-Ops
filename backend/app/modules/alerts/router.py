from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.schemas import AlertRead
from app.modules.alerts.service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service(session: AsyncSession = Depends(get_session)) -> AlertService:
    return AlertService(session, AlertRepository(session))


@router.get("", response_model=list[AlertRead])
async def list_alerts(
    resolved: bool | None = Query(default=False),
    service: AlertService = Depends(get_alert_service),
) -> list[AlertRead]:
    return await service.list_alerts(resolved=resolved)


@router.get("/pending-notifications", response_model=list[AlertRead])
async def pending_notifications(
    service: AlertService = Depends(get_alert_service),
) -> list[AlertRead]:
    return await service.list_pending_notifications()


@router.patch("/{alert_id}/resolve", response_model=AlertRead)
async def resolve_alert(
    alert_id: int,
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    return await service.resolve(alert_id)


@router.patch("/{alert_id}/notified", response_model=AlertRead)
async def mark_alert_notified(
    alert_id: int,
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    return await service.mark_notified(alert_id)
