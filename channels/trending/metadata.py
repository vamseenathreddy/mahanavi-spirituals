"""Title, description, tags and comment for a trending Short. Descriptions carry a short summary only: no source names or links (owner request 2026-10-20); the card keeps its small source line."""
from __future__ import annotations

from channels.trending import config as cfg
from channels.trending import fan_lines
from channels.trending import regions
from channels.trending.sources import Story, complete, trim

DISCLOSURE = ("ఈ ఛానెల్ తెలుగుదేశం పార్టీ అనుకూల దృక్పథంతో నడుస్తుంది. ఇందులోని విశ్లేషణ మా అభిప్రాయం; వార్తలు "
              "పబ్లిక్ వార్తా నివేదికల నుంచి తీసుకున్నవి.\n"
              "This channel is run from a pro-TDP point of view. The analysis is our opinion; the facts come from public news "
              "reports.")

DISCLOSURE_HISTORY = ("ఈ పోస్ట్ తెలుగుదేశం పార్టీ చరిత్ర, ఎన్టీఆర్, చంద్రబాబు గారి గురించి బహిరంగంగా లభించే సమాచారం ఆధారంగా అభిమానుల దృక్పథంతో రూపొందింది. ఇందులోని విశ్లేషణ మా అభిప్రాయం.\n"
                      "This post is built from publicly available Telugu Desam Party history, told from a supporter's point of view. "
                      "The analysis is our opinion.")

DISCLOSURE_JSP = ("ఈ పోస్ట్ జనసేన పార్టీ దృక్పథంతో ఉంది. ఇందులోని విశ్లేషణ మా అభిప్రాయం; వార్తలు పబ్లిక్ వార్తా నివేదికల నుంచి "
                  "తీసుకున్నవి.\n"
                  "This post is from a Janasena point of view. The analysis is our opinion; the facts come from public news "
                  "reports.")
INTRO_JSP = "జనసేన, పవన్ కళ్యాణ్ గారి కార్యక్రమాలు, ప్రజా సమస్యలపై వార్తలు."

