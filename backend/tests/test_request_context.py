from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_response_echoes_or_creates_request_id() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        generated = await client.get("/health")
        supplied = await client.get("/health", headers={"X-Request-ID": "request-42"})

    assert generated.headers["X-Request-ID"]
    assert supplied.headers["X-Request-ID"] == "request-42"
