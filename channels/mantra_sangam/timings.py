"""Daily Hindi timing Shorts for Channel B: Rahu Kaal, Shubh Muhurat, Durmuhurat.

Hindi version of Channel A' three daily timing Shorts. The times are computed locally
with the Swiss Ephemeris (mahanavi.panchang.local_provider), so no Panchang API and no quota is
used. Times are computed for New Delhi coordinates, but no city name is shown anywhere (owner request 2026-10-20).
"""
from datetime import date, timedelta

from mahanavi.panchang.local_provider import DELHI, LocalPanchangProvider

LOCATION_NAME_HI, LOCATION_NAME_EN = "दिल्ली", "New Delhi"
LOCATION = DELHI

KINDS = ("rahu", "shubh", "durm")
WEEKDAY_HI = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
WEEKDAY_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
# the day's deity and mantra (Mon Shiva ... Sun Surya)
DEITY_MANTRA = [
    ("शिव", "ॐ नमः शिवाय"),
    ("हनुमान", "ॐ हनुमते नमः"),
    ("गणेश", "ॐ गं गणपतये नमः"),
    ("विष्णु", "ॐ नमो भगवते वासुदेवाय"),
    ("लक्ष्मी", "ॐ श्रीं महालक्ष्म्यै नमः"),
    ("शनि", "ॐ शं शनैश्चराय नमः"),
    ("सूर्य", "ॐ घृणिः सूर्याय नमः"),
]
# Engagement questions (must differ from OPINION, the subscribe line, which sits on the card too).
COMMENT_PROMPTS = {
    "rahu": ["आज आप कौन सा काम राहु काल के बाद शुरू करेंगे? कमेंट में बताएं",
             "क्या आप राहु काल मानते हैं? कमेंट में हाँ या ना लिखें",
             "इस समय का इंतज़ार किसे है? कमेंट में जय श्री राम लिखें"],
    "shubh": ["आज आप कौन सा शुभ काम शुरू करने वाले हैं? कमेंट में बताएं",
              "इस शुभ समय में पूजा करेंगे? कमेंट में 🙏 लिखें",
              "आज का शुभ मुहूर्त अपने परिवार को शेयर करें"],
    "durm": ["आज आप कौन सा काम इस समय के बाद करेंगे? कमेंट में बताएं",
             "क्या आप दुर्मुहूर्त का ध्यान रखते हैं? कमेंट में बताएं",
             "यह जानकारी अपने परिवार को शेयर करें"],
}
CTA = {"rahu": "रोज़ राहु काल जानने के लिए सब्सक्राइब करें",
       "shubh": "रोज़ शुभ मुहूर्त जानने के लिए सब्सक्राइब करें",
       "durm": "रोज़ दुर्मुहूर्त जानने के लिए सब्सक्राइब करें"}
OPINION = "अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे"


def tithi_hi(tithi: str) -> tuple[str, bool]:
    """('शुक्ल सप्तमी', special?) from the provider's English sunrise tithi; special tithis lead the title."""
    from mahanavi.content import beej_mantras as bm

    paksha, key = bm.split_tithi(tithi)
    if not key:
        return "", False
    name = bm.TITHI_NAME[key][1]
    if key in ("purnima", "amavasya"):
        return name, True
    return f"{bm.PAKSHA[paksha][1]} {name}", key in ("ekadashi", "trayodashi", "chaturdashi")


def date_hi(d: date) -> str:
    return f"{d.day} {MONTH_HI[d.month - 1]} {d.year}, {WEEKDAY_HI[d.weekday()]}"


def _other(p) -> str:
    parts = [f"यमगंड: {p.yamagandam}", f"गुलिक काल: {p.gulika_kalam}", f"वर्ज्य: {p.varjyam}"]
    return "  |  ".join(x for x in parts if not x.endswith(": "))


def timing_row(kind: str, d: date) -> dict:
    """One engine content row for the given kind and (IST) date."""
    prov = LocalPanchangProvider(*LOCATION)
    p = prov.fetch(d)
    deity, mantra = DEITY_MANTRA[d.weekday()]
    pick = COMMENT_PROMPTS[kind][d.toordinal() % 3]
    row = {
        "id": f"{kind}-{d.isoformat()}", "category": kind, "special": "", "source": "Local Swiss Ephemeris panchang",
        "text_primary": "", "text_secondary": "",
        "t_date": date_hi(d), "t_place": "",
        "t_mantra_label": f"आज के देव: {deity}", "t_mantra": mantra,
        "t_comment": pick, "t_sub": CTA[kind], "t_opinion": OPINION,
        "weekday_en": WEEKDAY_EN[d.weekday()], "date_iso": d.isoformat(),
        "rahu": p.rahu_kalam, "durm_times": p.durmuhurtham, "abhijit": p.abhijit_muhurtham,
        "brahma": prov.brahma_muhurta(d), "yamagandam": p.yamagandam, "gulika": p.gulika_kalam, "varjyam": p.varjyam,
        "tithi_hi": tithi_hi(p.tithi)[0], "tithi_special": tithi_hi(p.tithi)[1],
    }
    if kind == "rahu":
        row.update(t_title="आज का राहु काल", t_label="समय", t_time=p.rahu_kalam,
                   t_note="इस समय नया शुभ कार्य शुरू न करें", t_other=_other(p))
    elif kind == "shubh":
        if p.abhijit_muhurtham:
            row.update(t_title="आज के शुभ मुहूर्त", t_label="अभिजीत मुहूर्त", t_time=p.abhijit_muhurtham,
                       t_note=f"ब्रह्म मुहूर्त: {row['brahma']}", t_other="")
        else:
            amrit = prov.amrit_chaughadiya(d)
            row.update(t_title="आज के शुभ मुहूर्त", t_label="अमृत चौघड़िया" if amrit else "ब्रह्म मुहूर्त",
                       t_time=amrit or row["brahma"],
                       t_note=f"आज {WEEKDAY_HI[d.weekday()]} है, अभिजीत मुहूर्त नहीं माना जाता", t_other=f"ब्रह्म मुहूर्त: {row['brahma']}")
    else:
        row.update(t_title="आज का दुर्मुहूर्त", t_label="समय", t_time=p.durmuhurtham.replace(", ", "\n"),
                   t_note="इस समय शुभ कार्य टालें", t_other=f"राहु काल: {p.rahu_kalam}  |  यमगंड: {p.yamagandam}")
    return row


def fetch_row_for(kind: str):
    """fetch_row(used_ids) for ChannelPipeline: today's row in IST, once per day."""
    import datetime as dt
    from zoneinfo import ZoneInfo

    def fetch(used_ids):
        today = dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()
        return timing_row(kind, today)
    return fetch
