from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.ledger.models import LedgerEntry


class LedgerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_entries(self, entries: Sequence[LedgerEntry]) -> None:
        self._session.add_all(list(entries))
        await self._session.flush()

    async def get_for_order(self, order_id: int) -> list[LedgerEntry]:
        result = await self._session.execute(
            select(LedgerEntry)
            .where(LedgerEntry.order_id == order_id)
            .order_by(LedgerEntry.entry_type)
        )
        return list(result.scalars().all())

    async def get_for_orders(self, order_ids: Sequence[int]) -> list[LedgerEntry]:
        if not order_ids:
            return []
        result = await self._session.execute(
            select(LedgerEntry).where(LedgerEntry.order_id.in_(order_ids))
        )
        return list(result.scalars().all())
