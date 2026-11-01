"""strip_links: remove web links from video descriptions (owner request 2026-11-01: no links in any description).

Every uploader runs its description through this on the way out. A line that was only a link with a label
("Videos: https://...", "Playlist: https://...") is dropped entirely; a line with other text keeps that text.
Hashtags and @handles are untouched. Comments are not changed here."""
from __future__ import annotations

import re

_URL = re.compile(r"(?:https?://|www\.)\S+|\b(?:youtu\.be|t\.me|chat\.whatsapp\.com|wa\.me|bit\.ly)/\S+", re.IGNORECASE)
_TRAIL = re.compile(r"[\s\-–—:|>▶•➡⭐\U0001F000-\U0001FFFF☀-➿]+$")


def strip_links(text: str | None) -> str:
    if not text:
        return text or ""
    out: list[str] = []
    for line in text.split("\n"):
        if not _URL.search(line):
            out.append(line)
            continue
        rest = _URL.sub("", line).rstrip()
        bare = _TRAIL.sub("", rest).strip()
        if not bare or rest.rstrip().endswith((":", "-", "–", "—", "|")):
            continue   # the line was a label for the link: drop it
        out.append(rest)
    cleaned = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()
