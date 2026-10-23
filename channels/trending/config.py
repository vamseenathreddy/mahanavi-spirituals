"""Languages, niches, labels, playlists text and render config for the trending-news Shorts channel.

One channel, six languages, seven niches. Each (niche, language) pair has its own playlist. Everything on the card is
text over a niche-coloured gradient with the channel's own approved music, under 5 seconds."""
from __future__ import annotations

import dataclasses
from pathlib import Path

from channels.engine.render import ChannelConfig, TextBlock
from channels.trending import portraits

REPO_ROOT = Path(__file__).resolve().parents[2]
CHANNEL_DIR = Path(__file__).resolve().parent
FONTS = REPO_ROOT / "channels/engine/assets/fonts"

BRAND = "Pulse TDP Fans"
HANDLE = "@PulseTDPFans"
LANGS = ["te"]          # 2026-10-17: Telugu only (TDP-supportive channel)
NICHES = ["chandrababu", "lokesh", "tdp", "nda", "development", "innovations", "join", "voice", "counter", "amaravati", "local", "ntr", "ysrcp"]   # Janasena is switched off: TDP-only channel
# 2026-10-18: 6 posts a day for now (was 12). One day = these 6 posts in order, repeating daily:
# 2026-10-18 (later): CURRENT NEWS ONLY, no old achievements. Every post is a fresh headline raised in the voice of a
# hardcore fan (Babu's stage style: "తమ్ముళ్లూ", "తెలుగుదేశం అభిమానులారా"), and one post a day answers
# negative propaganda with a fact. The evergreen bank niches (innovations, join, voice) are not in the rotation.
# 2026-10-18 (focus): Amaravati, Lokesh helping people and rising, positive Nuzvid and Chatrai news.
# Nuzvid and Chatrai ("local") are not in the daily pattern: one post a month, on the 1st (see plan()).
NTR_ENABLED = False   # 2026-10-23: NTR Shorts got 13/31/99 views vs 1.5k+ for news cards, so they are off (flip to True to bring them back)
DAY_PATTERN = ["amaravati", "lokesh", "chandrababu", "development", "counter", "lokesh"]   # 2026-10-22: ysrcp paused, reach test
NEWS_NICHES = ["amaravati", "lokesh", "chandrababu", "counter", "tdp", "nda", "development"]   # "local" only posts monthly   # the only niches that may post

LANG_EN = {"te": "Telugu", "hi": "Hindi", "en": "English", "ta": "Tamil", "kn": "Kannada", "ml": "Malayalam"}
LANG_NATIVE = {"te": "తెలుగు", "hi": "हिन्दी", "en": "English", "ta": "தமிழ்", "kn": "ಕನ್ನಡ", "ml": "മലയാളം"}
NICHE_EN = {"chandrababu": "Chandrababu Naidu", "lokesh": "Nara Lokesh", "tdp": "Telugu Desam Party",
            "nda": "NDA Alliance", "development": "AP Development", "innovations": "CM Innovations",
            "join": "Join TDP", "voice": "Your Constituency", "counter": "Facts and Answers",
            "amaravati": "Amaravati", "local": "Nuzvid and Chatrai", "ntr": "NTR and TDP History", "ysrcp": "YSRCP Misrule Exposed"}
NICHE_TAG = {"chandrababu": "ChandrababuNaidu", "lokesh": "NaraLokesh", "tdp": "TDP", "nda": "NDAAlliance",
             "development": "APDevelopment", "innovations": "Innovations",
             "join": "JoinTDP", "voice": "MyConstituency", "counter": "TDPFacts",
             "amaravati": "Amaravati", "local": "Nuzvid", "ntr": "NTR", "ysrcp": "YSRCPFailures"}
NICHE_NATIVE = {
    "te": ["చంద్రబాబు", "నారా లోకేశ్", "తెలుగుదేశం", "కూటమి", "అభివృద్ధి", "ఆవిష్కరణలు", "టీడీపీలో చేరండి", "మీ నియోజకవర్గం", "నిజం చెబుదాం", "అమరావతి", "నూజివీడు, చాట్రాయి", "ఎన్టీఆర్, తెలుగుదేశం చరిత్ర", "వైసీపీ బండారం"],
    "en": list(NICHE_EN.values()),
}
LANG_TAG = {"te": "TeluguNews", "en": "IndiaNews"}
# Join links for the community channels. Fill in when the user creates them; empty = line omitted.
# YouTube @handles to tag in every description and pinned comment (CMO, Chandrababu, Lokesh, TDP leaders and pages).
# Only exact, official handles, e.g. "@example". Left empty until verified.
MENTIONS: list[str] = []
WHATSAPP_URL = "https://chat.whatsapp.com/E70aL6tTrzT4eftmUV9npI"
TELEGRAM_URL = "https://t.me/PulseBoostingTDP"
# (subscribe line, join-groups line, comment line), drawn under the headline
CTA = {
    "te": ("తమ్ముళ్లూ, ఇలాంటి వార్తల కోసం ఛానల్‌ను సబ్‌స్క్రైబ్ చేయండి", "వాట్సాప్, టెలిగ్రామ్ గ్రూపుల్లో చేరండి",
           "ఇలాంటి వార్తల కోసం ఛానల్‌ను సబ్‌స్క్రైబ్ చేయండి"),
    "en": ("6 Telugu updates daily. Subscribe", "Join our WhatsApp and Telegram groups",
           "You may never see this channel again unless you subscribe right now"),
}
INTRO = {
    "te": "తెలుగుదేశం, చంద్రబాబు, లోకేశ్ గారి పాలన, అభివృద్ధిపై వార్తలు. రోజుకు 6 షార్ట్స్.",
    "en": "News on TDP, Chandrababu Naidu, Nara Lokesh and Andhra Pradesh development. 6 Shorts a day.",
}