# The channel speaks as a hardcore fan: passionate slogans, never attacks on anyone, never a claim the story does not
# support. One line per post, chosen by the story key. No emoji on the card (the card font would draw boxes).
ANGLES = {
    "chandrababu": ["తమ్ముళ్లూ, మన నాయకుడు చంద్రబాబు గారు ప్రజల కోసమే పనిచేస్తున్నారు! జై బాబు!",
                    "తెలుగుదేశం అభిమానులారా, గర్వంగా చెప్పండి: మన నాయకుడు చంద్రబాబు! జై టీడీపీ!",
                    "విజన్ ఉన్న నాయకుడు ఒక్కరే, మన చంద్రబాబు గారే! జై తెలుగుదేశం!"],
    "lokesh": ["తమ్ముళ్లూ, యువ నాయకుడు లోకేశ్ గారికి అండగా నిలుద్దాం! జై లోకేశ్!",
               "పసుపు సైనికులారా, చినబాబు వేగం చూశారా! జై తెలుగుదేశం!",
               "యువతకు భరోసా మన లోకేశ్ అన్న! జై టీడీపీ!",
               "ఆపదలో ఉన్నవారికి అండగా నిలిచే లోకేశ్ గారికి సలాం! తమ్ముళ్లూ, జై లోకేశ్!",
               "కష్టపడే నాయకుడు, ఎదుగుతున్న నాయకుడు మన లోకేశ్! తెలుగుదేశం అభిమానులారా, జై టీడీపీ!"],
    "tdp": ["తమ్ముళ్లూ, పసుపు జెండా ఎప్పటికీ ఎగురుతూనే ఉంటుంది! జై తెలుగుదేశం!",
            "తెలుగు జాతి ఆత్మగౌరవం మన తెలుగుదేశం! జై టీడీపీ!",
            "తెలుగుదేశం అభిమానులారా, అందరం ఒక్కటిగా నిలబడదాం! జై ఎన్టీఆర్! జై బాబు!"],
    "nda": ["తమ్ముళ్లూ, కూటమి బలంతో రాష్ట్రం ముందుకు! జై తెలుగుదేశం!",
            "అందరం కలిసి అభివృద్ధి వైపు నడుద్దాం! జై టీడీపీ!"],
    "development": ["తమ్ముళ్లూ, ఇదీ మన పాలన వేగం! జై చంద్రబాబు!",
                    "అభివృద్ధి కళ్లముందే కనిపిస్తోంది! తెలుగుదేశం అభిమానులారా, గర్వపడండి! జై టీడీపీ!",
                    "రాష్ట్రం పరుగులు తీస్తోంది, పసుపు సైన్యం గర్వపడే క్షణం! జై బాబు!"],
    "amaravati": ["తమ్ముళ్లూ, మన రాజధాని అమరావతి పరుగులు తీస్తోంది! జై అమరావతి! జై బాబు!",
                  "అమరావతి తెలుగు జాతి ఆత్మగౌరవం! తెలుగుదేశం అభిమానులారా, గర్వపడండి! జై టీడీపీ!",
                  "ఐదు కోట్ల ఆంధ్రుల రాజధాని అమరావతి! జై తెలుగుదేశం!"],
    "local": ["తమ్ముళ్లూ, మన నూజివీడు, చాట్రాయి అభివృద్ధి బాటలో! జై తెలుగుదేశం!",
              "మన ఊరు, మన గర్వం! పసుపు సైనికులారా, ఇలాగే ముందుకు సాగుదాం! జై టీడీపీ!"],
    "innovations": ["టెక్నాలజీ అంటే మన బాబు గారే! జై సీబీఎన్!", "కొత్త ఆలోచనలకు కేరాఫ్ మన తెలుగుదేశం! జై టీడీపీ!"],
    "join": ["పసుపు సైనికులారా, కదలిరండి! జై తెలుగుదేశం!", "మన పార్టీ, మన బాధ్యత! తెలుగుదేశంలో చేరండి!",
             "తెలుగుదేశం కుటుంబంలో మీరూ ఒకరు కండి! జై టీడీపీ!"],
    "voice": ["మీ ఊరి అభివృద్ధి గళం వినిపించండి! జై తెలుగుదేశం!", "మీ నియోజకవర్గం, మీ గళం! కామెంట్ చేయండి!"],
    "counter": ["తమ్ముళ్లూ, తప్పుడు ప్రచారాన్ని నమ్మకండి, నిజం మన వైపే! జై తెలుగుదేశం!",
                "అసత్యాలను తిప్పికొడదాం, నిజాన్ని నిలబెడదాం! తెలుగుదేశం అభిమానులారా, షేర్ చేయండి! జై బాబు!",
                "మాటలు కాదు, చేతలు! నిజం నిప్పులాంటిది! జై టీడీపీ!"],
    "ysrcp": ["తమ్ముళ్లూ, గత ప్రభుత్వ బండారం బయటపడుతోంది! జై తెలుగుదేశం!",
              "ప్రజల సొమ్ము ప్రజలకే చెందాలి! పసుపు సైనికులారా, నిజం అందరికీ చేరాలి! జై టీడీపీ!",
              "లెక్కలు తేలుతున్నాయి, నిజాలు బయటపడుతున్నాయి! తెలుగుదేశం అభిమానులారా, షేర్ చేయండి! జై బాబు!",
              "ఐదేళ్ల విధ్వంసానికి లెక్కలు చెప్పాల్సిందే! తమ్ముళ్లూ, జై తెలుగుదేశం!"],
    "janasena": ["జనసేనాని అంటే జనం గుండె చప్పుడు! జై జనసేన!", "జై పవన్ కళ్యాణ్! జై జనసేన!", "ప్రజల పక్షాన జనసేన గళం! జై జనసేన!"],
}
ANGLES["ntr"] = ["జై ఎన్టీఆర్! జై తెలుగుదేశం!", "తమ్ముళ్లూ, అన్న ఎన్టీఆర్ స్ఫూర్తి మనతోనే! జై టీడీపీ!",
                 "తెలుగు వారి ఆత్మగౌరవం మన తెలుగుదేశం! జై ఎన్టీఆర్! జై బాబు!"]

