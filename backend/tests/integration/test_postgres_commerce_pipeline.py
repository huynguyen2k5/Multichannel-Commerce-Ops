from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts import AlertService
from app.modules.alerts.repository import AlertRepository
from app.modules.channels import Channel, ChannelService
from app.modules.channels.repository import ChannelRepository
from app.modules.inventory import InventoryService
from app.modules.ledger import LedgerEntryType, LedgerService
from app.modules.ledger.repository import LedgerRepository
from app.modules.orders import (
    OrderImportItem,
    OrderImportRequest,
    OrderImportStatus,
    OrderService,
)
from app.modules.orders.repository import OrderRepository
from app.modules.products import Product, ProductService
from app.modules.products.repository import ProductRepository
from app.modules.reconciliation import (
    ReconciliationRequest,
    ReconciliationService,
    ReconciliationStatus,
    SourceOrderSnapshot,
)
from app.modules.reconciliation.repository import ReconciliationRepository
from app.modules.reports import ReportsService
from app.modules.reports.repository import ReportsRepository
from app.shared.errors import BusinessRuleError
from tests.integration.postgres_container import PostgresTestEnvironment


def _build_order_service(session: AsyncSession) -> OrderService:
    product_repo = ProductRepository(session)
    product_service = ProductService(product_repo)
    return OrderService(
        session=session,
        repository=OrderRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        product_service=product_service,
        inventory_service=InventoryService(
            session=session,
            product_service=product_service,
            alert_service=AlertService(session, AlertRepository(session)),
        ),
        ledger_service=LedgerService(LedgerRepository(session)),
    )


def _build_reconciliation_service(session: AsyncSession) -> ReconciliationService:
    return ReconciliationService(
        session=session,
        repository=ReconciliationRepository(session),
        channel_service=ChannelService(ChannelRepository(session)),
        order_service=_build_order_service(session),
        ledger_service=LedgerService(LedgerRepository(session)),
        alert_service=AlertService(session, AlertRepository(session)),
    )


@pytest.fixture
async def pg_session() -> AsyncGenerator[AsyncSession, None]:
    env = PostgresTestEnvironment()
    env.start()
    await env.init_schema()
    try:
        async for session in env.get_session():
            yield session
    finally:
        await env.stop()


