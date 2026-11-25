"""Vedas series card content, Telugu (Mahanavi): mantra in Telugu script + Telugu meaning, English meaning under it."""
from __future__ import annotations

from mahanavi.content import vedas as v

HEAD = "వేద మంత్రం"
VERSES: list[tuple[str, str]] = [(m.te_read, m.te_mean) for m in v.MANTRAS]
MEANING_EN: list[str] = [m.en_mean for m in v.MANTRAS]
HEADS: list[str] = [v.HEAD_TE[m.veda] for m in v.MANTRAS]
SUBS: list[str] = [m.ref_te for m in v.MANTRAS]


def count() -> int:
    return len(VERSES)
