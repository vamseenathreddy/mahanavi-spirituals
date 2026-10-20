"""Playlist links for the Telugu Mahanavi Shorts (owner request 2026-10-20): every beej mantra, Purana and muhurta Short
shows all three series playlists at the top of its description, and its card has a line before the subscribe reminder
that sends viewers to those links. Links are looked up when the Short is posted; a playlist that cannot be found is left
out, and any failure returns an empty block so an upload is never lost."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

URL = "https://www.youtube.com/playlist?list="
LABELS = {"beej": "బీజ మంత్రాలు", "puranas": "పురాణ కథలు", "muhurtas": "రోజువారీ ముహూర్తాలు"}
ORDER = ["beej", "puranas", "muhurtas"]
TITLES = {"puranas": "Purana Stories & Concepts",
          "muhurtas": "Daily Muhurtams (Rahu Kalam, Shubha Ghadiyalu, Durmuhurtham)"}

# The line before the subscribe reminder on the card: three short lines so they stay at full size.
CARD_LINES = {
    "beej": "ఇలాంటి బీజ మంత్రాలన్నీ ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి",
    "puranas": "ఇలాంటి పురాణ కథలన్నీ ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి",
    "muhurtas": "ఇలాంటి ముహూర్తాలన్నీ ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి",
}


def resolve(youtube, settings) -> dict[str, str]:
    """{category: playlist id} for the playlists that exist (beej is created if missing)."""
    from channels.beej import playlists as beej_playlists

    ids: dict[str, str] = {}
    try:
        ids["beej"] = beej_playlists.ensure_playlist(youtube, "mahanavi")
    except Exception as exc:  # noqa: BLE001
        logger.warning("beej playlist lookup failed: %s", exc)
    known = {"puranas": getattr(settings, "playlist_id_puranas", None),
             "muhurtas": getattr(settings, "playlist_id_muhurtas", None)}
    ids.update({k: v for k, v in known.items() if v})
    missing = [k for k, v in known.items() if not v]
    if missing:
        try:
            by_title = {t: i for i, t, _n in beej_playlists.list_playlists(youtube)}
            for k in missing:
                if TITLES[k] in by_title:
                    ids[k] = by_title[TITLES[k]]
        except Exception as exc:  # noqa: BLE001
            logger.warning("playlist list failed: %s", exc)
    return ids


def block(youtube, settings, current: str) -> str:
    """Top-of-description block: this series' playlist first, then the other two. '' when nothing was found."""
    try:
        ids = resolve(youtube, settings)
    except Exception as exc:  # noqa: BLE001
        logger.warning("playlist links unavailable: %s", exc)
        return ""
    order = [current] + [k for k in ORDER if k != current]
    lines = [f"{'▶ ఈ ప్లేలిస్ట్ చూడండి' if k == current else '▶'} {LABELS[k]}: {URL}{ids[k]}" for k in order if k in ids]
    if not lines:
        return ""
    return "మా 3 ప్లేలిస్ట్‌లు (Playlists):\n" + "\n".join(lines)


class WithPlaylists:
    """Wraps an SEO object so its description starts with the playlist block (everything else passes through)."""

    def __init__(self, seo, top: str) -> None:
        self._seo, self._top = seo, top

    def __getattr__(self, name):
        return getattr(self._seo, name)

    @property
    def description(self) -> str:
        base = self._seo.description
        return f"{self._top}\n\n{base}" if self._top else base

    def full_caption(self) -> str:
        base = self._seo.full_caption()
        return f"{self._top}\n\n{base}" if self._top else base
