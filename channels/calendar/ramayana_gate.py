"""Gate for the Mahanavi 10-day Ramayana story Shorts: one per day from 2026-11-06, at a day-seeded random minute in
15:00-15:50 IST (moved from 14:00 on 2026-11-08, owner request), latest 15:55. Skips when all ten are posted.

  STATE_FILE=data/mahanavi_ramayana_state.json POST_SLOT=ramayana python -m channels.calendar.ramayana_gate
"""
import datetime as dt
import os
import sys

from channels.engine import gate, state as state_mod
from mahanavi.content import ramayana_daily as rd


def main() -> int:
    today = dt.datetime.now(gate.IST).date()
    if os.environ.get("FORCE_POST") != "true" and rd.next_story(today, state_mod.load()["used_ids"]) is None:
        print("DECISION: skip, no Ramayana story is due")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"post=false\ndate={today.isoformat()}\n")
        return 0
    return gate.run("ramayana", dt.time(15, 0), 50, dt.time(15, 55))


if __name__ == "__main__":
    sys.exit(main())
