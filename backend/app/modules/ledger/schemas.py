from decimal import Decimal

from pydantic import BaseModel


class SaleItemRecord(BaseModel):
    unit_price: Decimal
    unit_cost: Decimal
    quantity: int


class OrderSaleRecord(BaseModel):
    order_id: int
    items: list[SaleItemRecord]
