"""
Telugu text constants and formatting helpers used by the image renderer.

Kept separate from renderer.py so the Telugu vocabulary (labels, month
names, deity names) can be reviewed/edited by a Telugu speaker without
touching any Pillow/layout code.
"""

from __future__ import annotations

from datetime import date

from mahanavi.core.models import Deity

TELUGU_WEEKDAYS: dict[int, str] = {
    0: "సోమవారం",   # Monday
    1: "మంగళవారం",  # Tuesday
    2: "బుధవారం",    # Wednesday
    3: "గురువారం",   # Thursday
    4: "శుక్రవారం",   # Friday
    5: "శనివారం",    # Saturday
    6: "ఆదివారం",    # Sunday
}

TELUGU_MONTHS: dict[int, str] = {
    1: "జనవరి", 2: "ఫిబ్రవరి", 3: "మార్చి", 4: "ఏప్రిల్",
    5: "మే", 6: "జూన్", 7: "జూలై", 8: "ఆగస్టు",
    9: "సెప్టెంబర్", 10: "అక్టోబర్", 11: "నవంబర్", 12: "డిసెంబర్",
}

DEITY_TELUGU_NAMES: dict[Deity, str] = {
    Deity.SHIVA: "శివుడు",
    Deity.HANUMAN: "హనుమంతుడు",
    Deity.GANESHA: "గణేశుడు",
    Deity.SAI: "సాయిబాబా",
    Deity.LAKSHMI: "లక్ష్మీదేవి",
    Deity.VENKATESWARA: "వేంకటేశ్వరుడు",
    Deity.SURYA: "సూర్యభగవానుడు",
}

# Order matters here — this is the display order in the Panchang panel.
PANCHANG_LABELS: dict[str, str] = {
    "tithi": "తిథి",
    "nakshatram": "నక్షత్రం",
    "sunrise": "సూర్యోదయం",
    "sunset": "సూర్యాస్తమయం",
    "varjyam": "వర్జ్యం",
    "rahu_kalam": "రాహు కాలం",
    "yamagandam": "యమగండం",
    "gulika_kalam": "గుళిక కాలం",
    "durmuhurtham": "దుర్ముహూర్తం",
    "abhijit_muhurtham": "అభిజిత్ ముహూర్తం",
}

_TELUGU_DIGITS = "౦౧౨౩౪౫౬౭౮౯"


def to_telugu_numerals(value: int) -> str:
    """Convert an integer (e.g. a year) to Telugu numeral digits."""
    return "".join(_TELUGU_DIGITS[int(ch)] for ch in str(value))


def format_telugu_date(for_date: date) -> str:
    """Return e.g. '౨౦ జూలై ౨౦౨౬, సోమవారం' for the given date."""
    day = to_telugu_numerals(for_date.day)
    month = TELUGU_MONTHS[for_date.month]
    year = to_telugu_numerals(for_date.year)
    weekday = TELUGU_WEEKDAYS[for_date.weekday()]
    return f"{day} {month} {year}, {weekday}"
