"""Themes for the long Bible-verse videos (King James Version, public domain). One theme per video, rotating."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "themes.json"
ORDER = ["peace", "anxiety", "strength", "hope", "healing", "love", "sleep"]
# One theme per weekday (Monday = 0). Strength starts the week, sleep lands on Saturday night in the US.
WEEKDAY = ["strength", "anxiety", "peace", "hope", "healing", "sleep", "love"]


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def theme_for(index: int) -> tuple[str, dict]:
    key = ORDER[index % len(ORDER)]
    return key, load()["themes"][key]


def theme_for_date(day) -> tuple[str, dict]:
    key = WEEKDAY[day.weekday()]
    return key, load()["themes"][key]
