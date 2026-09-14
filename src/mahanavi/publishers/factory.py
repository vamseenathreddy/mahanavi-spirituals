"""
Factory for constructing the list of publish targets to run each day,
based on Settings. YouTube and Telegram are treated as required (per the
project's core requirements); Facebook and Instagram are opt-in via
MAHANAVI_ENABLE_FACEBOOK / MAHANAVI_ENABLE_INSTAGRAM.
"""

from __future__ import annotations

from mahanavi.config import Settings
from mahanavi.core.interfaces import Uploader
from mahanavi.exceptions import ConfigError
from mahanavi.publishers.facebook_uploader import FacebookUploader
from mahanavi.publishers.instagram_uploader import InstagramUploader
from mahanavi.publishers.telegram_uploader import TelegramUploader
from mahanavi.publishers.youtube_playwright_uploader import YouTubePlaywrightUploader


def build_publishers(settings: Settings) -> list[Uploader]:
    publishers: list[Uploader] = []

    # YouTube is always included — it's the primary target.
    if settings.youtube_community_post_method == "playwright":
        publishers.append(YouTubePlaywrightUploader(settings))
    else:
        raise ConfigError(
            f"Unsupported MAHANAVI_YOUTUBE_COMMUNITY_POST_METHOD="
            f"'{settings.youtube_community_post_method}'. Only 'playwright' is "
            "implemented (the YouTube Data API has no Community Post endpoint "
            "as of this writing)."
        )

    # Telegram is always included.
    if not settings.telegram_bot_token or not settings.telegram_channel_id:
        raise ConfigError(
            "Telegram publishing requires MAHANAVI_TELEGRAM_BOT_TOKEN and "
            "MAHANAVI_TELEGRAM_CHANNEL_ID to be set."
        )
    publishers.append(
        TelegramUploader(
            bot_token=settings.telegram_bot_token,
            channel_id=settings.telegram_channel_id,
            max_retries=settings.max_retries,
            backoff_seconds=settings.retry_backoff_seconds,
        )
    )

    if settings.enable_facebook:
        if not settings.facebook_page_id or not settings.facebook_page_access_token:
            raise ConfigError(
                "MAHANAVI_ENABLE_FACEBOOK=true requires MAHANAVI_FACEBOOK_PAGE_ID "
                "and MAHANAVI_FACEBOOK_PAGE_ACCESS_TOKEN."
            )
        publishers.append(
            FacebookUploader(
                page_id=settings.facebook_page_id,
                page_access_token=settings.facebook_page_access_token,
                max_retries=settings.max_retries,
                backoff_seconds=settings.retry_backoff_seconds,
            )
        )

    if settings.enable_instagram:
        if not settings.instagram_business_account_id or not settings.instagram_access_token:
            raise ConfigError(
                "MAHANAVI_ENABLE_INSTAGRAM=true requires MAHANAVI_INSTAGRAM_BUSINESS_ACCOUNT_ID "
                "and MAHANAVI_INSTAGRAM_ACCESS_TOKEN."
            )
        publishers.append(
            InstagramUploader(
                ig_user_id=settings.instagram_business_account_id,
                access_token=settings.instagram_access_token,
                image_public_base_url=settings.instagram_image_public_base_url or "",
                max_retries=settings.max_retries,
                backoff_seconds=settings.retry_backoff_seconds,
            )
        )

    return publishers
