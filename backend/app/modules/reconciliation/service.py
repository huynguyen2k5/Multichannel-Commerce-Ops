from collections import defaultdict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.models import AlertSeverity, AlertType
from app.modules.alerts.service import AlertService
from app.modules.channels.service import ChannelService
from app.modules.ledger.models import LedgerEntryType
from app.modules.ledger.repository import LedgerRepository
from app.modules.orders.repository import OrderRepository
from app.modules.reconciliation.models import ReconciliationLog, ReconciliationStatus
from app.modules.reconciliation.repository import ReconciliationRepository
from app.modules.reconciliation.schemas import (
    ReconciliationMismatch,
    ReconciliationRead,
    ReconciliationRequest,
)
from app.shared.errors import NotFoundError
from app.shared.time import utc_now


class ReconciliationService:
    def __init__(
        self,
        session: AsyncSession,
        repository: ReconciliationRepository,
        channel_service: ChannelService,
        order_repository: OrderRepository,
        ledger_repository: LedgerRepository,
        alert_service: AlertService,
    ) -> None:
        self._session = session
        self._repository = repository
        self._channels = channel_service
        self._orders = order_repository
        self._ledger = ledger_repository
        self._alerts = alert_service

    async def reconcile(self, payload: ReconciliationRequest) -> ReconciliationRead:
        started_at = utc_now()
        async with self._session.begin():
            channel = await self._channels.get_by_code(payload.source_system)
            assert channel.id is not None

            source_ids = [order.external_order_id for order in payload.orders]
            local_orders = await self._orders.get_by_external_ids(channel.id, source_ids)
            local_by_external = {order.external_order_id: order for order in local_orders}
            order_ids = [order.id for order in local_orders if order.id is not None]

            ledger_entries = await self._ledger.get_for_orders(order_ids)
            ledger_by_order: dict[int, dict[LedgerEntryType, Decimal]] = defaultdict(dict)
            for entry in ledger_entries:
                ledger_by_order[entry.order_id][entry.entry_type] = entry.amount

            items = await self._orders.get_items_for_orders(order_ids)
            expected_cogs: dict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))
            for item in items:
                expected_cogs[item.order_id] += item.unit_cost * item.quantity

            mismatches: list[ReconciliationMismatch] = []
            for source_order in payload.orders:
                local = local_by_external.get(source_order.external_order_id)
                if local is None or local.id is None:
                    mismatches.append(
                        ReconciliationMismatch(
                            external_order_id=source_order.external_order_id,
                            code="MISSING_ORDER",
                            expected=str(source_order.total_amount),
                            actual=None,
                        )
                    )
                    continue

                if local.total_amount != source_order.total_amount:
                    mismatches.append(
                        ReconciliationMismatch(
                            external_order_id=source_order.external_order_id,
                            code="TOTAL_MISMATCH",
                            expected=str(source_order.total_amount),
                            actual=str(local.total_amount),
                        )
                    )

                entries = ledger_by_order.get(local.id, {})
                revenue = entries.get(LedgerEntryType.REVENUE)
                if revenue != source_order.total_amount:
                    mismatches.append(
                        ReconciliationMismatch(
                            external_order_id=source_order.external_order_id,
                            code="REVENUE_MISMATCH",
                            expected=str(source_order.total_amount),
                            actual=None if revenue is None else str(revenue),
                        )
                    )

                cogs = entries.get(LedgerEntryType.COGS)
                expected = expected_cogs[local.id]
                if cogs != expected:
                    mismatches.append(
                        ReconciliationMismatch(
                            external_order_id=source_order.external_order_id,
                            code="COGS_MISMATCH",
                            expected=str(expected),
                            actual=None if cogs is None else str(cogs),
                        )
                    )

            status = (
                ReconciliationStatus.MISMATCH
                if mismatches
                else ReconciliationStatus.SUCCESS
            )
            log = await self._repository.create(
                ReconciliationLog(
                    source_system=payload.source_system,
                    status=status,
                    records_checked=len(payload.orders),
                    mismatches_found=len(mismatches),
                    detail_json={
                        "mismatches": [mismatch.model_dump() for mismatch in mismatches]
                    },
                    started_at=started_at,
                    completed_at=utc_now(),
                )
            )

            if mismatches:
                await self._alerts.create_once(
                    alert_type=AlertType.RECONCILIATION_MISMATCH,
                    severity=AlertSeverity.CRITICAL,
                    dedup_key=f"reconciliation_mismatch:{payload.source_system}",
                    message=(
                        f"{payload.source_system} reconciliation found "
                        f"{len(mismatches)} mismatch(es)"
                    ),
                )

        return ReconciliationRead.model_validate(log)

    async def list_history(self) -> list[ReconciliationRead]:
        return [
            ReconciliationRead.model_validate(log)
            for log in await self._repository.list()
        ]

    async def get(self, reconciliation_id: int) -> ReconciliationRead:
        log = await self._repository.get_by_id(reconciliation_id)
        if log is None:
            raise NotFoundError(
                "RECONCILIATION_NOT_FOUND",
                f"Reconciliation id '{reconciliation_id}' does not exist",
                details={"reconciliation_id": reconciliation_id},
            )
        return ReconciliationRead.model_validate(log)
