from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.inventory.schemas import InventoryItemRead
from app.modules.inventory.service import InventoryService
from app.modules.products.service import ProductService, get_product_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


def get_inventory_service(
    session: AsyncSession = Depends(get_session),
    product_service: ProductService = Depends(get_product_service),
) -> InventoryService:
    return InventoryService(session, product_service)


@router.get("", response_model=list[InventoryItemRead])
async def list_inventory(
    service: InventoryService = Depends(get_inventory_service),
) -> list[InventoryItemRead]:
    return await service.list_inventory()
