import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlmodel import select

from app.database import SessionFactory, engine
from app.modules.alerts.models import Alert, AlertSeverity, AlertType
from app.modules.channels.models import Channel
from app.modules.ledger.models import LedgerEntry, LedgerEntryType
from app.modules.orders.models import Order, OrderItem, OrderStatus
from app.modules.products.models import Product
from app.modules.reconciliation.models import ReconciliationLog, ReconciliationStatus

CHANNELS = [
    Channel(code="shopee", name="Shopee", platform_type="marketplace"),
    Channel(code="tiktok", name="TikTok Shop", platform_type="marketplace"),
    Channel(code="website", name="Website", platform_type="direct"),
]

PRODUCTS = [
    Product(
        sku="BAG-CNV",
        name="Canvas Tote Bag - Cream",
        cost_price=Decimal("120000.00"),
        current_stock=0,
        reorder_threshold=10,
    ),
    Product(
        sku="TEE-BLK-M",
        name="Classic Tee - Black / M",
        cost_price=Decimal("150000.00"),
        current_stock=40,
        reorder_threshold=8,
    ),
    Product(
        sku="CAP-BLK",
        name="Logo Cap - Black",
        cost_price=Decimal("180000.00"),
        current_stock=5,
        reorder_threshold=10,
    ),
    Product(
        sku="HOODIE-GRY-M",
        name="Oversized Hoodie - Gray / M",
        cost_price=Decimal("320000.00"),
        current_stock=3,
        reorder_threshold=15,
    ),
    Product(
        sku="HOODIE-BLK-M",
        name="Oversized Hoodie - Black / M",
        cost_price=Decimal("320000.00"),
        current_stock=22,
        reorder_threshold=10,
    ),
    Product(
        sku="TEE-WHT-L",
        name="Classic Tee - White / L",
        cost_price=Decimal("140000.00"),
        current_stock=35,
        reorder_threshold=8,
    ),
    Product(
        sku="CAP-WHT",
        name="Logo Cap - White",
        cost_price=Decimal("180000.00"),
        current_stock=18,
        reorder_threshold=5,
    ),
    Product(
        sku="TEE-WHT-M",
        name="Classic Tee - White / M",
        cost_price=Decimal("140000.00"),
        current_stock=50,
        reorder_threshold=8,
    ),
]


