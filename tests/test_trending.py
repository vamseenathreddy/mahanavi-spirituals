"""Trending news channel: sources, planning, metadata. No network."""
from datetime import datetime, timedelta, timezone

from channels.trending import config as cfg
from channels.trending import metadata, post
from channels.trending.sources import (Story, clean_title, fresh_enough, is_informative, matches_language,
                                       parse_rss, pick_story)

RSS = """<?xml version="1.0"?><rss><channel>
<item><title>భారత్ ఘన విజయం, కోహ్లీ సెంచరీ - Eenadu</title><link>https://n/1</link>
<pubDate>Fri, 16 Oct 2026 10:00:00 GMT</pubDate><source url="x">Eenadu</source></item>
<item><title>Eenadu</title><link>https://n/2</link><source url="x">Eenadu</source></item>
</channel></rss>"""


def test_parse_rss_strips_publisher_and_keeps_source():
    items = parse_rss(RSS)
    assert items[0].headline == "భారత్ ఘన విజయం, కోహ్లీ సెంచరీ"
    assert items[0].publisher == "Eenadu" and items[0].link == "https://n/1"
    assert items[0].published == datetime(2026, 10, 16, 10, 0, tzinfo=timezone.utc)
    assert [is_informative(s) for s in items] == [True, False]  # a bare publisher name is not a headline


def test_clean_title_removes_hashtags_and_emoji():
    assert clean_title("Big win 🔥 #Shorts #IPL now") == "Big win now"


def test_language_matching():
    assert matches_language("భారత్ ఘన విజయం", "te") and not matches_language("India wins", "te")
    assert matches_language("India wins big", "en") and not matches_language("भारत जीता", "en")
    assert matches_language("வெற்றி பெற்றது", "ta") and matches_language("ಭಾರತ ಗೆದ್ದಿತು", "kn")
    assert matches_language("ഇന്ത്യ ജയിച്ചു", "ml") and matches_language("भारत जीता", "hi")


def test_plan_is_telugu_only_and_cycles_the_day_pattern():
    seen = [cfg.plan(i) for i in range(12)]
    assert {l for l, _ in seen} == {"te"} and cfg.LANGS == ["te"] and {n for _, n in seen} == set(cfg.DAY_PATTERN)


def test_labels_cover_every_language_and_niche():
    for lang in cfg.LANGS:
        assert len(cfg.NICHE_NATIVE[lang]) == len(cfg.NICHES)
        assert lang in cfg.CTA and lang in cfg.INTRO and lang in cfg.LANG_TAG
        for n in cfg.NICHES:
            t, d = cfg.playlist_for(lang, n)
            assert len(t) <= 150 and len(d) <= 5000 and "<" not in t + d


def test_pick_story_skips_used_and_stale_and_prefers_short():  # equal coverage and rank order, short first
    now = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)
    long_ = Story("A very long headline " * 6, "P", "l1", now - timedelta(hours=1))
    stale = Story("Stale but fine headline here", "P", "l2", now - timedelta(hours=40))
    used = Story("Already posted headline right here", "P", "l3", now - timedelta(hours=1))
    short = Story("Fresh short headline for today", "P", "l4", now - timedelta(hours=2))
    long_.rank, stale.rank, used.rank, short.rank = 1, 2, 3, 4
    got = pick_story("development", "en", {used.key}, None, now, fetch_bank=lambda n: [], fetch_news=lambda n, l: [long_, stale, used, short])
    assert got is short
    assert pick_story("development", "en", {short.key, used.key, long_.key}, None, now,
                      fetch_bank=lambda n: [], fetch_news=lambda n, l: [stale, used, short, long_]) is None
    assert not fresh_enough(stale, now, 30) and fresh_enough(stale, now, 48)


