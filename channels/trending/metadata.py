"""Title, description, tags and comment for a trending Short. The source is always named and linked."""
from __future__ import annotations

from channels.trending import config as cfg
from channels.trending import regions
from channels.trending.sources import Story, trim

DISCLOSURE = ("ఈ ఛానెల్ తెలుగుదేశం పార్టీ అనుకూల దృక్పథంతో నడుస్తుంది. ఇందులోని విశ్లేషణ మా అభిప్రాయం; వార్తలు పేర్కొన్న "
              "మూలాల నుంచి తీసుకున్నవి. హక్కులు ఆయా ప్రచురణకర్తలవి.\n"
              "This channel is run from a pro-TDP point of view. The analysis is our opinion; the facts come from the "
              "sources named above. All rights belong to the original publishers.")

DISCLOSURE_JSP = ("ఈ పోస్ట్ జనసేన పార్టీ దృక్పథంతో ఉంది. ఇందులోని విశ్లేషణ మా అభిప్రాయం; వార్తలు పేర్కొన్న మూలాల నుంచి "
                  "తీసుకున్నవి. హక్కులు ఆయా ప్రచురణకర్తలవి.\n"
                  "This post is from a Janasena point of view. The analysis is our opinion; the facts come from the "
                  "sources named above. All rights belong to the original publishers.")
INTRO_JSP = "జనసేన, పవన్ కళ్యాణ్ గారి కార్యక్రమాలు, ప్రజా సమస్యలపై వార్తలు."

# The channel speaks as a hardcore fan: passionate slogans, never attacks on anyone, never a claim the story does not
# support. One line per post, chosen by the story key. No emoji on the card (the card font would draw boxes).
ANGLES = {
    "chandrababu": ["తెలుగు తమ్ముళ్లూ, మన నాయకుడు చంద్రబాబు గారు ప్రజల కోసమే పనిచేస్తున్నారు! జై బాబు!",
                    "తెలుగుదేశం అభిమానులారా, గర్వంగా చెప్పండి: మన నాయకుడు చంద్రబాబు! జై టీడీపీ!",
                    "విజన్ ఉన్న నాయకుడు ఒక్కరే, మన చంద్రబాబు గారే! జై తెలుగుదేశం!"],
    "lokesh": ["తెలుగు తమ్ముళ్లూ, యువ నాయకుడు లోకేశ్ గారికి అండగా నిలుద్దాం! జై లోకేశ్!",
               "పసుపు సైనికులారా, చినబాబు వేగం చూశారా! జై తెలుగుదేశం!",
               "యువతకు భరోసా మన లోకేశ్ అన్న! జై టీడీపీ!"],
    "tdp": ["తెలుగు తమ్ముళ్లూ, పసుపు జెండా ఎప్పటికీ ఎగురుతూనే ఉంటుంది! జై తెలుగుదేశం!",
            "తెలుగు జాతి ఆత్మగౌరవం మన తెలుగుదేశం! జై టీడీపీ!",
            "తెలుగుదేశం అభిమానులారా, అందరం ఒక్కటిగా నిలబడదాం! జై ఎన్టీఆర్! జై బాబు!"],
    "nda": ["తెలుగు తమ్ముళ్లూ, కూటమి బలంతో రాష్ట్రం ముందుకు! జై తెలుగుదేశం!",
            "అందరం కలిసి అభివృద్ధి వైపు నడుద్దాం! జై టీడీపీ!"],
    "development": ["తెలుగు తమ్ముళ్లూ, ఇదీ మన పాలన వేగం! జై చంద్రబాబు!",
                    "అభివృద్ధి కళ్లముందే కనిపిస్తోంది! తెలుగుదేశం అభిమానులారా, గర్వపడండి! జై టీడీపీ!",
                    "రాష్ట్రం పరుగులు తీస్తోంది, పసుపు సైన్యం గర్వపడే క్షణం! జై బాబు!"],
    "innovations": ["టెక్నాలజీ అంటే మన బాబు గారే! జై సీబీఎన్!", "కొత్త ఆలోచనలకు కేరాఫ్ మన తెలుగుదేశం! జై టీడీపీ!"],
    "join": ["పసుపు సైనికులారా, కదలిరండి! జై తెలుగుదేశం!", "మన పార్టీ, మన బాధ్యత! తెలుగుదేశంలో చేరండి!",
             "తెలుగుదేశం కుటుంబంలో మీరూ ఒకరు కండి! జై టీడీపీ!"],
    "voice": ["మీ ఊరి అభివృద్ధి గళం వినిపించండి! జై తెలుగుదేశం!", "మీ నియోజకవర్గం, మీ గళం! కామెంట్ చేయండి!"],
    "counter": ["తెలుగు తమ్ముళ్లూ, తప్పుడు ప్రచారాన్ని నమ్మకండి, నిజం మన వైపే! జై తెలుగుదేశం!",
                "అసత్యాలను తిప్పికొడదాం, నిజాన్ని నిలబెడదాం! తెలుగుదేశం అభిమానులారా, షేర్ చేయండి! జై బాబు!",
                "మాటలు కాదు, చేతలు! నిజం నిప్పులాంటిది! జై టీడీపీ!"],
    "janasena": ["జనసేనాని అంటే జనం గుండె చప్పుడు! జై జనసేన!", "జై పవన్ కళ్యాణ్! జై జనసేన!", "ప్రజల పక్షాన జనసేన గళం! జై జనసేన!"],
}
ANGLE = {k: v[0] for k, v in ANGLES.items()}   # first line of each, for tests and fallbacks
SLOGAN = {"janasena": "జై జనసేన!"}


