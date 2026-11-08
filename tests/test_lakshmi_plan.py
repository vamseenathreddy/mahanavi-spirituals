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


def test_telugu_name_moves_to_2pm_from_9_nov(monkeypatch):
    import datetime as dt
    seen = {}
    monkeypatch.setattr(p.gate_mod, "decide", lambda slot, now, st, ws, wm, latest, force=False: (seen.update(ws=ws, latest=latest) or (False, "x", "d")))
    monkeypatch.setattr(p.state_mod, "load", lambda: {})
    p.gate("name", dt.datetime(2026, 11, 8, 18, 30, tzinfo=p.IST))
    assert seen["ws"] == dt.time(18, 0)
    p.gate("name", dt.datetime(2026, 11, 9, 14, 30, tzinfo=p.IST))
    assert seen["ws"] == dt.time(14, 0) and seen["latest"] == dt.time(15, 0)
