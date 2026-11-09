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
