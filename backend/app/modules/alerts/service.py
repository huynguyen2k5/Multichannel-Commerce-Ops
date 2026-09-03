from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.models import Alert, AlertSeverity, AlertType
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.schemas import AlertRead, LowStockAlertRequest
from app.shared.errors import NotFoundError
from app.shared.time import utc_now


class AlertService:
    def __init__(self, session: AsyncSession, repository: AlertRepository) -> None:
        self._session = session
        self._repository = repository

    async def create_once(
        self,
        *,
        alert_type: AlertType,
        severity: AlertSeverity,
        dedup_key: str,
        message: str,
    ) -> Alert:
        existing = await self._repository.get_active_by_dedup_key(dedup_key)
        if existing is not None:
            return existing

        alert = Alert(
            type=alert_type,
            severity=severity,
            dedup_key=dedup_key,
            message=message,
        )
        try:
            async with self._session.begin_nested():
                self._session.add(alert)
                await self._session.flush()
            return alert
        except IntegrityError:
            # Concurrent creators can race the lookup; the partial unique index keeps
            # one active alert per deduplication key without aborting the outer transaction.
            existing = await self._repository.get_active_by_dedup_key(dedup_key)
            if existing is None:
                raise
            return existing

    async def create_low_stock(self, payload: LowStockAlertRequest) -> Alert | None:
        if payload.current_stock > payload.reorder_threshold:
            return None
        return await self.create_once(
            alert_type=AlertType.LOW_STOCK,
            severity=AlertSeverity.WARNING,
            dedup_key=f"low_stock:{payload.sku}",
            message=(
                f"SKU {payload.sku} is low on stock: "
                f"{payload.current_stock} remaining (threshold {payload.reorder_threshold})"
            ),
        )

    async def list_alerts(self, *, resolved: bool | None = None) -> list[AlertRead]:
        return [
            AlertRead.model_validate(alert)
            for alert in await self._repository.list_all(resolved=resolved)
        ]

    async def list_pending_notifications(self) -> list[AlertRead]:
        return [
            AlertRead.model_validate(alert)
            for alert in await self._repository.list_pending_notifications()
        ]

    async def resolve(self, alert_id: int) -> AlertRead:
        """Resolve an alert as a top-level transactional operation."""
        async with self._session.begin():
            alert = await self._require(alert_id)
            if not alert.resolved:
                alert.resolved = True
                alert.resolved_at = utc_now()
                await self._session.flush()
        return AlertRead.model_validate(alert)

    async def mark_notified(self, alert_id: int) -> AlertRead:
        """Persist delivery state only after the notification channel succeeds."""
        async with self._session.begin():
            alert = await self._require(alert_id)
            if alert.notified_at is None:
                alert.notified_at = utc_now()
                await self._session.flush()
        return AlertRead.model_validate(alert)

    async def _require(self, alert_id: int) -> Alert:
        alert = await self._repository.get_by_id(alert_id)
        if alert is None:
            raise NotFoundError(
                "ALERT_NOT_FOUND",
                f"Alert id '{alert_id}' does not exist",
                details={"alert_id": alert_id},
            )
        return alert
