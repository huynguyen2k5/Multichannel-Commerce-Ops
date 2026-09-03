from decimal import Decimal

from pydantic import BaseModel


class InventoryItemRead(BaseModel):
    product_id: int
    sku: str
    name: str
    cost_price: Decimal
    current_stock: int
    reorder_threshold: int
    is_low_stock: bool
