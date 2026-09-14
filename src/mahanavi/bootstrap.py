"""
Composition root: builds every concrete component from Settings and wires
them into a DailyPipeline. This is the ONE place in the codebase that
imports every concrete implementation — every other module only depends
on the ABCs in core/interfaces.py. Swapping any component (e.g. a real
Telegram notifier once Module 7's notifier is ready) means changing one
line here.
"""

from __future__ import annotations

import logging

from mahanavi.config import Settings
from mahanavi.content.generator import TemplateContentGenerator
from mahanavi.database.db import DatabaseManager
from mahanavi.database.repositories import ImageHistoryRepository, PostLogRepository
from mahanavi.images.renderer import PillowImageRenderer
from mahanavi.images.selector import RandomImageSelector
from mahanavi.notifications.logging_notifier import LoggingNotifier
from mahanavi.notifications.telegram_notifier import TelegramNotifier
from mahanavi.panchang.factory import get_panchang_provider
from mahanavi.pipeline import DailyPipeline
from mahanavi.publishers.factory import build_publishers

logger = logging.getLogger(__name__)


def build_pipeline(settings: Settings) -> DailyPipeline:
    db = DatabaseManager(settings.database_path)
    image_history_repo = ImageHistoryRepository(db)
    post_log_repo = PostLogRepository(db)

    return DailyPipeline(
        image_selector=RandomImageSelector(settings, image_history_repo),
        panchang_provider=get_panchang_provider(settings),
        image_renderer=PillowImageRenderer(settings),
        content_generator=TemplateContentGenerator(settings),
        publishers=build_publishers(settings),
        post_log_repo=post_log_repo,
        notifier=_build_notifier(settings),
    )


def _build_notifier(settings: Settings) -> LoggingNotifier | TelegramNotifier:
    if settings.telegram_bot_token and settings.telegram_admin_chat_id:
        return TelegramNotifier(
            bot_token=settings.telegram_bot_token,
            admin_chat_id=settings.telegram_admin_chat_id,
            timezone=settings.timezone,
            max_retries=settings.max_retries,
            backoff_seconds=settings.retry_backoff_seconds,
        )
    logger.warning(
        "MAHANAVI_TELEGRAM_ADMIN_CHAT_ID is not set — falling back to LoggingNotifier. "
        "You will NOT receive real notifications about run success/failure. "
        "Set MAHANAVI_TELEGRAM_ADMIN_CHAT_ID to enable real Telegram alerts."
    )
    return LoggingNotifier()