# (window start hour IST, slot id): one post every 2 hours from midnight, at a random minute inside the first
# 40 minutes of its window. The language rotates each post, so the first six posts (00:00 to 10:00) cover all six.
SLOTS = [(2 * i, f"t{i + 1}") for i in range(12)]
WINDOW_MINUTES = 40
# Only these slots post (the other workflows still get pinged and skip at the gate). Raise back to all 12 to double the volume.
ACTIVE_SLOTS = {"t1", "t4", "t5", "t7", "t10", "t11"}   # 00:00, 06:00, 08:00, 12:00, 18:00, 20:00 IST

WHITE, GOLD, SOFT = (255, 255, 255), (255, 210, 120), (225, 220, 225)
INK, RED, BROWN = (28, 8, 0), (150, 10, 20), (70, 30, 0)   # dark text on the TDP-yellow cards
_YELLOW = ((255, 222, 20), (250, 190, 0))
PALETTES = {k: _YELLOW for k in NICHES}
ACCENT = {k: RED for k in NICHES}
PALETTES["janasena"] = ((120, 8, 20), (206, 28, 40))   # Janasena cards: red background, white text
ACCENT["janasena"] = (255, 214, 0)


def _fonts(lang: str):
    """(font for all text, native-script font to mix in or ''). Hind covers Devanagari and Latin; the Noto Tamil,
    Kannada and Malayalam fonts also carry Latin, digits and punctuation, so they need no mixing. Telugu keeps
    plain Ponnala for Telugu characters (standing rule) over a Latin-capable Noto font."""
    latin = REPO_ROOT / "assets/fonts/NotoSansTelugu-Variable.ttf"
    if lang == "hi":
        return FONTS / "Hind-Bold.ttf", ""
    if lang == "en":
        return latin, ""
    if lang == "te":
        return latin, str(REPO_ROOT / "assets/fonts/Ponnala-Regular.ttf")
    raise ValueError(f"unsupported language {lang}")


def render_cfg(lang: str, niche: str) -> ChannelConfig:
    main, native = _fonts(lang)
    label_font = FONTS / "Hind-Bold.ttf" if lang == "hi" else main
    accent = ACCENT[niche]
    layouts = [dict(anchor=a, primary=p, secondary=BROWN, accent=accent, ornament=o)
               for a, p, o in ((0.44, INK, True), (0.42, (90, 0, 10), False), (0.46, INK, True))]
    if niche == "janasena":
        layouts = [dict(anchor=a, primary=WHITE, secondary=(255, 232, 232), accent=accent, ornament=o)
                   for a, o in ((0.44, True), (0.42, False), (0.46, True))]
    return ChannelConfig(
        channel_name=BRAND,
        assets_dir=CHANNEL_DIR / "assets",
        # 2026-10-17: no "TRENDING #n" label on the Short (rank and niche live in the description); bigger text,
        # more reading matter (summary + up to four related headlines) filling the space the label and big logo used.
        blocks=[TextBlock(field="text_primary", font=main, size=96, color_key="primary", bold=True),
                TextBlock(field="text_summary", font=main, size=78, color_key="secondary", bold=False),
                TextBlock(field="text_related", font=main, size=74, color_key="secondary", bold=False)],
        corner_field="text_secondary",
        bg_overlay=portraits.make_overlay(str(main)),
        text_shadow=False,
        scrim=False,
        font_channel_label=main,
        telugu_font=native,
        music_glob="music/approved/*.mp3",
        music_rotate=True,
        logo_path=str(CHANNEL_DIR / "assets/logo.png"),
        watermark_handle=HANDLE,
        safe_bottom=1290,
        text_max_w=880,
        text_anchor=0.46,
        cta_text=CTA[lang][0],  # subscribe line only (no join-groups line on the card)
        cta_size=38,
        cta_max_w=960,
        logo_width=170,
        logo_y=235,
        safe_top=330,
        layouts=layouts,
        palettes=[PALETTES[niche]],
    )


def niche_label(lang: str, niche: str) -> str:
    return NICHE_NATIVE[lang][NICHES.index(niche)]


def plan(seq: int, day=None, state: dict | None = None) -> tuple[str, str]:
    """(language, niche) for the seq-th post: Telugu always; niches follow DAY_PATTERN. On the 1st of a month, the
    third post of the day is the monthly Nuzvid and Chatrai post, once (state['local_month'] remembers it)."""
    niche = DAY_PATTERN[seq % len(DAY_PATTERN)]
    if NTR_ENABLED and day is not None and seq % len(DAY_PATTERN) == 3 and day.toordinal() % 2 == 0:
        niche = "ntr"   # every other day the fourth post is NTR and Telugu Desam history instead of a news post
    if day is not None and day.day == 1 and seq % len(DAY_PATTERN) == 2 and (state or {}).get("local_month") != day.strftime("%Y-%m"):
        niche = "local"
    return LANGS[0], niche


def playlist_for(lang: str, niche: str) -> tuple[str, str]:
    nat, en = niche_label(lang, niche), NICHE_EN[niche]
    title = f"{en} | {nat} (Telugu) - {BRAND}"[:150]
    desc = (f"{INTRO[lang]}\n\nSourced coverage of {en} in Telugu. Every Short names its source and links "
            f"the original story. Subscribe to {BRAND}.\n\n"
            f"#{NICHE_TAG[niche]} #{LANG_TAG[lang]} #TDP #Shorts #PulseTDPFans")
    return title, desc
