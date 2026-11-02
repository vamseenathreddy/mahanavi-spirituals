import datetime as dt

from channels import lakshmi108_plan as p


def test_name_number_is_stateless_and_in_order():
    assert p.plan("name", dt.date(2026, 11, 5)) is None
    assert p.plan("name", dt.date(2026, 11, 6)) == 1
    assert p.plan("name", dt.date(2027, 2, 21)) == 108
    assert p.plan("name", dt.date(2027, 2, 22)) is None


def test_recap_is_friday_only_and_covers_previous_seven():
    assert p.plan("recap", dt.date(2026, 11, 6)) is None
    assert p.plan("recap", dt.date(2026, 11, 13)) == 1
    assert p.plan("recap", dt.date(2026, 11, 20)) == 8
    assert p.plan("recap", dt.date(2027, 2, 26)) == 106
    assert p.plan("recap", dt.date(2026, 11, 14)) is None


def test_posting_time_varies_day_to_day():
    minutes = {p.gate_mod.target_time("lakshmi108_name", dt.date(2026, 11, d), *p.WINDOWS["name"][:2]) .minute for d in range(6, 20)}
    secs = {p.jitter_seconds("name", dt.date(2026, 11, d)) for d in range(6, 20)}
    assert len(minutes) > 3 and len(secs) > 3