def test_only_top_10_and_widest_coverage_first():
    now = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)
    mk = lambda h, rank, rel=(): Story(h, "P", f"l{rank}", now - timedelta(hours=1), rank=rank, related=rel)  # noqa: E731
    low = mk("Rank twelve headline that is out of the top ten", 12, (("a", "x"),) * 5)
    plain = mk("Rank one headline with no other outlets", 1)
    wide = mk("Rank four headline carried by several outlets", 4, (("a", "x"), ("b", "y")))
    got = pick_story("development", "en", set(), None, now, fetch_bank=lambda n: [], fetch_news=lambda n, l: [low, plain, wide])
    assert got is wide  # outranks rank 1 on coverage; rank 12 is outside the top 10
    assert pick_story("development", "en", {plain.key, wide.key}, None, now, fetch_bank=lambda n: [], fetch_news=lambda n, l: [low, plain, wide]) is None


def test_card_has_positive_angle_and_description_has_disclosure():
    s = Story("అమరావతిలో కొత్త ఐటీ పార్క్ ప్రారంభం", "Eenadu", "l", None, rank=3)
    row = metadata.row_for(s, "te", "development")
    assert "TRENDING" not in "".join(str(v) for v in row.values()) and any(row["text_related"].startswith(a) for a in metadata.ANGLES["development"] + metadata.fan_lines.ANGLES_MORE["development"])
    d = metadata.description(s, "te", "development")
    assert "pro-TDP" in d and "Source:" not in d and "Eenadu" not in d and "#TDP" in d
    assert "| TDP |" in metadata.title(s, "te", "development")


def test_twelve_two_hourly_slots_from_midnight():
    assert [h for h, _ in cfg.SLOTS] == list(range(0, 24, 2)) and len({s for _, s in cfg.SLOTS}) == 12


def test_failing_source_does_not_stop_the_slot():
    now = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)
    ok = Story("Trending video title worth showing", "Chan", "yt1", now - timedelta(hours=1), "bank")

    def boom(*_):
        raise RuntimeError("down")
    assert pick_story("innovations", "en", set(), object(), now, fetch_news=boom, fetch_bank=lambda n: [ok]) is ok


def test_current_news_niches_never_post_old_facts():
    from channels.trending import config as cfg
    assert set(cfg.DAY_PATTERN) <= set(cfg.NEWS_NICHES)
    old = Story("Old achievement fact headline here", "P", "l", None, "bank")
    assert pick_story("chandrababu", "te", set(), None, fetch_news=lambda *_: [], fetch_bank=lambda n: [old]) is None


def test_choose_falls_through_to_other_niches():
    story = Story("Fallback story headline here", "P", "l", None)
    calls = []

    def fetch(n, lang, used, yt):
        calls.append(n)
        return story if n == "tdp" else None
    niche, got = post.choose("te", "development", set(), None, fetch=fetch)
    assert got is story and niche == "tdp" and calls[0] == "development"


def test_metadata_names_source_and_mixes_english():
    s = Story("ఆసియా కప్ ఫైనల్‌లో భారత్ ఘన విజయం", "Eenadu", "https://n/1", None)
    m = metadata.bundle(s, "te", "development")
    assert len(m["title"]) <= 100 and "Pulse TDP Fans" in m["title"]
    assert "Source:" not in m["description"] and "Eenadu" not in m["description"] and "https://n/1" not in m["description"]
    assert "https://n/1" not in m["comment"] and m["language"] == "te"
    assert len(metadata.hashtags("te", "development")) <= 15 and sum(len(t) + 1 for t in m["tags"]) <= 500


def test_long_title_is_trimmed_to_100():
    s = Story("word " * 60, "P", "l", None)
    assert len(metadata.title(s, "te", "chandrababu")) <= 100


def test_related_headlines_come_from_the_story_cluster():
    desc = ('&lt;ol&gt;&lt;li&gt;&lt;a href="x"&gt;ఇది రెండవ పత్రిక శీర్షిక ఇక్కడ&lt;/a&gt;&amp;nbsp;&amp;nbsp;'
            '&lt;font color="#6f6f6f"&gt;Sakshi&lt;/font&gt;&lt;/li&gt;&lt;/ol&gt;')
    rss = (f'<rss><channel><item><title>ప్రధాన శీర్షిక ఇక్కడ ఉంది - Eenadu</title><link>https://n/1</link>'
           f'<description>{desc}</description><source url="x">Eenadu</source></item></channel></rss>')
    got = parse_rss(rss)[0].related
    assert got == (("ఇది రెండవ పత్రిక శీర్షిక ఇక్కడ", "Sakshi"),)


