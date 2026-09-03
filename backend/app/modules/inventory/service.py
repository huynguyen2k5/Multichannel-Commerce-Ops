from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.modules.alerts.service import AlertService
from app.modules.inventory.schemas import InventoryItemRead
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.shared.errors import BusinessRuleError, NotFoundError
from app.shared.time import utc_now


class InventoryService:
    def __init__(
        self,
        session: AsyncSession,
        product_repository: ProductRepository,
        alert_service: AlertService | None = None,
    ) -> None:
        self._session = session
        self._products = product_repository
        self._alerts = alert_service

    async def consume(self, product_id: int, quantity: int) -> Product:
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        statement = (
            update(Product)
            .where(col(Product.id) == product_id, col(Product.current_stock) >= quantity)
            .values(
                current_stock=Product.current_stock - quantity,
                updated_at=utc_now(),
            )
            .returning(Product)
        )
        result = await self._session.execute(statement)
        product = result.scalar_one_or_none()
        if product is not None:
            if self._alerts is not None:
                await self._alerts.create_low_stock(product)
            return product

        existing = await self._products.get_by_id(product_id)
        if existing is None:
            raise NotFoundError(
                "PRODUCT_NOT_FOUND",
                f"Product id '{product_id}' does not exist",
                details={"product_id": product_id},
            )
        raise BusinessRuleError(
            "INSUFFICIENT_STOCK",
            f"Insufficient stock for SKU '{existing.sku}'",
            details={
                "sku": existing.sku,
                "requested": quantity,
                "available": existing.current_stock,
            },
        )

    async def list_inventory(self) -> list[InventoryItemRead]:
        products = await self._products.list_all()
        return [
            InventoryItemRead(
                product_id=product.id or 0,
                sku=product.sku,
                name=product.name,
                cost_price=product.cost_price,
                current_stock=product.current_stock,
                reorder_threshold=product.reorder_threshold,
                is_low_stock=product.current_stock <= product.reorder_threshold,
            )
            for product in products
        ]
