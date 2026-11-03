import datetime as dt

from channels import chanakya_plan as p
from mahanavi.content import chanakya_neeti as cn


def test_one_sutra_a_day_never_repeats_and_has_an_example():
    assert cn.days() == len(cn.SUTRAS) == len(cn.EXAMPLES) == 105
    te = [cn.sutra(d, "te") for d in range(cn.days())]
    assert len(set(te)) == cn.days()
    assert all(cn.example(d, "hi") and cn.example(d, "te") for d in range(cn.days()))


def test_plan_window():
    assert p.plan(dt.date(2026, 11, 2)) is None
    assert p.plan(dt.date(2026, 11, 3)) == 0
    assert p.plan(dt.date(2026, 11, 4)) is None
    assert p.plan(dt.date(2026, 11, 5)) == 1
    assert p.plan(p.SERIES_START + dt.timedelta(days=2 * (cn.days() - 1))) == cn.days() - 1
    assert p.plan(p.SERIES_START + dt.timedelta(days=2 * cn.days())) is None


def test_no_telugu_in_hindi_text_and_vice_versa():
    for pairs in (cn.SUTRAS, cn.EXAMPLES):
        for hi, te in pairs:
            assert not any("ఀ" <= ch <= "౿" for ch in hi)
            assert not any("ऀ" <= ch <= "ॿ" for ch in te)


def test_jitter_pause_is_off_in_tests_and_random_otherwise(monkeypatch):
    from mahanavi.publishers import jitter
    assert jitter.pause() == 0     # conftest sets POST_JITTER=off
    monkeypatch.delenv("POST_JITTER")
    slept = []
    monkeypatch.setattr(jitter.time, "sleep", slept.append)
    vals = {jitter.pause() for _ in range(30)}
    assert len(vals) > 5 and max(vals) <= 59 and len(slept) == 30