# Two or three more lines under every news post, so the card reads like a short fan note and not just a headline
# (owner request 2026-10-20). Fan voice, no claim beyond what the story says. Chosen by the story key.
NOTES = {
    "amaravati": ["అమరావతి అంటే ఐదు కోట్ల ఆంధ్రుల కల. రాజధాని నిర్మాణం ముందుకు సాగితే రాష్ట్ర భవిష్యత్తు మారుతుంది. ఈ వార్త ఆ దిశగా మరో అడుగు.",
                  "రాజధాని పనులు వేగం అందుకుంటే ఉద్యోగాలు, పెట్టుబడులు పెరుగుతాయి. అమరావతి మన ఆత్మగౌరవం అని తమ్ముళ్లు గర్వంగా చెబుతారు.",
                  "అమరావతి కోసం భూములిచ్చిన రైతుల త్యాగాన్ని మరచిపోకూడదు. వారి కలను నిజం చేసే ప్రతి అడుగూ మనందరికీ గర్వకారణం."],
    "lokesh": ["కష్టంలో ఉన్నవారికి వెంటనే స్పందించే నాయకుడిని ప్రజలు గుర్తుపెట్టుకుంటారు. యువతకు ఉద్యోగాలు, అవకాశాలు ఇవ్వాలన్నదే లోకేశ్ గారి ధ్యేయం అని అభిమానులు చెబుతారు.",
               "చిన్న సమస్యకైనా అండగా నిలవడం నాయకత్వ లక్షణం. లోకేశ్ గారి ఈ వేగం యువతకు స్ఫూర్తి అని పసుపు సైన్యం గర్వపడుతోంది.",
               "ఎదుగుతున్న నాయకుడు ప్రజల మధ్యే ఉండాలి. ఆ దారిలోనే లోకేశ్ గారు ముందుకు సాగుతున్నారని తమ్ముళ్లు అంటున్నారు."],
    "chandrababu": ["అభివృద్ధి, సంక్షేమం రెండింటినీ సమన్వయం చేయడం చంద్రబాబు గారి పాలనా శైలి అని అభిమానులు అంటారు. ఈ వార్త ఆ దిశలో మరో సూచన.",
                    "విజన్ ఉన్న నాయకుడు ముందు చూపుతో నిర్ణయాలు తీసుకుంటారు. రాష్ట్రం కోసం రాత్రింబవళ్లు పనిచేసే నాయకుడు మన చంద్రబాబు గారు అని కార్యకర్తలు గర్వంగా చెబుతారు.",
                    "అనుభవం, దూరదృష్టి కలిసిన నాయకత్వం రాష్ట్రానికి భరోసా. ఈ వార్తను అందరికీ షేర్ చేయండి."],
    "counter": ["ప్రచారం కాదు, వాస్తవమే ముఖ్యం. ఏ విషయమైనా నిజమా కాదా చూసి నమ్మడం మనందరి బాధ్యత.",
                "తప్పుడు ప్రచారం ఎంత వేగంగా వ్యాపిస్తుందో, నిజం అంత వేగంగా చేరాలి. మీ మిత్రులకు ఈ నిజాన్ని షేర్ చేయండి.",
                "అసత్యాన్ని నమ్మే ముందు ఒక్కసారి ఆధారాలు చూడండి. నిజం ఎప్పుడూ నిలుస్తుంది."],
    "ysrcp": ["ఇది వార్తల్లో వచ్చిన విషయం మాత్రమే. విచారణ, కోర్టు నిర్ణయాలే తుది నిజం తేలుస్తాయి. అప్పటివరకు ప్రజలు వాస్తవాలను గమనించాలి.",
              "ప్రజల సొమ్ము ఎక్కడికి వెళ్లిందో లెక్క తేలాలని తెలుగుదేశం అభిమానులు కోరుతున్నారు. ఈ వార్తను అందరికీ షేర్ చేయండి.",
              "గత ఐదేళ్ల పాలనపై వస్తున్న నివేదికలను ప్రజలు గమనిస్తున్నారు. నిజం నిలకడగా బయటకు వస్తుందని తమ్ముళ్లు నమ్ముతున్నారు."],
    "tdp": ["తెలుగుదేశం కార్యకర్తల కష్టమే పార్టీ బలం. ఇలాంటి వార్తలు వారికి మరింత ఉత్సాహాన్నిస్తాయి.",
            "పసుపు జెండా కోసం ఏళ్ల తరబడి శ్రమించిన కార్యకర్తలకు వందనాలు. ఈ వార్తను మీ తమ్ముళ్లందరికీ షేర్ చేయండి.",
            "తెలుగు ప్రజల ఆత్మగౌరవమే తెలుగుదేశం పునాది. ఆ స్ఫూర్తితో అందరం కలిసి ముందుకు సాగుదాం."],
    "nda": ["కూటమి బలం అంటే మూడు పార్టీల సమన్వయం. రాష్ట్ర అభివృద్ధి కోసం అందరూ కలిసి పనిచేయడం ప్రజలకు భరోసా.",
            "కేంద్రం, రాష్ట్రం కలిసి నడిస్తే అభివృద్ధికి రెట్టింపు వేగం వస్తుందని కూటమి అభిమానులు నమ్ముతారు.",
            "ఐక్యతే బలం. ఈ కూటమి కృషి ఫలితాలు ప్రజలకు చేరాలని ఆశిద్దాం."],
    "development": ["రోడ్లు, పరిశ్రమలు, ఉద్యోగాలు: అభివృద్ధి కళ్లముందే కనిపిస్తే ప్రజలకు నమ్మకం పెరుగుతుంది. ఈ వార్త అలాంటి ఒక అడుగు.",
                    "ఒక్క పెట్టుబడి వేల కుటుంబాలకు ఉపాధి అవుతుంది. అభివృద్ధి వేగం ఇలాగే కొనసాగాలని తమ్ముళ్లు కోరుకుంటున్నారు.",
                    "రాష్ట్రం ముందుకు సాగుతుంటే ప్రతి తెలుగువాడికీ గర్వమే. ఈ వార్తను మీ ఊరి వాళ్లకూ చేరవేయండి."],
    "local": ["మన ఊరి అభివృద్ధి మన గర్వం. ఇలాంటి మంచి వార్తలను అందరికీ చేరవేద్దాం.",
              "నూజివీడు, చాట్రాయి ప్రజల కోసం జరిగే ప్రతి మంచి పనికీ మన మద్దతు ఉండాలి."],
}


