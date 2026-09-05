from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.service import InventoryService
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService
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

    service = InventoryService(session, ProductService(ProductRepository(session)))
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

    service = InventoryService(session, ProductService(ProductRepository(session)))
    with pytest.raises(BusinessRuleError) as error:
        await service.consume(product.id, 2)

    assert error.value.code == "INSUFFICIENT_STOCK"


async def test_inventory_repository_atomic_conditional_decrement(session: AsyncSession) -> None:
    from app.modules.inventory.repository import InventoryRepository

    product = Product(
        sku="CAP-WHT",
        name="White Cap",
        cost_price=Decimal("180000.00"),
        current_stock=2,
        reorder_threshold=1,
    )
    session.add(product)
    await session.commit()
    assert product.id is not None

    repository = InventoryRepository(session)
    # Successful conditional decrement
    first = await repository.consume_stock(product.id, 2)
    assert first is not None
    assert first.current_stock == 0

    # Failing conditional decrement (guard: current_stock >= 1 fails when current_stock == 0)
    second = await repository.consume_stock(product.id, 1)
    assert second is None

    persisted = await ProductRepository(session).get_by_id(product.id)
    assert persisted is not None
    assert persisted.current_stock == 0
