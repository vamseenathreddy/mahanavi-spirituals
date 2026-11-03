"""Stdlib-only gate for the Hindi Purana Concept Shorts (Divine Mantra Sangam and Devotional Trance Beats).

They post every other day, on the days the Chanakya card does not (from Wed 4 Nov 2026), at a day-seeded random minute inside a window.
    python -m channels.purana_hindi_plan --channel sangam|trance [--now 2026-11-04T01:00:00]   # writes post=true/false
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

from channels import chanakya_plan as cp
from channels.engine import gate as gate_mod
from channels.engine import state as state_mod

IST = ZoneInfo("Asia/Kolkata")
# channel: (window start, window minutes, latest)
WINDOWS = {"sangam": (dt.time(0, 20), 100, dt.time(2, 15)), "trance": (dt.time(11, 0), 100, dt.time(13, 15))}


def is_post_day(d: dt.date) -> bool:
    return d > cp.SERIES_START and cp.plan(d) is None


def gate(channel: str, now: dt.datetime) -> int:
    d = now.astimezone(IST).date()
    ws, wm, latest = WINDOWS[channel]
    if not is_post_day(d) and os.environ.get("FORCE_POST") != "true":
        post, msg, iso = False, f"DECISION: skip, not a Purana concept day ({d})", d.isoformat()
    else:
        post, msg, iso = gate_mod.decide(f"purana_hi_{channel}", now, state_mod.load(), ws, wm, latest,
                                         force=os.environ.get("FORCE_POST") == "true")
    print(msg)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"post={'true' if post else 'false'}\ndate={iso}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", choices=sorted(WINDOWS), required=True)
    ap.add_argument("--now", default="")
    a = ap.parse_args()
    sys.exit(gate(a.channel, dt.datetime.fromisoformat(a.now).replace(tzinfo=IST) if a.now else dt.datetime.now(IST)))
