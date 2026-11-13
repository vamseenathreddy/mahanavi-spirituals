"""YouTube metadata for the Hindi timing Shorts. Titles mix Hindi with the English term."""
import os

from channels.mantra_sangam import timings

CHANNEL = "Divine Mantra Sangam"
NAMES = {  # (hindi, english)
    "rahu": ("राहु काल", "Rahu Kaal"),
    "shubh": ("शुभ मुहूर्त", "Shubh Muhurat"),
    "durm": ("दुर्मुहूर्त", "Durmuhurat"),
}
# 2026-10-17: titles carry the date, weekday and sunrise tithi plus one proven hook, so no two days share a title.
# {d} "17 अक्टूबर", {wd} weekday, {t} tithi (may be empty). Special tithis (Ekadashi, Purnima, Amavasya...) lead.
TITLE_FMT = {
    "rahu": ["आज का राहु काल {d} {wd}{t} | Rahu Kaal Today", "{wd} {d}{t} - राहु काल का समय | Rahu Kaal Time",
             "राहु काल आज कब है? {d} {wd}{t} | Rahu Kalam"],
    "shubh": ["आज का शुभ मुहूर्त {d} {wd}{t} | Shubh Muhurat Today", "{wd} {d}{t} - अभिजीत मुहूर्त कब है | Abhijit Muhurat",
              "शुभ मुहूर्त आज {d} {wd}{t} | Good Time Today"],
    "durm": ["आज का दुर्मुहूर्त {d} {wd}{t} | Durmuhurat Today", "{wd} {d}{t} - दुर्मुहूर्त का समय | Durmuhurat Time",
             "दुर्मुहूर्त आज कब है? {d} {wd}{t} | Panchang"],
}
SPECIAL_FMT = {
    "rahu": "{tt} {d} {wd} - आज का राहु काल | Rahu Kaal",
    "shubh": "{tt} {d} {wd} - आज का शुभ मुहूर्त | Shubh Muhurat",
    "durm": "{tt} {d} {wd} - आज का दुर्मुहूर्त | Durmuhurat",
}
TAGS = {
    "rahu": ["#RahuKaal", "#RahuKalam", "#राहुकाल", "#Panchang"],
    "shubh": ["#ShubhMuhurat", "#AbhijitMuhurat", "#शुभमुहूर्त", "#Panchang"],
    "durm": ["#Durmuhurat", "#दुर्मुहूर्त", "#Panchang", "#Hindu"],
}
COMMON = ["#DivineMantraSangam", "#Shorts", "#HindiDevotional", "#आजकापंचांग", "#Hindu", "#Spirituality"]


def _d(row):
    import datetime as dt
    d = dt.date.fromisoformat(row["date_iso"])
    return f"{d.day} {d.strftime('%b %Y')}"


def title(row):
    import datetime as dt
    d = dt.date.fromisoformat(row["date_iso"])
    date_s = f"{d.day} {timings.MONTH_HI[d.month - 1]}"
    wd = timings.WEEKDAY_HI[d.weekday()]
    tithi = row.get("tithi_hi", "")
    if tithi and row.get("tithi_special"):
        t = SPECIAL_FMT[row["category"]].format(tt=tithi, d=date_s, wd=wd)
    else:
        t = TITLE_FMT[row["category"]][d.toordinal() % 3].format(d=date_s, wd=wd, t=f", {tithi}" if tithi else "")
    return t[:100]


def hashtags(row):
    out, seen = [], set()
    for h in TAGS[row["category"]] + COMMON:
        if h.lower() not in seen:
            seen.add(h.lower()); out.append(h)
    return out[:15]


def description(row):
    hi, en = NAMES[row["category"]]
    k = row["category"]
    dts = timings.date_hi(__import__('datetime').date.fromisoformat(row['date_iso']))
    lines = [f"आज का {hi} ({en}) - {dts}: सही समय, पंचांग और आज का मंत्र। शुभ काम शुरू करने से पहले देखें।", ""]
    if k == "rahu":
        lines += [f"राहु काल: {row['rahu']}", f"यमगंड: {row['yamagandam']}", f"गुलिक काल: {row['gulika']}",
                  f"वर्ज्य: {row['varjyam']}", f"दुर्मुहूर्त: {row['durm_times']}"]
    elif k == "shubh":
        lines += [f"अभिजीत मुहूर्त: {row['abhijit'] or 'आज नहीं'}", f"ब्रह्म मुहूर्त: {row['brahma']}"]
    else:
        lines += [f"दुर्मुहूर्त: {row['durm_times']}", f"राहु काल: {row['rahu']}"]
    lines += ["", f"{row['t_mantra_label']}: {row['t_mantra']}", "",
              f"रोज़ का पंचांग, राहु काल और शुभ मुहूर्त जानने के लिए {CHANNEL} को सब्सक्राइब करें 🙏", "",
              f"{en} today, {row['weekday_en']} {_d(row)}. Daily Hindu panchang: Rahu Kaal, Shubh Muhurat, "
              f"Durmuhurat and mantra. Subscribe to {CHANNEL}.", ""]
    contact = os.environ.get("CONTACT_EMAIL", "")
    if contact:
        lines += [f"Contact: {contact}", ""]
    lines += [" ".join(hashtags(row))]
    return "\n".join(lines)


def tags(row):
    hi, en = NAMES[row["category"]]
    base = [f"{en} today", en, hi, "आज का पंचांग", "panchang today", "Hindi panchang", "Hindu panchang",
            "daily panchang", "आज का राहु काल", "आज का शुभ मुहूर्त", "आज का दुर्मुहूर्त", "आज का पंचांग today", "shubh muhurat today", "Hindi devotional shorts", CHANNEL]
    out, total = [], 0
    for t in base:
        c = len(t) + (2 if " " in t else 0)
        if total + c <= 450:
            out.append(t); total += c
    return out


def bundle(row, special=None):
    return {"title": title(row), "description": description(row), "tags": tags(row), "localizations": None,
            "comment": row["t_comment"] + " \U0001F64F", "language": "hi"}


def captions(row):
    return {}
