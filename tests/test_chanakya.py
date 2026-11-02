import datetime as dt

from channels import chanakya_plan as p
from mahanavi.content import chanakya_neeti as cn


def test_cards_never_repeat_and_cover_all():
    seen = []
    for d in range(cn.days()):
        seen += cn.card(d, "te")
    assert len(seen) == len(set(seen)) == cn.days() * cn.PER_CARD
    assert all(len(cn.card(d, "hi")) == cn.PER_CARD for d in range(cn.days()))


def test_plan_window_and_extension():
    assert p.plan(dt.date(2026, 11, 8)) is None
    assert p.plan(dt.date(2026, 11, 9)) == 0
    assert p.plan(p.SERIES_START + dt.timedelta(days=cn.days() - 1)) == cn.days() - 1
    assert p.plan(p.SERIES_START + dt.timedelta(days=cn.days())) is None


def test_no_telugu_in_hindi_text_and_vice_versa():
    for hi, te in cn.SUTRAS:
        assert not any("ఀ" <= ch <= "౿" for ch in hi)
        assert not any("ऀ" <= ch <= "ॿ" for ch in te)
