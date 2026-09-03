from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.reconciliation.models import ReconciliationLog


class ReconciliationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: ReconciliationLog) -> ReconciliationLog:
        self._session.add(log)
        await self._session.flush()
        return log

    async def get_by_id(self, reconciliation_id: int) -> ReconciliationLog | None:
        return await self._session.get(ReconciliationLog, reconciliation_id)

    async def list(self, *, limit: int = 100) -> list[ReconciliationLog]:
        result = await self._session.execute(
            select(ReconciliationLog)
            .order_by(ReconciliationLog.started_at.desc(), ReconciliationLog.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
