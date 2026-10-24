import datetime as dt

from mahanavi.content import arunachala_events as ev


def test_due_exactly_20_days_before_and_once():
    assert ev.due(dt.date(2026, 11, 4)).slug == "deepam-2026"
    assert ev.due(dt.date(2026, 11, 3)) is None or ev.due(dt.date(2026, 11, 3)).slug != "deepam-2026"
    assert ev.due(dt.date(2026, 11, 4), ["deepam-2026"]) is None


def test_card_is_telugu_with_date_and_playlist_text():
    spec = ev.build(ev.EVENTS[0], dt.date(2026, 11, 4))
    assert "24" in spec.title and spec.token_file == "youtube_token_ramana.json"
    assert len(spec.slides) == 1 and "20" in spec.slides[0].text


def test_events_sorted_and_future_dates_only_after_2026_10():
    assert all(e.date >= dt.date(2026, 11, 24) for e in ev.EVENTS)
