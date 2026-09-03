from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.service import AlertService
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.inventory.service import InventoryService
from app.modules.ledger.repository import LedgerRepository
from app.modules.ledger.service import LedgerService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderDetail,
    OrderImportRequest,
    OrderImportResponse,
    OrderImportStatus,
    OrderRead,
)
from app.modules.orders.service import OrderService
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(session: AsyncSession = Depends(get_session)) -> OrderService:
    alert_service = AlertService(session, AlertRepository(session))
    return OrderService(
        session=session,
        repository=OrderRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        product_service=ProductService(ProductRepository(session)),
        inventory_service=InventoryService(
            session, ProductRepository(session), alert_service=alert_service
        ),
        ledger_service=LedgerService(LedgerRepository(session)),
    )


@router.post("/import", response_model=OrderImportResponse, status_code=status.HTTP_201_CREATED)
async def import_order(
    payload: OrderImportRequest,
    response: Response,
    service: OrderService = Depends(get_order_service),
) -> OrderImportResponse:
    result = await service.import_order(payload)
    if result.status is OrderImportStatus.DUPLICATE:
        response.status_code = status.HTTP_200_OK
    return result


@router.get("", response_model=list[OrderRead])
async def list_orders(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: OrderService = Depends(get_order_service),
) -> list[OrderRead]:
    return await service.list_orders(limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderDetail:
    return await service.get_order(order_id)
