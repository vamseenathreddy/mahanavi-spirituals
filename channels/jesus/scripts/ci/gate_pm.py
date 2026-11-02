"""Gate for the Jesus Worship Waves SECOND Bible Quote Short of the day: day-seeded target minute inside
02:30-04:20 IST (a late backup run may still post until 05:00 IST). It shares the quote state file with
the 12 AM Quote and uses POST_SLOT=pm so it has its own daily marker. Run via:

  POST_SLOT=pm python -m channels.jesus.scripts.ci.gate_pm
"""
import datetime as dt
import sys

from channels.engine import gate

WINDOW_START = dt.time(2, 30)
WINDOW_MINUTES = 110
LATEST = dt.time(5, 0)

if __name__ == "__main__":
    sys.exit(gate.run("jesus_pm", WINDOW_START, WINDOW_MINUTES, LATEST))
