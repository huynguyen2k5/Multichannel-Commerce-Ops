from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import case, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.channels.models import Channel
from app.modules.ledger.models import LedgerEntry, LedgerEntryType
from app.modules.orders.models import Order


class ReportsRepository:
    """Read-only cross-domain aggregation repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _range(report_date: date) -> tuple[datetime, datetime]:
        start = datetime.combine(report_date, time.min, tzinfo=UTC)
        return start, start + timedelta(days=1)

    async def daily_channels(
        self,
        report_date: date,
    ) -> list[tuple[str, str, int, Decimal, Decimal]]:
        start, end = self._range(report_date)
        revenue = func.coalesce(
            func.sum(
                case(
                    (LedgerEntry.entry_type == LedgerEntryType.REVENUE, LedgerEntry.amount),
                    else_=0,
                )
            ),
            0,
        )
        cogs = func.coalesce(
            func.sum(
                case(
                    (LedgerEntry.entry_type == LedgerEntryType.COGS, LedgerEntry.amount),
                    else_=0,
                )
            ),
            0,
        )
        statement = (
            select(
                Channel.code,
                Channel.name,
                func.count(func.distinct(Order.id)),
                revenue,
                cogs,
            )
            .join(Order, Order.channel_id == Channel.id)
            .join(LedgerEntry, LedgerEntry.order_id == Order.id)
            .where(Order.order_date >= start, Order.order_date < end)
            .group_by(Channel.id, Channel.code, Channel.name)
            .order_by(Channel.code)
        )
        result = await self._session.execute(statement)
        return [
            (str(code), str(name), int(order_count), Decimal(revenue_total), Decimal(cogs_total))
            for code, name, order_count, revenue_total, cogs_total in result.all()
        ]
