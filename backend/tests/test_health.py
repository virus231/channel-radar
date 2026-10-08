import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import create_app


def test_health_works_without_database_or_network(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = create_app()

    async def request():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/healthz")

    response = asyncio.run(request())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
