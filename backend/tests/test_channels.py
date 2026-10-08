import asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from app.models import Channel


def test_empty_channel_list(application):
    async def request():
        async with AsyncClient(
            transport=ASGITransport(app=application), base_url="http://test"
        ) as client:
            return await client.get("/api/channels")

    response = asyncio.run(request())
    assert response.status_code == 200
    assert response.json() == []


def test_channel_list_reads_saved_channels(application, database):
    with Session(database) as session:
        session.add(Channel(username="example_channel", title="Приклад"))
        session.commit()

    async def request():
        async with AsyncClient(
            transport=ASGITransport(app=application), base_url="http://test"
        ) as client:
            return await client.get("/api/channels")

    response = asyncio.run(request())
    assert response.status_code == 200
    channel = response.json()[0]
    assert (channel["id"], channel["username"], channel["title"]) == (1, "example_channel", "Приклад")
    assert channel["status"] == "pending"
    assert channel["subscribers"] is None
    assert channel["post_count"] == 0
