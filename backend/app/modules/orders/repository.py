from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.orders.models import Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_identity(self, channel_id: int, external_order_id: str) -> Order | None:
        result = await self._session.execute(
            select(Order).where(
                Order.channel_id == channel_id,
                Order.external_order_id == external_order_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, order_id: int) -> Order | None:
        return await self._session.get(Order, order_id)

    async def create(self, order: Order) -> Order:
        self._session.add(order)
        await self._session.flush()
        return order

    async def add_items(self, items: Sequence[OrderItem]) -> None:
        self._session.add_all(list(items))
        await self._session.flush()

    async def list(self, *, limit: int, offset: int) -> list[Order]:
        result = await self._session.execute(
            select(Order).order_by(Order.order_date.desc(), Order.id.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def get_items(self, order_id: int) -> list[OrderItem]:
        result = await self._session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id)
        )
        return list(result.scalars().all())

    async def get_by_external_ids(
        self,
        channel_id: int,
        external_order_ids: Sequence[str],
    ) -> list[Order]:
        if not external_order_ids:
            return []
        result = await self._session.execute(
            select(Order).where(
                Order.channel_id == channel_id,
                Order.external_order_id.in_(external_order_ids),
            )
        )
        return list(result.scalars().all())

    async def get_items_for_orders(self, order_ids: Sequence[int]) -> list[OrderItem]:
        if not order_ids:
            return []
        result = await self._session.execute(
            select(OrderItem).where(OrderItem.order_id.in_(order_ids))
        )
        return list(result.scalars().all())
