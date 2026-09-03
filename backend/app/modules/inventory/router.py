from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.inventory.schemas import InventoryItemRead
from app.modules.inventory.service import InventoryService
from app.modules.products.repository import ProductRepository

router = APIRouter(prefix="/inventory", tags=["inventory"])


def get_inventory_service(session: AsyncSession = Depends(get_session)) -> InventoryService:
    return InventoryService(session, ProductRepository(session))


@router.get("", response_model=list[InventoryItemRead])
async def list_inventory(
    service: InventoryService = Depends(get_inventory_service),
) -> list[InventoryItemRead]:
    return await service.list_inventory()
