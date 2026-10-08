from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models import Channel, ChannelObservation, Post, PostObservation
from app.telegram import InvalidPreview, PreviewUnavailable, fetch_preview


async def collect_channel(channel_id, engine, transport=None, observed_at=None):
    observed_at = observed_at or datetime.now(timezone.utc)
    with Session(engine) as session:
        channel = session.get(Channel, channel_id)
        username = channel.username
        channel.status = 'collecting'
        channel.last_attempt_at = observed_at
        channel.last_error = None
        session.commit()
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False, transport=transport) as client:
            preview = await fetch_preview(username, client)
    except PreviewUnavailable:
        status, error = 'unavailable', 'Публічне прев’ю каналу недоступне.'
    except (httpx.HTTPError, InvalidPreview):
        status, error = 'error', 'Не вдалося зібрати дані Telegram. Спробу не завершено.'
    else:
        with Session(engine) as session:
            channel = session.get(Channel, channel_id)
            for item in preview.posts:
                session.merge(Post(channel_id=channel_id, message_id=item.message_id,
                    published_at=item.published_at, text=item.text, original_url=item.original_url))
            session.flush()
            session.merge(ChannelObservation(channel_id=channel_id, observed_at=observed_at, subscribers=preview.subscribers))
            for item in preview.posts:
                session.merge(PostObservation(channel_id=channel_id, message_id=item.message_id,
                    observed_at=observed_at, views=item.views, reactions=item.reactions))
            channel.title = preview.title
            channel.status = 'ready'
            channel.last_success_at = observed_at
            channel.last_error = None
            session.commit()
        return
    with Session(engine) as session:
        channel = session.get(Channel, channel_id)
        channel.status = status
        channel.last_error = error
        session.commit()
