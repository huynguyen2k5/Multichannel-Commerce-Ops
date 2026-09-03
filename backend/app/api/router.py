from fastapi import APIRouter

from app.modules.mock_channels.router import router as mock_router

api_router = APIRouter()

# Mock APIs intentionally live outside /api/v1 so their source-like contract stays distinct.
api_router.include_router(mock_router)
