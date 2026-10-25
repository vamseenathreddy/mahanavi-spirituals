"""Mahanavi "Temple Secrets" series (owner request 2026-10-24): one temple a week, ONE card with 10+ points
(history, architecture, rituals, records, beliefs). Every point comes from published sources (Wikipedia pages on the
temple and its architecture, the temple's own history, TTD and similar official pages); beliefs and legends are worded
as "నమ్మకం" (belief), never as fact. No made-up "hidden" claims. Add temples to TEMPLES in the order they should post;
the poster takes the first one not yet in state["used_ids"] and warns when fewer than 4 are left.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from mahanavi.content import calendar_days as cal
from mahanavi.content.request_shorts import RequestShort, Slide

PLAYLIST_TITLE = "దేవాలయ రహస్యాలు | Temple Secrets in Telugu | Mahanavi Spirituals"
PLAYLIST_DESC = ("ప్రతి వారం ఒక ప్రసిద్ధ దేవాలయం: చరిత్ర, నిర్మాణం, సంప్రదాయాలు, ఆసక్తికర విశేషాలు.\n"
                 "One famous temple every week: history, architecture, traditions and lesser-known facts, in Telugu.")
PLAYLIST_LINE = "అన్ని దేవాలయ రహస్యాలు ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి"
DISCLAIMER_TE = "ఈ వివరాలు ప్రచురిత చరిత్ర, ఆలయ సంప్రదాయాల ఆధారంగా ఇచ్చాం. నమ్మకాలను 'నమ్మకం' అని చెప్పాం 🙏"
DISCLAIMER_EN = "Facts come from published history and temple traditions; beliefs are marked as beliefs."
LOW_STOCK = 4


@dataclass(frozen=True)
class Temple:
    slug: str
    te: str                  # card heading: "<temple> రహస్యాలు"
    en: str
    god: str                 # key of calendar_days.OBS used for the background photo: ekadashi (Vishnu), shivaratri (Shiva), purnima (Lakshmi/Devi)
    points: tuple[str, ...]  # 10 or more short Telugu lines (about 45 characters each)
    tags: tuple[str, ...] = ()


TEMPLES: tuple[Temple, ...] = (
    Temple("tirumala", "తిరుమల శ్రీవారి రహస్యాలు", "Tirumala Srivari Temple", "ekadashi", (
        "ఏడవ శిఖరం వేంకటాద్రి, ఎత్తు 853 మీటర్లు",
        "శ్రీవారు తూర్పు ముఖంగా, స్వయంభూ మూర్తి",
        "మూలవిరాట్టు సుమారు 8 అడుగుల ఎత్తు",
        "ఆనంద నిలయ విమానం బంగారు తాపడం",
        "పంచ బేరాలు: ధ్రువ, కౌతుక, స్నపన, ఉత్సవ, బలి",
        "108 దివ్యదేశాల్లో ఒకటి",
        "640 శాసనాలు, 3,000 రాగి ఫలకాలు",
        "వకుళమాత పోటును పర్యవేక్షిస్తుందని నమ్మకం",
        "ముందుగా భూవరాహ స్వామి దర్శనం సంప్రదాయం",
        "స్వామి పుష్కరిణి వైకుంఠ తీర్థమని నమ్మకం",
        "1517లో శ్రీకృష్ణదేవరాయలు విగ్రహ ప్రతిష్ఠ",
        "1119లో రామానుజులు తిరుపతి జీయర్ మఠం స్థాపన",
        "1843 నుంచి 1933 వరకు హథీరామ్‌జీ మఠం పాలన",
        "రోజు ప్రారంభం సుప్రభాతం, తోమాల సేవతో",
    ), ("tirumala secrets", "tirumala temple facts", "venkateswara swamy secrets", "tirupati balaji", "తిరుమల రహస్యాలు", "శ్రీవారి విశేషాలు")),
)


def used_and_next(used: list[str]) -> Temple | None:
    return next((t for t in TEMPLES if t.slug not in used), None)


def left(used: list[str]) -> int:
    return sum(1 for t in TEMPLES if t.slug not in used)


def build(t: Temple, today: dt.date) -> RequestShort:
    cal.PLAYLIST_LINES["secrets"] = PLAYLIST_LINE
    lines = list(t.points)
    slides = (Slide("points", 16.0, t.te, "\n".join(lines)),)   # one card
    title = f"{t.te} | {len(lines)} నిజాలు | {t.en} Secrets in Telugu"
    title_en = f"{t.en} Secrets: {len(lines)} Facts Every Devotee Should Know"
    desc_te = f"🙏 {t.te}\n\n" + "\n".join(f"• {x}" for x in lines) + f"\n\n{DISCLAIMER_TE}"
    desc_en = f"{t.en}: {len(lines)} lesser-known facts, history and traditions, in Telugu.\n{DISCLAIMER_EN}"
    tags = [x for x in t.tags if x.isascii()] + ["temple secrets telugu", "telugu devotional", "temple history telugu"]   # ASCII only: YouTube rejected the Telugu-script tags ("invalidTags")
    hashtags = ["#Shorts", "#TempleSecrets", f"#{t.slug.title()}", "#Telugu", "#Devotional"]
    spec = cal._common(f"secrets_{t.slug}", t.god, slides, title, title_en, desc_te, desc_en, tags, hashtags,
                       t.en, "secrets", today)
    return spec
