from __future__ import annotations

from datetime import date

from mahanavi.core.models import Deity
from mahanavi.images.telugu_text import (
    DEITY_TELUGU_NAMES,
    PANCHANG_LABELS,
    format_telugu_date,
    to_telugu_numerals,
)


def test_to_telugu_numerals() -> None:
    assert to_telugu_numerals(2026) == "౨౦౨౬"
    assert to_telugu_numerals(0) == "౦"
    assert to_telugu_numerals(9) == "౯"


def test_format_telugu_date_monday() -> None:
    result = format_telugu_date(date(2026, 7, 20))  # a Monday
    assert result.startswith("౨౦ జూలై ౨౦౨౬")
    assert result.endswith("సోమవారం")


def test_format_telugu_date_sunday() -> None:
    result = format_telugu_date(date(2026, 7, 26))  # a Sunday
    assert result.endswith("ఆదివారం")


def test_all_deities_have_telugu_names() -> None:
    for deity in Deity:
        assert deity in DEITY_TELUGU_NAMES
        assert DEITY_TELUGU_NAMES[deity]


def test_panchang_labels_cover_all_fields() -> None:
    expected_fields = {
        "tithi", "nakshatram", "varjyam", "rahu_kalam", "yamagandam",
        "gulika_kalam", "durmuhurtham", "abhijit_muhurtham", "sunrise", "sunset",
    }
    assert set(PANCHANG_LABELS.keys()) == expected_fields
