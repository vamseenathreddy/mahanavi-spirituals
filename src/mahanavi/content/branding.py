"""
branding.py: the channel's brand name and one short "<series> by
Channel A" tagline per series, prepended to every Short's
description (explicit request, 2026-10-03: "I want in every short
description like example 'puranakathalu by mahanavi spirituals' means
I want to increase brand value").

A single shared constant (rather than each SEO module inventing its
own wording) so every series' tagline follows the exact same format
and the brand name itself is spelled identically everywhere -- change
BRAND_NAME once here and every series picks it up.

This is deliberately a plain, short, English-script line (not
Telugu) -- a tagline is a visual/brand signature meant to be
instantly recognizable on repeat viewing across every series, which
works better as one fixed, simple string than as content competing
for the viewer's reading attention. It is placed as the very FIRST
line of the description, ahead of even the hook -- brand recall was
the explicit goal of this request, so the tagline gets the single
highest-visibility spot (the snippet shown before YouTube's mobile
"...more" cutoff), ahead of the hook line that held that spot before.
"""

from __future__ import annotations

BRAND_NAME = "Mahanavi Spirituals"

# One short, recognizable English name per series -- matches the
# user's own example wording ("puranakathalu") for the Purana Story
# series, extended to the same style for every other series.
SERIES_TAGLINE_NAME: dict[str, str] = {
    "rahu_kalam": "Rahu Kalam",
    "shubha_ghadiyalu": "Shubha Ghadiyalu",
    "durmuhurtham": "Durmuhurtham",
    "rashi_mantra": "Rashi Mantra",
    "purana_short": "Purana Kathalu",
    "purana_concept": "Purana Shorts",
    "gita_sloka": "Bhagavad Gita Sloka",
}


def brand_tagline(series_key: str) -> str:
    """e.g. brand_tagline("purana_short") -> "Purana Kathalu by Channel A"."""
    name = SERIES_TAGLINE_NAME[series_key]
    return f"{name} by {BRAND_NAME}"


BRAND_TITLE_SUFFIX = f" | {BRAND_NAME}"
BRAND_TAGS = [BRAND_NAME.lower(), "mahanavi", "mahanavispirituals", "mahanavi spirituals telugu"]


def brand_title(title: str, limit: int = 100) -> str:
    """Put the channel name in the title of every Channel A Short (2026-10-09 request: Google searches for
    "mahanavi spirituals" were being corrected to "mahanavami"; the exact name in every title/tag/description
    teaches Google that it is a real brand). Already-branded titles are untouched; a long title is cut
    (with an ellipsis) so the name always fits."""
    if "mahanavi" in title.lower():
        return title
    room = limit - len(BRAND_TITLE_SUFFIX)
    base = title if len(title) <= room else title[: room - 1].rstrip() + "\u2026"
    return base + BRAND_TITLE_SUFFIX


TAG_LIMIT = 480   # YouTube rejects uploads whose tags total over 500 characters (a tag with a space costs 2 more)


def _tag_cost(tag: str) -> int:
    return len(tag) + (2 if " " in tag else 0) + 1


def brand_tags(tags: list[str]) -> list[str]:
    """Clean the tags (no blanks, duplicates or < > characters), then append the brand tags that are not already
    there (case-insensitive). The result stays under YouTube's 500 character tag limit: brand tags are reserved
    first, then the original tags fill the rest in order (2026-11-16: calendar Shorts failed with invalidTags)."""
    seen: set[str] = set()
    clean: list[str] = []
    for t in tags:
        t = " ".join(t.replace("<", " ").replace(">", " ").split())
        if t and t.lower() not in seen:
            seen.add(t.lower())
            clean.append(t)
    brand = [t for t in BRAND_TAGS if t.lower() not in seen]
    budget = TAG_LIMIT - sum(_tag_cost(t) for t in brand)
    kept: list[str] = []
    for t in clean:
        c = _tag_cost(t)
        if c <= budget and len(t) <= 100:
            kept.append(t)
            budget -= c
    return kept + brand
