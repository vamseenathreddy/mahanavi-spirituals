"""Vishnu Sahasranamam card content, Hindi (Divine Mantra Sangam): Devanagari verse + Hindi meaning, English meaning under it."""
from __future__ import annotations

from mahanavi.content import vishnu_sahasra as v

HEAD = "विष्णु सहस्रनाम"
VERSES: list[tuple[str, str]] = [(v.quad(x), y) for x, y in zip(v.SA, v.HI_MEAN)]
MEANING_EN: list[str] = list(v.EN_MEAN)
HEADS: list[str] = [HEAD] * len(VERSES)
SUBS: list[str] = ["श्री विष्णु सहस्रनाम स्तोत्र"] * len(VERSES)


def count() -> int:
    return len(VERSES)
