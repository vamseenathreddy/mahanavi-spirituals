"""schedule_calendar_ahead.py: upload the monthly festival and vrata list Shorts in advance, scheduled in YouTube.

Each month's festival card goes public 10 days before the month starts (7 PM IST), its vrata card the next evening.
Safe to run every day: a card whose title is already on the channel is skipped, so each run schedules only what is missing
(at most --max uploads per run to stay inside the daily YouTube quota) and the earliest releases go first.

    python -m mahanavi.scripts.schedule_calendar_ahead --from 2026-12 --months 24 --max 4 [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from mahanavi.scripts import post_calendar_short as pcs

IST = ZoneInfo("Asia/Kolkata")
LEAD_DAYS = {"festivals": 10, "vratas": 9}


def plan(start: str, months: int, now: dt.datetime) -> list[tuple[dt.datetime, str, str]]:
    y, m = (int(x) for x in start.split("-"))
    out = []
    for i in range(months):
        yy, mm = y + (m - 1 + i) // 12, (m - 1 + i) % 12 + 1
        first = dt.date(yy, mm, 1)
        for kind, lead in LEAD_DAYS.items():
            at = dt.datetime.combine(first - dt.timedelta(days=lead), dt.time(19, 0), tzinfo=IST)
            if at > now + dt.timedelta(hours=1):
                out.append((at, kind, f"{yy}-{mm:02d}"))
    return sorted(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from", dest="start", default="2026-12")
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--max", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    now = dt.datetime.now(IST)
    todo = plan(args.start, args.months, now)
    print(f"{len(todo)} cards to cover, first release {todo[0][0] if todo else '-'}")
    done = 0
    for at, kind, month in todo:
        if done >= args.max:
            break
        cmd = ["--kind", kind, "--month", month, "--publish-at", at.isoformat(), "--skip-if-exists"]
        if args.dry_run:
            print(f"DRY {kind} {month} -> public at {at:%Y-%m-%d %H:%M} IST")
            if pcs.main(cmd + ["--dry-run"]) != 0:
                return 1
            done += 1
            continue
        rc = pcs.main(cmd)
        if rc != 0:
            print(f"::error::stopped at {kind} {month} (quota or upload problem); the next daily run continues from here")
            return 1
        done += 1
    print(f"processed {done} card(s) this run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
