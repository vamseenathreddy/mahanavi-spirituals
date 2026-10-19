import datetime as dt
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("daily_digest", Path(__file__).resolve().parents[1] / "scripts/ci/daily_digest.py")
dd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dd)


def _day(i, v):
    return {"day": f"2026-10-{10 + i:02d}", "views": v, "minutes": v // 2, "likes": v // 20, "comments": 1, "shares": 2, "gained": 3, "lost": 1}


def test_helpers():
    assert dd.fmt_num(19138) == "19.1K" and dd.fmt_num(773) == "773"
    assert dd.pct_change(150, 100) == "▲50%" and dd.pct_change(50, 100) == "▼50%" and dd.pct_change(5, 0) == "new"
    assert len(dd.sparkline([1, 5, 3])) == 3 and dd.sparkline([0, 0]) == "▁▁"


def test_channel_message_and_summary():
    d = {"name": "X", "subs": 1234, "total_views": 99999, "videos": 80, "daily": [_day(i, 100 + 50 * i) for i in range(7)],
         "prev": {"views": 400, "minutes": 100, "likes": 20, "comments": 3, "shares": 1, "gained": 5, "lost": 1},
         "top": [{"title": "Top video", "views": 300, "likes": 12, "avg_pct": 140.0, "gained": 4}], "weak": None,
         "sources": [("Shorts feed", 800), ("YouTube search", 100)], "countries": [("IN", 900)], "uploads_yesterday": 3}
    m = dd.build_channel_message("Mahanavi", d, dt.date(2026, 10, 19), 7)
    assert "Subscribers: 1,234" in m and "Top video" in m and "Shorts feed" in m and "uploaded yesterday" in m
    assert "—" not in m
    s = dd.build_summary([("Mahanavi", {"views": 1050, "prev_views": 400, "net": 14, "subs": 1234, "likes": 50}, ""), ("Y", None, "token not available")],
                         dt.date(2026, 10, 19), 7)
    assert "Mahanavi" in s and "token not available" in s and "All channels" in s


def test_trending_text_ends_cleanly():
    from channels.trending.sources import complete
    assert complete("ఒకటి ఇది? రెండు ఇదే! మూడు సగం...", 100, soft=False) == "ఒకటి ఇది? రెండు ఇదే!"
    assert complete("headline with no stop and a dangling tail...", 100, soft=False) == ""
    assert not complete("నాడు నీతులా?: వైఎస్...", 100).endswith(("…", "..."))
