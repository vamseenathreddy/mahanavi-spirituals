"""Gate for the Mahanavi 10-day Ramayana story Shorts: one per day from 2026-11-06, at a day-seeded random minute in
15:00-15:50 IST until Mon 9 Nov, then 9:00-9:50 AM IST from Tue 10 Nov (owner request). Skips when all ten are posted.

  STATE_FILE=data/mahanavi_ramayana_state.json POST_SLOT=ramayana python -m channels.calendar.ramayana_gate
"""
import datetime as dt
import os
import sys

from channels.engine import gate, state as state_mod
from mahanavi.content import ramayana_daily as rd


MOVE_TO_MORNING = dt.date(2026, 11, 10)


def main() -> int:
    today = dt.datetime.now(gate.IST).date()
    if os.environ.get("FORCE_POST") != "true" and rd.next_story(today, state_mod.load()["used_ids"]) is None:
        print("DECISION: skip, no Ramayana story is due")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"post=false\ndate={today.isoformat()}\n")
        return 0
    if today >= MOVE_TO_MORNING:   # owner request 2026-11-09: 9-10 AM from Tue 10 Nov (today's story still goes out at 3 PM)
        return gate.run("ramayana", dt.time(9, 0), 50, dt.time(9, 55))
    return gate.run("ramayana", dt.time(15, 0), 50, dt.time(15, 55))


if __name__ == "__main__":
    sys.exit(main())