# Per-niche rotation counter, set by post.py from the state file before the card is built. With it, the angle and the note
# walk through their pools in order (the pools have different lengths, so the pairs keep changing) and a line returns
# only after the whole pool was used. Without it (tests, other tools) the story key picks the line as before.
VARIANT: int | None = None


def _pool(base: dict, more: dict, niche: str) -> list:
    return list(base.get(niche, [])) + list(more.get(niche, []))


def _pick(lines: list, key: str, lo: int, shift: int = 0) -> str:
    if not lines:
        return ""
    if VARIANT is not None:
        return lines[(VARIANT + shift) % len(lines)]
    return lines[int(key[lo:lo + 6] or "0", 16) % len(lines)]


def note(niche: str, key: str = "") -> str:
    return _pick(_pool(NOTES, fan_lines.NOTES_MORE, niche), key, 2, 3) if key else ""


ANGLE = {k: v[0] for k, v in ANGLES.items()}   # first line of each, for tests and fallbacks
SLOGAN = {"janasena": "జై జనసేన!"}


HOOKS = ["తమ్ముళ్లూ!", "తెలుగుదేశం అభిమానులారా!", "పసుపు సైనికులారా!", "తమ్ముళ్లూ, చూశారా!", "జై తెలుగుదేశం!"]
HOOKS_COUNTER = ["తమ్ముళ్లూ, ఇదీ అసలు నిజం!", "తప్పుడు ప్రచారానికి తిరుగులేని జవాబు!", "తెలుగుదేశం అభిమానులారా, నిజం ఇదే!", "పనితోనే సమాధానం!"]
HOOKS_JSP = ["జై జనసేన!", "జనసేన శ్రేణులకు శుభవార్త!", "జై పవన్ కళ్యాణ్!"]


