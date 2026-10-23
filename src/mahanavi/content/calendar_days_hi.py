"""Hindi calendar Shorts for Devotional Trance Beats (and Divine Mantra Sangam): "kal ka vishesh" (do / don't), the monthly
festival list and the monthly vrat calendar (Ekadashi, Pradosh, Sankashti ...). Same engine as calendar_days.py (Telugu):
vratas come from the real Swiss-Ephemeris tithi (Hyderabad sunrise, a close match for most of India), festivals are a curated list
for North Indian dates (refresh yearly; a warning is printed once the list runs out). One card per Short, public only.
Festival dates checked against a published 2026 calendar: Dhanteras 6 Nov, Diwali 8 Nov, Govardhan Puja 9 Nov,
Bhai Dooj 11 Nov, Chhath 15 Nov, Dev Uthani Ekadashi 20 Nov, Kartik Purnima 24 Nov.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from mahanavi.content.beej_mantras import CHANNELS, DEITIES, MONTH_NAME, WEEKDAY_NAME, _TRANCE_FOOTER
from mahanavi.content.calendar_days import _dedupe_spans, computed
from mahanavi.content.request_shorts import _HI_FOOTER, RequestShort, Slide

CATEGORIES = ("tomorrow", "festivals", "vratas")


@dataclass(frozen=True)
class ObsHi:
    key: str
    hi: str
    en: str
    god: str
    photo: str
    why: str
    dos: tuple[str, str, str]
    donts: tuple[str, str, str]
    tags: tuple[str, ...] = ()


OBS: dict[str, ObsHi] = {o.key: o for o in (
    ObsHi("ekadashi", "एकादशी", "Ekadashi", "vishnu", "vishnu", "भगवान विष्णु का प्रिय एकादशी व्रत",
          ("व्रत या फलाहार रखें", "विष्णु सहस्रनाम का पाठ करें", "तुलसी दल से भगवान विष्णु की पूजा करें"),
          ("चावल और अनाज न खाएँ", "दिन में न सोएँ", "लहसुन, प्याज और मांसाहार न खाएँ"),
          ("ekadashi kab hai", "ekadashi vrat niyam", "एकादशी व्रत", "vishnu sahasranamam")),
    ObsHi("pradosham", "प्रदोष व्रत", "Pradosh Vrat", "shiva", "shiva", "संध्या के समय शिव पूजा का विशेष प्रदोष काल",
          ("शाम को शिव मंदिर में दर्शन करें", "शिवलिंग पर जल, दूध और बेलपत्र चढ़ाएँ", "ॐ नमः शिवाय का जाप करें"),
          ("संध्या समय सोएँ नहीं", "मांस और मदिरा से दूर रहें", "क्रोध और झगड़े से बचें"),
          ("pradosh vrat", "pradosh vrat kab hai", "प्रदोष व्रत", "shiv bhajan")),
    ObsHi("sankashti", "संकष्टी चतुर्थी", "Sankashti Chaturthi", "ganesha", "ganesha", "गणपति को प्रिय संकष्टी चतुर्थी",
          ("गणपति को दूर्वा और लाल फूल चढ़ाएँ", "संकष्टहर गणपति स्तोत्र पढ़ें", "चंद्र दर्शन के बाद पूजा कर व्रत खोलें"),
          ("चंद्रोदय से पहले भोजन न करें", "लहसुन और प्याज न खाएँ", "मांसाहार न करें"),
          ("sankashti chaturthi", "sankashti chaturthi kab hai", "संकष्टी चतुर्थी", "ganesh bhajan")),
    ObsHi("shivaratri", "मासिक शिवरात्रि", "Masik Shivaratri", "shiva", "shiva", "हर महीने आने वाली शिवरात्रि का व्रत",
          ("शिवलिंग का अभिषेक करें", "बेलपत्र अर्पित करें", "रात में शिव नाम का स्मरण करें"),
          ("मांस और मदिरा से दूर रहें", "व्यर्थ समय न गँवाएँ", "क्रोध और झगड़े से बचें"),
          ("masik shivratri", "masik shivratri kab hai", "मासिक शिवरात्रि", "om namah shivaya")),
    ObsHi("purnima", "पूर्णिमा", "Purnima", "lakshmi", "lakshmi", "सत्यनारायण व्रत के लिए शुभ पूर्णिमा",
          ("सत्यनारायण कथा करें", "चंद्रमा को जल या दूध अर्पित करें", "दान-पुण्य करें"),
          ("मांस और मदिरा से दूर रहें", "किसी का अपमान न करें", "तामसिक भोजन न करें"),
          ("purnima kab hai", "purnima vrat", "पूर्णिमा व्रत", "satyanarayan katha")),
    ObsHi("amavasya", "अमावस्या", "Amavasya", "shiva", "shiva", "पितरों को याद करने की अमावस्या",
          ("पितरों के लिए तर्पण करें", "जरूरतमंदों को भोजन कराएँ", "घर में दीपक जलाएँ"),
          ("नए काम की शुरुआत न करें", "बाल और नाखून न काटें", "मांसाहार न करें"),
          ("amavasya kab hai", "amavasya upay", "अमावस्या", "pitru tarpan")),
    # curated festivals
    ObsHi("dhanteras", "धनतेरस", "Dhanteras", "lakshmi", "lakshmi", "धन्वंतरि और लक्ष्मी-कुबेर पूजन, दिवाली का पहला दिन",
          ("शाम को धन्वंतरि और लक्ष्मी-कुबेर की पूजा करें", "घर के बाहर यम दीपक जलाएँ", "बर्तन या सोना-चाँदी शगुन के रूप में खरीदें"),
          ("शाम को घर में अंधेरा न रखें", "उधार लेन-देन न करें (परंपरा)", "चाकू जैसी तेज़ धार की चीज़ें न खरीदें (परंपरा)"),
          ("dhanteras kab hai", "dhanteras puja vidhi", "धनतेरस पूजा", "dhanteras 2026")),
    ObsHi("diwali", "दीपावली", "Deepavali", "lakshmi", "lakshmi", "दीपों का पर्व, लक्ष्मी-गणेश पूजन",
          ("प्रदोष काल में लक्ष्मी-गणेश की पूजा करें", "घर की सफ़ाई कर दीपक और रंगोली सजाएँ", "बड़ों के चरण छूकर मिठाई बाँटें"),
          ("शाम को घर में अंधेरा न रखें", "पटाखे सावधानी से जलाएँ", "विवाद और कड़वे बोल से बचें"),
          ("diwali puja vidhi", "lakshmi puja", "दीपावली लक्ष्मी पूजा", "diwali 2026")),
    ObsHi("govardhan", "गोवर्धन पूजा", "Govardhan Puja", "krishna", "krishna", "श्रीकृष्ण द्वारा गोवर्धन पर्वत उठाने की याद का पर्व",
          ("गोबर से गोवर्धन बनाकर पूजा करें", "अन्नकूट का भोग लगाएँ", "गौ माता की सेवा करें"),
          ("भोजन का अपमान न करें", "मांसाहार न करें", "पूजा में जल्दबाज़ी न करें"),
          ("govardhan puja", "govardhan puja vidhi", "गोवर्धन पूजा", "annakut")),
    ObsHi("bhaidooj", "भाई दूज", "Bhai Dooj", "lakshmi", "lakshmi", "भाई-बहन के प्रेम का पर्व",
          ("बहन भाई को तिलक लगाकर आरती करे", "भाई बहन को उपहार दे", "यमराज और यमुना जी का स्मरण करें"),
          ("बहन के घर खाली हाथ न जाएँ", "भाई-बहन आपस में विवाद न करें", "तामसिक भोजन न करें"),
          ("bhai dooj", "bhai dooj tilak time", "भाई दूज", "bhaiya dooj")),
    ObsHi("chhath", "छठ पूजा (संध्या अर्घ्य)", "Chhath Puja", "surya", "surya", "सूर्य देव और छठी मैया की उपासना का महापर्व",
          ("संध्या अर्घ्य के समय जल में खड़े होकर सूर्य को अर्घ्य दें", "शुद्धता और सात्विक भोजन का पालन करें", "ठेकुआ और फल का प्रसाद चढ़ाएँ"),
          ("पूजा सामग्री को जूठा न करें", "लहसुन, प्याज और मांसाहार से दूर रहें", "अर्घ्य के समय देर न करें"),
          ("chhath puja", "chhath puja vidhi", "छठ पूजा", "chhath geet")),
    ObsHi("devuthani", "देवउठनी एकादशी", "Dev Uthani Ekadashi", "vishnu", "vishnu", "भगवान विष्णु के जागने का दिन (20 या 21 नवंबर, अपना पंचांग देखें)",
          ("भगवान विष्णु को जगाने के मंत्र पढ़ें", "तुलसी विवाह करें", "व्रत रखकर दीपदान करें"),
          ("चावल न खाएँ", "दिन में न सोएँ", "लहसुन, प्याज और मांसाहार न खाएँ"),
          ("dev uthani ekadashi", "tulsi vivah", "देवउठनी एकादशी", "dev uthani ekadashi puja vidhi")),
    ObsHi("kartik_purnima", "कार्तिक पूर्णिमा", "Kartik Purnima", "shiva", "shiva", "देव दीपावली और पवित्र स्नान की कार्तिक पूर्णिमा",
          ("पवित्र नदी में या घर पर स्नान करें", "दीपदान करें", "सत्यनारायण कथा और दान करें"),
          ("मांस और मदिरा से दूर रहें", "किसी का अपमान न करें", "पूजा और स्नान में आलस न करें"),
          ("kartik purnima", "dev diwali", "कार्तिक पूर्णिमा", "kartik purnima snan")),
)}

# curated 2026 festival dates -> key (extend each year; a warning is printed when this list runs out)
FESTIVALS: dict[dt.date, str] = {
    dt.date(2026, 11, 6): "dhanteras",
    dt.date(2026, 11, 8): "diwali",
    dt.date(2026, 11, 9): "govardhan",
    dt.date(2026, 11, 11): "bhaidooj",
    dt.date(2026, 11, 15): "chhath",
    dt.date(2026, 11, 20): "devuthani",
    dt.date(2026, 11, 24): "kartik_purnima",
}
FESTIVALS_END = max(FESTIVALS)
PRIORITY = ["dhanteras", "diwali", "govardhan", "bhaidooj", "chhath", "devuthani", "kartik_purnima", "ekadashi", "pradosham",
            "sankashti", "shivaratri", "purnima", "amavasya"]
VRATAS = ("ekadashi", "pradosham", "sankashti", "shivaratri", "purnima", "amavasya")
FESTIVAL_KEYS = tuple(FESTIVALS.values())
_REPLACES = {"diwali": ("amavasya",), "kartik_purnima": ("purnima",), "devuthani": ("ekadashi",)}


def observances(d: dt.date) -> list[str]:
    keys = [FESTIVALS[d]] if d in FESTIVALS else []
    keys += _dedupe_spans(d, [k for k in computed(d) if k in OBS])
    for f in list(keys):
        keys = [k for k in keys if k not in _REPLACES.get(f, ())]
    return sorted(dict.fromkeys(keys), key=PRIORITY.index)


def stale(d: dt.date) -> bool:
    return d > FESTIVALS_END


def next_special(after: dt.date) -> tuple[dt.date, list[str]] | None:
    day = after + dt.timedelta(days=1)
    obs = observances(day)
    return (day, obs) if obs else None


def month_items(year: int, month: int, kinds: tuple[str, ...]) -> list[tuple[dt.date, str]]:
    d = dt.date(year, month, 1)
    out: list[tuple[dt.date, str]] = []
    while d.month == month:
        for k in observances(d):
            if k in kinds:
                out.append((d, k))
        d += dt.timedelta(days=1)
    return out


# ---------------------------------------------------------------------------------------------------- building
DISCLAIMER = "तिथियाँ हैदराबाद के सूर्योदय पंचांग के अनुसार हैं। अपने स्थानीय पंचांग या पंडित जी से भी पुष्टि करें 🙏"
DISCLAIMER_EN = "Dates follow the Hyderabad sunrise panchang. Please also check your local panchang or priest."
CTA = ("आने वाले सभी व्रत और त्योहार जानने के लिए चैनल को सब्सक्राइब करें", "हर व्रत और त्योहार की तारीख़ पहले से जानें")
BASE_TAGS = ["hindu calendar", "hindu festivals", "vrat calendar", "panchang hindi", "sanatana dharma", "हिंदू त्योहार", "व्रत त्योहार", "shorts"]
PLAYLIST_TITLES = {
    "tomorrow": ("कल का विशेष | क्या करें, क्या न करें | Tomorrow's Festival Do's and Don'ts (Hindi)",
                 "कल कौन सा व्रत या त्योहार है? क्या करें, क्या न करें? हर विशेष दिन से एक दिन पहले शाम को।\n"
                 "Tomorrow's festival or vrat in Hindi with simple do's and don'ts: Ekadashi, Pradosh, Sankashti, Purnima, Amavasya."),
    "festivals": ("त्योहार कैलेंडर 2026 | Hindu Festival Calendar (Hindi)",
                  "हर महीने के त्योहारों की तारीख़ें पहले से जानें।\nMonth-wise Hindu festival dates: Dhanteras, Diwali, Bhai Dooj, Dev Uthani Ekadashi and more."),
    "vratas": ("एकादशी प्रदोष संकष्टी कैलेंडर | Vrat Calendar (Hindi)",
               "हर महीने एकादशी, प्रदोष, संकष्टी चतुर्थी, पूर्णिमा, अमावस्या की तारीख़ें।\nMonthly Ekadashi, Pradosh, Sankashti Chaturthi, Purnima and Amavasya dates in Hindi."),
}
PLAYLIST_LABELS = {"tomorrow": "कल का विशेष", "festivals": "त्योहार कैलेंडर", "vratas": "व्रत कैलेंडर"}
PLAYLIST_LINES = {
    "tomorrow": "ऐसे और कल के विशेष एक ही जगह!\nडिस्क्रिप्शन में प्लेलिस्ट लिंक\nदिए हैं, कृपया ज़रूर देखें",
    "festivals": "सभी त्योहारों की तारीख़ें एक ही जगह!\nडिस्क्रिप्शन में प्लेलिस्ट लिंक\nदिए हैं, कृपया ज़रूर देखें",
    "vratas": "सभी व्रतों की तारीख़ें एक ही जगह!\nडिस्क्रिप्शन में प्लेलिस्ट लिंक\nदिए हैं, कृपया ज़रूर देखें",
}


def playlist_ids(youtube) -> dict[str, str]:
    from channels.engine import upload

    return {cat: upload.find_or_create_playlist(youtube, t, d, "hi") for cat, (t, d) in PLAYLIST_TITLES.items()}


def playlist_block(youtube, current: str) -> str:
    try:
        ids = playlist_ids(youtube)
    except Exception:  # noqa: BLE001
        return ""
    order = [current] + [c for c in CATEGORIES if c != current]
    return "▶ प्लेलिस्ट (Playlists):\n" + "\n".join(
        f"{'▶' if c == current else '•'} {PLAYLIST_LABELS[c]}: https://www.youtube.com/playlist?list={ids[c]}" for c in order if c in ids)


def _wd(d: dt.date) -> str:
    return WEEKDAY_NAME[d.weekday()][1].removesuffix("वार")


def _short_date(d: dt.date) -> str:
    return f"{d.day} {MONTH_NAME[d.month - 1][1]}"


def _long_date(d: dt.date) -> str:
    return f"{WEEKDAY_NAME[d.weekday()][1]} · {d.day} {MONTH_NAME[d.month - 1][1]} {d.year}"


def _common(channel: str, slug: str, obs: ObsHi, slides, title: str, title_en: str, desc: str, desc_en: str,
            tags: list[str], hashtags: list[str], header: str, category: str, photo_day: dt.date) -> RequestShort:
    from mahanavi.content.beej_mantras import _photo_for

    cfg = CHANNELS[channel]
    dei = DEITIES[obs.god] if obs.god in DEITIES else DEITIES["vishnu"]
    top, mid, bottom, glow = dei.palette
    tags = [t for t in dict.fromkeys(tags + BASE_TAGS) if len(t) <= 30]
    while sum(len(t) + (2 if " " in t else 0) + 1 for t in tags) > 440:
        tags.pop(-2)
    footer = _HI_FOOTER if channel == "mantra_sangam" else _TRANCE_FOOTER
    footer_en = ("Divine Mantra Sangam is a Hindi devotional channel: daily Rahu Kaal, Shubh Muhurat, mantras and Purana stories."
                 if channel == "mantra_sangam" else "Devotional Trance Beats: Hindi devotional mantras, bhajans and kirtan.")
    return RequestShort(
        slug=slug, handle="", comment_id="", deity_te=obs.hi, bg_top=top, bg_mid=mid, bg_bottom=bottom, glow=glow,
        slides=slides, title=title[:99] + ("…" if len(title) > 100 else ""), title_en=title_en[:100],
        description_te=desc, description_en=desc_en, hashtags=hashtags, tags=tags,
        bg_image=_photo_for(dei.key, photo_day), lang="hi", token_file=cfg["token_file"], expected_channel=cfg["expected"],
        watermark=cfg["watermark"], header=header, tag_footer=CTA[0], cta_lines=CTA,
        playlist_line=PLAYLIST_LINES[category], footer_main=footer, footer_en=footer_en)


def build_tomorrow(channel: str, day: dt.date, keys: list[str]) -> RequestShort:
    o = OBS[keys[0]]
    others = [OBS[k].hi for k in keys[1:]]
    name = o.hi + (f" + {', '.join(others)}" if others else "")
    en = o.en + (f" + {', '.join(OBS[k].en for k in keys[1:])}" if others else "")
    body = [name, o.why, *(f"करें: {x}" for x in o.dos), *(f"न करें: {x}" for x in o.donts)]
    slides = (Slide("points", 16.0, f"कल का विशेष · {_short_date(day)}", "\n".join(body)),)   # one card
    title = f"कल {name} {_short_date(day)}: क्या करें, क्या न करें | {en} Niyam"
    title_en = f"Tomorrow {en} ({day.day} {day.strftime('%b')}): Do's and Don'ts in Hindi"
    desc = (f"🙏 कल ({_long_date(day)}): {name}\n{o.why}\n\n✅ क्या करें:\n" + "\n".join(f"• {x}" for x in o.dos)
            + "\n\n❌ क्या न करें:\n" + "\n".join(f"• {x}" for x in o.donts) + f"\n\n{DISCLAIMER}")
    desc_en = f"Tomorrow, {day.strftime('%A %d %B %Y')}: {en}. Simple do's and don'ts in Hindi.\n{DISCLAIMER_EN}"
    tags = [o.en.lower(), f"{o.en.lower()} {day.year}", f"{o.en.lower()} date", f"{o.en.lower()} hindi", *o.tags, o.hi]
    hashtags = ["#Shorts", f"#{o.en.split()[0]}", "#HinduCalendar", "#Devotional", "#Hindi"]
    return _common(channel, f"cal_tomorrow_{day.isoformat()}", o, slides, title, title_en, desc, desc_en, tags, hashtags,
                   _long_date(day), "tomorrow", day)


def _list_post(channel: str, year: int, month: int, kinds: tuple[str, ...], category: str, heading: str, cover: str,
               title_tail: str, en: str, override: list[str] | None = None) -> RequestShort:
    items = month_items(year, month, kinds)
    mname = MONTH_NAME[month - 1][1]
    lines = list(override) if override else [f"{d.day} {mname} ({_wd(d)}) · {OBS[k].hi}" for d, k in items]
    slides = (Slide("points", 14.0, f"{mname} {year} {heading}", "\n".join(lines) if lines else "इस महीने कोई विशेष तिथि नहीं"),)  # one card
    title = f"{mname} {year} {title_tail} | {en}"
    title_en = f"{en} - {dt.date(year, month, 1).strftime('%B %Y')} Hindi Calendar"
    desc = f"🙏 {mname} {year} {heading}:\n\n" + "\n".join(f"• {ln}" for ln in lines) + f"\n\n{DISCLAIMER}"
    desc_en = f"{en} for {dt.date(year, month, 1).strftime('%B %Y')} in Hindi.\n{DISCLAIMER_EN}"
    tags = [en.lower(), f"{en.lower()} {year}", f"{mname} {year}", f"{dt.date(year, month, 1).strftime('%B').lower()} {year} festivals",
            "hindu calendar 2026", "ekadashi dates", "pradosh dates", "sankashti dates", "एकादशी कब है", "त्योहार कब है"]
    hashtags = ["#Shorts", "#HinduCalendar", f"#{en.split()[0]}", "#Panchang", "#Hindi"]
    return _common(channel, f"cal_{category}_{year}-{month:02d}", OBS[cover], slides, title, title_en, desc, desc_en, tags, hashtags,
                   f"{mname} {year}", category, dt.date(year, month, 1))


# Whole month on one card: festivals and the main vratas (owner request 2026-10-23). Curated per month; a month without
# an entry falls back to the computed festival list. Devuthani Ekadashi follows the Smarta day (Nov 20), Tulsi Vivah Nov 21.
FULL_MONTH: dict[tuple[int, int], list[str]] = {
    (2026, 11): [
        "5 नवंबर · रमा एकादशी",
        "6 नवंबर · धनतेरस",
        "7 नवंबर · मासिक शिवरात्रि",
        "8 नवंबर · नरक चतुर्दशी, दिवाली",
        "9 नवंबर · अमावस्या, गोवर्धन पूजा",
        "11 नवंबर · भाई दूज",
        "15 नवंबर · छठ पूजा (संध्या अर्घ्य)",
        "20 नवंबर · देवउठनी एकादशी",
        "21 नवंबर · तुलसी विवाह",
        "24 नवंबर · कार्तिक पूर्णिमा, देव दिवाली",
        "27 नवंबर · संकष्टी चतुर्थी",
    ],
}


def build_festivals(channel: str, year: int, month: int) -> RequestShort:
    items = month_items(year, month, FESTIVAL_KEYS)
    cover = items[0][1] if items else "diwali"
    return _list_post(channel, year, month, FESTIVAL_KEYS, "festivals", "के त्योहार", cover,
                      "के त्योहार: धनतेरस, दिवाली, भाई दूज, देवउठनी एकादशी", "Festival Calendar",
                      FULL_MONTH.get((year, month)))


def build_vratas(channel: str, year: int, month: int) -> RequestShort:
    return _list_post(channel, year, month, VRATAS, "vratas", "व्रत तारीख़ें", "ekadashi",
                      "एकादशी, प्रदोष, संकष्टी, पूर्णिमा, अमावस्या तिथियाँ", "Vrat Calendar")
