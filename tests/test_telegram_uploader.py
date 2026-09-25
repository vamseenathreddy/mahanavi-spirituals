from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import requests_mock

from mahanavi.core.models import SeoContent
from mahanavi.exceptions import TelegramUploadError
from mahanavi.publishers.telegram_uploader import CAPTION_LIMIT, TelegramUploader

BOT_TOKEN = "123:ABC"
CHANNEL_ID = "@testchannel"
SEND_PHOTO_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"


def _seo(caption_body: str = "Hello devotees") -> SeoContent:
    return SeoContent(
        title_telugu="Title",
        description_telugu=caption_body,
        keywords_english=["a"],
        hashtags_telugu=["#a"],
        hashtags_trending=["#b"],
        alt_text="alt",
    )


def _image(tmp_path: Path) -> Path:
    p = tmp_path / "image.jpg"
    p.write_bytes(b"fake-jpeg-bytes")
    return p


def _uploader(max_retries: int = 0) -> TelegramUploader:
    return TelegramUploader(
        bot_token=BOT_TOKEN, channel_id=CHANNEL_ID, max_retries=max_retries, backoff_seconds=0
    )


def test_missing_credentials_raise() -> None:
    with pytest.raises(TelegramUploadError):
        TelegramUploader(bot_token="", channel_id=CHANNEL_ID)
    with pytest.raises(TelegramUploadError):
        TelegramUploader(bot_token=BOT_TOKEN, channel_id="")


def test_successful_publish(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(
            SEND_PHOTO_URL,
            json={"ok": True, "result": {"message_id": 42, "chat": {"username": "testchannel"}}},
        )
        result = _uploader().publish(_image(tmp_path), _seo())

    assert result.success is True
    assert result.post_url == "https://t.me/testchannel/42"


def test_telegram_api_error_response(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(SEND_PHOTO_URL, json={"ok": False, "description": "chat not found"})
        result = _uploader().publish(_image(tmp_path), _seo())

    assert result.success is False
    assert "chat not found" in result.error_message


def test_http_failure_after_retries(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(SEND_PHOTO_URL, status_code=500)
        result = _uploader(max_retries=1).publish(_image(tmp_path), _seo())

    assert result.success is False
    assert m.call_count == 2


def test_long_caption_is_truncated_before_sending(tmp_path: Path) -> None:
    from mahanavi.text_utils import fit_text

    long_caption = "x" * (CAPTION_LIMIT + 500)
    fitted = fit_text(long_caption, CAPTION_LIMIT)
    assert len(fitted) == CAPTION_LIMIT
    assert fitted.endswith("…")


def test_short_caption_is_untouched() -> None:
    from mahanavi.text_utils import fit_text

    short_caption = "Om Namah Shivaya"
    assert fit_text(short_caption, CAPTION_LIMIT) == short_caption
