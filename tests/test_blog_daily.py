import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("blog_daily", Path(__file__).resolve().parents[1] / "scripts" / "ci" / "blog_daily.py")
bd = importlib.util.module_from_spec(spec); sys.modules["blog_daily"] = bd; spec.loader.exec_module(bd)


def test_bank_valid_and_unique():
    posts = bd.load_posts()
    assert len(posts) >= 4
    assert len({p["id"] for p in posts}) == len(posts) and len({p["title"] for p in posts}) == len(posts)
    for p in posts:
        assert (bd.ROOT / "assets" / "blog" / p["hero"]).exists(), p["hero"]
        assert len(p["sections"]) >= 4 and p["faq"] and p["labels"]


def test_ad_in_middle_once():
    for p in bd.load_posts():
        h = bd.build_html(p, "ca-pub-1", "99")
        assert h.count("adsbygoogle") >= 2 and h.count('<ins class="adsbygoogle"') == 1
        assert 0.2 < h.index("<ins") / len(h) < 0.7, p["id"]
        assert "<ins" not in bd.build_html(p, "", "") and bd.AD_MARK in bd.build_html(p, "", "")


def test_duplicate_groups_by_video():
    spec2 = importlib.util.spec_from_file_location("blog_stats", Path(__file__).resolve().parents[1] / "scripts" / "ci" / "blog_stats.py")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ci"))
    bs = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(bs)
    ours = {"title": "a", "labels": ["Muhurta"], "published": "2026-11-12T12:22", "content": '<img src="https://i.ytimg.com/vi/ZiDfOf_LX2U/hqdefault.jpg">'}
    ifttt = {"title": "a | M", "labels": ["Holi"], "published": "2026-11-12T13:06", "content": '<iframe src="https://www.youtube.com/embed/ZiDfOf_LX2U"></iframe>'}
    other = {"title": "b", "labels": [], "published": "2026-11-12T10:00", "content": "https://www.youtube.com/watch?v=4Ok9gWSoO2k"}
    article = {"title": "c", "labels": ["Daily Article"], "published": "2026-11-12T09:00", "content": "youtube.com/embed/ZiDfOf_LX2U"}
    g = bs.duplicate_groups([ours, ifttt, other, article])
    assert len(g) == 1 and {p["title"] for p in g[0]} == {"a", "a | M"}
