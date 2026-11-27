"""Vishnu Sahasranamam card content, Telugu (Mahanavi): verse in Telugu script + Telugu meaning, English meaning under it."""
from __future__ import annotations

from mahanavi.content import vishnu_sahasra as v

HEAD = "విష్ణు సహస్రనామం"
VERSES: list[tuple[str, str]] = [(v.quad(x), y) for x, y in zip(v.TE_READ, v.TE_MEAN)]
MEANING_EN: list[str] = list(v.EN_MEAN)
HEADS: list[str] = [HEAD] * len(VERSES)
SUBS: list[str] = ["శ్రీ విష్ణు సహస్రనామ స్తోత్రం"] * len(VERSES)


def count() -> int:
    return len(VERSES)