def hook(niche: str, key: str) -> str:
    hooks = HOOKS_JSP if niche == "janasena" else HOOKS_COUNTER if niche in ("counter", "ysrcp") else HOOKS
    return _pick(hooks, key, 6, 1)


def angle(niche: str, key: str = "") -> str:
    lines = _pool(ANGLES, fan_lines.ANGLES_MORE, niche)
    return _pick(lines, key, 0) if key else lines[0]


def join_lines() -> list[str]:
    out = []
    if cfg.WHATSAPP_URL:
        out.append(f"జై తెలుగుదేశం! మా WhatsApp గ్రూప్‌లో చేరండి: {cfg.WHATSAPP_URL}")
    if cfg.TELEGRAM_URL:
        out.append(f"మా Telegram గ్రూప్‌లో కూడా చేరండి: {cfg.TELEGRAM_URL}")
    return out


def hashtags(lang: str, niche: str, story: Story | None = None) -> list[str]:
    """YouTube shows the first three above the title: keep those the strongest. Then the district tags for this post."""
    tags = ["#TDP", "#AndhraPradesh", "#ChandrababuNaidu", "#PulseTDPFans", "#Shorts", f"#{cfg.NICHE_TAG[niche]}",
            "#NaraLokesh", "#TeluguNews", "#TeluguDesam"]
    if niche == "janasena":  # Janasena point of view only: no TDP tags
        tags = ["#Janasena", "#PawanKalyan", "#AndhraPradesh", "#PulseTDPFans", "#Shorts", "#TeluguNews",
                "#JanaSenaParty", "#DeputyCM"]
    if niche == "join":
        tags += ["#JoinTDP", "#TDPMembership"]
    if niche == "ntr":
        tags = ["#NTR", "#TDP", "#TeluguDesam", "#PulseTDPFans", "#Shorts", "#NandamuriTarakaRamaRao", "#TDPHistory",
                "#JaiNTR", "#AnnaNTR", "#ChandrababuNaidu", "#AndhraPradesh", "#TeluguPride", "#TeluguNews"]
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
    tail = f" | {'Janasena' if niche == 'janasena' else 'NTR | TDP' if niche == 'ntr' else 'TDP'} | {cfg.BRAND}"
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
    if niche == "ntr":
        words = [cfg.BRAND, "NTR", "ఎన్టీఆర్", "N. T. Rama Rao", "Nandamuri Taraka Rama Rao", "Anna NTR", "Telugu Desam Party",
                 "తెలుగుదేశం పార్టీ", "TDP history", "తెలుగుదేశం చరిత్ర", "Telugu Vari Atma Gouravam", "తెలుగు వారి ఆత్మగౌరవం",
                 "Chandrababu Naidu", "చంద్రబాబు నాయుడు", "Telugu Desam founder", "NTR Bhavan", "Andhra Pradesh", "Telugu pride",
                 "Anna Canteen", "TDP", "shorts"]
    elif story is not None:
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
    if story.kind == "ntr":
        return ["తెలుగు ప్రజలందరి కోసం: ఆంధ్రప్రదేశ్, తెలంగాణ, ప్రపంచవ్యాప్తంగా ఉన్న తెలుగు వారు.",
                "For Telugu people everywhere: Andhra Pradesh, Telangana and the Telugu diaspora.", ""]
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
    if note(niche, story.key):
        more += [note(niche, story.key), ""]
    if story.related:
        more += ["ముఖ్యాంశాలు (Key points):" if niche == "ntr" else "Also in the news:"] + [f"- {h}" for h, _ in story.related] + [""]
    if niche == "ntr":
        from channels.trending.ntr_bank import english_line
        more += [english_line(story.headline) + ". Telugu Desam Party history, NTR and Chandrababu Naidu, told for Telugu supporters.", ""]
    return "\n".join([
        story.headline, "",
        *more,
        INTRO_JSP if niche == "janasena" else cfg.INTRO[lang],
        "" if niche == "janasena" else cfg.INTRO["en"], "",
        *area_lines(story),
        *join_lines(), *([""] if join_lines() else []),
        *([mention_line(), ""] if cfg.MENTIONS else []),
        DISCLOSURE_JSP if niche == "janasena" else DISCLOSURE_HISTORY if niche == "ntr" else DISCLOSURE, "",
        f"{cfg.BRAND}: like, share and subscribe.", "",
        " ".join(hashtags(lang, niche, story)),
    ])


