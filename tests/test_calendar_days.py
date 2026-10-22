import datetime as dt

from channels.calendar import gate
from mahanavi.content import calendar_days as cal


def test_known_dates():
    assert cal.observances(dt.date(2026, 11, 5)) == ["ekadashi"]
    assert cal.observances(dt.date(2026, 11, 8)) == ["diwali"]       # curated day replaces the generic amavasya
    assert cal.observances(dt.date(2026, 11, 24)) == ["karthika_pournami"]
    assert cal.observances(dt.date(2026, 11, 17)) == []


def test_tomorrow_and_lists():
    day, keys = cal.next_special(dt.date(2026, 11, 4))
    assert day == dt.date(2026, 11, 5) and keys == ["ekadashi"]
    assert cal.next_special(dt.date(2026, 11, 17)) is None
    s = cal.build_tomorrow(day, keys)
    assert "ఏకాదశి" in s.title and len(s.title) <= 100 and s.slides[1].text.count("\n") == 2
    v = cal.build_vratas(2026, 11)
    assert all(len(sl.text.split("\n")) <= 5 for sl in v.slides if sl.kind == "points")
    assert cal.build_festivals(2026, 11).slides[0].text


def test_gate_eligibility():
    assert gate.eligible("festivals", dt.date(2026, 10, 28)) and not gate.eligible("festivals", dt.date(2026, 10, 29))
    assert gate.eligible("vratas", dt.date(2026, 11, 30)) and gate.eligible("vratas", dt.date(2026, 2, 28))
    assert gate.next_month(dt.date(2026, 12, 28)) == (2027, 1)
