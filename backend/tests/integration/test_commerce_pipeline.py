from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.service import AlertService
from app.modules.channels.models import Channel
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.service import ChannelService
from app.modules.inventory.service import InventoryService
from app.modules.ledger.models import LedgerEntryType
from app.modules.ledger.repository import LedgerRepository
from app.modules.ledger.service import LedgerService
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderImportItem,
    OrderImportRequest,
    OrderImportStatus,
)
from app.modules.orders.service import OrderService
from app.modules.products.models import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService
from app.modules.reconciliation.models import ReconciliationStatus
from app.modules.reconciliation.repository import ReconciliationRepository
from app.modules.reconciliation.schemas import (
    ReconciliationRequest,
    SourceOrderSnapshot,
)
from app.modules.reconciliation.service import ReconciliationService
from app.modules.reports.repository import ReportsRepository
from app.modules.reports.service import ReportsService


def _order_service(session: AsyncSession) -> OrderService:
    products = ProductRepository(session)
    product_service = ProductService(products)
    return OrderService(
        session=session,
        repository=OrderRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        product_service=product_service,
        inventory_service=InventoryService(
            session,
            product_service,
            alert_service=AlertService(session, AlertRepository(session)),
        ),
        ledger_service=LedgerService(LedgerRepository(session)),
    )


def _reconciliation_service(session: AsyncSession) -> ReconciliationService:
    return ReconciliationService(
        session=session,
        repository=ReconciliationRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        order_service=_order_service(session),
        ledger_service=LedgerService(LedgerRepository(session)),
        alert_service=AlertService(session, AlertRepository(session)),
    )


async def test_paid_order_pipeline_is_idempotent_and_reconciles(
    session: AsyncSession,
) -> None:
    channel = Channel(code="shopee", name="Shopee", platform_type="marketplace")
    product = Product(
        sku="TEE-BLK-M",
        name="Black Tee",
        cost_price=Decimal("150.00"),
        current_stock=20,
        reorder_threshold=2,
    )
    session.add_all([channel, product])
    await session.commit()

    payload = OrderImportRequest(
        channel="shopee",
        external_order_id="SP-E2E-1",
        order_date=datetime(2026, 9, 3, 2, 0, tzinfo=UTC),
        total_amount=Decimal("500.00"),
        items=[
            OrderImportItem(
                sku="TEE-BLK-M",
                quantity=2,
                unit_price=Decimal("250.00"),
            )
        ],
    )

    service = _order_service(session)
    imported = await service.import_order(payload)
    duplicate = await service.import_order(payload)

    assert imported.status is OrderImportStatus.IMPORTED
    assert duplicate.status is OrderImportStatus.DUPLICATE
    assert duplicate.order_id == imported.order_id

    persisted_product = await ProductRepository(session).get_by_sku("TEE-BLK-M")
    assert persisted_product is not None
    assert persisted_product.current_stock == 18

    entries = await LedgerRepository(session).get_for_orders([imported.order_id])
    by_type = {entry.entry_type: entry.amount for entry in entries}
    assert by_type == {
        LedgerEntryType.REVENUE: Decimal("500.00"),
        LedgerEntryType.COGS: Decimal("300.00"),
    }

    report = await ReportsService(ReportsRepository(session)).daily_report(date(2026, 9, 3))
    assert report.totals.orders == 1
    assert report.totals.revenue == Decimal("500.00")
    assert report.totals.cogs == Decimal("300.00")
    assert report.totals.gross_profit == Decimal("200.00")

    reconciliation = await _reconciliation_service(session).reconcile(
        ReconciliationRequest(
            source_system="shopee",
            orders=[
                SourceOrderSnapshot(
                    external_order_id="SP-E2E-1",
                    total_amount=Decimal("500.00"),
                )
            ],
        )
    )
    assert reconciliation.status is ReconciliationStatus.SUCCESS
    assert reconciliation.records_checked == 1
    assert reconciliation.mismatches_found == 0
