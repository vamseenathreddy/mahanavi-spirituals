"""Near-duplicate memory for Pulse Boosting. The exact-headline key (Story.key) lets the same story through when another
outlet words it differently, so every post also remembers a fingerprint of its headline and link; a new candidate that
looks like a recent post is skipped. Bank variants (evergreen posts) are exempt: they are reframed on purpose."""
from __future__ import annotations

import re
from urllib.parse import urlsplit

KEEP = 400          # recent posts remembered
THRESHOLD = 0.5     # share of the smaller headline's word stems that match an earlier headline


def stems(text: str) -> frozenset:
    """Word stems: Telugu words carry case endings, so only the first 5 characters of each word count."""
    return frozenset(w[:5] for w in re.split(r"[^\w\u0900-\u0dff]+", text.casefold()) if len(w) >= 3)


def link_key(link: str) -> str:
    u = urlsplit(link or "")
    return f"{u.netloc.lower().removeprefix('www.')}{u.path.rstrip('/')}" if u.netloc else ""


def entry(headline: str, link: str) -> dict:
    return {"s": sorted(stems(headline)), "l": link_key(link)}


def is_duplicate(headline: str, link: str, recent) -> bool:
    mine, lk = stems(headline), link_key(link)
    for r in recent or ():
        if lk and r.get("l") == lk:
            return True
        theirs = frozenset(r.get("s", ()))
        small = min(len(mine), len(theirs))
        if small >= 3 and len(mine & theirs) / small >= THRESHOLD:
            return True
    return False


def remember(state: dict, headline: str, link: str) -> None:
    state["recent"] = (state.get("recent", []) + [entry(headline, link)])[-KEEP:]
