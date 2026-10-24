"""Where the stories come from. Two free, real-world sources only; nothing is written or embellished here.

1. Google News topic feeds, one per language edition (te, hi, ta, kn, ml, en). Native-language headlines come
   straight from the publisher, so no translation is involved. Needs no key.
2. YouTube "most popular in India" (videos.list chart=mostPopular, 1 quota unit), filtered to the language and
   category. Used as a source for Cinema and Viral, and as a fallback for the other niches.

Every story carries its publisher (or YouTube channel) and a link, which go on the card and in the description.
parse_rss, clean_title, matches_language and fresh_enough are pure functions so tests need no network."""
from __future__ import annotations

import email.utils
import hashlib
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from channels.trending import dedupe

USER_AGENT = "Mozilla/5.0 (compatible; trending-shorts-bot/1.0)"

# language -> (hl, gl, ceid, unicode block start, end) ; en uses Latin.
EDITIONS = {
    "te": ("te", "IN", "IN:te"),
    "hi": ("hi", "IN", "IN:hi"),
    "ta": ("ta", "IN", "IN:ta"),
    "kn": ("kn", "IN", "IN:kn"),
    "ml": ("ml", "IN", "IN:ml"),
    "en": ("en-IN", "IN", "IN:en"),
}
SCRIPT_RANGE = {"te": (0x0C00, 0x0C7F), "hi": (0x0900, 0x097F), "ta": (0x0B80, 0x0BFF),
                "kn": (0x0C80, 0x0CFF), "ml": (0x0D00, 0x0D7F)}

# niche -> Google News topic, and YouTube category (None = overall chart)
NEWS_TOPIC = {"breaking": "NATION", "sports": "SPORTS", "cinema": "ENTERTAINMENT", "technology": "TECHNOLOGY",
              "business": "BUSINESS", "health": "HEALTH", "viral": "NATION"}
YT_CATEGORY = {"breaking": "25", "sports": "17", "cinema": "24", "technology": "28", "viral": None}
TOP_N = 10
# order of sources to try per niche
SOURCE_ORDER = {"innovations": ("bank", "news"), "development": ("news",), "join": ("bank",), "voice": ("bank",),
                "janasena": ("news", "bank"), "ntr": ("bank",)}
DEFAULT_ORDER = ("news",)   # current news only: a quiet feed skips the slot instead of posting an old fact

