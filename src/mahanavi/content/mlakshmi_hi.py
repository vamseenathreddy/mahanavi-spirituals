"""Mahalakshmi Ashtakam card content (Hindi): verse + meaning, English meaning under it."""
from __future__ import annotations

from mahanavi.content import mahalakshmi_ashtakam as m

HEAD = "महालक्ष्मी अष्टकम्"
VERSES: list[tuple[str, str]] = [(m.quad(x), y) for x, y in zip(m.SA, m.HI_MEAN)]
MEANING_EN: list[str] = list(m.EN_MEAN)
HEADS: list[str] = [HEAD] * len(VERSES)
SUBS: list[str] = ["श्री महालक्ष्मी अष्टकम्"] * len(VERSES)


def count() -> int:
    return len(VERSES)
