"""Gate for the Telugu reflection videos: Wednesday and Sunday, a random minute in 19:00-19:40 IST (Telugu evening
viewing time), never after 20:30."""
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

from channels.engine import gate

IST = ZoneInfo("Asia/Kolkata")
DAYS = {2, 6}   # Wednesday, Sunday

if __name__ == "__main__":
    forced = "--force" in sys.argv or os.environ.get("FORCE_POST") == "true"
    if dt.datetime.now(IST).weekday() not in DAYS and not forced:
        print("DECISION: skip, the reflection video posts on Wednesday and Sunday")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("post=false\ndate=\n")
        sys.exit(0)
    sys.exit(gate.run("jesus_reflect", dt.time(19, 0), 40, dt.time(20, 30)))
