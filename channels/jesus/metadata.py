"""Everything YouTube sees besides the pixels for Jesus Worship Waves' two daily Shorts:
the morning Bible Quote and the evening Bible Quiz. English leads, Telugu follows."""
import os

CHANNEL = "Jesus Worship Waves"
COMMON_TAGS = ["#తెలుగుబైబిల్", "#నేటివాక్యం", "#యేసుక్రీస్తు", "#Jesus", "#TeluguChristian", "#యేసుప్రభు"]
CORE_TAGS = ["#Shorts", "#బైబిల్వచనం", "#JesusWorshipWaves"]
CAT_TAGS = {
    "quote": ["#BibleVerse", "#Scripture", "#WordOfGod", "#DailyVerse"],
    "quiz": ["#BibleQuiz", "#BibleTrivia", "#QuizTime", "#TeluguBibleQuiz"],
}
KEYWORDS = ["నేటి బైబిల్ వచనం", "తెలుగు బైబిల్", "యేసుక్రీస్తు", "బైబిల్ వచనం", "దేవుని వాక్యము", "తెలుగు క్రైస్తవ",
            "Telugu Bible verse", "Telugu Christian shorts", "Jesus", "Bible verse of the day Telugu", "Gospel"]
EXTRA_KEYWORDS = {
    "quote": ["నేటి వాక్యం", "ఈ రోజు బైబిల్ వాక్యం", "తెలుగు బైబిల్ వాక్యాలు", "bible verse of the day", "daily bible verse Telugu",
              "telugu bible verses"],
    "quiz": ["bible quiz", "bible trivia", "bible quiz Telugu", "guess the bible verse", "బైబిల్ క్విజ్"],
}
COMMENTS = {
    "quote": "ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు. 🙏\nYou may never see this channel again unless you subscribe right now. 🙏",
}
DISCLOSURE = ("Visuals are digitally created worship artwork. Background music is an original "
              "composition. Scripture English text is public-domain (KJV/WEB).")
TAG_LIMIT = 500


def _short(text, n):
    words = text.split()
    return " ".join(words[:n]) + ("…" if len(words) > n else "")


def title(row, special=None):
    if row["category"] == "quote":
        te_words = " ".join(row["verse_te"].split()[:6])
        for cand in (f"{row['ref_te']} | {te_words}… | నేటి బైబిల్ వచనం | {row['ref_en']}",
                     f"{row['ref_te']} | నేటి బైబిల్ వచనం | Bible Verse of the Day",
                     f"{row['ref_te']} | నేటి బైబిల్ వచనం"):
            if len(cand) <= 100:
                return cand
    for cand in (f"Bible Quiz: {row['question_en']} | బైబిల్ క్విజ్",
                 f"Bible Quiz: {row['question_en']}",
                 "Bible Quiz | బైబిల్ క్విజ్"):
        if len(cand) <= 100:
            return cand
    return "Bible Quiz"


def hashtags(row, special=None):
    tags = CORE_TAGS + CAT_TAGS[row["category"]] + COMMON_TAGS
    seen, out = set(), []
    for h in tags:
        if h.lower() not in seen:
            seen.add(h.lower())
            out.append(h)
    return out[:15]


def description(row, special=None, playlist_url=None, contact=None):
    playlist_url = playlist_url if playlist_url is not None else os.environ.get("PLAYLIST_URL", "")
    contact = contact if contact is not None else os.environ.get("CONTACT_EMAIL", "")
    out = []
    if row["category"] == "quote":
        out += [row["text_primary"], row["text_secondary"], "", row["apply_te"], row["apply_en"], ""]
        out += [f"వచనం: {row['ref_te']} ({row['ref_en']})", ""]
    else:
        out += [row["question_en"], row["question_te"], "", "Pick A, B, C or D, then check the pinned comment.", ""]
        out += [row["opt_a"], row["opt_b"], row["opt_c"], row["opt_d"], "",
                f"Answer: {row['correct_letter']}) {row['answer']} ({row['ref_en']}) - see the pinned comment.", ""]
    out += [DISCLOSURE, "", f"ప్రతి రోజు కొత్త బైబిల్ వచనం కోసం {CHANNEL} ను సబ్‌స్క్రైబ్ చేయండి.",
            f"Subscribe to {CHANNEL} for a new Bible verse every day."]
    if playlist_url:
        out += [f"Playlist: {playlist_url}"]
    out += ["", f"© {CHANNEL}."]
    if contact:
        out += [f"Contact: {contact}"]
    out += ["", " ".join(hashtags(row))]
    return "\n".join(out)


def fit_tags(tags, limit=TAG_LIMIT):
    out, total, seen = [], 0, set()
    for tg in tags:
        k = tg.lower()
        if k in seen:
            continue
        cost = len(tg) + (2 if " " in tg else 0) + (1 if out else 0)
        if total + cost > limit:
            continue
        seen.add(k)
        out.append(tg)
        total += cost
    return out


def tags(row, special=None):
    return fit_tags(KEYWORDS + EXTRA_KEYWORDS[row["category"]])


def localizations(row, special=None):
    if row["category"] == "quote":
        te_title = f"{row['ref_te']} | నేటి బైబిల్ వచనం | యేసు ఆరాధన"
        te_desc = "\n".join([row["text_secondary"], "", row["apply_te"], "", " ".join(hashtags(row))])
    else:
        te_title = f"బైబిల్ క్విజ్ | {row['question_te']} | యేసు ఆరాధన"
        te_desc = "\n".join([row["text_secondary"], "", row["question_te"], "", " ".join(hashtags(row))])
    return {"te": {"title": te_title[:100], "description": te_desc}}


def srt(text, seconds=5):
    lines = "\n".join(s.strip() for s in text.split("|"))
    return f"1\n00:00:00,000 --> 00:00:{seconds:02d},000\n{lines}\n"


def captions(row):
    return {"en": srt(row["text_primary"]), "te": srt(row["text_secondary"].replace('"', "").replace("'", ""))}


def comment(row):
    if row["category"] == "quote":
        return COMMENTS["quote"]
    return (f"Answer: {row['correct_letter']}) {row['answer']} ({row['ref_en']}). Did you get it right? 🙏\n"
            f"సమాధానం: {row['correct_letter']}) {row['answer_te']} ({row['ref_te']}). మీరు సరిగ్గా చెప్పారా? 🙏")


def bundle(row, special=None):
    return {"title": title(row), "description": description(row), "tags": tags(row),
            "localizations": localizations(row), "comment": comment(row)}