HOOKS = ["తెలుగు తమ్ముళ్లూ!", "తెలుగుదేశం అభిమానులారా!", "పసుపు సైనికులారా!", "తమ్ముళ్లూ, చూశారా!", "జై తెలుగుదేశం!"]
HOOKS_COUNTER = ["తమ్ముళ్లూ, ఇదీ అసలు నిజం!", "తప్పుడు ప్రచారానికి తిరుగులేని జవాబు!", "తెలుగుదేశం అభిమానులారా, నిజం ఇదే!", "పనితోనే సమాధానం!"]
HOOKS_JSP = ["జై జనసేన!", "జనసేన శ్రేణులకు శుభవార్త!", "జై పవన్ కళ్యాణ్!"]


def hook(niche: str, key: str) -> str:
    hooks = HOOKS_JSP if niche == "janasena" else HOOKS_COUNTER if niche == "counter" else HOOKS
    return hooks[int(key[6:10] or "0", 16) % len(hooks)]


def angle(niche: str, key: str = "") -> str:
    lines = ANGLES[niche]
    return lines[int(key[:6] or "0", 16) % len(lines)] if key else lines[0]


def join_lines() -> list[str]:
    out = []
    if cfg.WHATSAPP_URL:
        out.append(f"జై తెలుగుదేశం! మా WhatsApp గ్రూప్‌లో చేరండి: {cfg.WHATSAPP_URL}")
    if cfg.TELEGRAM_URL:
        out.append(f"మా Telegram గ్రూప్‌లో కూడా చేరండి: {cfg.TELEGRAM_URL}")
    return out


def hashtags(lang: str, niche: str, story: Story | None = None) -> list[str]:
    """YouTube shows the first three above the title: keep those the strongest. Then the district tags for this post."""
    tags = ["#TDP", "#AndhraPradesh", "#ChandrababuNaidu", "#PulseBoosting", "#Shorts", f"#{cfg.NICHE_TAG[niche]}",
            "#NaraLokesh", "#TeluguNews", "#TeluguDesam"]
    if niche == "janasena":  # Janasena point of view only: no TDP tags
        tags = ["#Janasena", "#PawanKalyan", "#AndhraPradesh", "#PulseBoosting", "#Shorts", "#TeluguNews",
                "#JanaSenaParty", "#DeputyCM"]
    if niche == "join":
        tags += ["#JoinTDP", "#TDPMembership"]
    if story is not None:
        for _te, en, region in regions.for_post(story.key, f"{story.headline} {story.summary}", 3):
            tags += ["#" + en.replace(" ", ""), "#" + region]
    seen, out = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out[:15]


def title(story: Story, lang: str, niche: str) -> str:
    tail = f" | {'Janasena' if niche == 'janasena' else 'TDP'} | {cfg.BRAND}"
    head = story.headline
    if len(head) + len(tail) <= 100:
        return head + tail
    cut = head[: 100 - len(tail) - 1].rsplit(" ", 1)[0].rstrip(",.:;-")
    return f"{cut}…{tail}"


