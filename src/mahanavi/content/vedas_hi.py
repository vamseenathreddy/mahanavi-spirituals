"""Vedas series card content, Hindi (Divine Mantra Sangam): Devanagari mantra + Hindi meaning, English meaning under it."""
from __future__ import annotations

from mahanavi.content import vedas as v

HEAD = "वेद मंत्र"
VERSES: list[tuple[str, str]] = [(m.sa, m.hi_mean) for m in v.MANTRAS]
MEANING_EN: list[str] = [m.en_mean for m in v.MANTRAS]
HEADS: list[str] = [v.HEAD_HI[m.veda] for m in v.MANTRAS]
SUBS: list[str] = [m.ref_hi for m in v.MANTRAS]


def count() -> int:
    return len(VERSES)
