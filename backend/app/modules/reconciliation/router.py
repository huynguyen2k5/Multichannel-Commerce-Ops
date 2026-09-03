from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.alerts import AlertService, get_alert_service
from app.modules.channels import ChannelService, get_channel_service
from app.modules.ledger import LedgerService, get_ledger_service
from app.modules.orders.router import get_order_service
from app.modules.orders.service import OrderService
from app.modules.reconciliation.repository import ReconciliationRepository
from app.modules.reconciliation.schemas import ReconciliationRead, ReconciliationRequest
from app.modules.reconciliation.service import ReconciliationService

router = APIRouter(prefix="/reconciliations", tags=["reconciliation"])


def get_reconciliation_repository(
    session: AsyncSession = Depends(get_session),
) -> ReconciliationRepository:
    return ReconciliationRepository(session)


def get_reconciliation_service(
    session: AsyncSession = Depends(get_session),
    repository: ReconciliationRepository = Depends(get_reconciliation_repository),
    channel_service: ChannelService = Depends(get_channel_service),
    order_service: OrderService = Depends(get_order_service),
    ledger_service: LedgerService = Depends(get_ledger_service),
    alert_service: AlertService = Depends(get_alert_service),
) -> ReconciliationService:
    return ReconciliationService(
        session=session,
        repository=repository,
        channel_service=channel_service,
        order_service=order_service,
        ledger_service=ledger_service,
        alert_service=alert_service,
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
