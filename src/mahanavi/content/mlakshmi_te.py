"""Mahalakshmi Ashtakam card content (Telugu): verse + meaning, English meaning under it."""
from __future__ import annotations

from mahanavi.content import mahalakshmi_ashtakam as m

HEAD = "మహాలక్ష్మీ అష్టకం"
VERSES: list[tuple[str, str]] = [(m.quad(x), y) for x, y in zip(m.TE_READ, m.TE_MEAN)]
MEANING_EN: list[str] = list(m.EN_MEAN)
HEADS: list[str] = [HEAD] * len(VERSES)
SUBS: list[str] = ["శ్రీ మహాలక్ష్మీ అష్టకం"] * len(VERSES)


def count() -> int:
    return len(VERSES)
