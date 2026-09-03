from datetime import date
from decimal import Decimal

from app.modules.reports.repository import ReportsRepository
from app.modules.reports.schemas import ChannelPerformance, DailyReport, DailyTotals


class ReportsService:
    def __init__(self, repository: ReportsRepository) -> None:
        self._repository = repository

    async def daily_report(self, report_date: date) -> DailyReport:
        rows = await self._repository.daily_channels(report_date)
        channels = [
            ChannelPerformance(
                channel=code,
                channel_name=name,
                orders=orders,
                revenue=revenue,
                cogs=cogs,
                gross_profit=revenue - cogs,
            )
            for code, name, orders, revenue, cogs in rows
        ]
        total_orders = sum(channel.orders for channel in channels)
        total_revenue = sum((channel.revenue for channel in channels), start=Decimal("0.00"))
        total_cogs = sum((channel.cogs for channel in channels), start=Decimal("0.00"))
        return DailyReport(
            date=report_date,
            totals=DailyTotals(
                orders=total_orders,
                revenue=total_revenue,
                cogs=total_cogs,
                gross_profit=total_revenue - total_cogs,
            ),
            channels=channels,
        )
