import datetime as dt

from channels import verse_series as vs
from mahanavi.content import shiv_tandav_hi as st
from mahanavi.scripts import post_verse_series as pv


def test_plan_runs_15_days_from_10_nov():
    k = "shiv_tandav_hi"
    assert vs.plan(k, dt.date(2026, 11, 9)) is None
    assert [vs.plan(k, dt.date(2026, 11, 10 + i)) for i in range(15)] == list(range(15))
    assert vs.plan(k, dt.date(2026, 11, 25)) is None


def test_content_complete():
    assert st.count() == 15 and all(v.strip() and m.strip() for v, m in st.VERSES)


def test_metadata_fits_youtube_limits():
    for d in range(st.count()):
        title, desc, tags, title_en, desc_en = pv.metadata("shiv_tandav_hi", d)
        assert len(title) <= 100 and len(desc) < 5000 and "http" not in desc
        assert sum(len(t) + (2 if " " in t else 0) + 1 for t in tags) < 450


def test_trance_series_and_metadata():
    k = "shiv_tandav_trance"
    assert vs.plan(k, dt.date(2026, 11, 10)) == 0 and vs.plan(k, dt.date(2026, 11, 25)) is None
    t1 = pv.metadata(k, 0)[0]
    t2 = pv.metadata("shiv_tandav_hi", 0)[0]
    assert t1 != t2 and len(t1) <= 100


def test_english_meaning_for_every_verse():
    assert len(st.MEANING_EN) == st.count() and all(m.strip() for m in st.MEANING_EN)
    assert "Meaning in English" in pv.metadata("shiv_tandav_hi", 0)[1]


def test_vedas_series_ten_days_from_26_nov():
    for k in ("vedas_te", "vedas_hi"):
        assert vs.plan(k, dt.date(2026, 11, 25)) is None
        assert [vs.plan(k, dt.date(2026, 11, 26) + dt.timedelta(days=i)) for i in range(10)] == list(range(10))
        assert vs.plan(k, dt.date(2026, 12, 6)) is None
    assert vs.SERIES["vedas_te"].channel == "mahanavi" and vs.SERIES["vedas_hi"].channel == "mantra_sangam"


def test_vedas_content_complete_and_rotating():
    from mahanavi.content import vedas, vedas_hi, vedas_te

    assert vedas_te.count() == vedas_hi.count() == 10
    assert [m.veda for m in vedas.MANTRAS[:4]] == ["rig", "yajur", "sama", "atharva"]
    for m in vedas.MANTRAS:
        assert all(x.strip() for x in (m.sa, m.te_read, m.te_mean, m.hi_mean, m.en_mean, m.title_te, m.title_hi, m.title_en))
    assert len({m.sa for m in vedas.MANTRAS}) == 10      # no mantra twice


def test_vedas_metadata_no_numbers_no_links_fits_limits():
    import re

    for k in ("vedas_te", "vedas_hi"):
        for d in range(10):
            title, desc, tags, title_en, desc_en = pv.metadata(k, d)
            assert len(title) <= 100 and len(title_en) <= 100 and len(desc) < 5000 and "http" not in desc
            assert not re.search(r"\b\d+\s*/\s*\d+\b|\bpart \d+\b|\bverse \d+\b", (title + desc).lower())
            assert sum(len(t) + (2 if " " in t else 0) + 1 for t in tags) < 450
    assert pv.metadata("vedas_te", 0)[0] != pv.metadata("vedas_hi", 0)[0]
