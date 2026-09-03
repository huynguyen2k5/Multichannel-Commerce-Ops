from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.modules.products.models import Product
from app.shared.time import utc_now


class InventoryRepository:
    """Encapsulates inventory storage operations.

    Note: In MCO V1, physical stock is persisted on products.current_stock.
    This repository owns atomic database updates and stock decrement queries.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def consume_stock(self, product_id: int, quantity: int) -> Product | None:
        """Atomically decrement stock if and only if sufficient stock exists."""
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
        return result.scalar_one_or_none()
