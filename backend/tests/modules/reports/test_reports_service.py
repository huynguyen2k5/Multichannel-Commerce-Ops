from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.channels.models import Channel
from app.modules.ledger.models import LedgerEntry, LedgerEntryType
from app.modules.orders.models import Order
from app.modules.reports.repository import ReportsRepository
from app.modules.reports.service import ReportsService


async def test_daily_report_aggregates_by_channel(session: AsyncSession) -> None:
    shopee = Channel(code="shopee", name="Shopee", platform_type="marketplace")
    website = Channel(code="website", name="Website", platform_type="direct")
    session.add_all([shopee, website])
    await session.flush()
    assert shopee.id is not None and website.id is not None

    orders = [
        Order(
            channel_id=shopee.id,
            external_order_id="SP-1",
            order_date=datetime(2026, 9, 1, 2, tzinfo=UTC),
            total_amount=Decimal("500.00"),
        ),
        Order(
            channel_id=website.id,
            external_order_id="WEB-1",
            order_date=datetime(2026, 9, 1, 3, tzinfo=UTC),
            total_amount=Decimal("300.00"),
        ),
    ]
    session.add_all(orders)
    await session.flush()
    for order, revenue, cogs in [
        (orders[0], Decimal("500.00"), Decimal("300.00")),
        (orders[1], Decimal("300.00"), Decimal("180.00")),
    ]:
        assert order.id is not None
        session.add_all(
            [
                LedgerEntry(order_id=order.id, entry_type=LedgerEntryType.REVENUE, amount=revenue),
                LedgerEntry(order_id=order.id, entry_type=LedgerEntryType.COGS, amount=cogs),
            ]
        )
    await session.commit()

    report = await ReportsService(ReportsRepository(session)).daily_report(date(2026, 9, 1))

    assert report.totals.orders == 2
    assert report.totals.revenue == Decimal("800.00")
    assert report.totals.cogs == Decimal("480.00")
    assert report.totals.gross_profit == Decimal("320.00")
    assert [channel.channel for channel in report.channels] == ["shopee", "website"]
