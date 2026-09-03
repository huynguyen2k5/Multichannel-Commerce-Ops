from fastapi import APIRouter

from app.modules.orders.router import router as orders_router

api_router = APIRouter()
api_router.include_router(orders_router)