def test_meta_description_and_trim():
    from channels.trending.sources import _meta_description, trim
    page = '<html><head><meta property="og:description" content="Gill &amp; co named for the tour."></head></html>'
    assert _meta_description(page) == "Gill & co named for the tour."
    assert _meta_description('<meta name="description" content="Plain one">') == "Plain one"
    assert len(trim("word " * 100, 50)) <= 51 and trim("short", 50) == "short"


def test_enrich_keeps_only_same_language_related_and_row_has_source_last():
    from channels.trending.sources import enrich
    s = Story("భారత్ ఘన విజయం, కోహ్లీ సెంచరీ", "Eenadu", "l", None, "news",
              related=(("భారత్ గెలుపు, అభిమానుల సంబరాలు", "Sakshi"), ("India win the final in style", "Hindu"),
                       ("మరో తెలుగు శీర్షిక ఇక్కడ ఉంది", "A"), ("ఇంకొక తెలుగు శీర్షిక ఇక్కడ ఉంది", "B")))
    import channels.trending.sources as src
    src.article_summary = lambda *a, **k: "ఇది ప్రచురణకర్త సారాంశం"
    enrich(s, "te")
    assert len(s.related) == 3 and all("India" not in h for h, _ in s.related)
    row = metadata.row_for(s, "te", "development")
    assert row["text_summary"] and "• " in row["_bullets"] and row["text_secondary"] == "Source: Eenadu"
    assert metadata.note("development", s.key) in row["text_related"]   # the 2 to 3 line fan note sits under the angle line
    assert "Also in the news:" in metadata.description(s, "te", "development")


def test_news_stories_drops_other_language_headlines(monkeypatch):
    import channels.trending.sources as src
    xml = ("<rss><channel>"
           "<item><title>ಭಾರತ ತಂಡ ನ್ಯೂಜಿಲೆಂಡ್ ಪ್ರವಾಸಕ್ಕೆ ಆಯ್ಕೆ ಘೋಷಣೆ - ಪ್ರಜಾವಾಣಿ</title><link>a</link><source>ಪ್ರಜಾವಾಣಿ</source></item>"
           "<item><title>टेस्ला ने उड़ने वाली कार दिखाई, हवा में पलटी - दैनिक भास्कर</title><link>b</link><source>दैनिक भास्कर</source></item>"
           "</channel></rss>")
    monkeypatch.setattr(src, "_get", lambda *a, **k: xml)
    got = src.news_stories("health", "kn")
    assert [s.link for s in got] == ["a"]


def test_playlist_add_waits_for_a_new_playlist_instead_of_failing(monkeypatch):
    import channels.trending.playlists as pl
    from googleapiclient.errors import HttpError

    class Resp:
        status = 404
        reason = "Not Found"

    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise HttpError(Resp(), b"playlistNotFound")
        return "ok"

    monkeypatch.setattr(pl.time, "sleep", lambda s: None)
    assert pl._settled(flaky) == "ok" and calls["n"] == 3
    always = lambda: (_ for _ in ()).throw(HttpError(Resp(), b"x"))  # noqa: E731
    assert pl._settled(always, empty={"items": []}) == {"items": []}


def test_summary_accepts_decoder_success_key(monkeypatch):
    import sys
    import types
    import channels.trending.sources as src
    mod = types.ModuleType("googlenewsdecoder")
    mod.gnewsdecoder = lambda link, interval=1: {"success": True, "decoded_url": "https://example.com/a"}
    monkeypatch.setitem(sys.modules, "googlenewsdecoder", mod)
    monkeypatch.setattr(src, "_get", lambda *a, **k: '<meta property="og:description" content="ఇది ప్రచురణకర్త సారాంశం మరియు మరిన్ని వివరాలు ఇక్కడ">')
    assert src.article_summary("l", "te", "వేరే శీర్షిక") != ""


