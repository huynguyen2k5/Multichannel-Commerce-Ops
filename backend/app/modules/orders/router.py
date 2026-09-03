from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import OrderImportRequest, OrderImportResponse, OrderImportStatus
from app.modules.orders.service import OrderService
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(session: AsyncSession = Depends(get_session)) -> OrderService:
    return OrderService(
        session=session,
        repository=OrderRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        product_service=ProductService(ProductRepository(session)),
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
