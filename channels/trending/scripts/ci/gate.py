"""Gate for the trending channel: POST_SLOT (t1..t4) picks the slot; a day-seeded random minute inside its window."""
import datetime as dt
import os
import sys

from channels.engine import gate
from channels.trending import config as cfg

if __name__ == "__main__":
    slot = os.environ["POST_SLOT"]
    today = dt.datetime.now(gate.IST).date()
    if os.environ.get("FORCE_POST") != "true" and not cfg.AUTO_POSTING:
        print("DECISION: skip, automatic Pulse TDP posting is switched off (channels/trending/config.py AUTO_POSTING)")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("post=false\ndate=\n")
        sys.exit(0)
    if os.environ.get("FORCE_POST") != "true" and slot not in cfg.slots_for(today):
        print(f"DECISION: skip, {slot} is not one of today's slots ({sorted(cfg.slots_for(today))}; Fri-Sun 6 posts, Mon-Thu 3)")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("post=false\ndate=\n")
        sys.exit(0)
    hour = dict((s, h) for h, s in cfg.SLOTS)[slot]
    # latest = window start + 2 hours, so a late ping can still post but never into the next slot
    sys.exit(gate.run(f"trending_{slot}", dt.time(hour, 0), cfg.WINDOW_MINUTES, dt.time(min(hour + 2, 23), 59)))
