"""Gate for the Mahanavi calendar Shorts (three kinds, one workflow each). Posts only when there is something to post:

  tips      : every day 20:30-21:10 IST, one pooja rule (content/calendar_days.TIPS)
  tomorrow  : daily 19:30-20:10 IST, only when tomorrow has a festival / vrata
  festivals : the 28th of the month (monthly festival list for NEXT month), 19:00-19:40 IST
  vratas    : the 30th (or last day of a shorter month), Ekadashi / Pradosham / Sankashti list for NEXT month, 19:00-19:40 IST

  CAL_KIND=tomorrow|festivals|vratas POST_SLOT=cal_<kind> STATE_FILE=data/beej_state.json python -m channels.calendar.gate
"""
import calendar
import datetime as dt
import os
import sys

from channels.engine import gate
from mahanavi.content import calendar_days

IST = gate.IST
WINDOWS = {"tips": (dt.time(20, 30), 90, dt.time(22, 30)),
           "tomorrow": (dt.time(19, 30), 110, dt.time(22, 0)),
           "festivals": (dt.time(19, 0), 110, dt.time(22, 0)),
           "vratas": (dt.time(19, 0), 110, dt.time(22, 0))}


def next_month(d: dt.date) -> tuple[int, int]:
    return (d.year + (d.month == 12), d.month % 12 + 1)


def eligible(kind: str, today: dt.date, channel: str = "mahanavi") -> bool:
    if kind == "tips":
        return channel == "mahanavi"
    if kind == "tomorrow":
        if channel != "mahanavi":
            from mahanavi.content import calendar_days_hi
            return calendar_days_hi.next_special(today) is not None
        return calendar_days.next_special(today) is not None
    last = calendar.monthrange(today.year, today.month)[1]
    return today.day == (min(28, last) if kind == "festivals" else min(30, last))


def main() -> int:
    kind = os.environ["CAL_KIND"]
    channel = os.environ.get("CAL_CHANNEL", "mahanavi")
    today = dt.datetime.now(IST).date()
    if os.environ.get("FORCE_POST") != "true" and not eligible(kind, today, channel):
        print(f"DECISION: skip, nothing to post for '{kind}' today")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"post=false\ndate={today.isoformat()}\n")
        return 0
    start, minutes, latest = WINDOWS[kind]
    return gate.run(f"cal_{kind}", start, minutes, latest)


if __name__ == "__main__":
    sys.exit(main())