# TDP-supportive channel (2026-10-17): Telugu political search feeds, keyword-filtered.
POLITICAL_QUERY = {
    "chandrababu": ["చంద్రబాబు నాయుడు", "సీఎం చంద్రబాబు"],
    "lokesh": ["నారా లోకేశ్", "మంత్రి లోకేశ్", "లోకేశ్ సాయం", "లోకేశ్ ఉద్యోగాలు ఐటీ", "లోకేశ్ ఆదుకున్నారు"],
    "amaravati": ["అమరావతి రాజధాని పనులు", "అమరావతి అభివృద్ధి", "అమరావతి నిర్మాణం"],
    "local": ["నూజివీడు", "చాట్రాయి", "నూజివీడు నియోజకవర్గం అభివృద్ధి", "చాట్రాయి మండలం"],
    "tdp": ["తెలుగుదేశం పార్టీ", "టీడీపీ"],
    "nda": ["కూటమి ప్రభుత్వం", "కూటమి ప్రభుత్వం ఆంధ్రప్రదేశ్ అభివృద్ధి", "ఎన్డీఏ ఆంధ్రప్రదేశ్"],
    "janasena": ["జనసేన పవన్ కళ్యాణ్", "డిప్యూటీ సీఎం పవన్ కళ్యాణ్"],
    "counter": ["వైసీపీ ఆరోపణలకు కూటమి కౌంటర్", "జగన్ ఆరోపణలపై మంత్రి స్పందన", "వైసీపీ విమర్శలకు టీడీపీ సమాధానం", "వైసీపీపై మంత్రి ఫైర్", "జగన్‌పై మంత్రి ధ్వజం", "వైసీపీ నేతలకు కౌంటర్"],
    "ysrcp": ["జగన్ హయాంలో కుంభకోణం", "వైసీపీ హయాంలో అవినీతి", "వైసీపీ హయాంలో అక్రమాలు", "జగన్ అక్రమాస్తుల కేసు విచారణ",
              "లిక్కర్ స్కామ్ వైసీపీ", "వైసీపీ నేతలపై కేసు", "వైసీపీ తప్పుడు ప్రచారం బయటపడింది", "వైసీపీ హయాంలో నిధుల దుర్వినియోగం",
              "జగన్ సమాధానం చెప్పాలి", "వైసీపీని నిలదీసిన మంత్రి", "వైసీపీ హయాంలో పోలవరం నష్టం", "వైసీపీ హయాంలో అప్పులు బకాయిలు",
              "జగన్ ప్రభుత్వ నిర్వాకం", "వైసీపీ హయాంలో రోడ్లు అమరావతి నష్టం", "జగన్ హయాంలో లెక్కలు శ్వేతపత్రం", "వైసీపీ నేతల అక్రమాలు బట్టబయలు"],
    # Government Orders (GOs) the AP government has issued, as reported by the news outlets. Outlets only, no influencers.
    "go": ["ప్రభుత్వం జీవో జారీ", "ఏపీ ప్రభుత్వం ఉత్తర్వులు జారీ", "జీవో విడుదల ఏపీ ప్రభుత్వం", "ప్రభుత్వ ఉత్తర్వులు జారీ ఆంధ్రప్రదేశ్",
           "కూటమి ప్రభుత్వం జీవో", "నిధులు మంజూరు జీవో"],
    "development": "ఆంధ్రప్రదేశ్ అభివృద్ధి పెట్టుబడులు", "innovations": "ఆంధ్రప్రదేశ్ ప్రభుత్వం కొత్త పథకం సాంకేతికత",
}
# Headlines that are about the opposition or about trouble are skipped: the channel only carries positive stories.
EXCLUDE = ("వైఎస్ఆర్సీపీ", "వైసీపీ", "జగన్", "YSRCP", "YCP", "Jagan", "అరెస్ట్", "హత్య", "మృతి", "ప్రమాదం", "దాడి",
           "అత్యాచారం", "విమర్శ", "ఆరోపణ", "కుంభకోణం", "వివాదం", "మరణ", "ఆత్మహత్య", "కేసు", "దుర్ఘటన", "నిరసన", "సమాధి", "గల్లంతు", "విషాదం", "దుర్మరణం", "బలి", "హతం", "అగ్నిప్రమాదం",
           "వరద", "భూకంపం", "సినిమా", "చిత్రం", "నటన", "హీరో", "మూవీ", "ట్రైలర్", "బాక్సాఫీస్", "ఓజీ")
SUBJECT = {  # the headline must actually be about the niche's subject
    "chandrababu": ("చంద్రబాబు", "సీఎం", "బాబు"), "lokesh": ("లోకేశ్", "లోకేష్"), "tdp": ("టీడీపీ", "తెలుగుదేశం", "తెదేపా"),
    "nda": ("కూటమి", "ఎన్డీఏ", "జనసేన", "బీజేపీ"), "janasena": ("జనసేన", "పవన్"),
    "development": ("ఆంధ్రప్రదేశ్", "ఏపీ", "అమరావతి", "రాష్ట్ర", "విశాఖ"),
    "counter": ("వైసీపీ", "వైఎస్ఆర్సీపీ", "జగన్"), "ysrcp": ("వైసీపీ", "వైఎస్ఆర్సీపీ", "జగన్"),
    "go": ("జీవో", "జీఓ", "ఉత్తర్వు", "ఉత్తర్వులు"),
    "amaravati": ("అమరావతి",), "local": ("నూజివీడు", "చాట్రాయి"),
}
# The 'counter' niche: a headline where the government or TDP answers the opposition. Tragedy and crime headlines stay out;
# the opposition's own names are allowed here (they are the subject), and a reply word is required.
COUNTER_REPLY = ("కౌంటర్", "స్పందన", "సమాధానం", "ఖండించ", "తిప్పికొట్ట", "మండిపడ్డ", "విమర్శలకు", "ఆరోపణలకు", "అబద్ధ", "నిజం", "ఫైర్", "ధ్వజ", "చురక", "గట్టి సమాధానం")
COUNTER_BAD = ("కాల్పు", "ఎన్‌కౌంటర్", "ఘర్షణ", "గొడవ", "బెదిరింపు", "పోలీసు", "అరెస్ట్", "హత్య", "మృతి", "ప్రమాదం", "దాడి", "అత్యాచారం", "మరణ", "ఆత్మహత్య", "దుర్ఘటన", "విషాదం", "దుర్మరణం",
               "సినిమా", "చిత్రం", "హీరో", "మూవీ", "ట్రైలర్")
