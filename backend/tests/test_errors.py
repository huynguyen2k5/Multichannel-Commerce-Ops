from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.shared.errors import NotFoundError


async def test_application_error_uses_standard_contract() -> None:
    app = create_app()
    router = APIRouter()

    @router.get("/missing")
    async def missing() -> None:
        raise NotFoundError("TEST_NOT_FOUND", "Test resource not found")

    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/missing", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 404
    assert response.headers["X-Request-ID"] == "req-123"
    assert response.json() == {
        "error": {
            "code": "TEST_NOT_FOUND",
            "message": "Test resource not found",
            "request_id": "req-123",
        }
    }


async def test_validation_errors_use_standard_contract() -> None:
    app = create_app()
    router = APIRouter()

    @router.get("/quantity")
    async def quantity(value: int) -> dict[str, int]:
        return {"value": value}

    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/quantity?value=invalid")

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["request_id"]
