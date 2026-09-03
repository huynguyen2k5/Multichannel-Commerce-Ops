from collections.abc import Sequence
from decimal import Decimal

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.ledger.models import LedgerEntry, LedgerEntryType
from app.modules.ledger.repository import LedgerRepository
from app.modules.ledger.schemas import OrderSaleRecord


class LedgerService:
    def __init__(self, repository: LedgerRepository) -> None:
        self._repository = repository

    async def record_sale(self, record: OrderSaleRecord) -> None:
        revenue = sum(
            (item.unit_price * item.quantity for item in record.items),
            start=Decimal("0.00"),
        )
        cogs = sum(
            (item.unit_cost * item.quantity for item in record.items),
            start=Decimal("0.00"),
        )
        await self._repository.add_entries(
            [
                LedgerEntry(
                    order_id=record.order_id,
                    entry_type=LedgerEntryType.REVENUE,
                    amount=revenue,
                ),
                LedgerEntry(
                    order_id=record.order_id,
                    entry_type=LedgerEntryType.COGS,
                    amount=cogs,
                ),
            ]
        )

    async def get_entries_for_orders(self, order_ids: Sequence[int]) -> list[LedgerEntry]:
        return await self._repository.get_for_orders(order_ids)


def get_ledger_service(session: AsyncSession = Depends(get_session)) -> LedgerService:
    return LedgerService(LedgerRepository(session))
