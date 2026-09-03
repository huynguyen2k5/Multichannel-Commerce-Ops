import asyncio
from decimal import Decimal

from sqlmodel import select

from app.database import SessionFactory
from app.modules.channels.models import Channel
from app.modules.products.models import Product

CHANNELS = (
    Channel(code="shopee", name="Shopee", platform_type="marketplace"),
    Channel(code="tiktok", name="TikTok Shop", platform_type="marketplace"),
    Channel(code="website", name="Website", platform_type="direct"),
)

PRODUCTS = (
    Product(
        sku="TEE-BLK-M",
        name="Classic Tee - Black / M",
        cost_price=Decimal("150000.00"),
        current_stock=40,
        reorder_threshold=8,
    ),
    Product(
        sku="TEE-WHT-L",
        name="Classic Tee - White / L",
        cost_price=Decimal("140000.00"),
        current_stock=35,
        reorder_threshold=8,
    ),
    Product(
        sku="CAP-WHT",
        name="Logo Cap - White",
        cost_price=Decimal("180000.00"),
        current_stock=18,
        reorder_threshold=5,
    ),
)


async def seed() -> None:
    async with SessionFactory() as session, session.begin():
        for channel in CHANNELS:
            existing = await session.scalar(select(Channel).where(Channel.code == channel.code))
            if existing is None:
                session.add(channel)

        for product in PRODUCTS:
            existing = await session.scalar(select(Product).where(Product.sku == product.sku))
            if existing is None:
                session.add(product)


if __name__ == "__main__":
    asyncio.run(seed())
