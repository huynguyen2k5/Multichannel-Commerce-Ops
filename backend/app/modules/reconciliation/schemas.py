from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.reconciliation.models import ReconciliationStatus


class SourceOrderSnapshot(BaseModel):
    external_order_id: str = Field(min_length=1, max_length=100)
    total_amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)


class ReconciliationRequest(BaseModel):
    source_system: str = Field(min_length=1, max_length=64)
    orders: list[SourceOrderSnapshot] = Field(min_length=1, max_length=1000)


class ReconciliationMismatch(BaseModel):
    external_order_id: str
    code: str
    expected: str | None = None
    actual: str | None = None


class ReconciliationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_system: str
    status: ReconciliationStatus
    records_checked: int
    mismatches_found: int
    detail_json: dict[str, object]
    started_at: datetime
    completed_at: datetime
