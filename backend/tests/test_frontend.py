import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import create_app


def test_serves_frontend_without_masking_api_or_asset_errors(tmp_path):
    (tmp_path / "index.html").write_text("<html>Channel Radar</html>")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('radar')")
    app = create_app(frontend_dir=tmp_path)

    async def requests():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            return [
                await client.get(route)
                for route in [
                    "/", "/channels/example", "/assets/app.js",
                    "/api/missing", "/api", "/assets/missing.js",
                    "/missing.js", "/%2e%2e/outside.txt",
                ]
            ]

    responses = asyncio.run(requests())
    assert responses[0].text == "<html>Channel Radar</html>"
    assert responses[1].text == responses[0].text
    assert responses[2].text == "console.log('radar')"
    for response in responses[3:]:
        assert response.status_code == 404
        assert "<html>" not in response.text
