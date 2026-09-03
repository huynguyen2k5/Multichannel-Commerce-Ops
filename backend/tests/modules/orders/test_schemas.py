from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.orders.schemas import OrderImportRequest


def test_import_contract_rejects_inconsistent_total() -> None:
    with pytest.raises(ValidationError):
        OrderImportRequest(
            channel="shopee",
            external_order_id="SP-1",
            order_date=datetime.now(UTC),
            total_amount=Decimal("999.00"),
            items=[{"sku": "TEE-BLK-M", "quantity": 2, "unit_price": "250.00"}],
        )


def test_import_contract_rejects_duplicate_sku_lines() -> None:
    with pytest.raises(ValidationError):
        OrderImportRequest(
            channel="shopee",
            external_order_id="SP-2",
            order_date=datetime.now(UTC),
            total_amount=Decimal("500.00"),
            items=[
                {"sku": "TEE-BLK-M", "quantity": 1, "unit_price": "250.00"},
                {"sku": "TEE-BLK-M", "quantity": 1, "unit_price": "250.00"},
            ],
        )
