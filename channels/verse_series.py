"""Stdlib-only plan + gate for the daily verse series (one verse a day, no repeats, one Short each).

A series is a row in SERIES. The day index is (date - start).days, so no counter can drift or repeat; outside 0..count-1 nothing posts.
The posting minute is day-seeded random inside the window (channels/engine/gate.py).

    python -m channels.verse_series --series shiv_tandav_hi [--now 2026-11-10T09:30:00]     # writes post=true/false
"""
import argparse
import datetime as dt
import hashlib
import os
import sys
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from channels.engine import gate as gate_mod
from channels.engine import state as state_mod

IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True)
class Series:
    key: str
    start: dt.date
    count: int
    window: tuple          # (window start, window minutes, latest)
    slot: str              # POST_SLOT marker in the channel's state file
    lang: str              # "hi" or "te"
    channel: str           # music / image set: "mantra_sangam", "trance_beats", "mahanavi"
    channel_word: str      # must appear in the YouTube channel title the token acts as
    image_hint: str = ""   # only background pictures whose file name contains this (falls back to all)


SERIES = {
    # Divine Mantra Sangam: Shiv Tandav Stotram, 15 verses, 9:00-9:50 AM IST from Tue 10 Nov 2026
    "shiv_tandav_hi": Series("shiv_tandav_hi", dt.date(2026, 11, 10), 15, (dt.time(9, 0), 50, dt.time(9, 55)), "shiv_tandav", "hi", "mantra_sangam", "mantra sangam", "shiva"),
}


def plan(key: str, d: dt.date) -> int | None:
    s = SERIES[key]
    n = (d - s.start).days
    return n if 0 <= n < s.count else None


def jitter_seconds(key: str, d: dt.date) -> int:
    return int(hashlib.sha256(f"verse-{key}-sec-{d.isoformat()}".encode()).hexdigest(), 16) % 60


def gate(key: str, now: dt.datetime) -> int:
    d = now.astimezone(IST).date()
    s = SERIES[key]
    if plan(key, d) is None:
        post, msg, iso = False, f"DECISION: skip, no {key} verse on {d} (series {s.start} for {s.count} days)", d.isoformat()
    else:
        post, msg, iso = gate_mod.decide(f"verse_{key}", now, state_mod.load(), *s.window, force=os.environ.get("FORCE_POST") == "true")
    print(msg)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"post={'true' if post else 'false'}\ndate={iso}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", choices=sorted(SERIES), required=True)
    ap.add_argument("--now", default="")
    a = ap.parse_args()
    sys.exit(gate(a.series, dt.datetime.fromisoformat(a.now).replace(tzinfo=IST) if a.now else dt.datetime.now(IST)))
