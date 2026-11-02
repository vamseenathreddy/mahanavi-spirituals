import re

from mahanavi.content.lakshmi108 import NAMES, SOURCES, STOTRA_SOURCE


def test_108_complete_and_clean():
    assert len(NAMES) == 108
    for i, (te, tr, mean, l1, l_en, l2, src) in enumerate(NAMES, 1):
        assert te and tr and mean and l1 and l_en and l2, i
        assert src in SOURCES, i
        assert re.search(r"[ఀ-౿]", te) and not re.search(r"[ऀ-ॿ]", te + l1 + l2), i
        assert not re.search(r"[ఀ-౿]", tr + mean + l_en), i
        assert "—" not in l1 + l_en + l2, i   # no em dash anywhere
        assert len(l1) + len(l_en) + len(l2) < 260, i


def test_story_names_carry_a_source():
    by = {n[1]: n[6] for n in NAMES}
    assert by["Samudratanaya"] == "VP" and by["Vishnu Vakshasthala Sthita"] == "VP" and by["Hiranmayi"] == "SS"
    assert by["Mahakali"] == "DM" and STOTRA_SOURCE
