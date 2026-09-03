from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.channels.service import ChannelService
from app.modules.inventory.service import InventoryService
from app.modules.orders.models import Order, OrderItem
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderImportRequest,
    OrderImportResponse,
    OrderImportStatus,
)
from app.modules.products.service import ProductService


class OrderService:
    """Application service owning the order-import transaction boundary."""

    def __init__(
        self,
        session: AsyncSession,
        repository: OrderRepository,
        channel_service: ChannelService,
        product_service: ProductService,
        inventory_service: InventoryService,
    ) -> None:
        self._session = session
        self._repository = repository
        self._channel_service = channel_service
        self._product_service = product_service
        self._inventory_service = inventory_service

    async def import_order(self, payload: OrderImportRequest) -> OrderImportResponse:
        try:
            async with self._session.begin():
                channel = await self._channel_service.get_by_code(payload.channel)
                assert channel.id is not None

                existing = await self._repository.get_by_identity(
                    channel.id,
                    payload.external_order_id,
                )
                if existing is not None:
                    assert existing.id is not None
                    return OrderImportResponse(
                        status=OrderImportStatus.DUPLICATE,
                        order_id=existing.id,
                    )

                product_by_sku = {
                    item.sku: await self._product_service.get_by_sku(item.sku)
                    for item in payload.items
                }

                order = await self._repository.create(
                    Order(
                        channel_id=channel.id,
                        external_order_id=payload.external_order_id,
                        order_date=payload.order_date,
                        status=payload.status,
                        total_amount=payload.total_amount,
                        source_updated_at=payload.source_updated_at,
                    )
                )
                assert order.id is not None

                order_items: list[OrderItem] = []
                for item in payload.items:
                    product = product_by_sku[item.sku]
                    assert product.id is not None
                    order_items.append(
                        OrderItem(
                            order_id=order.id,
                            product_id=product.id,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            unit_cost=product.cost_price,
                        )
                    )
                await self._repository.add_items(order_items)

                for order_item in order_items:
                    await self._inventory_service.consume(
                        order_item.product_id,
                        order_item.quantity,
                    )

            return OrderImportResponse(
                status=OrderImportStatus.IMPORTED,
                order_id=order.id,
            )
        except IntegrityError:
            # A concurrent retry can race the pre-insert lookup. The database unique
            # constraint is the final authority; the losing request becomes a no-op.
            await self._session.rollback()
            channel = await self._channel_service.get_by_code(payload.channel)
            assert channel.id is not None
            existing = await self._repository.get_by_identity(
                channel.id,
                payload.external_order_id,
            )
            if existing is None:
                raise
            assert existing.id is not None
            return OrderImportResponse(
                status=OrderImportStatus.DUPLICATE,
                order_id=existing.id,
            )
