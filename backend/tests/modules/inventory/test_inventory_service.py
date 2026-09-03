from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.service import InventoryService
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.shared.errors import BusinessRuleError


async def test_consume_stock_uses_atomic_guard(session: AsyncSession) -> None:
    product = Product(
        sku="CAP-WHT",
        name="White Cap",
        cost_price=Decimal("180000.00"),
        current_stock=5,
        reorder_threshold=2,
    )
    session.add(product)
    await session.commit()
    assert product.id is not None

    service = InventoryService(session, ProductRepository(session))
    updated = await service.consume(product.id, 3)
    await session.commit()

    assert updated.current_stock == 2


async def test_consume_stock_rejects_oversell(session: AsyncSession) -> None:
    product = Product(
        sku="CAP-WHT",
        name="White Cap",
        cost_price=Decimal("180000.00"),
        current_stock=1,
        reorder_threshold=2,
    )
    session.add(product)
    await session.commit()
    assert product.id is not None

    service = InventoryService(session, ProductRepository(session))
    with pytest.raises(BusinessRuleError) as error:
        await service.consume(product.id, 2)

    assert error.value.code == "INSUFFICIENT_STOCK"
