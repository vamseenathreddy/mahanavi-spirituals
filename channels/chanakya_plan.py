"""Stdlib-only plan + gate for the Chanakya Neeti Shorts (5 teachings a card, one card a day, no repeats).

Day index = (date - SERIES_START).days; the card is content/chanakya_neeti.card(day, lang). Telugu posts on Mahanavi
Spirituals, Hindi on Divine Mantra Sangam. The posting minute is day-seeded random inside a window.

    python -m channels.chanakya_plan --lang te|hi [--now 2026-11-09T13:00:00]    # writes post=true/false
"""
import argparse
import datetime as dt
import hashlib
import os
import sys
from zoneinfo import ZoneInfo

from channels.engine import gate as gate_mod
from channels.engine import state as state_mod
from mahanavi.content import chanakya_neeti as cn

IST = ZoneInfo("Asia/Kolkata")
SERIES_START = dt.date(2026, 11, 9)       # Monday: day 1
STEP = 2                                  # one card every other day (9, 11, 13 Nov ...)
# (window start, window minutes, latest)
WINDOWS = {"te": (dt.time(0, 0), 110, dt.time(2, 15)), "hi": (dt.time(0, 10), 110, dt.time(2, 15))}
SLOTS = {"te": "chanakya", "hi": "chanakya_hi"}


def plan(d: dt.date) -> int | None:
    """0 based day index for that date, or None outside the series (more teachings are added at the end of SUTRAS to extend it)."""
    n = (d - SERIES_START).days
    if n < 0 or n % STEP:
        return None
    i = n // STEP
    return i if i < cn.days() else None


def jitter_seconds(lang: str, d: dt.date) -> int:
    return int(hashlib.sha256(f"chanakya-{lang}-sec-{d.isoformat()}".encode()).hexdigest(), 16) % 60


def gate(lang: str, now: dt.datetime) -> int:
    d = now.astimezone(IST).date()
    ws, wm, latest = WINDOWS[lang]
    if plan(d) is None:
        post, msg, iso = False, f"DECISION: skip, no Chanakya card on {d} (series from {SERIES_START}, {cn.days()} days)", d.isoformat()
    else:
        post, msg, iso = gate_mod.decide(f"chanakya_{lang}", now, state_mod.load(), ws, wm, latest,
                                         force=os.environ.get("FORCE_POST") == "true")
    print(msg)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"post={'true' if post else 'false'}\ndate={iso}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["te", "hi"], required=True)
    ap.add_argument("--now", default="")
    a = ap.parse_args()
    sys.exit(gate(a.lang, dt.datetime.fromisoformat(a.now).replace(tzinfo=IST) if a.now else dt.datetime.now(IST)))
