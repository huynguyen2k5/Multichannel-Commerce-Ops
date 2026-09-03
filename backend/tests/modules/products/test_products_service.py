from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService
from app.shared.errors import NotFoundError


async def test_product_lookup_returns_cost_and_stock(session: AsyncSession) -> None:
    session.add(
        Product(
            sku="TEE-BLK-M",
            name="Black Tee M",
            cost_price=Decimal("150000.00"),
            current_stock=20,
            reorder_threshold=5,
        )
    )
    await session.commit()

    product = await ProductService(ProductRepository(session)).get_by_sku("TEE-BLK-M")

    assert product.cost_price == Decimal("150000.00")
    assert product.current_stock == 20


async def test_product_lookup_rejects_unknown_sku(session: AsyncSession) -> None:
    service = ProductService(ProductRepository(session))

    with pytest.raises(NotFoundError) as error:
        await service.get_by_sku("UNKNOWN")

    assert error.value.code == "PRODUCT_NOT_FOUND"
