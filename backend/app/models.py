from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, ForeignKeyConstraint, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Channel(Base):
    __tablename__ = 'channels'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    title: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default='pending', server_default='pending')
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)


class Post(Base):
    __tablename__ = 'posts'

    channel_id: Mapped[int] = mapped_column(ForeignKey('channels.id'), primary_key=True)
    message_id: Mapped[int] = mapped_column(primary_key=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    text: Mapped[str] = mapped_column(Text)
    original_url: Mapped[str] = mapped_column(Text)


class ChannelObservation(Base):
    __tablename__ = 'channel_observations'

    channel_id: Mapped[int] = mapped_column(ForeignKey('channels.id'), primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    subscribers: Mapped[int | None] = mapped_column(BigInteger)


class PostObservation(Base):
    __tablename__ = 'post_observations'
    __table_args__ = (ForeignKeyConstraint(['channel_id', 'message_id'], ['posts.channel_id', 'posts.message_id']),)

    channel_id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    views: Mapped[int | None] = mapped_column(BigInteger)
    reactions: Mapped[dict[str, int] | None] = mapped_column(JSON(none_as_null=True))
