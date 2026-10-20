"""Deity photo behind every Hindi card, matched to the card's mantra (owner request 2026-10-20: god images instead of
plain text cards). Photos live in assets/images/deities. The day's deity follows the weekday (Mon Shiva, Tue Hanuman,
Wed Ganesha, Thu Vishnu, Fri Lakshmi, Sat Shani, Sun Surya); Purana stories use the god the story is about;
Rashi mantras use the planet's deity. Each god has several photos, rotated by date."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

DEITIES = Path(__file__).resolve().parents[2] / "assets" / "images" / "deities"

PHOTOS = {
    "kurma": ["puranic_kurma", "puranic_manthan"], "manthan": ["puranic_manthan"], "varaha": ["puranic_varaha"],
    "dashavatara": ["puranic_dashavatara"], "garuda": ["puranic_garuda"], "dakshinamurthy": ["puranic_dakshinamurthy"],
    "sheshashayi": ["puranic_sheshashayi"],
    "g_surya": ["graha_surya"], "g_chandra": ["graha_chandra"], "g_mangala": ["graha_mangala"], "g_budha": ["graha_budha"],
    "g_guru": ["graha_guru"], "g_shukra": ["graha_shukra"], "g_shani": ["graha_shani"], "g_rahu": ["graha_rahu"],
    "g_ketu": ["graha_ketu"],
    "ayyappa": ['ayyappa_n1', 'ayyappa_n2', 'ayyappa_n3'],
    "annapurna": ['annapurna_n1', 'annapurna_n2'],
    "gita": ['gita_n1', 'gita_n2', 'gita_n3', 'gita_n4', 'gita_n5', 'gita_n6', 'gita_n7', 'gita_n8', 'gita_n9', 'gita_n10'],

    "shiva": ["shiva_g1", "shiva_g2", "shivafamily_n1", "shivafamily_n2"], "hanuman": ["hanuman_g1", "hanuman_g2"], "ganesha": ["ganesha_g1", "ganesha_g2"],
    "vishnu": ["vishnu_g1", "vishnu_g3", "vishnu_g5", "vishnu_g2"], "lakshmi": ["lakshmi_g1", "lakshmi_g2"],
    "shani": ["shani_g1", "shani_g3", "shani_g5"], "surya": ["surya_g2"], "durga": ["durga_g1", "durga_g2", "durga_n1", "durga_n2", "durga_n3", "durga_n4", "durga_n5", "durga_n6", "durga_n7", "durga_n8", "durga_n9", "durga_n10"],
    "krishna": ["krishna_g1", "krishna_n1", "krishna_n2", "krishna_n3", "krishna_n4", "krishna_n5", "krishna_n6", "krishna_n7", "krishna_n8", "krishna_n9", "krishna_n10"], "rama": ["rama_g1", "rama_g2", "rama_n1", "rama_n2", "rama_n3", "rama_n4", "rama_n5", "rama_n6", "rama_n7", "rama_n8", "rama_n9", "rama_n10"], "narasimha": ["narasimha_g1", "narasimha_g2", "narasimha_n1", "narasimha_n2", "narasimha_n3"],
    "saraswati": ["saraswati_g2", "saraswati_n1", "saraswati_n2", "saraswati_n3", "saraswati_n4", "saraswati_n5", "saraswati_n6", "saraswati_n7", "saraswati_n8", "saraswati_n9", "saraswati_n10"], "murugan": ["murugan_g1", "murugan_g2"], "parvati": ["parvati_g2"],
    "dattatreya": ["dattatreya_g1", "dattatreya_g3", "dattatreya_g5"], "venkateswara": ["venkateswara_g1"],
}
WEEKDAY = ["shiva", "hanuman", "ganesha", "vishnu", "lakshmi", "shani", "surya"]
PLANET = {"mars": "g_mangala", "venus": "g_shukra", "mercury": "g_budha", "jupiter": "g_guru", "saturn": "g_shani",
          "sun": "g_surya", "moon": "g_chandra", "rahu": "g_rahu", "ketu": "g_ketu"}
KEYWORDS = [
    ("कूर्म", "kurma"), ("समुद्र मंथन", "manthan"), ("समुद्रमंथन", "manthan"), ("वराह", "varaha"), ("दशावतार", "dashavatara"), ("गरुड़", "garuda"), ("दक्षिणामूर्ति", "dakshinamurthy"), ("शेषशायी", "sheshashayi"), ("अनंतशयन", "sheshashayi"),
    ("अयप्पा", "ayyappa"), ("अन्नपूर्णा", "annapurna"),  # first match wins, so the specific forms come before the general ones
    ("नरसिंह", "narasimha"), ("हनुमान", "hanuman"), ("गणेश", "ganesha"), ("गजानन", "ganesha"), ("सरस्वती", "saraswati"),
    ("लक्ष्मी", "lakshmi"), ("दुर्गा", "durga"), ("पार्वती", "parvati"), ("कार्तिकेय", "murugan"), ("स्कंद", "murugan"),
    ("कृष्ण", "krishna"), ("राम", "rama"), ("शिव", "shiva"), ("महादेव", "shiva"), ("शनि", "shani"), ("सूर्य", "surya"),
    ("विष्णु", "vishnu"), ("नारायण", "vishnu"), ("हरि", "vishnu"), ("वामन", "vishnu"), ("वराह", "vishnu"), ("कूर्म", "vishnu"),
    ("मत्स्य", "vishnu"), ("दत्तात्रेय", "dattatreya"), ("देवी", "durga"),
]

import re as _re

EN_RULES = [  # English title keywords, first match wins (the English title names the story's main deity most reliably)
    ("narasimha", "narasimha"), ("kurma", "kurma"), ("varaha", "varaha"), ("dattatreya", "dattatreya"),
    ("venkateswara", "venkateswara"), ("annapurna", "annapurna"), ("ayyappa", "ayyappa"), ("kartikeya", "murugan"),
    ("hanuman", "hanuman"), ("ganesha", "ganesha"), ("lakshmi", "lakshmi"), ("deepavali", "lakshmi"),
    ("savitri", "lakshmi"), ("krishna", "krishna"), ("kaliya", "krishna"), ("rukmini", "krishna"), ("sudama", "krishna"),
    ("draupadi", "krishna"), ("rama", "rama"), ("shabari", "rama"), ("jatayu", "rama"), ("ahalya", "rama"),
    ("vibhishana", "rama"), ("saraswati", "saraswati"), ("gayatri", "surya"), ("surya", "surya"), ("shani", "shani"),
    ("parvati", "parvati"), ("kedara gauri", "parvati"), ("durga", "durga"), ("devi", "durga"), ("goddess", "durga"),
    ("kali", "durga"), ("lalita", "durga"), ("chamunda", "durga"), ("shami", "durga"), ("shiva", "shiva"),
    ("shivaratri", "shiva"), ("pradosham", "shiva"), ("kannappa", "shiva"), ("lingodbhava", "shiva"),
    ("kamadahana", "shiva"), ("atmalinga", "shiva"), ("tripura", "shiva"), ("somnath", "shiva"), ("bhairava", "shiva"),
    ("bhagiratha", "shiva"), ("markandeya", "shiva"), ("meenakshi", "shiva"), ("vishnu", "vishnu"), ("hayagriva", "vishnu"),
    ("ekadashi", "vishnu"), ("gajendra", "vishnu"), ("vamana", "vishnu"), ("matsya", "vishnu"), ("tulasi", "vishnu"),
]


def god_for_title_en(title_en: str) -> str | None:
    t = (title_en or "").lower()
    for word, god in EN_RULES:
        if _re.search(r"\b" + _re.escape(word), t):
            return god
    return None


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
        god = god_for_title_en(row.get("title_en", "")) or god_for_text(row.get("title_hi", ""), row.get("invocation_hi", ""), row.get("moral_hi", ""),
                           row.get("purana_hi", ""), row.get("t_story", "")) or weekday
    else:
        god = weekday            # Rahu Kaal / Shubh Muhurat / Durmuhurat, mantra of the day
    return _pick(god, date_key)
