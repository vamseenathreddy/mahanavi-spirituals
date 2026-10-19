"""Gate for the Friday video: only on Fridays (IST), at a day-seeded random minute in 19:00-19:40 (peak Friday-evening
viewing for Telugu audiences), never after 21:30."""
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

from channels.engine import gate

IST = ZoneInfo("Asia/Kolkata")

if __name__ == "__main__":
    forced = "--force" in sys.argv or os.environ.get("FORCE_POST") == "true"
    if dt.datetime.now(IST).weekday() != 4 and not forced:
        print("DECISION: skip, the weekly development video posts on Fridays only")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("post=false\ndate=\n")
        sys.exit(0)
    sys.exit(gate.run("weekly_dev", dt.time(19, 0), 40, dt.time(21, 30)))
