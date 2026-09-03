from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.service import AlertService
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.ledger.repository import LedgerRepository
from app.modules.orders.repository import OrderRepository
from app.modules.reconciliation.repository import ReconciliationRepository
from app.modules.reconciliation.schemas import ReconciliationRead, ReconciliationRequest
from app.modules.reconciliation.service import ReconciliationService

router = APIRouter(prefix="/reconciliations", tags=["reconciliation"])


def get_reconciliation_service(
    session: AsyncSession = Depends(get_session),
) -> ReconciliationService:
    return ReconciliationService(
        session=session,
        repository=ReconciliationRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        order_repository=OrderRepository(session),
        ledger_repository=LedgerRepository(session),
        alert_service=AlertService(session, AlertRepository(session)),
    )


@router.post("", response_model=ReconciliationRead, status_code=status.HTTP_201_CREATED)
async def run_reconciliation(
    payload: ReconciliationRequest,
    service: ReconciliationService = Depends(get_reconciliation_service),
) -> ReconciliationRead:
    return await service.reconcile(payload)


@router.get("", response_model=list[ReconciliationRead])
async def list_reconciliations(
    service: ReconciliationService = Depends(get_reconciliation_service),
) -> list[ReconciliationRead]:
    return await service.list_history()


@router.get("/{reconciliation_id}", response_model=ReconciliationRead)
async def get_reconciliation(
    reconciliation_id: int,
    service: ReconciliationService = Depends(get_reconciliation_service),
) -> ReconciliationRead:
    return await service.get(reconciliation_id)
