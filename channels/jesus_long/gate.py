"""Gate for the long Bible-verse videos: every day, a random minute in 17:30-18:10 IST (8:00 AM US
Eastern, when the US morning audience is starting its day), never after 19:30."""
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

from channels.engine import gate

IST = ZoneInfo("Asia/Kolkata")
DAYS = set(range(7))

if __name__ == "__main__":
    forced = "--force" in sys.argv or os.environ.get("FORCE_POST") == "true"
    if dt.datetime.now(IST).weekday() not in DAYS and not forced:
        print("DECISION: skip, the long Bible video posts every day")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("post=false\ndate=\n")
        sys.exit(0)
    sys.exit(gate.run("jesus_long", dt.time(17, 30), 40, dt.time(19, 30)))