def test_political_filter_is_positive_and_excludes_opposition_and_sakshi(monkeypatch):
    import channels.trending.sources as src
    assert src.is_positive("అమరావతిలో కొత్త పెట్టుబడులు ప్రారంభం") and not src.is_positive("జగన్ పై విమర్శ అభివృద్ధి")
    assert not src.is_positive("రోడ్డు ప్రమాదంలో ఇద్దరు మృతి")
    xml = ("<rss><channel>"
           "<item><title>చంద్రబాబు సమక్షంలో కొత్త పరిశ్రమ ఒప్పందం - సాక్షి</title><link>a</link><source>సాక్షి</source></item>"
           "<item><title>చంద్రబాబు సమక్షంలో కొత్త పరిశ్రమ ఒప్పందం ఖరారు - ఆంధ్రజ్యోతి</title><link>b</link><source>ఆంధ్రజ్యోతి</source></item>"
           "<item><title>చంద్రబాబు కొత్త పెట్టుబడులు ప్రారంభం - ఇతర</title><link>c</link><source>ఇతర</source></item>"
           "</channel></rss>")
    monkeypatch.setattr(src, "_get", lambda *a, **k: xml)
    got = src.political_stories("chandrababu")
    assert [x.link for x in got] == ["b", "c"] and got[0].rank == 1


def test_bank_facts_are_complete_and_distinct():
    from channels.trending.bank import bank_stories
    b = bank_stories()
    assert len(b) >= 12 and len({s.key for s in b}) == len(b)
    assert all(s.summary and s.link.startswith("https://") and matches_language(s.headline, "te") for s in b)


def test_seo_covers_regions_and_stays_within_limits():
    from channels.trending import regions
    s = Story("గుంటూరులో కొత్త పరిశ్రమ ఒప్పందం, అభివృద్ధికి ఊతం", "Eenadu", "https://n/1", None, summary="కర్నూలు, విశాఖపట్నం ప్రస్తావన")
    ds = regions.for_post(s.key, s.headline + s.summary, 8)
    assert [d[1] for d in ds][:3] == ["Guntur", "Kurnool", "Visakhapatnam"] or {"Guntur", "Kurnool"} <= {d[1] for d in ds}
    m = metadata.bundle(s, "te", "development")
    assert len(m["description"]) < 5000 and len(m["title"]) <= 100
    assert sum(len(t) + (2 if " " in t else 0) + 1 for t in m["tags"]) <= 500
    assert "#Guntur" in metadata.hashtags("te", "development", s) and len(metadata.hashtags("te", "development", s)) <= 15
    assert "175" in m["description"]
    # a day of different stories reaches all three regions
    seen = {d[2] for i in range(12) for d in regions.for_post(f"k{i}", "", 6)}
    assert len(seen) == 3


def test_day_pattern_mix_and_new_banks():
    from channels.trending.bank import bank_stories
    day = [cfg.plan(i)[1] for i in range(12)]
    assert len(cfg.DAY_PATTERN) == 12 and len(cfg.ACTIVE_SLOTS) == 12 and cfg.ACTIVE_SLOTS <= {s for _, s in cfg.SLOTS}
    assert "innovations" not in day and day.count("counter") == 2 and day.count("ysrcp") == 5 and "janasena" not in day and "janasena" not in cfg.NICHES
    assert [cfg.plan(i)[1] for i in range(12, 24)] == day and set(day) <= set(cfg.NICHES)
    for n in ("join", "voice"):
        b = bank_stories(n)
        assert b and len({s.key for s in b}) == len(b) and all(matches_language(s.headline, "te") for s in b)
    assert len(bank_stories("join")) == 78
    for n in cfg.NICHES:
        s = bank_stories(n)[0]
        m = metadata.bundle(s, "te", n)
        assert len(m["title"]) <= 100 and len(m["description"]) < 5000