async def test_postgres_critical_multichannel_pipeline(pg_session: AsyncSession) -> None:
    session = pg_session

    # 1. Seed products and channels
    shopee = Channel(code="shopee", name="Shopee", platform_type="marketplace")
    tiktok = Channel(code="tiktok", name="TikTok Shop", platform_type="social_commerce")
    web = Channel(code="web", name="Direct Website", platform_type="direct")

    tee = Product(
        sku="TEE-BLK-M",
        name="Black T-Shirt Medium",
        cost_price=Decimal("150.00"),
        current_stock=20,
        reorder_threshold=3,
    )
    hoodie = Product(
        sku="HOODIE-GRY-L",
        name="Grey Hoodie Large",
        cost_price=Decimal("500.00"),
        current_stock=10,
        reorder_threshold=2,
    )
    session.add_all([shopee, tiktok, web, tee, hoodie])
    await session.commit()

    order_svc = _build_order_service(session)

    # 2. Import orders from multiple channels
    # Order 1: Shopee
    sp_order = await order_svc.import_order(
        OrderImportRequest(
            channel="shopee",
            external_order_id="SP-PG-001",
            order_date=datetime(2026, 9, 3, 2, 0, tzinfo=UTC),
            total_amount=Decimal("500.00"),
            items=[OrderImportItem(sku="TEE-BLK-M", quantity=2, unit_price=Decimal("250.00"))],
        )
    )
    assert sp_order.status is OrderImportStatus.IMPORTED

    # Order 2: TikTok Shop
    tt_order = await order_svc.import_order(
        OrderImportRequest(
            channel="tiktok",
            external_order_id="TT-PG-001",
            order_date=datetime(2026, 9, 3, 3, 30, tzinfo=UTC),
            total_amount=Decimal("800.00"),
            items=[OrderImportItem(sku="HOODIE-GRY-L", quantity=1, unit_price=Decimal("800.00"))],
        )
    )
    assert tt_order.status is OrderImportStatus.IMPORTED

    # Order 3: Web Direct
    web_order = await order_svc.import_order(
        OrderImportRequest(
            channel="web",
            external_order_id="WEB-PG-001",
            order_date=datetime(2026, 9, 3, 5, 15, tzinfo=UTC),
            total_amount=Decimal("1060.00"),
            items=[
                OrderImportItem(sku="TEE-BLK-M", quantity=1, unit_price=Decimal("260.00")),
                OrderImportItem(sku="HOODIE-GRY-L", quantity=1, unit_price=Decimal("800.00")),
            ],
        )
    )
    assert web_order.status is OrderImportStatus.IMPORTED

    # 3. Verify stock decremented accurately under PostgreSQL row-level semantics
    product_repo = ProductRepository(session)
    persisted_tee = await product_repo.get_by_sku("TEE-BLK-M")
    persisted_hoodie = await product_repo.get_by_sku("HOODIE-GRY-L")
    assert persisted_tee is not None and persisted_tee.current_stock == 17  # 20 - 2 - 1
    assert persisted_hoodie is not None and persisted_hoodie.current_stock == 8  # 10 - 1 - 1

    # 4. Verify ledger entries created (revenue and cogs per order)
    ledger_repo = LedgerRepository(session)
    entries = await ledger_repo.get_for_orders(
        [sp_order.order_id, tt_order.order_id, web_order.order_id]
    )
    assert len(entries) == 6  # 2 per order (1 REVENUE, 1 COGS)

    sp_entries = {e.entry_type: e.amount for e in entries if e.order_id == sp_order.order_id}
    assert sp_entries == {
        LedgerEntryType.REVENUE: Decimal("500.00"),
        LedgerEntryType.COGS: Decimal("300.00"),  # 2 * 150
    }

    # 5. Verify reports aggregate correctly across channels
    reports_svc = ReportsService(ReportsRepository(session))
    report = await reports_svc.daily_report(date(2026, 9, 3))
    assert report.totals.orders == 3
    assert report.totals.revenue == Decimal("2360.00")  # 500 + 800 + 1060
    assert report.totals.cogs == Decimal("1450.00")  # 300 + 500 + 650
    assert report.totals.gross_profit == Decimal("910.00")

    assert len(report.channels) == 3
    channel_map = {c.channel: c for c in report.channels}
    assert channel_map["shopee"].revenue == Decimal("500.00")
    assert channel_map["tiktok"].revenue == Decimal("800.00")
    assert channel_map["web"].revenue == Decimal("1060.00")

    # 6. Run reconciliation and verify clean match
    recon_svc = _build_reconciliation_service(session)
    recon_res = await recon_svc.reconcile(
        ReconciliationRequest(
            source_system="shopee",
            orders=[
                SourceOrderSnapshot(
                    external_order_id="SP-PG-001",
                    total_amount=Decimal("500.00"),
                )
            ],
        )
    )
    assert recon_res.status is ReconciliationStatus.SUCCESS
    assert recon_res.records_checked == 1
    assert recon_res.mismatches_found == 0

    # 7. Test duplicate import idempotency
    dup_res = await order_svc.import_order(
        OrderImportRequest(
            channel="shopee",
            external_order_id="SP-PG-001",
            order_date=datetime(2026, 9, 3, 2, 0, tzinfo=UTC),
            total_amount=Decimal("500.00"),
            items=[OrderImportItem(sku="TEE-BLK-M", quantity=2, unit_price=Decimal("250.00"))],
        )
    )
    assert dup_res.status is OrderImportStatus.DUPLICATE
    assert dup_res.order_id == sp_order.order_id

    # Stock must NOT double-decrement
    persisted_tee_after = await product_repo.get_by_sku("TEE-BLK-M")
    assert persisted_tee_after is not None and persisted_tee_after.current_stock == 17

    # 8. Test isolation & overselling rejection
    with pytest.raises(BusinessRuleError) as exc_info:
        await order_svc.import_order(
            OrderImportRequest(
                channel="web",
                external_order_id="WEB-OVERSOLD-1",
                order_date=datetime(2026, 9, 3, 6, 0, tzinfo=UTC),
                total_amount=Decimal("12500.00"),
                items=[OrderImportItem(sku="TEE-BLK-M", quantity=50, unit_price=Decimal("250.00"))],
            )
        )
    assert exc_info.value.code == "INSUFFICIENT_STOCK"
