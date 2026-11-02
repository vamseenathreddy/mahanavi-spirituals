"""Stdlib-only plan + gate for the Lakshmi 108 names series (so the workflow gate needs no heavy install).

Name number = (date - SERIES_START) + 1; Friday recap = the 7 names of the week before. See
mahanavi/scripts/post_lakshmi_name.py for the full description.

    python -m channels.lakshmi108_plan --kind name|recap [--now 2026-11-06T18:30:00]   # writes post=true/false
"""
import argparse
import datetime as dt
import hashlib
import os
import sys
from zoneinfo import ZoneInfo

from channels.engine import gate as gate_mod
from channels.engine import state as state_mod

IST = ZoneInfo("Asia/Kolkata")
SERIES_START = dt.date(2026, 11, 6)          # name 1 (a Friday)
LAST_DAY = SERIES_START + dt.timedelta(days=107)   # name 108 (Sun 21 Feb 2027)
FIRST_RECAP = SERIES_START + dt.timedelta(days=7)  # Fri 13 Nov: recap of names 1-7
FINAL_RECAP = SERIES_START + dt.timedelta(days=7 * 16)  # Fri 26 Feb 2027: names 106-108

# (window start, window minutes, latest) per kind; the target minute inside the window is day-seeded random
WINDOWS = {"name": (dt.time(18, 0), 100, dt.time(21, 0)), "recap": (dt.time(9, 0), 100, dt.time(12, 0))}
# Hindi channels (Devotional Trance Beats): other slots in the day are 6-8 AM beej, 7-9 AM bhagavatam, 1-3 PM mantra, 7-9 PM gita
WINDOWS_HI = {"name": (dt.time(16, 30), 100, dt.time(19, 0)), "recap": (dt.time(10, 0), 100, dt.time(12, 30))}
SLOTS = {"name": "lakshmi", "recap": "lakshmi_recap"}


def plan(kind: str, d: dt.date) -> int | None:
    """name -> the name number 1..108 for that date; recap -> number of the first name of the week; None = nothing today."""
    if kind == "name":
        n = (d - SERIES_START).days + 1
        return n if 1 <= n <= 108 else None
    if d.weekday() != 4 or not (FIRST_RECAP <= d <= FINAL_RECAP):
        return None
    return 7 * ((d - SERIES_START).days // 7 - 1) + 1


def jitter_seconds(kind: str, d: dt.date, lang: str = "te") -> int:
    return int(hashlib.sha256(f"lakshmi-{kind}{'-hi' if lang == 'hi' else ''}-sec-{d.isoformat()}".encode()).hexdigest(), 16) % 60


def gate(kind: str, now: dt.datetime, lang: str = "te") -> int:
    """GitHub-Actions gate: post=true only inside the series dates and once per day, at the day's random minute."""
    d = now.astimezone(IST).date()
    num = plan(kind, d)
    ws, wm, latest = (WINDOWS_HI if lang == "hi" else WINDOWS)[kind]
    if num is None:
        post, msg, iso = False, f"DECISION: skip, no Lakshmi {kind} Short on {d} (series {SERIES_START} to {LAST_DAY})", d.isoformat()
    else:
        post, msg, iso = gate_mod.decide(f"lakshmi108_{kind}" + ("_hi" if lang == "hi" else ""), now, state_mod.load(), ws, wm, latest,
                                         force=os.environ.get("FORCE_POST") == "true")
    print(msg)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"post={'true' if post else 'false'}\ndate={iso}\n")
    return 0




if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["name", "recap"], required=True)
    ap.add_argument("--lang", choices=["te", "hi"], default="te")
    ap.add_argument("--now", default="")
    a = ap.parse_args()
    sys.exit(gate(a.kind, dt.datetime.fromisoformat(a.now).replace(tzinfo=IST) if a.now else dt.datetime.now(IST), a.lang))
