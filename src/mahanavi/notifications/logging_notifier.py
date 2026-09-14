"""
LoggingNotifier: a placeholder Notifier that just logs the message instead
of sending a real alert anywhere. Exists so DailyPipeline is fully
runnable before a real notifier (e.g. Telegram) is wired in — swap it out
by constructing DailyPipeline with a different Notifier implementation;
nothing else changes.
"""

from __future__ import annotations

import logging
from pathlib import Path

from mahanavi.core.interfaces import Notifier

logger = logging.getLogger(__name__)


class LoggingNotifier(Notifier):
    """Logs the notification instead of sending it anywhere. Placeholder."""

    def notify(self, message: str, screenshot_path: Path | None = None) -> None:
        logger.info("NOTIFICATION: %s%s", message, f" (screenshot: {screenshot_path})" if screenshot_path else "")
