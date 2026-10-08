import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import httpx
from bs4 import BeautifulSoup


class PreviewUnavailable(Exception):
    pass


class InvalidPreview(Exception):
    pass


@dataclass
class PreviewPost:
    message_id: int
    published_at: datetime
    text: str
    original_url: str
    views: int | None
    reactions: dict[str, int] | None


@dataclass
class Preview:
    title: str
    subscribers: int | None
    posts: list[PreviewPost]


def parse_counter(value):
    if value is None:
        return None
    value = re.sub(r'[\s,]', '', value).upper()
    match = re.fullmatch(r'(\d+(?:\.\d+)?)([KM]?)', value)
    if not match:
        raise InvalidPreview('Invalid counter')
    multiplier = {'': 1, 'K': 1000, 'M': 1000000}[match[2]]
    return int(Decimal(match[1]) * multiplier)


def parse_preview(html, username):
    soup = BeautifulSoup(html, 'html.parser')
    info = soup.select_one('.tgme_channel_info')
    history = soup.select_one('.tgme_channel_history')
    if info is None or history is None:
        if soup.select_one('.tgme_page_title') is not None:
            raise PreviewUnavailable()
        raise InvalidPreview('Missing channel preview')
    title = info.select_one('.tgme_channel_info_header_title')
    identity = info.select_one('.tgme_channel_info_header_username')
    if title is None or identity is None or identity.get_text(strip=True).lower() != f'@{username}':
        raise InvalidPreview('Invalid channel identity')
    subscribers = None
    for counter in info.select('.tgme_channel_info_counter'):
        kind = counter.select_one('.counter_type')
        value = counter.select_one('.counter_value')
        if kind and kind.get_text(strip=True) == 'subscribers':
            subscribers = parse_counter(value.get_text() if value else None)
    posts = []
    for message in history.select('.tgme_widget_message[data-post]'):
        match = re.fullmatch(rf'{re.escape(username)}/([1-9]\d*)', message['data-post'], re.IGNORECASE)
        timestamp = message.select_one('.tgme_widget_message_date time[datetime]')
        if match is None or timestamp is None:
            raise InvalidPreview('Invalid post identity or date')
        try:
            published_at = datetime.fromisoformat(timestamp['datetime'])
            if published_at.tzinfo is None:
                raise ValueError('Missing timezone')
        except ValueError as error:
            raise InvalidPreview('Invalid post date') from error
        text = message.select_one('.tgme_widget_message_text')
        if text:
            for br in text.select('br'):
                br.replace_with('\n')
            for block in text.select('p, div'):
                block.append('\n')
        views = message.select_one('.tgme_widget_message_views')
        reactions = {}
        for reaction in message.select('.tgme_reaction'):
            emoji = reaction.select_one('tg-emoji, .emoji')
            if 'tgme_reaction_paid' in reaction.get('class', []):
                key = 'paid'
            elif emoji:
                key = emoji.get_text(strip=True) or f"custom:{emoji.get('emoji-id', '')}"
                if key == 'custom:':
                    continue
                emoji.extract()
            else:
                continue
            reactions[key] = parse_counter(reaction.get_text(strip=True))
        message_id = int(match[1])
        posts.append(PreviewPost(
            message_id, published_at.astimezone(timezone.utc), text.get_text().strip() if text else '',
            f'https://t.me/{username}/{message_id}',
            parse_counter(views.get_text() if views else None), reactions or None,
        ))
    return Preview(title.get_text(strip=True), subscribers, posts)


async def fetch_preview(username, client):
    response = await client.get(f'https://t.me/s/{username}')
    if response.status_code in (301, 302, 303, 307, 308, 404):
        raise PreviewUnavailable()
    response.raise_for_status()
    if 'text/html' not in response.headers.get('content-type', ''):
        raise InvalidPreview('Expected HTML')
    return parse_preview(response.text, username)