# The 'ysrcp' niche: reported cases, scams and exposures from the previous government's time. The headline must name YSRCP or
# Jagan AND carry a reporting word; violence, deaths, women, family and film headlines stay out, and so do headlines where
# the opposition is itself the one making charges (we would be amplifying it).
YSRCP_REPORT = ("కుంభకోణం", "స్కామ్", "అవినీతి", "అక్రమ", "దుర్వినియోగం", "కేసు", "సీబీఐ", "ఈడీ", "సిట్", "చార్జిషీట్", "విచారణ",
                "తప్పుడు ప్రచారం", "బయటపడ", "కాగ్", "దోపిడీ", "మోసం", "హయాం", "హయాంలో", "బండారం", "బకాయి", "అప్పులు", "శ్వేతపత్రం",
                "నిలదీ", "ప్రశ్నించ", "సమాధానం చెప్పాల", "నిర్వాకం", "నష్టం", "లెక్కలు", "బట్టబయలు", "అక్రమాలు", "ఖర్చు")
YSRCP_BAD = COUNTER_BAD + ("డిమాండ్", "డిమాండ్ చేశ", "విమర్శ", "మండిపడ్డ", "ఆరోపణలు చేశ", "సినిమా", "భార్య", "కుమార్తె", "తల్లి", "చెల్లి", "షర్మిల", "భారతి", "కుటుంబ",
                           "మహిళ", "బాలిక", "మైనర్", "వ్యక్తిగత", "అక్రమ సంబంధ", "సాక్షి")
POSITIVE = ("అభివృద్ధి", "పెట్టుబడ", "ఉద్యోగ", "ప్రారంభ", "శంకుస్థాపన", "ఒప్పందం", "పథకం", "నిధులు", "ప్రశంస",
            "హర్షం", "శుభవార్త", "సాయం", "ఆదుక", "అండగా", "నిర్మాణ", "పనులు", "ప్రారంభం", "మంజూరు", "అమరావతి", "ఐటీ", "డేటా సెంటర్", "ఏఐ", "పరిశ్రమ", "రైతు", "మహిళ", "విద్య",
            "అవార్డు", "కృషి", "ఆవిష్కరణ", "సాంకేతిక", "మంజూరు", "పెంపు", "భరోసా", "సంక్షేమ", "లక్ష")
# Outlets preferred first (Eenadu, Andhra Jyothy, then other mainstream Telugu outlets).
PREFERRED = ("ఈనాడు", "Eenadu", "ఆంధ్రజ్యోతి", "Andhra Jyothy", "Andhrajyothy", "సాక్షి_x", "Sakshi_x")
BLOCKED_PUBLISHERS = ("సాక్షి", "Sakshi")  # the opposition-run outlet; not used as a source


def is_positive(headline: str, summary: str = "") -> bool:
    text = f"{headline} {summary}"
    if any(x.casefold() in text.casefold() for x in EXCLUDE):
        return False
    return any(x in text for x in POSITIVE)


