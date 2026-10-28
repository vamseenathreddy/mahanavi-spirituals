import datetime as dt

from channels.calendar import gate
from mahanavi.content import calendar_days as cal
from mahanavi.content import calendar_days_hi as hi


def test_today_post_only_on_special_days():
    assert gate.eligible("today", dt.date(2026, 10, 29), "mahanavi")
    assert gate.eligible("today", dt.date(2026, 10, 29), "mantra_sangam")
    assert not gate.eligible("today", dt.date(2026, 10, 30), "mahanavi")


def test_today_builders_use_today_wording():
    day = dt.date(2026, 10, 29)
    te = cal.build_today(day, cal.observances(day))
    assert te.slug == "cal_today_2026-10-29" and te.title.startswith("ఈరోజు")
    h = hi.build_today("mantra_sangam", day, hi.observances(day))
    assert h.title.startswith("आज") and "कल" not in h.slides[0].label
