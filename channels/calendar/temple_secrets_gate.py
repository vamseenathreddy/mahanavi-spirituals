"""Gate for the weekly Mahanavi "Temple Secrets" Short: Saturdays only, a day-seeded random minute in 22:00-23:50 IST.

  STATE_FILE=data/mahanavi_temple_secrets_state.json POST_SLOT=temple_secrets python -m channels.calendar.temple_secrets_gate
"""
import datetime as dt
import os
import sys

from channels.engine import gate

WEEKDAY = 5   # Saturday (Venkateswara's day)


def main() -> int:
    today = dt.datetime.now(gate.IST).date()
    if os.environ.get("FORCE_POST") != "true" and today.weekday() != WEEKDAY:
        print("DECISION: skip, Temple Secrets posts on Saturdays only")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"post=false\ndate={today.isoformat()}\n")
        return 0
    return gate.run("mahanavi_temple_secrets", dt.time(22, 0), 110, dt.time(23, 59))


if __name__ == "__main__":
    sys.exit(main())
