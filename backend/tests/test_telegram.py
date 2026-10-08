from datetime import datetime, timezone
from pathlib import Path

from app.telegram import parse_preview


FIXTURE = Path(__file__).parent / 'fixtures/preview.html'


def test_preview_normalizes_posts_and_available_metrics():
    preview = parse_preview(FIXTURE.read_text(), 'example_channel')
    assert preview.title == 'Тестовий канал'
    assert preview.subscribers == 2500000
    first, media = preview.posts
    assert first.message_id == 12
    assert first.text == 'Перший рядок\n\nДругий & третій'
    assert first.published_at == datetime(2026, 10, 7, 10, tzinfo=timezone.utc)
    assert first.original_url == 'https://t.me/example_channel/12'
    assert first.views == 1200
    assert first.reactions == {'👍': 12, 'custom:123456': 1300, 'paid': 3}
    assert media.message_id == 15
    assert media.text == ''
    assert media.views is None
    assert media.reactions is None


def test_empty_public_channel_keeps_unknown_subscribers():
    html = '<div class="tgme_channel_info"><div class="tgme_channel_info_header_title">Empty</div><div class="tgme_channel_info_header_username">@empty_channel</div></div><div class="tgme_channel_history"></div>'
    preview = parse_preview(html, 'empty_channel')
    assert preview.posts == []
    assert preview.subscribers is None


def test_unavailable_and_malformed_pages_are_distinct():
    import pytest
    from app.telegram import InvalidPreview, PreviewUnavailable

    with pytest.raises(PreviewUnavailable):
        parse_preview('<div class="tgme_page_title">Unavailable</div>', 'private_channel')
    with pytest.raises(InvalidPreview):
        parse_preview('<html>Gateway error</html>', 'example_channel')
    with pytest.raises(InvalidPreview):
        parse_preview(FIXTURE.read_text().replace('2026-10-07T12:00:00+02:00', 'not-a-date'), 'example_channel')
