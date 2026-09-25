"""
Scheduling: runs DailyPipeline once a day at settings.post_hour:post_minute
in settings.timezone, using APScheduler's cron trigger.

Kept separate from pipeline.py and main.py so the scheduling concern
(when to run) is independent of both the orchestration logic (what to run)
and process bootstrapping (how the process starts).
"""

from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from mahanavi.config import Settings
from mahanavi.pipeline import DailyPipeline

logger = logging.getLogger(__name__)

JOB_ID = "daily_devotional_post"

# If the process was down at the scheduled time (server restart, deploy,
# power outage), APScheduler will still fire the job as long as it comes
# back up within this many seconds of the scheduled time, rather than
# silently skipping that day's post entirely.
MISFIRE_GRACE_SECONDS = 3600


def build_scheduler(pipeline: DailyPipeline, settings: Settings) -> BlockingScheduler:
    tz = ZoneInfo(settings.timezone)
    scheduler = BlockingScheduler(timezone=tz)

    def _run_todays_job() -> None:
        today = datetime.now(tz).date()
        try:
            pipeline.run_for_date(today)
        except Exception:  # noqa: BLE001 - the scheduler must survive an unexpected crash
            logger.exception("Unhandled exception escaped DailyPipeline.run_for_date for %s", today)

    scheduler.add_job(
        func=_run_todays_job,
        trigger=CronTrigger(hour=settings.post_hour, minute=settings.post_minute, timezone=tz),
        id=JOB_ID,
        name="Mahanavi Spirituals daily devotional post",
        misfire_grace_time=MISFIRE_GRACE_SECONDS,
        coalesce=True,   # if multiple runs were missed, only run once on catch-up
        max_instances=1,  # never let two runs overlap
    )
    return scheduler
