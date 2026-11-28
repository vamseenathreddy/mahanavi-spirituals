"""Plan + gate for the Reddy Linux tech Shorts: two cards a day (morning and evening), never repeating.

Card index = (days since START) * 2 + slot, so nothing can drift. When the bank runs out nothing posts (a workflow warning says so).
    python -m channels.tech_series --slot am|pm [--now 2026-11-30T09:30:00]     # writes post=true/false
"""
import argparse
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

from channels.engine import gate as gate_mod
from channels.engine import state as state_mod

IST = ZoneInfo("Asia/Kolkata")
START = dt.date(2026, 11, 30)
WINDOWS = {"am": (dt.time(9, 0), 50, dt.time(9, 55)), "pm": (dt.time(18, 30), 50, dt.time(19, 25))}
SLOTS = {"am": 0, "pm": 1}


def card_index(d: dt.date, slot: str, total: int) -> int | None:
    n = (d - START).days * 2 + SLOTS[slot]
    return n if 0 <= n < total else None


def gate(slot: str, now: dt.datetime) -> int:
    from mahanavi.content import tech_bank

    d = now.astimezone(IST).date()
    idx = card_index(d, slot, tech_bank.count())
    if idx is None:
        post, msg, iso = False, f"DECISION: skip, no tech card for {d} {slot} (starts {START}, {tech_bank.count()} cards)", d.isoformat()
    else:
        os.environ["POST_SLOT"] = f"tech_{slot}"
        post, msg, iso = gate_mod.decide(f"tech_{slot}", now, state_mod.load(), *WINDOWS[slot], force=os.environ.get("FORCE_POST") == "true")
        if tech_bank.count() - idx <= 16:
            print(f"::warning::tech bank: only {tech_bank.count() - idx} cards left, add more to src/mahanavi/content/tech_bank.py")
    print(msg)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"post={'true' if post else 'false'}\ndate={iso}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", choices=sorted(SLOTS), required=True)
    ap.add_argument("--now", default="")
    a = ap.parse_args()
    sys.exit(gate(a.slot, dt.datetime.fromisoformat(a.now).replace(tzinfo=IST) if a.now else dt.datetime.now(IST)))
