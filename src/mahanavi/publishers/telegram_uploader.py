"""
TelegramUploader: publishes the generated image + caption to a Telegram
channel using the official Bot API (sendPhoto). No browser automation
needed here — Telegram's API supports this directly.

Setup required (documented in README): create a bot via @BotFather, get
its token, and add the bot as an admin of your channel so it can post.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import requests

from mahanavi.core.interfaces import Uploader
from mahanavi.core.models import PublishTarget, SeoContent, UploadResult
from mahanavi.exceptions import RetryExhaustedError, TelegramUploadError
from mahanavi.retry import retry_with_backoff
from mahanavi.text_utils import fit_text

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"

# Telegram's Bot API caption limit for media messages (sendPhoto) is 1024
# characters as of this writing. If Telegram changes this, update here.
CAPTION_LIMIT = 1024


class TelegramUploader(Uploader):
    """Publishes an image + caption to a Telegram channel via Bot API."""

    TARGET = PublishTarget.TELEGRAM

    def __init__(
        self,
        bot_token: str,
        channel_id: str,
        max_retries: int = 3,
        backoff_seconds: float = 5.0,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        if not bot_token or not channel_id:
            raise TelegramUploadError(
                "TelegramUploader requires both bot_token and channel_id to be set."
            )
        self._bot_token = bot_token
        self._channel_id = channel_id
        self._timeout_seconds = timeout_seconds
        self._session = session or requests.Session()

        self._send_photo = retry_with_backoff(
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            exceptions=(requests.RequestException,),
        )(self._send_photo_uncached)

    def publish(self, image_path: Path, seo: SeoContent) -> UploadResult:
        caption = fit_text(seo.full_caption(), CAPTION_LIMIT, context="Telegram caption")

        try:
            payload = self._send_photo(image_path, caption)
        except RetryExhaustedError as exc:
            return UploadResult(
                target=PublishTarget.TELEGRAM,
                success=False,
                error_message=f"Telegram upload failed after retries: {exc}",
            )
        except TelegramUploadError as exc:
            return UploadResult(
                target=PublishTarget.TELEGRAM,
                success=False,
                error_message=str(exc),
            )

        message = payload.get("result", {})
        chat = message.get("chat", {})
        username = chat.get("username")
        message_id = message.get("message_id")
        post_url = f"https://t.me/{username}/{message_id}" if username and message_id else None

        logger.info("Published to Telegram channel %s (message_id=%s)", self._channel_id, message_id)
        return UploadResult(target=PublishTarget.TELEGRAM, success=True, post_url=post_url)

    def _send_photo_uncached(self, image_path: Path, caption: str) -> dict:
        url = f"{TELEGRAM_API_BASE}/bot{self._bot_token}/sendPhoto"
        with image_path.open("rb") as photo_file:
            response = self._session.post(
                url,
                data={"chat_id": self._channel_id, "caption": caption},
                files={"photo": photo_file},
                timeout=self._timeout_seconds,
            )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        if not payload.get("ok", False):
            raise TelegramUploadError(f"Telegram API returned an error: {payload.get('description')}")
        return payload

