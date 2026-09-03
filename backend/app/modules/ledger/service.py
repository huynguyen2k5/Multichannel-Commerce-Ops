from decimal import Decimal

from app.modules.ledger.models import LedgerEntry, LedgerEntryType
from app.modules.ledger.repository import LedgerRepository
from app.modules.orders.models import Order, OrderItem


class LedgerService:
    def __init__(self, repository: LedgerRepository) -> None:
        self._repository = repository

    async def record_sale(self, order: Order, items: list[OrderItem]) -> None:
        assert order.id is not None
        revenue = sum(
            (item.unit_price * item.quantity for item in items),
            start=Decimal("0.00"),
        )
        cogs = sum(
            (item.unit_cost * item.quantity for item in items),
            start=Decimal("0.00"),
        )
        await self._repository.add_entries(
            [
                LedgerEntry(
                    order_id=order.id,
                    entry_type=LedgerEntryType.REVENUE,
                    amount=revenue,
                ),
                LedgerEntry(
                    order_id=order.id,
                    entry_type=LedgerEntryType.COGS,
                    amount=cogs,
                ),
            ]
        )
