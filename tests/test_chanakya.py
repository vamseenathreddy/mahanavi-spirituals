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


def test_concept_pick_next_is_fresh_only(tmp_path, monkeypatch):
    import channels.engine.used_registry as ur
    from mahanavi.content.purana_concept_shorts import PURANA_CONCEPT_SHORTS as C, is_paused
    from mahanavi.scripts import post_concept_short as pcs

    monkeypatch.setattr(ur, "DATA_DIR", tmp_path)
    live = [c for c in C if not is_paused(c)]
    used = {pcs.concept_id(c) for c in live[:5]}
    assert pcs.pick_next(C, used, []) == C.index(live[5])            # the first unused one
    assert pcs.pick_next(C, {pcs.concept_id(c) for c in live}, []) == -1   # all used: nothing to post
    posted = [live[5].title_te] if sum(c.title_te == live[5].title_te for c in C) == 1 else []
    if posted:
        assert pcs.pick_next(C, used, posted) == C.index(live[6])    # already on the channel: skipped


def test_hindi_concepts_cover_every_live_entry_and_pick_fresh(tmp_path, monkeypatch):
    import channels.engine.used_registry as ur
    from mahanavi.content import purana_concept_hindi as ph
    from mahanavi.content.purana_concept_shorts import PURANA_CONCEPT_SHORTS as C, is_paused
    from mahanavi.scripts import post_purana_hindi as pp

    monkeypatch.setattr(ur, "DATA_DIR", tmp_path)
    live = [i for i, c in enumerate(C) if not is_paused(c)]
    assert sorted(ph.HINDI) == live                       # every unpaused concept has a Hindi version, no extras
    assert pp.pick_next(set(), [], "sangam") == live[0]
    used = {pp.cid(i) for i in live[:3]}
    assert pp.pick_next(used, [], "sangam") == live[3]
    assert pp.pick_next({pp.cid(i) for i in live}, [], "sangam") == -1
    t, body, tags, *_ = pp.metadata(live[0])
    assert t and body and all(x.isascii() for x in tags if x == "Shorts")


def test_hindi_plan_runs_on_chanakya_off_days():
    from channels import purana_hindi_plan as p
    assert not p.is_post_day(dt.date(2026, 11, 3)) and p.is_post_day(dt.date(2026, 11, 4)) and not p.is_post_day(dt.date(2026, 11, 5))
    assert not p.is_post_day(dt.date(2026, 11, 6)) and p.is_post_day(dt.date(2026, 11, 8))


def test_fan_bank_items_are_unique_and_cover_every_fan_niche():
    from channels.trending import config as cfg
    from channels.trending import fan_bank
    keys = [s.key for n in cfg.FAN_PATTERN for s in fan_bank.stories(n)]
    assert len(keys) == len(set(keys)) == len([i for i in fan_bank.ITEMS if i[0] != "ntr"])
    assert all(fan_bank.stories(n) for n in cfg.FAN_PATTERN)


def test_fan_mode_picks_fresh_only_and_plans_fan_niches():
    from channels.trending import config as cfg
    from channels.trending import fan_bank
    from channels.trending.post import choose_fan
    assert cfg.FAN_MODE and cfg.plan(0)[1] in cfg.FAN_PATTERN
    used = set()
    seen = []
    assert "ntr" not in cfg.FAN_PATTERN
    for _ in range(len(fan_bank.ITEMS) - len(fan_bank.stories("ntr"))):
        n, s = choose_fan("chandrababu", used)
        assert n != "ntr"
        assert s is not None and s.key not in used
        used.add(s.key)
        seen.append(s.key)
    assert len(seen) == len(set(seen))


def test_fan_mode_posts_three_shorts_a_day_after_the_silence_days():
    import datetime as dt

    from channels.trending import config as cfg
    assert cfg.FAN_MODE
    assert cfg.slots_for(dt.date(2026, 11, 4)) == {"t6", "t10"} and cfg.slots_for(dt.date(2026, 11, 5)) == {"t2", "t6", "t10"}
    for d in (6, 7, 8, 9, 20):
        assert cfg.slots_for(dt.date(2026, 11, d)) == {"t2", "t6", "t10"}


def test_telugu_daily_from_10_nov():
    import datetime as dt
    assert [p.plan_for("te", dt.date(2026, 11, d)) for d in (3, 4, 5, 7, 9)] == [0, None, 1, 2, 3]
    assert [p.plan_for("te", dt.date(2026, 11, d)) for d in (10, 11, 12)] == [4, 5, 6]
    p.APPROVED_CARDS = 100
    try:
        assert [p.plan_for("te", dt.date(2026, 11, d)) for d in (10, 11, 12)] == [4, 5, 6]
        assert p.plan_for("hi", dt.date(2026, 11, 10)) == p.plan(dt.date(2026, 11, 10))
    finally:
        p.APPROVED_CARDS = 13
