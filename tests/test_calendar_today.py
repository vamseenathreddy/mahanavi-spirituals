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


def test_december_2026_is_covered_and_dates_are_unique():
    for d in (dt.date(2026, 12, 9), dt.date(2026, 12, 16), dt.date(2026, 12, 20), dt.date(2026, 12, 23)):
        assert cal.observances(d), d
    assert cal.observances(dt.date(2026, 11, 21)) == ["tulasi_vivaham"]       # sunrise Ekadashi dropped (Prabodhini is 20 Nov)
    assert "purnima" not in cal.observances(dt.date(2026, 12, 24))          # Datta Jayanti is 23 Dec, Purnima ends at sunrise
    assert hi.observances(dt.date(2026, 12, 20)) == ["gita_jayanti"]
    for month in (11, 12):
        assert cal.FULL_MONTH[(2026, month)] and hi.FULL_MONTH[(2026, month)]
    cal.build_festivals(2026, 12)
    hi.build_festivals("mantra_sangam", 2026, 12)
    for d in (dt.date(2026, 12, 20), dt.date(2026, 12, 23), dt.date(2026, 11, 13)):
        cal.build_today(d, cal.observances(d))
