"""Deity photo behind every Hindi card, matched to the card's mantra (owner request 2026-10-20: god images instead of
plain text cards). Photos live in assets/images/deities. The day's deity follows the weekday (Mon Shiva, Tue Hanuman,
Wed Ganesha, Thu Vishnu, Fri Lakshmi, Sat Shani, Sun Surya); Purana stories use the god the story is about;
Rashi mantras use the planet's deity. Each god has several photos, rotated by date."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

DEITIES = Path(__file__).resolve().parents[2] / "assets" / "images" / "deities"

PHOTOS = {
    "shiva": ["shiva_g1", "shiva_g2"], "hanuman": ["hanuman_g1", "hanuman_g2"], "ganesha": ["ganesha_g1", "ganesha_g2"],
    "vishnu": ["vishnu_g1", "vishnu_g3", "vishnu_g5", "vishnu_g2"], "lakshmi": ["lakshmi_g1", "lakshmi_g2"],
    "shani": ["shani_g1", "shani_g3", "shani_g5"], "surya": ["surya_g2"], "durga": ["durga_g1", "durga_g2"],
    "krishna": ["krishna_g1"], "rama": ["rama_g1", "rama_g2"], "narasimha": ["narasimha_g1", "narasimha_g2"],
    "saraswati": ["saraswati_g2"], "murugan": ["murugan_g1", "murugan_g2"], "parvati": ["parvati_g2"],
    "dattatreya": ["dattatreya_g1", "dattatreya_g3", "dattatreya_g5"], "venkateswara": ["venkateswara_g1"],
}
WEEKDAY = ["shiva", "hanuman", "ganesha", "vishnu", "lakshmi", "shani", "surya"]
PLANET = {"mars": "hanuman", "venus": "lakshmi", "mercury": "vishnu", "jupiter": "dattatreya", "saturn": "shani",
          "sun": "surya", "moon": "shiva", "rahu": "durga", "ketu": "ganesha"}
KEYWORDS = [  # first match wins, so the specific forms come before the general ones
    ("नरसिंह", "narasimha"), ("हनुमान", "hanuman"), ("गणेश", "ganesha"), ("गजानन", "ganesha"), ("सरस्वती", "saraswati"),
    ("लक्ष्मी", "lakshmi"), ("दुर्गा", "durga"), ("पार्वती", "parvati"), ("कार्तिकेय", "murugan"), ("स्कंद", "murugan"),
    ("कृष्ण", "krishna"), ("राम", "rama"), ("शिव", "shiva"), ("महादेव", "shiva"), ("शनि", "shani"), ("सूर्य", "surya"),
    ("विष्णु", "vishnu"), ("नारायण", "vishnu"), ("हरि", "vishnu"), ("वामन", "vishnu"), ("वराह", "vishnu"), ("कूर्म", "vishnu"),
    ("मत्स्य", "vishnu"), ("दत्तात्रेय", "dattatreya"), ("देवी", "durga"),
]


def _pick(god: str, date_key: str) -> Path | None:
    files = [DEITIES / f"{n}.jpg" for n in PHOTOS.get(god, []) if (DEITIES / f"{n}.jpg").exists()]
    return files[dt.date.fromisoformat(date_key).toordinal() % len(files)] if files else None


def god_for_text(*texts: str) -> str | None:
    for text in texts:           # title first, then invocation, then the story itself
        for word, god in KEYWORDS:
            if word in (text or ""):
                return god
    return None


def picker(date_key: str, row: dict | None):
    """Used as ChannelConfig.photo_picker; returns None to fall back to the channel's generic backgrounds."""
    row = row or {}
    cat = row.get("category")
    weekday = WEEKDAY[dt.date.fromisoformat(date_key).weekday()]
    if cat == "rashi":
        planet = (row.get("planet_en") or "").lower()
        god = next((g for k, g in PLANET.items() if k in planet), weekday)
    elif cat == "purana":
        god = god_for_text(row.get("title_hi", ""), row.get("invocation_hi", ""), row.get("moral_hi", ""),
                           row.get("purana_hi", ""), row.get("t_story", "")) or weekday
    else:
        god = weekday            # Rahu Kaal / Shubh Muhurat / Durmuhurat, mantra of the day
    return _pick(god, date_key)