def is_go_ok(headline: str) -> bool:
    """A Government Order headline: no opposition names, tragedy or film words (EXCLUDE), and the order must be about
    something the government is giving, building or allowing (so a GO that merely bans or fines something is skipped)."""
    if any(x.casefold() in headline.casefold() for x in EXCLUDE) or any(b in headline for b in GO_BAD):
        return False
    if any(t in headline for t in TELANGANA):
        return False
    from channels.trending.regions import mentioned

    ap = any(a in headline for a in AP_WORDS) or bool(mentioned(headline))
    return ap and any(x in headline for x in POSITIVE + GO_BENEFIT)


AP_WORDS = ("ఏపీ", "ఆంధ్ర", "అమరావతి", "కూటమి", "చంద్రబాబు", "లోకేశ్", "పవన్", "రాష్ట్ర ప్రభుత్వం", "సీఎం")
TELANGANA = ("తెలంగాణ", "హైదరాబాద్", "రేవంత్", "కేసీఆర్", "కోదాడ", "హుజూర్", "టీజీ", "జీహెచ్ఎంసీ", "వరంగల్", "కరీంనగర్")


GO_BAD = ("నిషేధం", "జరిమానా", "సస్పెండ్", "బదిలీ", "బదిలీలు", "రద్దు", "పదవీ", "ఇన్‌చార్జ్", "నియామకం", "సీఎస్", "కార్యదర్శి")
GO_BENEFIT = ("విడుదల", "అనుమతి", "ఆమోదం", "కేటాయింపు", "ఉచిత", "రాయితీ", "సబ్సిడీ", "ప్రోత్సాహ", "పింఛన్", "ఆరోగ్య", "గ్రీన్ సిగ్నల్")


def political_stories(niche: str, lang: str = "te", days: int | None = None, queries=None) -> list[Story]:
    """Telugu Google News search for the niche's subject: positive, non-opposition headlines, preferred outlets first."""
    import urllib.parse

    queries = queries or POLITICAL_QUERY[niche]
    queries = [queries] if isinstance(queries, str) else queries
    found, seen = [], set()
    for text in queries:  # several searches per niche = a wider pool of the latest stories
        q = urllib.parse.quote(f"{text} when:{days or (30 if niche == 'local' else 3 if niche in ('ysrcp', 'counter') else 2)}d")   # the monthly local post may use a month-old story
        url = f"https://news.google.com/rss/search?q={q}&hl=te&gl=IN&ceid=IN:te"
        try:
            batch = parse_rss(_get(url))
        except Exception as exc:  # noqa: BLE001 - one failing query must not lose the others
            print(f"::warning::news query '{text}' failed: {type(exc).__name__}")
            continue
        for x in batch:
            if x.link not in seen:
                seen.add(x.link)
                found.append(x)
    out = [s for s in found if is_informative(s) and matches_language(s.headline, "te")
           and not any(b in s.publisher for b in BLOCKED_PUBLISHERS)
           and (is_go_ok(s.headline) if niche == "go" else is_positive(s.headline) if niche not in ("counter", "ysrcp") else
                (any(w in s.headline for w in COUNTER_REPLY) and not any(b in s.headline for b in COUNTER_BAD)) if niche == "counter" else
                (any(w in s.headline for w in YSRCP_REPORT) and not any(b in s.headline for b in YSRCP_BAD)))
           and (niche not in SUBJECT or any(w in s.headline for w in SUBJECT[niche]))]
    from channels.trending.regions import mentioned

    out.sort(key=lambda x: (0 if mentioned(x.headline) else 1, 0 if any(p in x.publisher for p in PREFERRED) else 1, x.rank))
    for i, x in enumerate(out, start=1):
        x.rank = i
    return out


