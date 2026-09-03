from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DailyTotals(BaseModel):
    orders: int
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal


class ChannelPerformance(BaseModel):
    channel: str
    channel_name: str
    orders: int
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal


class DailyReport(BaseModel):
    date: date
    totals: DailyTotals
    channels: list[ChannelPerformance]
