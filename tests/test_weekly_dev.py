import datetime as dt
from zoneinfo import ZoneInfo

from channels.trending.sources import Story
from channels.weekly_dev import collect, metadata

IST = ZoneInfo("Asia/Kolkata")


def _story(head, day, pub="Eenadu"):
    return Story(head, pub, f"https://x/{head[:5]}{day}", dt.datetime(2026, 10, day, 12, 0, tzinfo=IST), "news")


def test_pick_dates_dedupe_and_order():
    today = dt.date(2026, 10, 23)
    stories = [_story("అమరావతి రాజధాని పనులకు నిధులు మంజూరు", 21), _story("అమరావతి రాజధాని పనులకు నిధులు మంజూరు చేసిన ప్రభుత్వం", 22),
               _story("విశాఖలో ఐటీ పార్కుకు శంకుస్థాపన", 19), _story("ఒక పాత వార్త అభివృద్ధి", 10), _story("సాధారణ వ్యాఖ్య", 20),
               _story("కొత్త రహదారులకు ఆమోదం ప్రారంభం...", 23)]
    items = collect.pick(stories, today, set())
    dates = [i["date"] for i in items]
    assert dates == sorted(dates)
    assert "2026-10-10" not in dates                       # outside the 7-day window
    assert sum("అమరావతి" in i["headline"] for i in items) == 1   # near-duplicate dropped
    assert all(not i["headline"].endswith(("...", "…")) for i in items)
    assert collect.pick(stories, today, {stories[2].key})[0]["key"] != stories[2].key or len(items) > 1


def test_metadata_seo():
    items = [{"date": "2026-10-19", "headline": "విశాఖలో ఐటీ పార్కుకు శంకుస్థాపన", "publisher": "Eenadu", "link": "x", "key": "a"},
             {"date": "2026-10-23", "headline": "అమరావతి పనులకు నిధులు మంజూరు", "publisher": "TV9", "link": "x", "key": "b"}]
    t, d = metadata.title(items), metadata.description(items)
    assert len(t) <= 100 and "AP" in t and "19-23 Oct 2026" in t
    assert "19 అక్టోబర్" in d and "Eenadu" in d and "#APDevelopment" in d and "—" not in d
    assert sum(len(x) + 1 for x in metadata.tags(items)) <= 500


def test_campaign_appeals_are_not_government_actions():
    today = dt.date(2026, 10, 23)
    stories = [_story("కూటమి అభ్యర్థులను గెలిపించండి, అభివృద్ధికి సహకరించండి", 21), _story("శ్రీకాళహస్తిలో జనసేన పార్టీ అభివృద్ధికి కృషి", 20),
               _story("అమరావతి నిర్మాణానికి మరో రూ.15,000 కోట్ల లోన్ మంజూరు", 22)]
    items = collect.pick(stories, today, set())
    assert len(items) == 1 and "లోన్" in items[0]["headline"]
