from __future__ import annotations

from pathlib import Path

import pytest

from mahanavi.config import Settings
from mahanavi.exceptions import ConfigError
from mahanavi.publishers.facebook_uploader import FacebookUploader
from mahanavi.publishers.factory import build_publishers
from mahanavi.publishers.instagram_uploader import InstagramUploader
from mahanavi.publishers.telegram_uploader import TelegramUploader
from mahanavi.publishers.youtube_playwright_uploader import YouTubePlaywrightUploader


def _settings(tmp_path: Path, **overrides: object) -> Settings:
    images_root = tmp_path / "Images"
    images_root.mkdir(parents=True, exist_ok=True)
    base = dict(
        images_root=images_root,
        output_dir=tmp_path / "out",
        database_path=tmp_path / "db.sqlite",
        log_dir=tmp_path / "logs",
        telegram_bot_token="token",
        telegram_channel_id="@chan",
    )
    base.update(overrides)
    return Settings(**base)


def test_default_publishers_are_youtube_and_telegram(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    publishers = build_publishers(settings)
    types = {type(p) for p in publishers}
    assert types == {YouTubePlaywrightUploader, TelegramUploader}


def test_missing_telegram_credentials_raises(tmp_path: Path) -> None:
    settings = _settings(tmp_path, telegram_bot_token=None)
    with pytest.raises(ConfigError):
        build_publishers(settings)


def test_facebook_included_when_enabled(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path, enable_facebook=True,
        facebook_page_id="123", facebook_page_access_token="tok",
    )
    publishers = build_publishers(settings)
    assert any(isinstance(p, FacebookUploader) for p in publishers)


def test_facebook_enabled_without_credentials_raises(tmp_path: Path) -> None:
    settings = _settings(tmp_path, enable_facebook=True)
    with pytest.raises(ConfigError):
        build_publishers(settings)


def test_instagram_included_when_enabled(tmp_path: Path) -> None:
    settings = _settings(
        tmp_path, enable_instagram=True,
        instagram_business_account_id="ig123", instagram_access_token="tok",
        instagram_image_public_base_url="https://example.com/images",
    )
    publishers = build_publishers(settings)
    assert any(isinstance(p, InstagramUploader) for p in publishers)


def test_instagram_enabled_without_credentials_raises(tmp_path: Path) -> None:
    settings = _settings(tmp_path, enable_instagram=True)
    with pytest.raises(ConfigError):
        build_publishers(settings)


def test_unsupported_youtube_method_raises(tmp_path: Path) -> None:
    settings = _settings(tmp_path, youtube_community_post_method="api")
    with pytest.raises(ConfigError):
        build_publishers(settings)
