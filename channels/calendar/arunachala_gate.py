"""Gate for the Ramana Maharshi TV "upcoming at Arunachala" Short: posts only when an event is exactly 20 days away
(a missed day is caught up for 3 days), at a day-seeded random minute in 20:00-21:50 IST, latest 22:00.

  STATE_FILE=data/ramana_arunachala_state.json POST_SLOT=ramana_arunachala python -m channels.calendar.arunachala_gate
"""
import datetime as dt
import os
import sys

from channels.engine import gate, state as state_mod
from mahanavi.content import arunachala_events as ev


def main() -> int:
    today = dt.datetime.now(gate.IST).date()
    if os.environ.get("FORCE_POST") != "true" and ev.due(today, state_mod.load()["used_ids"]) is None:
        print("DECISION: skip, no Arunachala event is 20 days away")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"post=false\ndate={today.isoformat()}\n")
        return 0
    return gate.run("ramana_arunachala", dt.time(20, 0), 110, dt.time(22, 0))


if __name__ == "__main__":
    sys.exit(main())
