from fastapi import APIRouter

from app.modules.alerts.router import router as alerts_router
from app.modules.inventory.router import router as inventory_router
from app.modules.orders.router import router as orders_router
from app.modules.reconciliation.router import router as reconciliation_router
from app.modules.reports.router import router as reports_router

api_router = APIRouter()
api_router.include_router(alerts_router)
api_router.include_router(orders_router)
api_router.include_router(inventory_router)
api_router.include_router(reports_router)
api_router.include_router(reconciliation_router)
