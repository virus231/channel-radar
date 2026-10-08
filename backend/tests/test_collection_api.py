import asyncio
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.database import get_session
from app.main import create_app


HTML = (Path(__file__).parent / 'fixtures/preview.html').read_text()


def collection_app(database, handler):
    app = create_app(telegram_transport=httpx.MockTransport(handler))

    def session():
        with Session(database) as connection:
            yield connection

    app.dependency_overrides[get_session] = session
    return app


def test_add_channel_collects_posts_and_repeat_returns_existing_channel(database):
    requests = []

    def telegram(request):
        requests.append(str(request.url))
        return httpx.Response(200, text=HTML, headers={'content-type': 'text/html'})

    async def scenario():
        app = collection_app(database, telegram)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            added = await client.post('/api/channels', json={'username': ' @Example_Channel '})
            assert added.status_code == 202
            assert added.json()['status'] == 'pending'
            channel = (await client.get('/api/channels/1')).json()
            assert channel['username'] == 'example_channel'
            assert channel['status'] == 'ready'
            assert channel['subscribers'] == 2500000
            assert channel['post_count'] == 2
            assert channel['last_success_at'].endswith('Z')
            posts = (await client.get('/api/channels/1/posts')).json()
            assert [post['message_id'] for post in posts['items']] == [15, 12]
            assert posts['items'][0]['views'] is None
            assert posts['items'][1]['views'] == 1200
            assert posts['items'][1]['reactions']['👍'] == 12
            assert posts['items'][1]['published_at'] == '2026-10-07T10:00:00Z'
            repeat = await client.post('/api/channels', json={'username': 'example_channel'})
            assert repeat.status_code == 200
            assert repeat.json()['id'] == 1
            assert repeat.json()['post_count'] == 2
            assert len((await client.get('/api/channels')).json()) == 1
        assert requests == ['https://t.me/s/example_channel']

    asyncio.run(scenario())


def test_response_is_sent_before_telegram_finishes_and_status_is_collecting(database):
    async def scenario():
        entered, release, body_sent = asyncio.Event(), asyncio.Event(), asyncio.Event()

        async def telegram(request):
            entered.set()
            await release.wait()
            return httpx.Response(200, text=HTML, headers={'content-type': 'text/html'})

        app = collection_app(database, telegram)

        async def wire(scope, receive, send):
            async def observe(message):
                if scope['method'] == 'POST' and message['type'] == 'http.response.body':
                    body_sent.set()
                await send(message)
            await app(scope, receive, observe)

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=wire), base_url='http://test') as client:
            post = asyncio.create_task(client.post('/api/channels', json={'username': 'example_channel'}))
            await asyncio.wait_for(entered.wait(), 2)
            try:
                assert body_sent.is_set()
                assert (await client.get('/api/channels/1')).json()['status'] == 'collecting'
            finally:
                release.set()
                await post

    asyncio.run(scenario())


def test_empty_channel_unavailable_and_http_failure_have_distinct_states(database):
    empty = HTML[:HTML.index('<div class="tgme_channel_history">')] + '<div class="tgme_channel_history"></div>'

    def telegram(request):
        username = request.url.path.rsplit('/', 1)[-1]
        if username == 'empty_channel':
            return httpx.Response(200, text=empty.replace('example_channel', 'empty_channel'), headers={'content-type': 'text/html'})
        if username == 'private_channel':
            return httpx.Response(302, headers={'location': 'https://elsewhere.test/secret'})
        raise httpx.ReadTimeout('private transport details', request=request)

    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=collection_app(database, telegram)), base_url='http://test') as client:
            for username, status in [('empty_channel', 'ready'), ('private_channel', 'unavailable'), ('error_channel', 'error')]:
                added = await client.post('/api/channels', json={'username': username})
                channel = (await client.get(f"/api/channels/{added.json()['id']}")).json()
                assert channel['status'] == status
                assert channel['post_count'] == 0
                assert 'private transport details' not in (channel['last_error'] or '')
                assert (channel['last_success_at'] is not None) == (status == 'ready')
            for username in ['https://evil.test', '@@durov', 'bad-name', 'аbc', '', 'x'*33]:
                assert (await client.post('/api/channels', json={'username': username})).status_code == 422
            assert (await client.get('/api/channels/999')).status_code == 404
            assert (await client.get('/api/channels/1/posts?limit=0')).status_code == 422

    asyncio.run(scenario())


def test_repeat_collection_preserves_post_keys_and_new_observation_time(database):
    from datetime import datetime, timezone
    from app.collection import collect_channel

    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=HTML, headers={'content-type': 'text/html'}))

    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=collection_app(database, transport.handler)), base_url='http://test') as client:
            await client.post('/api/channels', json={'username': 'example_channel'})
            observed = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
            await collect_channel(1, database, transport, observed)
            await collect_channel(1, database, transport, observed)
            assert (await client.get('/api/channels/1')).json()['post_count'] == 2
            posts = (await client.get('/api/channels/1/posts?limit=1')).json()
            assert posts['items'][0]['observed_at'] == '2026-10-09T12:00:00Z'
            assert posts['next_cursor'] == 15
            page = (await client.get('/api/channels/1/posts?before_message_id=15')).json()
            assert [post['message_id'] for post in page['items']] == [12]
            assert page['next_cursor'] is None
            filtered = (await client.get('/api/channels/1/posts?from=2026-10-08T00:00:00Z&to=2026-10-09T00:00:00Z')).json()
            assert [post['message_id'] for post in filtered['items']] == [15]

    asyncio.run(scenario())
