from mahanavi.content.branding import BRAND_TAGS, brand_tags


def test_brand_tags_stay_under_youtube_limit():
    tags = [f"telugu festival tag number {i} శుభ" for i in range(60)]
    out = brand_tags(tags)
    assert sum(len(t) + (2 if " " in t else 0) + 1 for t in out) <= 500
    assert all(b in out for b in BRAND_TAGS)


def test_brand_tags_cleans_duplicates_and_angle_brackets():
    out = brand_tags(["Aa", "aa", " ", "b<c>"])
    assert out.count("Aa") == 1 and "aa" not in out
    assert all("<" not in t and ">" not in t for t in out)
