from typing import Annotated, Literal
from datetime import datetime, timedelta, timezone
import re
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_serializer, field_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Channel, ChannelObservation, Post, PostObservation
from app.collection import collect_channel


class ChannelInput(BaseModel):
    username: str

    @field_validator('username')
    @classmethod
    def normalized_username(cls, value):
        value = value.strip().removeprefix('@').lower()
        if not re.fullmatch(r'[a-z0-9_]{1,32}', value):
            raise ValueError('Введіть Telegram username: літери, цифри або _.')
        return value


class ChannelResponse(BaseModel):
    id: int
    username: str
    title: str | None
    status: Literal['pending', 'collecting', 'ready', 'unavailable', 'error']
    subscribers: int | None
    post_count: int
    last_attempt_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    stale: bool
    coverage_from: datetime | None
    coverage_to: datetime | None

    @field_serializer('last_attempt_at', 'last_success_at', 'coverage_from', 'coverage_to')
    def utc_dates(self, value):
        if value is None:
            return None
        return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)).isoformat().replace('+00:00', 'Z')


class PostResponse(BaseModel):
    channel_id: int
    message_id: int
    published_at: datetime
    text: str
    original_url: str
    views: int | None
    reactions: dict[str, int] | None
    observed_at: datetime | None

    @field_serializer('published_at', 'observed_at')
    def utc_dates(self, value):
        if value is None:
            return None
        return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)).isoformat().replace('+00:00', 'Z')


class PostPage(BaseModel):
    items: list[PostResponse]
    next_cursor: int | None


def channel_response(session, channel):
    observation = session.scalar(select(ChannelObservation).where(ChannelObservation.channel_id == channel.id)
        .order_by(ChannelObservation.observed_at.desc()).limit(1))
    count, first, last = session.execute(select(func.count(), func.min(Post.published_at), func.max(Post.published_at))
        .where(Post.channel_id == channel.id)).one()
    success = channel.last_success_at
    if success is not None and success.tzinfo is None:
        success = success.replace(tzinfo=timezone.utc)
    return ChannelResponse(id=channel.id, username=channel.username, title=channel.title,
        status=channel.status, subscribers=observation.subscribers if observation else None,
        post_count=count, last_attempt_at=channel.last_attempt_at, last_success_at=success,
        last_error=channel.last_error, stale=success is None or datetime.now(timezone.utc)-success > timedelta(minutes=90),
        coverage_from=first, coverage_to=last)


def create_app(frontend_dir: Path | None = None, telegram_transport=None):
    application = FastAPI(title="Channel Radar")

    @application.get("/healthz")
    def health():
        return {"status": "ok"}

    @application.get("/api/channels", response_model=list[ChannelResponse])
    def channels(session: Annotated[Session, Depends(get_session)]):
        return [channel_response(session, channel) for channel in session.scalars(select(Channel).order_by(Channel.id))]

    @application.post('/api/channels', response_model=ChannelResponse, status_code=202)
    def add_channel(data: ChannelInput, background: BackgroundTasks, response: Response,
                    session: Annotated[Session, Depends(get_session)]):
        existing = session.scalar(select(Channel).where(Channel.username == data.username))
        if existing is not None:
            response.status_code = 200
            return channel_response(session, existing)
        channel = Channel(username=data.username)
        session.add(channel)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            existing = session.scalar(select(Channel).where(Channel.username == data.username))
            if existing is None:
                raise
            response.status_code = 200
            return channel_response(session, existing)
        background.add_task(collect_channel, channel.id, session.get_bind(), telegram_transport)
        return channel_response(session, channel)

    @application.get('/api/channels/{channel_id}', response_model=ChannelResponse)
    def channel_detail(channel_id: int, session: Annotated[Session, Depends(get_session)]):
        channel = session.get(Channel, channel_id)
        if channel is None:
            raise HTTPException(404, detail={'code': 'channel_not_found', 'message': 'Канал не знайдено.'})
        return channel_response(session, channel)

    @application.get('/api/channels/{channel_id}/posts', response_model=PostPage)
    def channel_posts(channel_id: int, session: Annotated[Session, Depends(get_session)],
                      limit: Annotated[int, Query(ge=1, le=100)] = 20,
                      before_message_id: Annotated[int | None, Query(gt=0)] = None,
                      from_date: Annotated[datetime | None, Query(alias='from')] = None,
                      to_date: Annotated[datetime | None, Query(alias='to')] = None):
        if session.get(Channel, channel_id) is None:
            raise HTTPException(404, detail={'code': 'channel_not_found', 'message': 'Канал не знайдено.'})
        query = select(Post).where(Post.channel_id == channel_id)
        if from_date is not None or to_date is not None:
            if from_date is None or to_date is None or from_date.tzinfo is None or to_date.tzinfo is None or from_date >= to_date:
                raise HTTPException(422, detail={'code': 'invalid_period', 'message': 'Потрібен UTC-період від початку до кінця.'})
            query = query.where(Post.published_at >= from_date.astimezone(timezone.utc), Post.published_at < to_date.astimezone(timezone.utc))
        if before_message_id is not None:
            query = query.where(Post.message_id < before_message_id)
        posts = session.scalars(query.order_by(Post.message_id.desc()).limit(limit+1)).all()
        items = []
        for post in posts[:limit]:
            observation = session.scalar(select(PostObservation).where(PostObservation.channel_id == channel_id,
                PostObservation.message_id == post.message_id).order_by(PostObservation.observed_at.desc()).limit(1))
            items.append(PostResponse(channel_id=channel_id, message_id=post.message_id, published_at=post.published_at,
                text=post.text, original_url=post.original_url, views=observation.views if observation else None,
                reactions=observation.reactions if observation else None, observed_at=observation.observed_at if observation else None))
        return PostPage(items=items, next_cursor=posts[limit-1].message_id if len(posts)>limit else None)

    frontend_root = (frontend_dir or Path(__file__).parents[2] / "frontend/dist").resolve()
    if frontend_root.is_dir():
        @application.get("/{route:path}", include_in_schema=False)
        def frontend(route: str):
            requested_file = (frontend_root / route).resolve()
            if route == "api" or route.startswith("api/") or not requested_file.is_relative_to(frontend_root):
                raise HTTPException(status_code=404)
            if requested_file.is_file():
                return FileResponse(requested_file)
            if route.startswith("assets/") or Path(route).suffix:
                raise HTTPException(status_code=404)
            return FileResponse(frontend_root / "index.html")

    return application


app = create_app()
