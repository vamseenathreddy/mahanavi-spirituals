from __future__ import annotations

from pathlib import Path

from mahanavi.bootstrap import _build_notifier
from mahanavi.config import Settings
from mahanavi.notifications.logging_notifier import LoggingNotifier
from mahanavi.notifications.telegram_notifier import TelegramNotifier


def _settings(tmp_path: Path, **overrides: object) -> Settings:
    images_root = tmp_path / "Images"
    images_root.mkdir(parents=True, exist_ok=True)
    base = dict(
        images_root=images_root,
        output_dir=tmp_path / "out",
        database_path=tmp_path / "db.sqlite",
        log_dir=tmp_path / "logs",
    )
    base.update(overrides)
    return Settings(**base)


def test_uses_telegram_notifier_when_admin_chat_configured(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path, telegram_bot_token="123:ABC", telegram_admin_chat_id="999",
    )
    notifier = _build_notifier(settings)
    assert isinstance(notifier, TelegramNotifier)


def test_falls_back_to_logging_notifier_without_admin_chat(tmp_path: Path) -> None:
    settings = _settings(tmp_path, telegram_bot_token="123:ABC", telegram_admin_chat_id=None)
    notifier = _build_notifier(settings)
    assert isinstance(notifier, LoggingNotifier)


def test_falls_back_to_logging_notifier_without_bot_token(tmp_path: Path) -> None:
    settings = _settings(tmp_path, telegram_bot_token=None, telegram_admin_chat_id="999")
    notifier = _build_notifier(settings)
    assert isinstance(notifier, LoggingNotifier)
