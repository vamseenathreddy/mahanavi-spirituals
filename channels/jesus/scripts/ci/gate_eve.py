"""Gate for the Jesus Worship Waves THIRD Bible Quote Short of the day: day-seeded target minute inside
17:00-18:50 IST (a late backup run may still post until 19:00 IST). It shares the quote state file with
the other two Quotes and uses POST_SLOT=eve so it has its own daily marker. Run via:

  POST_SLOT=eve python -m channels.jesus.scripts.ci.gate_eve
"""
import datetime as dt
import sys

from channels.engine import gate

WINDOW_START = dt.time(17, 0)
WINDOW_MINUTES = 110
LATEST = dt.time(19, 0)

if __name__ == "__main__":
    sys.exit(gate.run("jesus_eve", WINDOW_START, WINDOW_MINUTES, LATEST))