def tags(lang: str, niche: str, story: Story | None = None) -> list[str]:
    words = [cfg.BRAND, cfg.NICHE_EN[niche], cfg.niche_label(lang, niche), "TDP", "తెలుగుదేశం పార్టీ", "Telugu Desam Party",
             "Chandrababu Naidu", "చంద్రబాబు నాయుడు", "Nara Lokesh", "నారా లోకేశ్", "Andhra Pradesh", "ఆంధ్రప్రదేశ్",
             "Telugu news", "తెలుగు వార్తలు", "AP news", "AP politics", "AP assembly constituencies", "అన్ని నియోజకవర్గాలు", "shorts"]
    if niche == "janasena":
        words = [cfg.BRAND, "Janasena", "జనసేన", "Pawan Kalyan", "పవన్ కళ్యాణ్", "Deputy CM Pawan Kalyan", "Janasena Party",
                 "Andhra Pradesh", "ఆంధ్రప్రదేశ్", "Telugu news", "తెలుగు వార్తలు", "AP news", "AP politics", "shorts"]
    if story is not None:
        for te, en, region in regions.for_post(story.key, f"{story.headline} {story.summary}", 5):
            words += [en, te, f"{en} news"]
    out, total, seen = [], 0, set()
    for w in words:
        k = w.lower()
        cost = len(w) + (2 if " " in w else 0) + 1
        if k in seen or total + cost > 470:
            continue
        seen.add(k)
        out.append(w)
        total += cost
    return out


def source_line(story: Story) -> str:
    kind = "Source"
    return f"{kind}: {story.publisher}\nLink: {story.link}"


def area_lines(story: Story) -> list[str]:
    """Where this matters: districts the story names, then a rotation, across all three regions of Andhra Pradesh."""
    ds = regions.for_post(story.key, f"{story.headline} {story.summary}", 8)
    return [
        "ఈ వార్త ఆంధ్రప్రదేశ్‌లోని అన్ని జిల్లాలు, 175 నియోజకవర్గాల ప్రజల కోసం: " + ", ".join(d[0] for d in ds) + " మరియు ఉత్తరాంధ్ర, కోస్తాంధ్ర, రాయలసీమ ప్రాంతాలు.",
        "For people across Andhra Pradesh: " + ", ".join(d[1] for d in ds) + " and all 175 assembly constituencies.", ""]


def mention_line() -> str:
    ms = [m if m.startswith("@") else "@" + m for m in cfg.MENTIONS]
    return " ".join(ms[:8])   # a few well-chosen handles; long lists look like spam to YouTube


def description(story: Story, lang: str, niche: str) -> str:
    more = [angle(niche, story.key), ""]
    more += [story.summary, ""] if story.summary else []
    if story.related:
        more += ["Also reported:"] + [f"- {h} ({p})" for h, p in story.related] + [""]
    return "\n".join([
        story.headline, "",
        *more,
        source_line(story), "",
        INTRO_JSP if niche == "janasena" else cfg.INTRO[lang],
        "" if niche == "janasena" else cfg.INTRO["en"], "",
        *area_lines(story),
        *join_lines(), *([""] if join_lines() else []),
        *([mention_line(), ""] if cfg.MENTIONS else []),
        DISCLOSURE_JSP if niche == "janasena" else DISCLOSURE, "",
        f"{cfg.BRAND}: like, share and subscribe.", "",
        " ".join(hashtags(lang, niche, story)),
    ])


def bundle(story: Story, lang: str, niche: str) -> dict:
    return {
        "title": title(story, lang, niche),
        "description": description(story, lang, niche),
        "tags": tags(lang, niche, story),
        "comment": f"{source_line(story)}\n{cfg.CTA[lang][2]} {SLOGAN.get(niche, 'జై తెలుగుదేశం!')}" + (f"\n{mention_line()}" if cfg.MENTIONS else ""),
        "language": lang,
    }


def row_for(story: Story, lang: str, niche: str) -> dict:
    """The card: headline, the publisher's summary, related headlines, and a small source line."""
    head = story.headline
    if story.kind == "news":  # a fan's reaction in front of the latest news headline
        head = f"{hook(niche, story.key)} {head}"
    if len(head) > 110:
        head = head[:110].rsplit(" ", 1)[0].rstrip(",.:;-") + "…"
    kind = "Source"
    related = "\n".join([angle(niche, story.key)] + [f"• {h}" for h, _ in story.related[:2]])
    return {"id": story.key, "category": niche, "special": "",
            "text_primary": head, "text_summary": trim(story.summary, 190), "text_related": related,
            "text_secondary": f"{kind}: {story.publisher}"}
