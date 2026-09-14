from __future__ import annotations

from pathlib import Path

import pytest
import requests_mock

from mahanavi.exceptions import NotificationError
from mahanavi.notifications.telegram_notifier import (
    CAPTION_LIMIT,
    MESSAGE_LIMIT,
    TelegramNotifier,
)

BOT_TOKEN = "123:ABC"
ADMIN_CHAT_ID = "999999"
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
SEND_PHOTO_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"


def _notifier(**overrides) -> TelegramNotifier:
    kwargs = dict(bot_token=BOT_TOKEN, admin_chat_id=ADMIN_CHAT_ID, max_retries=0, backoff_seconds=0)
    kwargs.update(overrides)
    return TelegramNotifier(**kwargs)


def test_missing_credentials_raise() -> None:
    with pytest.raises(NotificationError):
        TelegramNotifier(bot_token="", admin_chat_id=ADMIN_CHAT_ID)
    with pytest.raises(NotificationError):
        TelegramNotifier(bot_token=BOT_TOKEN, admin_chat_id="")


def test_notify_without_screenshot_sends_text_message_only() -> None:
    with requests_mock.Mocker() as m:
        m.post(SEND_MESSAGE_URL, json={"ok": True, "result": {}})
        _notifier().notify("Run succeeded for 2026-07-20")

    assert m.call_count == 1
    assert m.request_history[0].url == SEND_MESSAGE_URL


def test_notify_with_screenshot_sends_both_photo_and_message(tmp_path: Path) -> None:
    screenshot = tmp_path / "shot.png"
    screenshot.write_bytes(b"fake-png-bytes")

    with requests_mock.Mocker() as m:
        m.post(SEND_PHOTO_URL, json={"ok": True, "result": {}})
        m.post(SEND_MESSAGE_URL, json={"ok": True, "result": {}})
        _notifier().notify("Run succeeded", screenshot_path=screenshot)

    urls_called = [r.url for r in m.request_history]
    assert SEND_PHOTO_URL in urls_called
    assert SEND_MESSAGE_URL in urls_called


def test_notify_with_nonexistent_screenshot_path_sends_message_only(tmp_path: Path) -> None:
    missing_screenshot = tmp_path / "does_not_exist.png"

    with requests_mock.Mocker() as m:
        m.post(SEND_MESSAGE_URL, json={"ok": True, "result": {}})
        _notifier().notify("Run succeeded", screenshot_path=missing_screenshot)

    assert m.call_count == 1
    assert m.request_history[0].url == SEND_MESSAGE_URL


def test_message_includes_timestamp() -> None:
    with requests_mock.Mocker() as m:
        m.post(SEND_MESSAGE_URL, json={"ok": True, "result": {}})
        _notifier().notify("Hello")

    from urllib.parse import parse_qs
    sent_text = parse_qs(m.request_history[0].text)["text"][0]
    assert "🕐" in sent_text
    assert "Hello" in sent_text


def test_api_error_is_logged_not_raised(caplog) -> None:
    with requests_mock.Mocker() as m:
        m.post(SEND_MESSAGE_URL, json={"ok": False, "description": "chat not found"})
        with caplog.at_level("ERROR"):
            _notifier().notify("Hello")  # must not raise

    assert any("chat not found" in record.message for record in caplog.records)


def test_http_failure_after_retries_is_logged_not_raised(caplog) -> None:
    with requests_mock.Mocker() as m:
        m.post(SEND_MESSAGE_URL, status_code=500)
        with caplog.at_level("ERROR"):
            _notifier(max_retries=1).notify("Hello")  # must not raise

    assert m.call_count == 2
    assert any("Telegram notification" in record.message for record in caplog.records)


def test_long_message_is_truncated_to_message_limit() -> None:
    with requests_mock.Mocker() as m:
        m.post(SEND_MESSAGE_URL, json={"ok": True, "result": {}})
        _notifier().notify("x" * (MESSAGE_LIMIT + 1000))

    from urllib.parse import parse_qs
    sent_text = parse_qs(m.request_history[0].text)["text"][0]
    assert len(sent_text) <= MESSAGE_LIMIT
