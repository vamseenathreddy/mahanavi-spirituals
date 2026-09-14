"""
TelegramNotifier: sends the operator (you) a Telegram message after every
run — success or failure, the posting time, the generated caption, and a
screenshot if one was captured (e.g. from the YouTube Playwright uploader).

This talks to a DIFFERENT chat than TelegramUploader: TelegramUploader
posts the devotional content to your public channel
(settings.telegram_channel_id); this class sends operator alerts to your
own personal/admin chat (settings.telegram_admin_chat_id) — typically your
own Telegram user ID, or a private "ops" group. Same bot, two destinations.

Setup: message your bot at least once from the admin account/group first —
Telegram bots cannot message a chat that hasn't initiated contact with them.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from mahanavi.core.interfaces import Notifier
from mahanavi.exceptions import NotificationError, RetryExhaustedError
from mahanavi.retry import retry_with_backoff
from mahanavi.text_utils import fit_text

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"
MESSAGE_LIMIT = 4096   # Telegram's sendMessage text limit
CAPTION_LIMIT = 1024   # Telegram's sendPhoto caption limit (lower than sendMessage)


class TelegramNotifier(Notifier):
    """Sends run-result notifications to an operator's Telegram chat."""

    def __init__(
        self,
        bot_token: str,
        admin_chat_id: str,
        timezone: str = "Asia/Kolkata",
        max_retries: int = 3,
        backoff_seconds: float = 5.0,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        if not bot_token or not admin_chat_id:
            raise NotificationError(
                "TelegramNotifier requires both bot_token and admin_chat_id to be set."
            )
        self._bot_token = bot_token
        self._admin_chat_id = admin_chat_id
        self._timezone = ZoneInfo(timezone)
        self._timeout_seconds = timeout_seconds
        self._session = session or requests.Session()

        self._send_message = retry_with_backoff(
            max_retries=max_retries, backoff_seconds=backoff_seconds,
            exceptions=(requests.RequestException,),
        )(self._send_message_uncached)
        self._send_photo = retry_with_backoff(
            max_retries=max_retries, backoff_seconds=backoff_seconds,
            exceptions=(requests.RequestException,),
        )(self._send_photo_uncached)

    def notify(self, message: str, screenshot_path: Path | None = None) -> None:
        timestamp = datetime.now(self._timezone).strftime("%Y-%m-%d %H:%M:%S %Z")
        full_text = f"🕐 {timestamp}\n\n{message}"

        # A failed notification must never crash the pipeline run that's
        # already finished by the time notify() is called — log and move on.
        try:
            if screenshot_path and screenshot_path.exists():
                caption = fit_text(full_text, CAPTION_LIMIT, context="Telegram notification photo caption")
                self._send_photo(screenshot_path, caption)
                # The photo caption may have been truncated — always also send
                # the full text separately so nothing is lost.
                self._send_message(fit_text(full_text, MESSAGE_LIMIT, context="Telegram notification message"))
            else:
                self._send_message(fit_text(full_text, MESSAGE_LIMIT, context="Telegram notification message"))
        except RetryExhaustedError as exc:
            logger.error("Failed to send Telegram notification after retries: %s", exc)
        except NotificationError as exc:
            logger.error("Failed to send Telegram notification: %s", exc)

    def _send_message_uncached(self, text: str) -> None:
        url = f"{TELEGRAM_API_BASE}/bot{self._bot_token}/sendMessage"
        response = self._session.post(
            url, data={"chat_id": self._admin_chat_id, "text": text},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok", False):
            raise NotificationError(f"Telegram sendMessage error: {payload.get('description')}")

    def _send_photo_uncached(self, screenshot_path: Path, caption: str) -> None:
        url = f"{TELEGRAM_API_BASE}/bot{self._bot_token}/sendPhoto"
        with screenshot_path.open("rb") as photo_file:
            response = self._session.post(
                url,
                data={"chat_id": self._admin_chat_id, "caption": caption},
                files={"photo": photo_file},
                timeout=self._timeout_seconds,
            )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok", False):
            raise NotificationError(f"Telegram sendPhoto error: {payload.get('description')}")
