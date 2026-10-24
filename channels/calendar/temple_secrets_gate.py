"""Gate for the weekly Mahanavi "Temple Secrets" Short: Fridays only, a day-seeded random minute in 17:00-18:50 IST.

  STATE_FILE=data/mahanavi_temple_secrets_state.json POST_SLOT=temple_secrets python -m channels.calendar.temple_secrets_gate
"""
import datetime as dt
import os
import sys

from channels.engine import gate

WEEKDAY = 4   # Friday evening


def main() -> int:
    today = dt.datetime.now(gate.IST).date()
    if os.environ.get("FORCE_POST") != "true" and today.weekday() != WEEKDAY:
        print("DECISION: skip, Temple Secrets posts on Fridays only")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"post=false\ndate={today.isoformat()}\n")
        return 0
    return gate.run("mahanavi_temple_secrets", dt.time(17, 0), 110, dt.time(19, 0))


if __name__ == "__main__":
    sys.exit(main())
