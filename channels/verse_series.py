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
    variant: str = "meaning"   # "meaning" = verse + meaning card; "chant" = first line + Har Har Mahadev, sound-led (Trance Beats)
    bg_channel: str = ""   # take pictures from this channel's backgrounds instead (Trance Beats has no Shiva pictures)
    image_skip: str = ""   # comma list: leave out background pictures whose file name contains any of these
    music_channel: str = ""   # take the Om music from this channel instead of `channel`
    bg_video: str = ""        # comma list of repo-relative mp4 clips, cross-faded into a never-repeating background; pictures when missing
    bg_shift: int = 0         # rotates which clip is used (so the two channels do not look identical)
    seconds: float = 0        # Short length; 0 = the shared default (15 s)


SERIES = {
    # Divine Mantra Sangam: Shiv Tandav Stotram, 15 verses, 9:00-9:50 AM IST from Tue 10 Nov 2026
    "shiv_tandav_hi": Series("shiv_tandav_hi", dt.date(2026, 11, 10), 15, (dt.time(9, 0), 50, dt.time(9, 55)), "shiv_tandav", "hi", "mantra_sangam", "mantra sangam", "shiva"),
    # Devotional Trance Beats: the same stotram as a chant loop, 15 days, 8:00-8:50 AM IST from Tue 10 Nov 2026
    "shiv_tandav_trance": Series("shiv_tandav_trance", dt.date(2026, 11, 10), 15, (dt.time(8, 0), 50, dt.time(8, 55)), "shiv_tandav_trance", "hi", "trance_beats", "trance beats", "shiva", "chant", "mantra_sangam"),
    # The 4 Vedas, one mantra a day for 10 days from Thu 26 Nov 2026 (owner approved the start 2026-11-25).
    # Mahanavi (Telugu + English) 11:00-11:50 AM IST; Divine Mantra Sangam (Hindi + English) 9:00-9:50 AM IST. Pictures and Om music from Sangam, no Shiva-only pictures.
    "vedas_te": Series("vedas_te", dt.date(2026, 11, 26), 10, (dt.time(11, 0), 50, dt.time(11, 55)), "vedas", "te", "mahanavi", "mahanavi", "", "meaning", "mantra_sangam", "shiva,nandi", "mantra_sangam"),
    "vedas_hi": Series("vedas_hi", dt.date(2026, 11, 26), 10, (dt.time(9, 0), 50, dt.time(9, 55)), "vedas", "hi", "mantra_sangam", "mantra sangam", "", "meaning", "", "shiva,nandi", ""),
    # Vishnu Sahasranamam, one verse a day from Sat 28 Nov 2026 (owner 2026-11-27). Mahanavi (Telugu + English) 10:00-10:55 AM IST,
    # Divine Mantra Sangam (Hindi + English) 10:00-10:55 AM IST. Each channel's own default music; Vishwaroopa video background when supplied.
    "vishnu_te": Series("vishnu_te", dt.date(2026, 11, 28), 10, (dt.time(10, 0), 50, dt.time(10, 55)), "vishnu", "te", "mahanavi", "mahanavi", "", "meaning", "mantra_sangam", "shiva,nandi", "", "assets/vishnu/vishwaroopa_a.mp4,assets/vishnu/vishwaroopa_b.mp4,assets/vishnu/vishwaroopa_c.mp4", 0, 8),
    "vishnu_hi": Series("vishnu_hi", dt.date(2026, 11, 28), 10, (dt.time(10, 0), 50, dt.time(10, 55)), "vishnu", "hi", "mantra_sangam", "mantra sangam", "", "meaning", "", "shiva,nandi", "", "assets/vishnu/vishwaroopa_a.mp4,assets/vishnu/vishwaroopa_b.mp4,assets/vishnu/vishwaroopa_c.mp4", 1, 8),
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