def bundle(story: Story, lang: str, niche: str) -> dict:
    return {
        "title": title(story, lang, niche),
        "description": description(story, lang, niche),
        "tags": tags(lang, niche, story),
        "comment": f"{cfg.CTA[lang][2]} {SLOGAN.get(niche, 'జై తెలుగుదేశం!')}" + (f"\n{mention_line()}" if cfg.MENTIONS else ""),
        "language": lang,
    }


def row_for(story: Story, lang: str, niche: str) -> dict:
    """The card: headline, the publisher's summary, related headlines, and a small source line."""
    head = story.headline
    if story.kind == "news":  # a fan's reaction in front of the latest news headline
        head = f"{hook(niche, story.key)} {head}"
    head = complete(head, 260) or head  # no trailing '…' or half sentence on the card
    kind = "Source"
    bullets = "\n".join([angle(niche, story.key)] + [f"• {h}" for h, _ in story.related[:2]])
    extra = note(niche, story.key)
    # The fan note (2 or 3 lines) takes the place of the other outlets' headlines on the card; those stay in the description.
    related = f"{angle(niche, story.key)}\n{extra}" if extra else bullets
    return {"id": story.key, "category": niche, "special": "",
            "text_primary": head, "text_summary": complete(story.summary, 400, soft=False),
            "text_related": related, "_bullets": bullets,
            "text_secondary": story.publisher if story.kind == "ntr" else f"{kind}: {story.publisher}"}


MIN_CARD_SCALE = 0.5   # below this the text is too small to read on a phone; trim the reading matter instead


def fit_row(row: dict, rcfg) -> dict:
    """Shrinking alone cannot fit a very long story. Keep the headline whole and the text as large as MIN_CARD_SCALE,
    and drop the least important reading matter step by step: second related line, both related lines, the summary's
    later sentences, the whole summary. Nothing is ever cut mid-sentence or ended with '...'."""
    from channels.engine import render
    layout = dict(anchor=0.44, primary=(0, 0, 0), secondary=(0, 0, 0), accent=(0, 0, 0), ornament=False)

    def ok(r: dict) -> bool:
        _laid, _total, fits, scale = render.fit_text(r, layout, rcfg)
        return fits and scale >= MIN_CARD_SCALE

    row = dict(row)
    if ok(row):
        return row
    if row.get("_bullets") and row["_bullets"] != row["text_related"]:   # the fan note does not fit: fall back to the headlines
        row["text_related"] = row["_bullets"]
        if ok(row):
            return row
    rel = row["text_related"].split("\n")
    for keep in (2, 1):          # angle line + one bullet, then the angle line alone
        row["text_related"] = "\n".join(rel[:keep])
        if ok(row):
            return row
    summary = row["text_summary"]
    first = complete(summary, 400, soft=False)
    for i in range(len(first) - 1, 0, -1):   # keep only the first sentence of the summary
        if first[i] in "?!.।" and i < len(first) - 1:
            row["text_summary"] = first[: i + 1]
            break
    if ok(row):
        return row
    row["text_summary"] = ""
    return row