@dataclass
class Story:
    headline: str
    publisher: str
    link: str
    published: datetime | None = None
    kind: str = "news"  # "news" | "yt"
    summary: str = ""   # the publisher's own one or two line summary (meta description), when available
    related: tuple = ()  # (headline, publisher) pairs from the same story cluster
    rank: int = 0        # position in the source's own trending order (1 = top); 0 = unknown

    @property
    def key(self) -> str:
        norm = re.sub(r"[\W_]+", " ", self.headline.casefold()).strip()[:90]
        return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]


def _strip_html(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def clean_title(title: str, publisher: str = "") -> str:
    """Drop the trailing ' - Publisher', hashtags, emoji-heavy tails and extra spaces."""
    t = _strip_html(title)
    if publisher and t.endswith(f" - {publisher}"):
        t = t[: -(len(publisher) + 3)]
    t = re.sub(r"#\S+", "", t)
    t = re.sub(r"[\U0001F000-\U0001FAFF☀-➿️]", "", t)
    t = re.sub(r"\s+", " ", t).strip(" -|:")
    return t


def parse_rss(xml_text: str) -> list[Story]:
    root = ET.fromstring(xml_text)
    out = []
    for position, item in enumerate(root.findall("./channel/item"), start=1):
        src = item.find("source")
        publisher = _strip_html(src.text) if src is not None and src.text else ""
        title = clean_title(item.findtext("title") or "", publisher)
        link = (item.findtext("link") or "").strip()
        when = None
        raw = (item.findtext("pubDate") or "").strip()
        if raw:
            try:
                when = email.utils.parsedate_to_datetime(raw)
            except (TypeError, ValueError):
                when = None
        if title and link:
            out.append(Story(title, publisher or "Google News", link, when, "news",
                             related=_related(item.findtext("description") or "", title), rank=position))
    return out


def _related(description_html: str, main_title: str) -> tuple:
    """Google News lists the other outlets' headlines for the same story in <description>. Real headlines only."""
    out = []
    for href_text, pub in re.findall(r"<a [^>]*>(.*?)</a>(?:&nbsp;|\s)*<font[^>]*>(.*?)</font>", description_html, re.S):
        head = clean_title(href_text, _strip_html(pub))
        pub = _strip_html(pub)
        if head and head.casefold() != main_title.casefold() and len(head) >= 18:
            out.append((head, pub))
    return tuple(out)


def is_informative(s: Story, min_chars: int = 18, min_words: int = 3) -> bool:
    h = s.headline.strip()
    if len(h) < min_chars or len(h.split()) < min_words or len(h) > 160:
        return False
    return h.casefold().rstrip(". ") != s.publisher.casefold().rstrip(". ")


def matches_language(text: str, lang: str) -> bool:
    """Native-script languages: at least a third of the letters are in that script. English: mostly ASCII letters."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    if lang == "en":
        return sum(c.isascii() for c in letters) / len(letters) > 0.9
    lo, hi = SCRIPT_RANGE[lang]
    return sum(lo <= ord(c) <= hi for c in letters) / len(letters) >= 0.33


def mostly_native(text: str, lang: str) -> bool:
    """Stricter than matches_language, for the card's body text: a Telugu card must not carry an English paragraph
    (some outlets put the English version of the story in their meta description). A few English words are fine
    (TDP, CM, MLA), but never more than 15% of the letters."""
    if lang == "en" or not matches_language(text, lang):
        return matches_language(text, lang)
    letters = [c for c in text if c.isalpha()]
    return sum(c.isascii() for c in letters) / len(letters) <= 0.15


def fresh_enough(s: Story, now: datetime, hours: int) -> bool:
    return s.published is None or now - s.published <= timedelta(hours=hours)


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def news_stories(niche: str, lang: str) -> list[Story]:
    if niche in POLITICAL_QUERY:
        return political_stories(niche, lang)
    hl, gl, ceid = EDITIONS[lang]
    url = (f"https://news.google.com/rss/headlines/section/topic/{NEWS_TOPIC[niche]}"
           f"?hl={hl}&gl={gl}&ceid={ceid}")
    # Google sometimes serves another language's outlet in an edition (a Hindi story in the kn feed): drop those,
    # otherwise the card shows glyphs the language's font lacks (boxes).
    return [s for s in parse_rss(_get(url)) if is_informative(s) and matches_language(s.headline, lang)]


def youtube_stories(yt, niche: str, lang: str) -> list[Story]:
    """Most popular videos in India right now, in this language. Surfaces the title and the creator's channel as the
    source; no footage is ever reused."""
    kw = dict(part="snippet", chart="mostPopular", regionCode="IN", maxResults=50)
    cat = YT_CATEGORY.get(niche)
    if cat:
        kw["videoCategoryId"] = cat
    items = yt.videos().list(**kw).execute().get("items", [])
    out = []
    for v in items:
        sn = v["snippet"]
        title = clean_title(sn.get("title", ""))
        if not matches_language(title, lang):
            continue
        when = None
        try:
            when = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            pass
        s = Story(title, sn.get("channelTitle", "YouTube"), f"https://www.youtube.com/watch?v={v['id']}", when, "yt")
        if is_informative(s):
            s.rank = len(out) + 1  # position among the language's trending videos
            out.append(s)
    return out


def _meta_description(page_html: str) -> str:
    for pat in (r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
                r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:description["\']',
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']'):
        m = re.search(pat, page_html, re.S | re.I)
        if m:
            return re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()
    return ""


def trim(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.:;-") + "…"


_ELLIPSIS = re.compile(r"\s*(\.{2,}|…)\s*$")
_STOPS = "?!.।|"
_SOFT = ":;,–—"


def complete(text: str, limit: int, soft: bool = True) -> str:
    """Text that ends cleanly, never with '…' or a half sentence. A source that already cut its own text ('...')
    loses the dangling fragment; text over `limit` is cut back to the last full sentence (or, for headlines, the
    last clause). Returns '' when nothing complete is left (callers then show less rather than a broken line)."""
    text = re.sub(r"\s+", " ", text or "").strip()
    cut = bool(_ELLIPSIS.search(text))
    text = _ELLIPSIS.sub("", text)
    if cut or len(text) > limit:
        window = text[:limit] if not cut or len(text) > limit else text
        stops = _STOPS + (_SOFT if soft else "")
        i = max(window.rfind(c) for c in stops)
        if i < len(window) * 0.35:  # no usable boundary: a headline keeps its words, a summary is dropped
            if not soft:
                return ""
            return window.rsplit(" ", 1)[0].rstrip(",.:;-–—|")
        text = window[: i + 1] if text[i] in _STOPS else window[:i]
    return text.strip().rstrip(":;,–—|").strip()


def article_summary(link: str, lang: str, headline: str, timeout: int = 15) -> str:
    """The publisher's own summary line (its meta description) for the story, or ''. Resolves Google News' encoded
    link first. Never copies article body text. Any failure returns ''."""
    try:
        from googlenewsdecoder import gnewsdecoder

        res = gnewsdecoder(link, interval=1)
        ok = res.get("status", res.get("success"))  # the decoder library reports it as "success" in newer versions
        url = res.get("decoded_url") if ok else ""
        if not url:
            print(f"::notice::no summary (link not decoded: {str(res)[:120]})")
            return ""
        page = _get(url, timeout)[:400_000]
        text = _meta_description(page)
        if not text or not mostly_native(text, lang) or text.casefold().startswith(headline.casefold()[:40]):
            print(f"::notice::no summary (page meta unusable: {text[:60]!r})")
            return ""
        return complete(text, 400, soft=False)
    except Exception as exc:  # noqa: BLE001
        print(f"::notice::no summary ({type(exc).__name__}: {exc})")
        return ""


TEASER = ("ప్రత్యేకతలివే", "ప్రత్యేకతలు ఇవే", "ఇవే", "ఇదే", "తెలుసా", "ఏంటో", "ఎవరో", "చూడండి", "ఎందుకంటే", "అసలు కారణం")


def has_substance(story: Story) -> bool:
    """A news card must carry facts, not a promise. Needs the publisher's own summary; a headline that teases
    ('ప్రత్యేకతలివే', 'తెలుసా') needs a fuller one so the card actually lists what it promised."""
    if story.kind != "news":
        return True
    summary = (story.summary or "").strip()
    if len(summary) < 60:
        return False
    if any(w in story.headline for w in TEASER) and len(summary) < 110:
        return False
    return True


def enrich(story: Story, lang: str) -> Story:
    """Add reading matter: the publisher's summary and up to four related headlines in the same language."""
    if story.kind == "news":
        story.summary = article_summary(story.link, lang, story.headline)
    story.related = tuple((complete(h, 160), p) for h, p in story.related if matches_language(h, lang) and complete(h, 160))[:4]
    return story


# 2026-10-25: what the channel's own views say. 20-22 Oct posts on these got 1,000-2,700 views each; 24 Oct posts on
# single-town local-body items (Nellore, Kurnool, one corporator's appeal) got 3-27. Rank hot stories first.
HOT = ("అమరావతి", "లోకేశ్", "లోకేష్", "క్వాంటమ్", "టవర్", "జగన్", "అవినాష్", "పులివెందుల", "బోండా", "పల్లా", "డీఎస్పీ", "ఫేక్",
       "కౌంటర్", "నామినేషన్", "పెట్టుబడి", "ఉద్యోగ", "ఎన్టీఆర్", "పవన్", "మంత్రి లోకేశ్", "సంగమం", "కార్నివాల్", "ట్విన్")
COLD = ("కార్పొరేటర్", "గెలుపునకు కృషి", "పిలుపు", "కర్నూలు", "నెల్లూరు", "Nellore", "డివిజన్", "వార్డు", "సస్పెండ్", "కాకినాడ", "ఒంగోలు")


def heat(s: Story) -> int:
    """Positive = historically high-view subject, negative = single-town or routine party item."""
    t = s.headline
    return sum(2 for x in HOT if x in t) - sum(3 for x in COLD if x in t)


def pick_story(niche: str, lang: str, used: set[str], yt=None, now: datetime | None = None,
               fetch_news=news_stories, fetch_yt=youtube_stories, fetch_bank=None, recent=()) -> Story | None:
    """First unused, informative, recent story for this niche and language. Tries the niche's sources in order, then
    widens the freshness window from 8 to 30 hours. Returns None when nothing qualifies."""
    now = now or datetime.now(timezone.utc)
    pools: list[list[Story]] = []
    if fetch_bank is None:
        from channels.trending.bank import bank_stories as fetch_bank
    for src in SOURCE_ORDER.get(niche, DEFAULT_ORDER):
        try:
            if src == "bank":
                pools.append(fetch_bank(niche))
            elif src == "news":
                pools.append(fetch_news(niche, lang))
            elif yt is not None:
                pools.append(fetch_yt(yt, niche, lang))
        except Exception as exc:  # noqa: BLE001 - one failing source must not stop the slot
            print(f"::warning::{src} source failed for {niche}/{lang}: {type(exc).__name__}: {exc}")
    for hours in ((720,) if niche == "local" else (8, 30, 72) if niche in ("ysrcp", "counter") else (8, 30)):
        for pool in pools:
            # Only the source's top 10. Widest coverage first (most outlets carrying the story = most reach), then
            # shorter headlines (they read better on a 5 second card), then the source's own order.
            top = [x for x in pool if 0 < x.rank <= TOP_N or x.rank == 0]
            ordered = top if niche == "ntr" else sorted(top, key=lambda x: (-heat(x), -len(x.related), len(x.headline) > 85, x.rank))
            for s in ordered:
                if s.key in used or not fresh_enough(s, now, hours):
                    continue
                if recent and s.kind in ("news", "yt") and dedupe.is_duplicate(s.headline, s.link, recent):
                    continue  # the same story worded by another outlet
                return s
    return None