async def seed_operations() -> None:
    now = datetime.now(UTC)
    async with SessionFactory() as session, session.begin():
        # 1. Channels
        channel_map: dict[str, Channel] = {}
        for ch in CHANNELS:
            existing = await session.scalar(select(Channel).where(Channel.code == ch.code))
            if existing is None:
                session.add(ch)
                await session.flush()
                channel_map[ch.code] = ch
            else:
                channel_map[ch.code] = existing

        # 2. Products
        product_map: dict[str, Product] = {}
        for prod in PRODUCTS:
            existing = await session.scalar(select(Product).where(Product.sku == prod.sku))
            if existing is None:
                session.add(prod)
                await session.flush()
                product_map[prod.sku] = prod
            else:
                existing.name = prod.name
                existing.cost_price = prod.cost_price
                existing.current_stock = prod.current_stock
                existing.reorder_threshold = prod.reorder_threshold
                session.add(existing)
                await session.flush()
                product_map[prod.sku] = existing

        # 3. Multi-channel Orders & Ledger
        order_templates = [
            # Today's orders
            ("shopee", "ORD-SHP-8801", now - timedelta(minutes=15), [
                ("TEE-BLK-M", 2, Decimal("250000.00")),
            ]),
            ("tiktok", "ORD-TT-9840", now - timedelta(minutes=45), [
                ("HOODIE-BLK-M", 1, Decimal("490000.00")),
            ]),
            ("website", "ORD-WEB-3011", now - timedelta(hours=1, minutes=10), [
                ("TEE-WHT-L", 1, Decimal("220000.00")),
                ("CAP-WHT", 1, Decimal("280000.00")),
            ]),
            ("shopee", "ORD-SHP-8802", now - timedelta(hours=2), [
                ("TEE-BLK-M", 1, Decimal("250000.00")),
                ("TEE-WHT-M", 1, Decimal("220000.00")),
            ]),
            ("tiktok", "ORD-TT-9841", now - timedelta(hours=3, minutes=20), [
                ("CAP-BLK", 2, Decimal("280000.00")),
            ]),
            ("website", "ORD-WEB-3012", now - timedelta(hours=4), [
                ("HOODIE-GRY-M", 1, Decimal("490000.00")),
            ]),
            ("shopee", "ORD-SHP-8803", now - timedelta(hours=5), [
                ("HOODIE-BLK-M", 2, Decimal("480000.00")),
            ]),
            ("tiktok", "ORD-TT-9842", now - timedelta(hours=6, minutes=15), [
                ("TEE-WHT-L", 1, Decimal("220000.00")),
                ("CAP-BLK", 1, Decimal("200000.00")),
            ]),
            ("website", "ORD-WEB-3013", now - timedelta(hours=7), [
                ("TEE-BLK-M", 3, Decimal("240000.00")),
            ]),
            ("shopee", "ORD-SHP-8804", now - timedelta(hours=8, minutes=30), [
                ("CAP-WHT", 1, Decimal("280000.00")),
            ]),

            # Yesterday's orders
            ("shopee", "ORD-SHP-8790", now - timedelta(days=1, hours=2), [
                ("TEE-WHT-M", 2, Decimal("220000.00")),
            ]),
            ("tiktok", "ORD-TT-9830", now - timedelta(days=1, hours=4), [
                ("HOODIE-BLK-M", 1, Decimal("490000.00")),
            ]),
            ("website", "ORD-WEB-3005", now - timedelta(days=1, hours=6), [
                ("TEE-BLK-M", 2, Decimal("250000.00")),
            ]),
            ("shopee", "ORD-SHP-8791", now - timedelta(days=1, hours=8), [
                ("CAP-BLK", 1, Decimal("280000.00")),
            ]),
            ("tiktok", "ORD-TT-9831", now - timedelta(days=1, hours=10), [
                ("TEE-WHT-L", 2, Decimal("220000.00")),
                ("CAP-WHT", 1, Decimal("280000.00")),
            ]),
            ("website", "ORD-WEB-3006", now - timedelta(days=1, hours=12), [
                ("HOODIE-GRY-M", 2, Decimal("490000.00")),
            ]),
        ]

        for ch_code, ext_id, order_time, items in order_templates:
            channel = channel_map[ch_code]
            assert channel.id is not None
            existing_order = await session.scalar(
                select(Order).where(
                    Order.channel_id == channel.id,
                    Order.external_order_id == ext_id,
                )
            )

            if existing_order is not None:
                continue

            total_amount = sum(qty * price for _, qty, price in items)
            order = Order(
                channel_id=channel.id,
                external_order_id=ext_id,
                order_date=order_time,
                status=OrderStatus.PAID,
                total_amount=total_amount,
                source_updated_at=order_time,
            )
            session.add(order)
            await session.flush()
            assert order.id is not None

            total_cogs = Decimal("0.00")
            for sku, qty, price in items:
                prod = product_map[sku]
                assert prod.id is not None
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=prod.id,
                    quantity=qty,
                    unit_price=price,
                    unit_cost=prod.cost_price,
                )
                session.add(order_item)
                total_cogs += prod.cost_price * qty

            session.add(
                LedgerEntry(
                    order_id=order.id,
                    entry_type=LedgerEntryType.REVENUE,
                    amount=total_amount,
                    created_at=order_time,
                )
            )
            session.add(
                LedgerEntry(
                    order_id=order.id,
                    entry_type=LedgerEntryType.COGS,
                    amount=total_cogs,
                    created_at=order_time,
                )
            )

        # 4. Alerts
        alerts_data = [
            (
                AlertType.LOW_STOCK,
                AlertSeverity.CRITICAL,
                "low_stock:BAG-CNV",
                "Stock level for 'BAG-CNV' (Canvas Tote Bag - Cream) is at 0 units, "
                "below reorder threshold of 10.",
                False,
                None,
            ),
            (
                AlertType.LOW_STOCK,
                AlertSeverity.WARNING,
                "low_stock:HOODIE-GRY-M",
                "Stock level for 'HOODIE-GRY-M' (Oversized Hoodie - Gray / M) is at 3 units, "
                "below reorder threshold of 15.",
                False,
                None,
            ),
            (
                AlertType.RECONCILIATION_MISMATCH,
                AlertSeverity.WARNING,
                "recon_mismatch:tiktok:ORD-TT-9842",
                "Reconciliation mismatch on TikTok Shop: ORD-TT-9842 amount mismatch "
                "(expected 450,000 VND, actual 420,000 VND).",
                False,
                None,
            ),
            (
                AlertType.LOW_STOCK,
                AlertSeverity.INFO,
                "low_stock:CAP-BLK",
                "Stock level for 'CAP-BLK' was low (5 units) and "
                "supplier reorder PO-401 has been triggered.",
                True,
                now - timedelta(hours=3),
            ),
        ]


        for a_type, a_sev, dedup, msg, is_resolved, resolved_time in alerts_data:
            existing_alert = await session.scalar(select(Alert).where(Alert.dedup_key == dedup))
            if existing_alert is None:
                session.add(
                    Alert(
                        type=a_type,
                        severity=a_sev,
                        dedup_key=dedup,
                        message=msg,
                        resolved=is_resolved,
                        resolved_at=resolved_time,
                        created_at=now - timedelta(hours=4),
                    )
                )

        # 5. Reconciliation runs
        existing_recons = await session.scalars(select(ReconciliationLog))
        if len(list(existing_recons.all())) == 0:
            session.add(
                ReconciliationLog(
                    source_system="shopee",
                    status=ReconciliationStatus.SUCCESS,
                    records_checked=50,
                    mismatches_found=0,
                    detail_json={"mismatches": []},
                    started_at=now - timedelta(hours=2),
                    completed_at=now - timedelta(hours=2) + timedelta(seconds=3),
                )
            )
            session.add(
                ReconciliationLog(
                    source_system="tiktok",
                    status=ReconciliationStatus.MISMATCH,
                    records_checked=45,
                    mismatches_found=2,
                    detail_json={
                        "mismatches": [
                            {
                                "external_order_id": "ORD-TT-9842",
                                "code": "TOTAL_MISMATCH",
                                "expected": "450000.00",
                                "actual": "420000.00",
                            },
                            {
                                "external_order_id": "ORD-TT-9845",
                                "code": "MISSING_ORDER",
                                "expected": "280000.00",
                                "actual": None,
                            },
                        ]
                    },
                    started_at=now - timedelta(hours=1),
                    completed_at=now - timedelta(hours=1) + timedelta(seconds=4),
                )
            )
            session.add(
                ReconciliationLog(
                    source_system="website",
                    status=ReconciliationStatus.SUCCESS,
                    records_checked=32,
                    mismatches_found=0,
                    detail_json={"mismatches": []},
                    started_at=now - timedelta(minutes=30),
                    completed_at=now - timedelta(minutes=30) + timedelta(seconds=2),
                )
            )


async def main() -> None:
    try:
        await seed_operations()
        print("Operational data successfully seeded!")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
