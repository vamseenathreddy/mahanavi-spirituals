"""Ramana Maharshi TV: "upcoming at Arunachala" Shorts, posted 20 days before each event (owner request 2026-10-24).

One card per event: date, occasion and what is special about it. Dates were checked against published sources:
Karthigai Deepam 24 Nov 2026 (drikpanchang), Sri Ramana Jayanti 25 Dec 2026, the 147th (hindu-blog.com; the Jayanti follows the Punarvasu
star in Margazhi), the 10-day Kartikai Deepam festival at Sri Ramanasramam (archive.arunachala.org events page). Pournami and
Maha Shivaratri dates come from the repo's Swiss-Ephemeris tithi engine (Hyderabad sunrise); Girivalam timings vary by hours, so every
card says to check the temple notice. Ramana Aradhana 2027 is not listed until its date is confirmed from the ashram calendar.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from mahanavi.content.beej_mantras import MONTH_NAME, WEEKDAY_NAME
from mahanavi.content.request_shorts import RequestShort, Slide

LEAD_DAYS = 20
CATCHUP_DAYS = 3            # a missed day is still posted for up to 3 days after the 20-day mark
PLAYLIST_TITLE = "Arunachala Upcoming Events & Festivals | అరుణాచలం రాబోయే విశేషాలు | Ramana Maharshi TV"
PLAYLIST_DESC = ("Upcoming festivals and special days at Arunachala (Tiruvannamalai) and Sri Ramanasramam, posted 20 days ahead: "
                 "Karthigai Deepam, Girivalam Pournami, Maha Shivaratri and Sri Ramana Jayanti, with date and speciality.\n\n"
                 "అరుణాచలం (తిరువణ్ణామలై) మరియు శ్రీ రమణాశ్రమంలో రాబోయే ఉత్సవాలు, 20 రోజులు ముందుగా.")
MAIN_PLAYLIST_TITLE = "Ramana Maharshi Teachings, Quotes & Self Enquiry (Who Am I?) | రమణ మహర్షి బోధనలు | Ramana Maharshi TV"
CHECK = "గిరి ప్రదక్షిణ సమయాలు ఆలయ ప్రకటన ప్రకారం చూడండి"

_PROD = ("ఈ వివరాలు ప్రచురిత పంచాంగాల ఆధారంగా ఇచ్చాం. అరుణాచల ఆలయం, శ్రీ రమణాశ్రమం ప్రకటనలను కూడా చూడండి 🙏")
_PROD_EN = "Dates follow published panchangs. Please also check the Arunachaleswara temple and Sri Ramanasramam notices."


@dataclass(frozen=True)
class Event:
    slug: str
    date: dt.date
    te: str
    en: str
    special: tuple[str, ...]        # Telugu lines
    special_en: str


GIRI = ("పౌర్ణమి రోజున అరుణాచల గిరి ప్రదక్షిణ (సుమారు 14 కి.మీ.) అత్యంత శ్రేష్ఠం",
        "అరుణాచల కొండ శివుని అగ్ని లింగ స్వరూపం",
        "చాలామంది రాత్రి పూట చెప్పులు లేకుండా నడుస్తారు",
        CHECK)
GIRI_EN = ("Girivalam, the roughly 14 km walk around Arunachala hill, is considered most auspicious on Pournami, "
           "the full moon day. The hill is revered as Shiva in the form of fire.")


def _p(y: int, m: int, d: int) -> Event:
    day = dt.date(y, m, d)
    name = MONTH_NAME[m - 1][0]
    return Event(f"pournami-{day.isoformat()}", day, f"{name} పౌర్ణమి గిరి ప్రదక్షిణ", f"{day.strftime('%B')} Pournami Girivalam", GIRI, GIRI_EN)


EVENTS: tuple[Event, ...] = (
    Event("deepam-2026", dt.date(2026, 11, 24), "కార్తిక దీపం · అరుణాచల మహాదీపం", "Karthigai Deepam (Maha Deepam)",
          ("కృత్తిక నక్షత్రం రోజున సాయంత్రం కొండ శిఖరంపై మహాదీపం వెలిగిస్తారు",
           "ఉదయం భరణి దీపంతో ఉత్సవం మొదలవుతుంది",
           "దీపం అగ్ని స్వరూపుడైన అరుణాచలేశ్వరునికి ప్రతీక",
           "శ్రీ రమణాశ్రమంలో పది రోజుల ఉత్సవం, భక్తులు గిరి ప్రదక్షిణ చేస్తారు"),
          "On Karthigai Nakshatram evening the Maha Deepam is lit on top of Arunachala hill, with Bharani Deepam at dawn. "
          "It symbolises Arunachaleswara as fire; Sri Ramanasramam holds a ten day festival."),
    Event("jayanti-2026", dt.date(2026, 12, 25), "శ్రీ రమణ మహర్షి 147వ జయంతి", "Sri Ramana Maharshi 147th Jayanti",
          ("మార్గళి మాసంలో పునర్వసు నక్షత్రం రోజున భగవాన్ జయంతి",
           "భగవాన్ 1879లో తిరుచ్చుళిలో జన్మించారు",
           "శ్రీ రమణాశ్రమంలో ప్రత్యేక పూజలు, పారాయణం",
           "ప్రపంచవ్యాప్తంగా ఆశ్రమాల్లో లైవ్ కార్యక్రమాలు"),
          "Bhagavan's birth anniversary falls on the Punarvasu star in the month of Margazhi. Special puja and parayanam are held at "
          "Sri Ramanasramam and streamed live worldwide."),
    _p(2026, 12, 24), _p(2027, 1, 22), _p(2027, 2, 20),
    Event("shivaratri-2027", dt.date(2027, 3, 6), "మహా శివరాత్రి · అరుణాచలం", "Maha Shivaratri at Arunachala",
          ("అరుణాచలం శివుని అగ్ని లింగ క్షేత్రం (పంచభూత క్షేత్రాల్లో అగ్ని)",
           "అరుణాచలేశ్వర ఆలయంలో రాత్రంతా జాగరణ, పూజలు",
           "చాలామంది భక్తులు ఉపవాసం ఉండి గిరి ప్రదక్షిణ చేస్తారు",
           "శ్రీ రమణాశ్రమంలో కూడా శివరాత్రి పూజ"),
          "Arunachala is the fire lingam among the Pancha Bhoota Kshetras. Night long vigil and puja at the temple, and many devotees fast and do Girivalam."),
    _p(2027, 3, 22),
    Event("chitra-2027", dt.date(2027, 4, 20), "చిత్రా పౌర్ణమి గిరి ప్రదక్షిణ", "Chitra Pournami Girivalam", GIRI, GIRI_EN),
    _p(2027, 5, 20), _p(2027, 6, 18), _p(2027, 7, 18), _p(2027, 8, 17), _p(2027, 9, 15), _p(2027, 10, 15),
)


def due(today: dt.date, done: list[str] | tuple[str, ...] = ()) -> Event | None:
    """The soonest event whose 20-day mark has arrived (never one already past) and is not posted yet."""
    for e in sorted(EVENTS, key=lambda x: x.date):
        mark = e.date - dt.timedelta(days=LEAD_DAYS)
        if e.slug not in done and mark <= today <= mark + dt.timedelta(days=CATCHUP_DAYS):
            return e
    return None


def stale(today: dt.date) -> bool:
    return max(e.date for e in EVENTS) < today + dt.timedelta(days=60)


def _long(d: dt.date) -> str:
    return f"{WEEKDAY_NAME[d.weekday()][0]} · {d.day} {MONTH_NAME[d.month - 1][0]} {d.year}"


def build(e: Event, today: dt.date) -> RequestShort:
    days = (e.date - today).days
    root = Path(__file__).resolve().parents[3] / "ramana" / "assets" / "backgrounds"
    photos = sorted(root.glob("photo_*.jpg"))
    bg = str(photos[e.date.toordinal() % len(photos)]) if photos else ""
    body = [e.te, f"{days} రోజుల్లో", *e.special]
    slides = (Slide("points", 16.0, "అరుణాచలం · రాబోయే విశేషం", "\n".join(body)),)
    title = f"{e.te} {e.date.day} {MONTH_NAME[e.date.month - 1][0]}: విశేషం | {e.en} {e.date.year} | Arunachala"
    title_en = f"{e.en}: {e.date.strftime('%d %B %Y')} at Arunachala Tiruvannamalai"
    desc = (f"🙏 {e.te}\n📅 {_long(e.date)} ({days} రోజుల్లో)\n\n" + "\n".join(f"• {x}" for x in e.special) + f"\n\n{_PROD}")
    desc_en = f"{e.en} on {e.date.strftime('%A %d %B %Y')} at Arunachala, Tiruvannamalai.\n{e.special_en}\n{_PROD_EN}"
    tags = [e.en.lower(), "arunachala", "tiruvannamalai", "girivalam", "ramana maharshi", "ramanasramam", "అరుణాచలం", "తిరువణ్ణామలై",
            "కార్తిక దీపం" if "deepam" in e.slug else "గిరి ప్రదక్షిణ", f"arunachala {e.date.year}", "shorts"]
    hashtags = ["#Shorts", "#Arunachala", "#Tiruvannamalai", "#RamanaMaharshi", "#అరుణాచలం"]
    return RequestShort(
        slug=f"arunachala_{e.slug}", handle="", comment_id="", deity_te="అరుణాచలం", bg_top=(20, 12, 8), bg_mid=(60, 30, 14),
        bg_bottom=(12, 8, 6), glow=(255, 170, 60), slides=slides, title=title[:100], description_te=desc, description_en=desc_en,
        title_en=title_en[:100], hashtags=hashtags, tags=tags, lang="te", token_file="youtube_token_ramana.json",
        expected_channel="Ramana", watermark="@RamanaMaharshiTV", header=_long(e.date), bg_image=bg,
        playlist_line="అరుణాచల విశేషాలన్నీ ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్ ఉంది",
        footer_main="రమణ మహర్షి TV: శ్రీ రమణ మహర్షి బోధనలు, ఆత్మ విచారణ మరియు అరుణాచల విశేషాలు.",
        footer_en="Ramana Maharshi TV: teachings, Self-enquiry and Arunachala.",
        cta_lines=("అరుణాచల విశేషాల కోసం ఛానల్ సబ్‌స్క్రైబ్ చేయండి", "రాబోయే ఉత్సవాలు 20 రోజులు ముందే తెలుసుకోండి"),
        tag_footer="")