def test_local_niche_posts_once_a_month_on_the_first():
    import datetime as d
    assert all(cfg.plan(i, d.date(2026, 11, 5))[1] != "local" for i in range(12))
    assert cfg.plan(2, d.date(2026, 11, 1))[1] == "local"
    assert cfg.plan(2, d.date(2026, 11, 1), {"local_month": "2026-11"})[1] != "local"
    assert "local" not in cfg.DAY_PATTERN and "local" not in cfg.NEWS_NICHES


def test_ntr_history_posts_every_other_day_and_are_complete(monkeypatch):
    monkeypatch.setattr(cfg, "NTR_ENABLED", True)
    import datetime as dt
    from channels.trending import ntr_bank
    d1, d2 = dt.date(2026, 10, 21), dt.date(2026, 10, 22)
    assert cfg.plan(3, d1)[1] != cfg.plan(3, d2)[1] and "ntr" in (cfg.plan(3, d1)[1], cfg.plan(3, d2)[1])
    assert cfg.plan(0, d1)[1] == cfg.DAY_PATTERN[0] and cfg.plan(3)[1] == cfg.DAY_PATTERN[3]
    stories = ntr_bank.ntr_stories()
    assert len(stories) >= 20 and len({s.key for s in stories}) == len(stories)
    for s in stories:
        meta = metadata.bundle(s, "te", "ntr")
        assert "NTR" in meta["title"] and len(meta["title"]) <= 100 and "#NTR" in meta["description"]
        assert s.summary and len(s.related) == 2 and ntr_bank.english_line(s.headline)


def test_every_news_niche_has_a_fan_note():
    for n in ("amaravati", "lokesh", "chandrababu", "counter", "tdp", "nda", "development", "local"):
        assert all(len(x) > 40 for x in metadata.NOTES[n]) and metadata.note(n, "abcdef0123456789")


def test_same_story_from_another_outlet_is_skipped():
    from datetime import datetime, timezone

    from channels.trending import dedupe
    from channels.trending.sources import Story, pick_story

    now = datetime.now(timezone.utc)
    first = Story("అమరావతిలో కొత్త సచివాలయ భవనం పనులు వేగంగా సాగుతున్నాయి", "A", "https://a.com/x", now)
    reworded = Story("అమరావతి సచివాలయ భవనం పనులు వేగంగా సాగుతున్నాయి", "B", "https://b.com/y", now)
    other = Story("లోకేశ్ ఐటీ ఉద్యోగాల కోసం కొత్త పథకం ప్రకటించారు", "C", "https://c.com/z", now)
    recent = [dedupe.entry(first.headline, first.link)]
    got = pick_story("development", "te", set(), None, now, fetch_bank=lambda n: [], fetch_news=lambda n, l: [reworded, other], recent=recent)
    assert got is other
    assert dedupe.is_duplicate("x", "https://www.a.com/x/", recent)  # same link, trailing slash and www ignored


def test_ntr_bank_never_repeats_a_title_or_text_and_never_ends():
    from channels.trending import ntr_bank

    posts = ntr_bank.ntr_stories()
    assert len({p.headline for p in posts}) == len(posts) == len(ntr_bank.ITEMS) * len(ntr_bank.OPENERS)
    assert len({p.summary for p in posts}) > len(posts) * 0.9


def test_choose_falls_back_to_ntr_history_when_news_is_quiet(monkeypatch):
    monkeypatch.setattr(cfg, "NTR_ENABLED", True)
    from channels.trending import post

    calls = []

    def fetch(n, lang, used, yt, **kw):
        calls.append(n)
        return "history" if n == "ntr" else None

    niche, got = post.choose("te", "lokesh", set(), None, fetch=fetch)
    assert (niche, got) == ("ntr", "history")


