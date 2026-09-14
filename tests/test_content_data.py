from __future__ import annotations

from mahanavi.content.data import (
    DEITY_CONTENT,
    GENERAL_ENGLISH_KEYWORDS,
    GENERAL_TELUGU_HASHTAGS,
    TRENDING_DEVOTIONAL_HASHTAGS,
)
from mahanavi.core.models import Deity


def test_every_deity_has_content() -> None:
    for deity in Deity:
        assert deity in DEITY_CONTENT
        content = DEITY_CONTENT[deity]
        assert content.telugu_name
        assert content.blessing_phrase
        assert content.mantra
        assert content.telugu_hashtags
        assert content.english_keywords


def test_general_lists_are_non_empty() -> None:
    assert GENERAL_TELUGU_HASHTAGS
    assert TRENDING_DEVOTIONAL_HASHTAGS
    assert GENERAL_ENGLISH_KEYWORDS


def test_hashtags_are_well_formed() -> None:
    for tag in TRENDING_DEVOTIONAL_HASHTAGS:
        assert tag.startswith("#")
        assert " " not in tag
    for tag in GENERAL_TELUGU_HASHTAGS:
        assert tag.startswith("#")
        assert " " not in tag
