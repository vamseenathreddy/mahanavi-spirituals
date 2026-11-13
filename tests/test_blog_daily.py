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
        assert "<ins" not in bd.build_html(p, "", "")