def test_ysrcp_niche_keeps_reported_exposures_and_drops_violence_family_and_film(monkeypatch):
    from channels.trending import sources

    heads = ["వైసీపీ హయాంలో మద్యం కుంభకోణం: సిట్ విచారణలో కీలక వివరాలు బయటపడ్డాయి - ఈనాడు",
             "జగన్ హయాంలో నిధుల దుర్వినియోగం బయటపడింది: కాగ్ నివేదిక వెల్లడి - ఆంధ్రజ్యోతి",
             "వైసీపీ నేత హత్య కేసులో కొత్త మలుపు - ఈనాడు",
             "జగన్ కుటుంబ వివాదంపై కొత్త కేసు - ఈనాడు",
             "జగన్ కూటమి ప్రభుత్వాన్ని తీవ్రంగా విమర్శించారు కేసు వివరాలు - ఈనాడు",
             "అమరావతిలో కొత్త భవనం ప్రారంభం - ఈనాడు"]
    items = "".join(f"<item><title>{h}</title><link>https://x.test/{i}</link><pubDate>Wed, 21 Oct 2026 04:00:00 GMT</pubDate>"
                    f"<source url='https://x.test'>{h.rsplit(' - ', 1)[1]}</source></item>" for i, h in enumerate(heads))
    monkeypatch.setattr(sources, "_get", lambda url, timeout=20: f"<rss><channel>{items}</channel></rss>")
    got = [s.headline for s in sources.political_stories("ysrcp", queries=["x"])]
    assert len(got) == 2 and all("హత్య" not in g and "కుటుంబ" not in g and "విమర్శ" not in g for g in got)
    from channels.trending import config as cfg, metadata
    assert cfg.niche_label("te", "ysrcp") and metadata.angle("ysrcp", "abcdef1234")


def test_fan_lines_rotate_and_do_not_repeat_until_the_pool_is_used():
    from channels.trending import metadata

    try:
        for niche in ("amaravati", "lokesh", "ysrcp", "development"):
            seen_a, seen_n = [], []
            for v in range(10):
                metadata.VARIANT = v
                seen_a.append(metadata.angle(niche, "abcdef123456"))
                seen_n.append(metadata.note(niche, "abcdef123456"))
            assert len(set(seen_a)) == 10 and len(set(seen_n)) >= 9
            pairs = {(a, n) for a, n in zip(seen_a, seen_n)}
            assert len(pairs) == 10
    finally:
        metadata.VARIANT = None


def test_has_substance_gate():
    from channels.trending.sources import Story, has_substance
    bare = Story("అమరావతి సంగమం ప్రత్యేకతలివే!", "Oneindia", "x")
    assert not has_substance(bare)                      # no summary: a promise with nothing behind it
    thin = Story("అమరావతి సంగమం ప్రత్యేకతలివే!", "Oneindia", "x", summary="రూ.597 కోట్లతో సంగమం నిర్మాణం జరుగుతోంది ఇది ఒక వార్త మాత్రమే.")
    assert not has_substance(thin)                      # teaser headline needs a fuller summary
    full = Story("అమరావతి సంగమం ప్రత్యేకతలివే!", "Oneindia", "x", summary="రూ.597 కోట్లతో నిర్మించే సంగమంలో వంతెన, పార్కులు, వాటర్ ఫ్రంట్, పర్యాటక కేంద్రాలు ఉంటాయి. పనులు వచ్చే ఏడాది ప్రారంభమవుతాయి.")
    assert has_substance(full)
    assert has_substance(Story("చంద్రబాబు సమీక్ష", "Eenadu", "x", summary="ముఖ్యమంత్రి చంద్రబాబు అమరావతి పనులపై సమీక్ష నిర్వహించి అధికారులకు ఆదేశాలు ఇచ్చారు."))


def test_ntr_is_once_a_week():
    import datetime as dt
    assert cfg.NTR_ENABLED is False
    ntr_days = [d for d in (dt.date(2026, 10, 19) + dt.timedelta(days=i) for i in range(14))
                for seq in range(6) if cfg.plan(seq, d)[1] == "ntr"]
    assert len(ntr_days) == 2 and all(d.weekday() == 6 for d in ntr_days)
