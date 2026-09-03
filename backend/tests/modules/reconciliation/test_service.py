from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.service import AlertService
from app.modules.channels.models import Channel
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.ledger.models import LedgerEntry, LedgerEntryType
from app.modules.ledger.repository import LedgerRepository
from app.modules.orders.models import Order, OrderItem
from app.modules.orders.repository import OrderRepository
from app.modules.products.models import Product
from app.modules.reconciliation.models import ReconciliationStatus
from app.modules.reconciliation.repository import ReconciliationRepository
from app.modules.reconciliation.schemas import ReconciliationRequest
from app.modules.reconciliation.service import ReconciliationService


async def _service(session: AsyncSession) -> ReconciliationService:
    return ReconciliationService(
        session=session,
        repository=ReconciliationRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        order_repository=OrderRepository(session),
        ledger_repository=LedgerRepository(session),
        alert_service=AlertService(session, AlertRepository(session)),
    )


async def test_reconciliation_detects_wrong_revenue(session: AsyncSession) -> None:
    channel = Channel(code="shopee", name="Shopee", platform_type="marketplace")
    product = Product(
        sku="TEE-BLK-M",
        name="Black Tee",
        cost_price=Decimal("150.00"),
        current_stock=10,
        reorder_threshold=2,
    )
    session.add_all([channel, product])
    await session.flush()
    assert channel.id is not None and product.id is not None

    order = Order(
        channel_id=channel.id,
        external_order_id="SP-1",
        order_date=datetime(2026, 9, 1, tzinfo=UTC),
        total_amount=Decimal("500.00"),
    )
    session.add(order)
    await session.flush()
    assert order.id is not None
    session.add(
        OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=Decimal("250.00"),
            unit_cost=Decimal("150.00"),
        )
    )
    session.add_all(
        [
            LedgerEntry(
                order_id=order.id,
                entry_type=LedgerEntryType.REVENUE,
                amount=Decimal("450.00"),
            ),
            LedgerEntry(
                order_id=order.id,
                entry_type=LedgerEntryType.COGS,
                amount=Decimal("300.00"),
            ),
        ]
    )
    await session.commit()

    result = await (await _service(session)).reconcile(
        ReconciliationRequest(
            source_system="shopee",
            orders=[{"external_order_id": "SP-1", "total_amount": "500.00"}],
        )
    )

    assert result.status is ReconciliationStatus.MISMATCH
    assert result.mismatches_found == 1
    codes = [item["code"] for item in result.detail_json["mismatches"]]
    assert codes == ["REVENUE_MISMATCH"]
    active_alerts = await AlertRepository(session).list(resolved=False)
    assert len(active_alerts) == 1


async def test_reconciliation_reports_clean_match(session: AsyncSession) -> None:
    channel = Channel(code="website", name="Website", platform_type="direct")
    product = Product(
        sku="CAP-WHT",
        name="White Cap",
        cost_price=Decimal("180.00"),
        current_stock=10,
        reorder_threshold=2,
    )
    session.add_all([channel, product])
    await session.flush()
    assert channel.id is not None and product.id is not None
    order = Order(
        channel_id=channel.id,
        external_order_id="WEB-1",
        order_date=datetime(2026, 9, 1, tzinfo=UTC),
        total_amount=Decimal("320.00"),
    )
    session.add(order)
    await session.flush()
    assert order.id is not None
    session.add(
        OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            unit_price=Decimal("320.00"),
            unit_cost=Decimal("180.00"),
        )
    )
    session.add_all(
        [
            LedgerEntry(order_id=order.id, entry_type=LedgerEntryType.REVENUE, amount=Decimal("320.00")),
            LedgerEntry(order_id=order.id, entry_type=LedgerEntryType.COGS, amount=Decimal("180.00")),
        ]
    )
    await session.commit()

    result = await (await _service(session)).reconcile(
        ReconciliationRequest(
            source_system="website",
            orders=[{"external_order_id": "WEB-1", "total_amount": "320.00"}],
        )
    )

    assert result.status is ReconciliationStatus.SUCCESS
    assert result.mismatches_found == 0
