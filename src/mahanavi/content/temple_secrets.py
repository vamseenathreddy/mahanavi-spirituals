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
    Temple("srisailam", "శ్రీశైలం మల్లికార్జున స్వామి రహస్యాలు", "Srisailam Mallikarjuna Temple", "shivaratri", (
        "12 జ్యోతిర్లింగాల్లో ఒకటి",
        "18 శక్తిపీఠాల్లో ఒకటి: భ్రమరాంబ అమ్మవారు",
        "జ్యోతిర్లింగం, శక్తిపీఠం ఒకే క్షేత్రంలో కొలువు",
        "కృష్ణా నది ఒడ్డున, నల్లమల అడవుల మధ్య ఆలయం",
        "నాగార్జునసాగర్ శ్రీశైలం టైగర్ రిజర్వ్ లోపల క్షేత్రం",
        "శాతవాహనుల కాలం నుంచే శ్రీపర్వత ప్రస్తావన",
        "ప్రాకార గోడలపై పురాణ గాథల చెక్కడాలు",
        "రెండవ హరిహరరాయలు ముఖమండపం కట్టించారు",
        "1667లో ఛత్రపతి శివాజీ గోపురం, ధర్మశాల కట్టించారు",
        "రెడ్డి రాజులు పాతాళగంగ మెట్లు కట్టించారు",
        "మల్లిక (పార్వతి), అర్జున (శివుడు) నుంచి పేరు వచ్చిందని నమ్మకం",
        "శివరాత్రి బ్రహ్మోత్సవాలకు లక్షల మంది భక్తులు",
    ), ("srisailam secrets", "srisailam temple facts", "mallikarjuna swamy jyotirlinga", "bhramaramba shakti peetham", "శ్రీశైలం రహస్యాలు", "మల్లికార్జున స్వామి")),
    Temple("kashi", "కాశీ విశ్వనాథ ఆలయ రహస్యాలు", "Kashi Vishwanath Temple", "shivaratri", (
        "12 జ్యోతిర్లింగాల్లో ఒకటి, గంగా తీరంలో",
        "విశ్వనాథ అంటే విశ్వానికి ప్రభువు",
        "స్కంద పురాణంలోని కాశీ ఖండంలో క్షేత్ర మహిమ",
        "ప్రస్తుత ఆలయం 1780లో అహల్యాబాయి హోల్కర్ కట్టించారు",
        "పంజాబ్ మహారాజా రంజిత్ సింగ్ శిఖరాలకు బంగారం ఇచ్చారు",
        "సుమారు ఒక టన్ను బంగారు తాపడం అని చెబుతారు",
        "1669లో ఆలయం ధ్వంసమై, తర్వాత పునర్నిర్మాణం జరిగింది",
        "2021 డిసెంబర్‌లో కాశీ విశ్వనాథ్ కారిడార్ ప్రారంభం",
        "కారిడార్ గంగా ఘాట్ల నుంచి ఆలయానికి నేరుగా దారి",
        "ఆలయం మణికర్ణికా, లలితా ఘాట్ల దగ్గర",
        "రోజూ ఐదు ఆరతులు: మంగళ నుంచి శయన వరకు",
        "కాశీలో మరణిస్తే మోక్షమని నమ్మకం",
    ), ("kashi vishwanath secrets", "kashi temple facts", "varanasi jyotirlinga", "kashi vishwanath corridor", "కాశీ రహస్యాలు", "కాశీ విశ్వనాథ్")),
    Temple("rameswaram", "రామేశ్వరం ఆలయ రహస్యాలు", "Rameswaram Ramanathaswamy Temple", "shivaratri", (
        "12 జ్యోతిర్లింగాల్లో ఒకటి, చార్‌ధామ్‌లో ఒకటి",
        "శ్రీరాముడు పూజించిన లింగమని నమ్మకం",
        "సీతమ్మ ఇసుకతో చేసిన లింగమని నమ్మకం",
        "హనుమంతుడు తెచ్చిన లింగానికి మొదటి పూజ సంప్రదాయం",
        "ఆలయంలో 22 తీర్థాలు, స్నానం సంప్రదాయం",
        "భారత ఆలయాల్లో పొడవైన ప్రాకార నడవాలు ఇక్కడే",
        "మూడవ ప్రాకారంలో సుమారు 1,212 స్తంభాలు",
        "సేతుపతి రాజులు ప్రాకారాల నిర్మాణం చేయించారు",
        "తమిళనాడులో పాంబన్ ద్వీపంలో ఉంది",
        "పాంబన్ వంతెన ద్వారా ద్వీపానికి చేరుకుంటారు",
        "అగ్ని తీర్థంలో సముద్ర స్నానం ప్రధాన ఆచారం",
        "రామసేతు ప్రారంభంగా నమ్మే ధనుష్కోడి దగ్గర్లో",
    ), ("rameswaram secrets", "rameswaram temple facts", "ramanathaswamy temple", "22 theerthams", "రామేశ్వరం రహస్యాలు", "చార్ ధామ్")),
    Temple("madurai", "మదురై మీనాక్షి ఆలయ రహస్యాలు", "Madurai Meenakshi Amman Temple", "purnima", (
        "మదురై మీనాక్షి అమ్మవారి ఆలయం, వైగై తీరంలో",
        "ఆలయ ప్రాంగణం సుమారు 14 ఎకరాలు",
        "14 గోపురాలు, దక్షిణ గోపురం సుమారు 52 మీటర్లు",
        "ఆయిరంకాల్ మండపంలో సుమారు 985 స్తంభాలు",
        "పొట్రామరై కొలను అంటే బంగారు తామర కొలను",
        "అమ్మవారు మీనాక్షి, స్వామి సుందరేశ్వరుడు",
        "చైత్ర మాసంలో మీనాక్షి తిరుకళ్యాణం, లక్షల మంది భక్తులు",
        "16వ శతాబ్దంలో నాయక రాజులు ప్రస్తుత రూపం ఇచ్చారు",
        "14వ శతాబ్దంలో దాడులతో ఆలయం దెబ్బతింది",
        "గోపురాలపై వేలాది రంగురంగుల బొమ్మలు",
        "సంగీత స్తంభాలు: తట్టితే స్వరాలు వినిపిస్తాయి",
        "రాత్రి సుందరేశ్వరుని పల్లకి అమ్మవారి గదికి వెళ్తుంది",
    ), ("meenakshi temple secrets", "madurai meenakshi facts", "meenakshi amman temple", "madurai temple", "మీనాక్షి ఆలయం", "మదురై రహస్యాలు")),
    Temple("puri", "పూరీ జగన్నాథ ఆలయ రహస్యాలు", "Puri Jagannath Temple", "ekadashi", (
        "చార్‌ధామ్‌లో ఒకటి, ఒడిశా పూరీ తీరంలో",
        "12వ శతాబ్దంలో అనంతవర్మన్ చోడగంగ దేవుడు ప్రారంభించారు",
        "ఆలయ శిఖరం సుమారు 65 మీటర్లు (214 అడుగులు)",
        "శిఖరంపై అష్టధాతు నీలచక్రం",
        "శిఖరంపై జెండాను ప్రతిరోజూ సాయంత్రం మారుస్తారు",
        "జగన్నాథుడు, బలభద్రుడు, సుభద్ర దారు (చెక్క) విగ్రహాలు",
        "నవకళేబరం: 12 నుంచి 19 ఏళ్లకు కొత్త చెక్క విగ్రహాలు",
        "ఏటా ఆషాఢంలో రథయాత్ర, మూడు భారీ రథాలు",
        "మహాప్రసాదం మట్టి కుండల్లో కట్టెల పొయ్యిపై వండుతారు",
        "ఒకదానిపై ఒకటి కుండలు పెట్టి వండే సంప్రదాయం",
        "సింహద్వారం వద్ద 22 మెట్లు (బైసీ పహచ)",
        "ఆనంద బజార్‌లో మహాప్రసాద విక్రయం",
    ), ("puri jagannath secrets", "jagannath temple facts", "jagannath rath yatra", "mahaprasad puri", "జగన్నాథ రహస్యాలు", "పూరీ జగన్నాథ్")),
    Temple("padmanabhaswamy", "పద్మనాభస్వామి ఆలయ రహస్యాలు", "Padmanabhaswamy Temple Thiruvananthapuram", "ekadashi", (
        "తిరువనంతపురం, 108 దివ్యదేశాల్లో ఒకటి",
        "అనంత శయనంలో విష్ణువు, మూడు ద్వారాల నుంచి దర్శనం",
        "విగ్రహం 12,008 సాలగ్రామాలతో చేశారని సంప్రదాయం",
        "అనంతుడు అనే సర్పంపై పవళించిన స్వామి",
        "1750లో మార్తాండ వర్మ రాజ్యాన్ని స్వామికి సమర్పించారు",
        "ట్రావెంకోర్ రాజులు 'పద్మనాభ దాసులు' అయ్యారు",
        "ఏడు అంతస్తుల గోపురం, సుమారు 30 మీటర్లు",
        "2011లో సుప్రీంకోర్టు ఆదేశంతో నేలమాళిగల తనిఖీ",
        "ఆరు నేలమాళిగల్లో B గది ఇంకా తెరవలేదు",
        "పురుషులకు ధోతీ, స్త్రీలకు చీర తప్పనిసరి",
        "2020లో సుప్రీంకోర్టు నిర్వహణ రాజకుటుంబానికి అప్పగించింది",
        "అల్పశి, పైంకుని ఉత్సవాలు ప్రసిద్ధం",
    ), ("padmanabhaswamy temple secrets", "padmanabhaswamy facts", "thiruvananthapuram temple", "anantha padmanabha", "పద్మనాభస్వామి", "తిరువనంతపురం")),
)


# Owner request 2026-11-02: no more Tirumala details in Shorts (the entry stays here, it is just never picked).
PAUSED = {"tirumala"}


def used_and_next(used: list[str]) -> Temple | None:
    return next((t for t in TEMPLES if t.slug not in used and t.slug not in PAUSED), None)


def left(used: list[str]) -> int:
    return sum(1 for t in TEMPLES if t.slug not in used and t.slug not in PAUSED)


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
