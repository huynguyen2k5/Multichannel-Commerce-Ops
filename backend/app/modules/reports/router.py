from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.reports.repository import ReportsRepository
from app.modules.reports.schemas import DailyReport
from app.modules.reports.service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_reports_repository(
    session: AsyncSession = Depends(get_session),
) -> ReportsRepository:
    return ReportsRepository(session)


def get_reports_service(
    repository: ReportsRepository = Depends(get_reports_repository),
) -> ReportsService:
    return ReportsService(repository)


@router.get("/daily", response_model=DailyReport)
async def daily_report(
    report_date: date = Query(default_factory=lambda: datetime.now(UTC).date(), alias="date"),
    service: ReportsService = Depends(get_reports_service),
) -> DailyReport:
    return await service.daily_report(report_date)
