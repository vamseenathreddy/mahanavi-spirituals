"""
Process entrypoint.

Normal operation (e.g. in Docker):
    python -m mahanavi.main
runs forever, posting once a day at the configured time.

Manual/debug operation:
    python -m mahanavi.main --run-now
    python -m mahanavi.main --run-now --date 2026-07-20
runs the full pipeline once immediately for today (or the given date) and
exits — this is the fastest way to test the whole pipeline end-to-end
without waiting for 5 AM or changing your system clock.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

from mahanavi.bootstrap import build_pipeline
from mahanavi.config import get_settings
from mahanavi.logging_config import configure_logging
from mahanavi.scheduler import build_scheduler

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mahanavi Spirituals daily devotional content pipeline.")
    parser.add_argument(
        "--run-now", action="store_true",
        help="Run the pipeline once immediately and exit, instead of starting the scheduler.",
    )
    parser.add_argument(
        "--date", type=str, default=None,
        help="ISO date (YYYY-MM-DD) to run for with --run-now. Defaults to today in the configured timezone.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_dir)
    pipeline = build_pipeline(settings)

    if args.run_now:
        tz = ZoneInfo(settings.timezone)
        target_date = date.fromisoformat(args.date) if args.date else datetime.now(tz).date()
        result = pipeline.run_for_date(target_date)
        return 0 if result.overall_success else 1

    scheduler = build_scheduler(pipeline, settings)
    logger.info(
        "Scheduler started — daily post at %02d:%02d %s. Press Ctrl+C to stop.",
        settings.post_hour, settings.post_minute, settings.timezone,
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
