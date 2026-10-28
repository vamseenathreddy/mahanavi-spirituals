"""Viewer-request Shorts: a one-off mantra Short made because a viewer asked for it in the comments
(first one: "Narsimha Swamy mantram send me", 2026-10-09). The Short is tagged to the viewer, uses a
background colour no scheduled Short uses, and is uploaded PRIVATE so the owner can verify it in
Studio before publishing.

Each request is a `RequestShort` spec: the slides (intro, one per mantra, outro), the SEO and the
reply text for the viewer's comment. Add a new spec to SPECS to make the next one.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mahanavi.content.alert_seo import _CHANNEL_FOOTER_EN, _CHANNEL_FOOTER_TE
from mahanavi.content.branding import BRAND_NAME


@dataclass(frozen=True)
class Slide:
    """kind "intro": label = small gold top line, text = title, translit = sub line, meaning = gold last line.
    kind "mantra": label = heading, text = the mantra, translit = English transliteration, meaning = one line.
    kind "points": label = heading, text = several points ("\n" separated), shown one per block.
    kind "outro": label = heading, text = up to 3 closing lines ("\n" separated); the CTA lines come from the spec."""
    kind: str
    seconds: float
    label: str = ""
    text: str = ""
    translit: str = ""
    meaning: str = ""
    benefits: tuple[str, ...] = ()   # kind "mantra": "who it is for" lines, drawn big under the mantra


@dataclass(frozen=True)
class RequestShort:
    slug: str
    handle: str               # the viewer's @handle, shown on the Short and tagged in the description ("" = none)
    comment_id: str           # the viewer's comment (for the reply once the Short is public)
    deity_te: str
    bg_top: tuple[int, int, int]
    bg_mid: tuple[int, int, int]
    bg_bottom: tuple[int, int, int]
    glow: tuple[int, int, int]
    slides: tuple[Slide, ...]
    title: str
    description_te: str
    description_en: str
    title_en: str
    hashtags: list[str]
    tags: list[str] = field(default_factory=list)
    lang: str = "te"                      # "te" Telugu (Ponnala) | "hi" Hindi (Hind)
    token_file: str = "youtube_token.json"
    expected_channel: str = "Mahanavi"    # refuse to upload unless the token's channel title contains this
    watermark: str = "@MahanaviSpirituals"
    header: str = ""                      # small line at the top of the mantra/points slides
    playlist_line: str = ""              # lines drawn just above the subscribe reminder (playlist pointer)
    cta_lines: tuple[str, ...] = ()       # closing lines on the outro (comment + subscribe)
    tag_footer: str = ""                  # footer on mantra slides ("" = none)
    footer_main: str = _CHANNEL_FOOTER_TE
    footer_en: str = _CHANNEL_FOOTER_EN
    bg_image: str = ""                    # file under assets/images/ used as the (dimmed) background; "" = plain gradient

    @property
    def total_seconds(self) -> float:
        return sum(s.seconds for s in self.slides)

    def description(self) -> str:
        return (f"{self.description_te}\n\n{self.footer_main}\n\n---\n\n{self.description_en}\n\n"
                f"{self.footer_en}\n\n{' '.join(self.hashtags)}")

    def reply_text(self, video_url: str) -> str:
        """Reply to the viewer's own comment once the Short is public."""
        return (f"{self.handle} మీరు అడిగిన {self.deity_te} మంత్రాలను ఈ వీడియోలో అందించాం 🙏 "
                f"బీజ మంత్రం, గాయత్రి, మహా మంత్రం అన్నీ ఉన్నాయి. చూడండి: {video_url}")

    def first_comment(self) -> str:
        lines = "\n".join(f"{s.label}: {s.text.replace(chr(10), ' ')}" for s in self.slides if s.kind == "mantra")
        return (f"🙏 {self.handle} గారి కోరిక మేరకు {self.deity_te} మంత్రాలు:\n\n{lines}\n\n"
                "ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు 🙏")


HANDLE = "@SsudharshanSsudharshan-h7n"

_NARASIMHA_SLIDES = (
    Slide("intro", 3.5, "మీ కోరిక మేరకు", "శ్రీ నరసింహ స్వామి\nమంత్రాలు", "బీజ మంత్రంతో సహా 4 మంత్రాలు", HANDLE),
    Slide("mantra", 5.5, "బీజ మంత్రం", "ఓం నృం నృం నృం నరసింహాయ నమః",
          "Om Nrim Nrim Nrim Narasimhaya Namah",
          "నరసింహ బీజాక్షరాలు: నృం · క్ష్రౌం"),
    Slide("mantra", 5.5, "మూల మంత్రం", "ఓం నమో భగవతే నరసింహాయ",
          "Om Namo Bhagavate Narasimhaya",
          "భగవంతుడైన నరసింహ స్వామికి నమస్కారం"),
    Slide("mantra", 7.5, "నరసింహ గాయత్రి", "ఓం వజ్రనఖాయ విద్మహే\nతీక్ష్ణదంష్ట్రాయ ధీమహి\nతన్నో నృసింహః ప్రచోదయాత్",
          "Om Vajranakhaya Vidmahe, Tikshna Damshtraya Dhimahi, Tanno Narasimhah Prachodayat",
          "వజ్రాల వంటి గోళ్లు, వాడి కోరలు గల నరసింహుడిని ధ్యానిస్తున్నాం"),
    Slide("mantra", 7.5, "మహా మంత్రం", "ఉగ్రం వీరం మహావిష్ణుం జ్వలంతం సర్వతోముఖమ్\nనృసింహం భీషణం భద్రం మృత్యుమృత్యుం నమామ్యహమ్",
          "Ugram Veeram Maha Vishnum Jwalantam Sarvato Mukham, Nrisimham Bhishanam Bhadram Mrityu-Mrityum Namamyaham",
          "మృత్యువుకే మృత్యువైన శుభకరుడు నృసింహునికి నమస్కారం"),
    Slide("outro", 4.5, "ఎలా చదవాలి?", "ప్రతి మంత్రం 11, 21 లేదా 108 సార్లు\nశనివారం, నరసింహ జయంతి రోజున చదవడం శుభప్రదం\nశుభ్రంగా, ప్రశాంతంగా కూర్చుని చదవండి"),
)

_DESC_TE = f"""🙏 {HANDLE} గారి కోరిక మేరకు శ్రీ నరసింహ స్వామి మంత్రాలు (బీజ మంత్రంతో సహా)

1) బీజ మంత్రం: ఓం నృం నృం నృం నరసింహాయ నమః
2) మూల మంత్రం: ఓం నమో భగవతే నరసింహాయ
3) నరసింహ గాయత్రి: ఓం వజ్రనఖాయ విద్మహే తీక్ష్ణదంష్ట్రాయ ధీమహి తన్నో నృసింహః ప్రచోదయాత్
4) మహా మంత్రం: ఉగ్రం వీరం మహావిష్ణుం జ్వలంతం సర్వతోముఖమ్ | నృసింహం భీషణం భద్రం మృత్యుమృత్యుం నమామ్యహమ్

ఎలా చదవాలి: శుభ్రంగా, ప్రశాంతంగా కూర్చుని ప్రతి మంత్రం 11, 21 లేదా 108 సార్లు చదవండి. శనివారం మరియు నరసింహ జయంతి రోజున చదవడం శుభప్రదమని సంప్రదాయం. ఉచ్చారణ కోసం గురువు లేదా పెద్దల వద్ద నేర్చుకోవడం మంచిది.

ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు. మరిన్ని మంత్రాల కోసం మహానవి స్పిరిచువల్స్ ఛానల్‌ను సబ్‌స్క్రైబ్ చేయండి 🙏"""

_DESC_EN = f"""Narasimha Swamy mantras, including the Beeja (seed) mantra, made on request for {HANDLE}.

1) Beeja mantra: Om Nrim Nrim Nrim Narasimhaya Namah
2) Moola mantra: Om Namo Bhagavate Narasimhaya
3) Narasimha Gayatri: Om Vajranakhaya Vidmahe, Tikshna Damshtraya Dhimahi, Tanno Narasimhah Prachodayat
4) Maha mantra: Ugram Veeram Maha Vishnum Jwalantam Sarvato Mukham, Nrisimham Bhishanam Bhadram Mrityu-Mrityum Namamyaham

How to chant: sit calmly in a clean place and chant each mantra 11, 21 or 108 times. Saturdays and Narasimha Jayanti are traditionally considered auspicious. Learn the pronunciation from a guru or elder if you can.

You may never see this channel again unless you subscribe right now. Subscribe to {BRAND_NAME} for more mantras."""

NARASIMHA = RequestShort(
    slug="narasimha_mantras",
    handle=HANDLE,
    comment_id="UgxXYvZw2NgMcZ7F28d4AaABAg",
    deity_te="శ్రీ నరసింహ స్వామి",
    bg_top=(6, 14, 52), bg_mid=(14, 40, 116), bg_bottom=(6, 18, 60), glow=(255, 176, 64),
    slides=_NARASIMHA_SLIDES,
    title="నరసింహ స్వామి బీజ మంత్రం + 3 మంత్రాలు | Narasimha Mantra",
    title_en="Narasimha Swamy Beeja Mantra + 3 Powerful Mantras | Narasimha Gayatri",
    description_te=_DESC_TE,
    description_en=_DESC_EN,
    header="శ్రీ నరసింహ స్వామి",
    cta_lines=("ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు", "మరిన్ని మంత్రాల కోసం సబ్‌స్క్రైబ్ చేయండి"),
    tag_footer=f"{HANDLE} గారి కోరిక మేరకు",
    hashtags=["#Shorts", "#నరసింహస్వామి", "#NarasimhaMantra", "#NarasimhaSwamy", "#Devotional"],
    tags=[
        "narasimha mantra", "narasimha swamy mantram", "narasimha beeja mantra", "narasimha gayatri",
        "ugram veeram mahavishnum", "lakshmi narasimha mantra", "narasimha mantra telugu",
        "నరసింహ స్వామి మంత్రం", "నరసింహ మంత్రం", "నరసింహ బీజ మంత్రం", "నరసింహ గాయత్రి",
        "నరసింహ జయంతి", "telugu devotional", "mahanavi spirituals", "shorts",
    ],
)

# ---- Shani Amavasya, Saturday 10 Oct 2026 (Amavasya tithi 9 Oct 9:37 PM to 10 Oct 9:21 PM IST, Hyderabad) ----
# Saturn is in Meena (Pisces) until about mid-2027: Sade Sati = Mesha, Meena, Kumbha; Ashtama Shani = Simha;
# Ardhashtama (4th) = Dhanussu (see content/rashi_current_transits.py).
_SHANI_BG: dict[str, Any] = dict(bg_top=(8, 8, 16), bg_mid=(26, 28, 58), bg_bottom=(8, 8, 16), glow=(130, 150, 255))

SHANI_TE = RequestShort(
    slug="shani_amavasya_te", handle="", comment_id="", deity_te="శని దేవుడు", **_SHANI_BG,
    slides=(
        Slide("intro", 3.5, "శనివారం · 10 అక్టోబర్ 2026", "శని అమావాస్య", "అమావాస్య: శుక్రవారం రాత్రి 9:37 నుండి శనివారం రాత్రి 9:21 వరకు", "శని దేవుని అనుగ్రహం కోసం"),
        Slide("points", 6.5, "ప్రాముఖ్యత", "శనివారం మరియు అమావాస్య కలిసి రావడం శని దేవుని పూజకు ప్రత్యేకమైన రోజు\nఈ రోజున పితృ దేవతలకు తర్పణం ఇవ్వడం కూడా శుభప్రదమని సంప్రదాయం"),
        Slide("points", 8.5, "ఏం చేయాలి?", "ఉదయం స్నానం చేసి శని దేవుని ధ్యానించండి\nసాయంత్రం నువ్వుల నూనె దీపం వెలిగించండి (రావి చెట్టు కింద లేదా శని ఆలయంలో)\nనల్ల నువ్వులు, మినుములు, ఇనుము, నల్లని వస్త్రం దానం చేయండి\nపెద్దలకు, శ్రామికులకు సేవ చేయండి"),
        Slide("points", 7.5, "ఏ రాశులపై ప్రభావం?", "ఏలినాటి శని: మేషం, మీనం, కుంభం\nఅష్టమ శని: సింహం\nఅర్ధాష్టమ శని: ధనుస్సు\nశని ప్రస్తుతం మీన రాశిలో ఉన్నాడు"),
        Slide("mantra", 7.0, "శని బీజ మంత్రం", "ఓం ప్రాం ప్రీం ప్రౌం సః శనయే నమః", "Om Pram Preem Proum Sah Shanaye Namah", "108 సార్లు జపించండి (కనీసం 11 సార్లు)"),
        Slide("outro", 4.0, "జై శని దేవా", "శని అమావాస్య శుభాకాంక్షలు"),
    ),
    title="శని అమావాస్య 10 అక్టోబర్: ప్రాముఖ్యత, చేయాల్సినవి, రాశులు | Shani Amavasya",
    title_en="Shani Amavasya 10 Oct 2026: Importance, Remedies, Affected Rashis, Mantra",
    description_te="""🙏 శని అమావాస్య: శనివారం, 10 అక్టోబర్ 2026
అమావాస్య తిథి: శుక్రవారం రాత్రి 9:37 నుండి శనివారం రాత్రి 9:21 వరకు (హైదరాబాద్).

ప్రాముఖ్యత: శనివారం మరియు అమావాస్య కలిసి రావడం శని దేవుని పూజకు, పితృ తర్పణానికి విశేషమైన రోజని సంప్రదాయం.

ఏం చేయాలి:
• ఉదయం స్నానం చేసి శని దేవుని ధ్యానించండి
• సాయంత్రం నువ్వుల నూనె దీపం వెలిగించండి (రావి చెట్టు కింద లేదా శని ఆలయంలో)
• నల్ల నువ్వులు, మినుములు, ఇనుము, నల్లని వస్త్రం దానం చేయండి
• పెద్దలకు, శ్రామికులకు సేవ చేయండి
• పితృ దేవతలకు తర్పణం ఇవ్వండి

ఏ రాశులపై ప్రభావం (శని ప్రస్తుతం మీన రాశిలో):
ఏలినాటి శని: మేషం, మీనం, కుంభం
అష్టమ శని: సింహం
అర్ధాష్టమ శని: ధనుస్సు

శని బీజ మంత్రం: ఓం ప్రాం ప్రీం ప్రౌం సః శనయే నమః
108 సార్లు జపించండి (కనీసం 11 సార్లు), ప్రశాంతంగా మాలతో.

ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు 🙏""",
    description_en="""Shani Amavasya, Saturday 10 October 2026 (Amavasya from Fri 9:37 PM to Sat 9:21 PM IST).

Why it matters: Saturday plus Amavasya is traditionally a special day for Shani worship and ancestor offerings (tarpan).
What to do: bathe and meditate on Shani Dev; light a sesame-oil lamp in the evening (under a peepal tree or at a Shani temple); donate black sesame, black urad, iron and black cloth; help elders and workers; offer tarpan to ancestors.
Rashis under Saturn's influence (Saturn is in Meena): Sade Sati - Mesha, Meena, Kumbha; Ashtama Shani - Simha; Ardhashtama - Dhanussu.
Shani beeja mantra: Om Pram Preem Proum Sah Shanaye Namah - chant 108 times (at least 11).""",
    hashtags=["#Shorts", "#శనిఅమావాస్య", "#ShaniAmavasya", "#శనిదేవుడు", "#Devotional"],
    tags=["shani amavasya", "shani amavasya 2026", "shani amavasya telugu", "shani mantra", "shani beeja mantra",
          "sade sati", "ఏలినాటి శని", "శని అమావాస్య", "శని మంత్రం", "శని దేవుడు", "10 october 2026 amavasya",
          "telugu devotional", "mahanavi spirituals", "shorts"],
    header="శని అమావాస్య",
    cta_lines=("ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు", "మరిన్ని మంత్రాల కోసం సబ్‌స్క్రైబ్ చేయండి"),
)

_HI_FOOTER = """🎬 और भक्ति Shorts देखें: https://www.youtube.com/@divinemantrasangam/shorts

दिव्य मंत्र संगम - हिंदी भक्ति चैनल। रोज़ राहु काल, शुभ मुहूर्त, दुर्मुहूर्त, मंत्र और पौराणिक कथाएं। सनातन धर्म को सबके करीब लाना हमारा उद्देश्य है।"""

SHANI_HI = RequestShort(
    slug="shani_amavasya_hi", handle="", comment_id="", deity_te="शनिदेव", **_SHANI_BG,
    slides=(
        Slide("intro", 3.5, "शनिवार · 10 अक्टूबर 2026", "शनि अमावस्या", "अमावस्या: शुक्रवार रात 9:37 से शनिवार रात 9:21 तक", "शनिदेव की कृपा के लिए"),
        Slide("points", 6.5, "महत्व", "शनिवार और अमावस्या का संयोग शनिदेव की पूजा के लिए विशेष माना जाता है\nइस दिन पितरों का तर्पण भी शुभ माना जाता है"),
        Slide("points", 8.5, "क्या करें?", "सुबह स्नान कर शनिदेव का ध्यान करें\nशाम को तिल या सरसों के तेल का दीपक जलाएं (पीपल के नीचे या शनि मंदिर में)\nकाले तिल, उड़द, लोहा और काला वस्त्र दान करें\nबुजुर्गों और श्रमिकों की सेवा करें"),
        Slide("points", 7.5, "किन राशियों पर प्रभाव?", "साढ़े साती: मेष, मीन, कुंभ\nअष्टम शनि (ढैय्या): सिंह\nचतुर्थ शनि (ढैय्या): धनु\nशनि अभी मीन राशि में हैं"),
        Slide("mantra", 7.0, "शनि बीज मंत्र", "ॐ प्रां प्रीं प्रौं सः शनये नमः", "Om Pram Preem Proum Sah Shanaye Namah", "108 बार जपें (कम से कम 11 बार)"),
        Slide("outro", 4.0, "जय शनिदेव", "शनि अमावस्या की शुभकामनाएं"),
    ),
    title="शनि अमावस्या 10 अक्टूबर: महत्व, उपाय, राशियां और मंत्र | Shani Amavasya",
    title_en="Shani Amavasya 10 Oct 2026: Importance, Remedies, Affected Rashis, Mantra",
    description_te="""🙏 शनि अमावस्या: शनिवार, 10 अक्टूबर 2026
अमावस्या तिथि: शुक्रवार रात 9:37 से शनिवार रात 9:21 तक।

महत्व: शनिवार और अमावस्या का संयोग शनिदेव की पूजा और पितृ तर्पण के लिए विशेष माना जाता है।

क्या करें:
• सुबह स्नान कर शनिदेव का ध्यान करें
• शाम को तिल या सरसों के तेल का दीपक जलाएं (पीपल के नीचे या शनि मंदिर में)
• काले तिल, उड़द, लोहा और काला वस्त्र दान करें
• बुजुर्गों और श्रमिकों की सेवा करें
• पितरों का तर्पण करें

किन राशियों पर प्रभाव (शनि अभी मीन राशि में):
साढ़े साती: मेष, मीन, कुंभ
अष्टम शनि (ढैय्या): सिंह
चतुर्थ शनि (ढैय्या): धनु

शनि बीज मंत्र: ॐ प्रां प्रीं प्रौं सः शनये नमः
108 बार जपें (कम से कम 11 बार), शांत मन से माला पर।

अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे 🙏""",
    description_en="""Shani Amavasya, Saturday 10 October 2026 (Amavasya from Fri 9:37 PM to Sat 9:21 PM IST).

Why it matters: Saturday plus Amavasya is traditionally a special day for Shani worship and ancestor offerings (tarpan).
What to do: bathe and meditate on Shani Dev; light a sesame or mustard oil lamp in the evening; donate black sesame, black urad, iron and black cloth; help elders and workers; offer tarpan.
Rashis under Saturn's influence (Saturn is in Meena): Sade Sati - Mesha, Meena, Kumbha; Dhaiya - Simha (8th) and Dhanu (4th).
Shani beeja mantra: Om Pram Preem Proum Sah Shanaye Namah - chant 108 times (at least 11).""",
    hashtags=["#Shorts", "#शनिअमावस्या", "#ShaniAmavasya", "#शनिदेव", "#Devotional"],
    tags=["shani amavasya", "shani amavasya 2026", "shani amavasya hindi", "shani mantra", "shani beej mantra",
          "sade sati", "साढ़े साती", "शनि अमावस्या", "शनि मंत्र", "शनिदेव", "10 october 2026 amavasya",
          "hindi devotional", "divine mantra sangam", "shorts"],
    lang="hi", token_file="youtube_token_mantra_sangam.json", expected_channel="Mantra Sangam",
    watermark="@DivineMantraSangam", header="शनि अमावस्या",
    cta_lines=("अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे", "ऐसे और मंत्रों के लिए सब्सक्राइब करें"),
    footer_main=_HI_FOOTER,
    footer_en="Divine Mantra Sangam is a Hindi devotional channel: daily Rahu Kaal, Shubh Muhurat, mantras and Purana stories.",
)


# ---- Atla Tadde, Wednesday 28 Oct 2026 (Ashwayuja Bahula Tadiya = Krishna Tritiya; Tritiya until about 10:37 PM, moonrise about 5:30 PM) ----
_ATLA_BG: dict[str, Any] = dict(bg_top=(70, 10, 34), bg_mid=(146, 32, 58), bg_bottom=(58, 8, 26), glow=(255, 196, 96))

ATLA_TE = RequestShort(
    slug="atla_tadde_te", handle="", comment_id="", deity_te="గౌరీ దేవి", **_ATLA_BG,
    slides=(
        Slide("intro", 3.5, "బుధవారం · 28 అక్టోబర్ 2026", "అట్ల తద్ది", "ఆశ్వయుజ బహుళ తదియ", "గౌరీ దేవి అనుగ్రహం కోసం"),
        Slide("points", 7.0, "అట్ల తద్ది అంటే?", "ఆశ్వయుజ పౌర్ణమి తర్వాత వచ్చే బహుళ తదియ నాడు ఆంధ్ర, తెలంగాణలో స్త్రీలు జరుపుకునే పండుగ\nగౌరీ దేవిని పూజించి, కన్యలు మంచి వరుడిని, వివాహితులు భర్త క్షేమాన్ని కోరుకుంటారని సంప్రదాయం"),
        Slide("points", 8.5, "ఎలా జరుపుకుంటారు?", "తెల్లవారుజామునే లేచి భోజనం చేస్తారు\nపగలంతా ఉపవాసం, గౌరీ పూజ\nసాయంత్రం చంద్రుడిని చూసి అట్లు నైవేద్యం పెట్టి ఉపవాసం విడుస్తారు\nఉయ్యాలలు ఊగుతూ, గోరింటాకు పెట్టుకుని, పాటలు పాడతారు"),
        Slide("points", 5.5, "ఈరోజు ప్రత్యేకత", "అట్లు అంటే దోసెలు, ఈ పండుగ పేరు కూడా అట్లతోనే వచ్చింది\nతదియ ఈరోజు రాత్రి వరకు ఉంటుంది, సాయంత్రం చంద్రోదయానికి పూజ చేసుకోండి"),
        Slide("outro", 4.0, "అట్ల తద్ది శుభాకాంక్షలు", "ఈ పండుగ మీ ఇంట్లో ఎలా జరుపుకుంటారు?\nకామెంట్‌లో చెప్పండి"),
    ),
    title="అట్ల తద్ది 28 అక్టోబర్: విశేషం, ఎలా జరుపుకుంటారు | Atla Tadde",
    title_en="Atla Tadde 28 Oct 2026: Meaning, Rituals and Why Women Fast",
    description_te="""🙏 అట్ల తద్ది శుభాకాంక్షలు! ఈరోజు ఆశ్వయుజ బహుళ తదియ, బుధవారం 28 అక్టోబర్ 2026.

అట్ల తద్ది అంటే ఏమిటి: ఆశ్వయుజ పౌర్ణమి తర్వాత వచ్చే బహుళ తదియ నాడు ఆంధ్ర, తెలంగాణలో స్త్రీలు గౌరీ దేవిని పూజిస్తూ జరుపుకునే పండుగ. కన్యలు మంచి వరుడిని, వివాహితులు భర్త క్షేమాన్ని కోరుకుంటారని సంప్రదాయం.

ఎలా జరుపుకుంటారు:
• తెల్లవారుజామునే లేచి భోజనం చేస్తారు
• పగలంతా ఉపవాసం ఉండి గౌరీ దేవిని పూజిస్తారు
• సాయంత్రం చంద్రుడిని చూసి అట్లు (దోసెలు) నైవేద్యం పెట్టి ఉపవాసం విడుస్తారు
• ఉయ్యాలలు ఊగుతూ, గోరింటాకు పెట్టుకుని, పాటలు పాడతారు

తదియ తిథి ఈరోజు రాత్రి వరకు ఉంటుంది. చంద్రోదయ సమయం ఊరిని బట్టి మారుతుంది, మీ స్థానిక పంచాంగం చూసుకోండి.

ఈ పండుగను మీ ఇంట్లో ఎలా జరుపుకుంటారు? కామెంట్‌లో చెప్పండి.""",
    description_en="""Atla Tadde, Wednesday 28 October 2026 (Ashwayuja Bahula Tadiya).

A festival of Andhra and Telangana women, on the third day after the Ashwayuja full moon. Women worship Goddess Gauri; unmarried girls pray for a good husband and married women for their husband's well-being.
How it is observed: wake before dawn and eat, fast through the day, worship Gauri, offer atlu (dosas) after seeing the moon, then break the fast. Swings, henna and folk songs are part of the day.
Tritiya lasts until the night of the 28th; moonrise time varies by city, so check your local panchang.""",
    hashtags=["#Shorts", "#అట్లతద్ది", "#AtlaTadde", "#గౌరీదేవి", "#Devotional"],
    tags=["atla tadde", "atla tadde 2026", "atla tadde telugu", "atla taddi", "అట్ల తద్ది", "అట్లతద్ది 2026",
          "ashwayuja bahula tadiya", "gauri puja", "telugu festival", "telugu devotional", "mahanavi spirituals", "shorts"],
    header="అట్ల తద్ది",
    cta_lines=("ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు", "మరిన్ని పండుగ విశేషాల కోసం సబ్‌స్క్రైబ్ చేయండి"),
)


def _atla_hi(slug: str, token_file: str, expected: str, watermark: str, tag_channel: str, footer: str, footer_en: str) -> RequestShort:
    return RequestShort(
        slug=slug, handle="", comment_id="", deity_te="गौरी माता", **_ATLA_BG,
        slides=(
            Slide("intro", 3.5, "बुधवार · 28 अक्टूबर 2026", "अट्ला तद्दे", "आज आंध्र और तेलंगाना का खास व्रत", "गौरी माता की कृपा के लिए"),
            Slide("points", 7.0, "अट्ला तद्दे क्या है?", "आश्विन पूर्णिमा के बाद कृष्ण पक्ष की तृतीया पर आंध्र-तेलंगाना की महिलाएं यह व्रत रखती हैं\nगौरी माता की पूजा होती है। परंपरा है कि कन्याएं अच्छे वर की और सुहागिनें पति की सलामती की कामना करती हैं"),
            Slide("points", 8.5, "कैसे मनाते हैं?", "सूर्योदय से पहले उठकर भोजन करते हैं\nदिन भर व्रत और गौरी पूजा\nशाम को चंद्र दर्शन कर अट्लु (डोसे) का भोग लगाकर व्रत खोलते हैं\nझूला झूलना, मेहंदी और लोकगीत इस दिन की पहचान हैं"),
            Slide("points", 5.5, "करवा चौथ से कनेक्शन", "उत्तर भारत में कल, 29 अक्टूबर को करवा चौथ है\nयह दोनों व्रत चंद्र दर्शन से खुलते हैं और सुहाग की मंगलकामना से जुड़े हैं"),
            Slide("outro", 4.0, "अट्ला तद्दे की शुभकामनाएं", "आपके यहां कौन सा व्रत मनाया जाता है?\nकमेंट में बताएं"),
        ),
        title="अट्ला तद्दे 28 अक्टूबर: क्या है, कैसे मनाते हैं | Atla Tadde",
        title_en="Atla Tadde 28 Oct 2026: What It Is and How It Is Observed (Karwa Chauth is tomorrow)",
        description_te=f"""🙏 अट्ला तद्दे की शुभकामनाएं! आज आश्विन कृष्ण तृतीया, बुधवार 28 अक्टूबर 2026।

अट्ला तद्दे क्या है: आश्विन पूर्णिमा के बाद कृष्ण पक्ष की तृतीया पर आंध्र प्रदेश और तेलंगाना की महिलाएं गौरी माता की पूजा करके यह व्रत रखती हैं। परंपरा है कि कन्याएं अच्छे वर की और सुहागिनें पति की सलामती की कामना करती हैं।

कैसे मनाते हैं:
• सूर्योदय से पहले उठकर भोजन करते हैं
• दिन भर व्रत रखकर गौरी माता की पूजा करते हैं
• शाम को चंद्र दर्शन कर अट्लु (डोसे) का भोग लगाकर व्रत खोलते हैं
• झूला झूलना, मेहंदी लगाना और लोकगीत गाना इस दिन की पहचान है

करवा चौथ से संबंध: उत्तर भारत में करवा चौथ कल, 29 अक्टूबर को है। दोनों व्रत चंद्र दर्शन के बाद खुलते हैं।

आपके यहां कौन सा व्रत मनाया जाता है? कमेंट में बताएं।

अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे 🙏""",
        description_en="""Atla Tadde, Wednesday 28 October 2026 (Ashwin Krishna Tritiya).

A fast kept by women of Andhra Pradesh and Telangana on the third day after the Ashwin full moon, with worship of Goddess Gauri. Wake before sunrise and eat, fast through the day, break the fast after moon sighting with an offering of atlu (dosas). Karwa Chauth falls tomorrow, 29 October, in North India.""",
        hashtags=["#Shorts", "#अट्लातद्दे", "#AtlaTadde", "#करवाचौथ", "#Devotional"],
        tags=["atla tadde", "atla tadde 2026", "atla tadde hindi", "अट्ला तद्दे", "अट्ला तद्दे 2026", "karwa chauth 2026",
              "gauri puja", "hindi devotional", tag_channel, "shorts"],
        lang="hi", token_file=token_file, expected_channel=expected, watermark=watermark, header="अट्ला तद्दे",
        cta_lines=("अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे", "ऐसे और व्रत-त्योहार जानने के लिए सब्सक्राइब करें"),
        footer_main=footer, footer_en=footer_en,
    )


ATLA_HI = _atla_hi("atla_tadde_hi", "youtube_token_mantra_sangam.json", "Mantra Sangam", "@DivineMantraSangam",
                   "divine mantra sangam", _HI_FOOTER,
                   "Divine Mantra Sangam is a Hindi devotional channel: daily Rahu Kaal, Shubh Muhurat, mantras and Purana stories.")
ATLA_HI_TB = _atla_hi("atla_tadde_hi_tb", "youtube_token_trance_beats.json", "Trance Beats", "@DevotionalTranceBeats",
                      "devotional trance beats",
                      "हिंदी भक्ति चैनल: रोज़ मंत्र, भजन और पौराणिक कथाएं। Devotional Trance Beats को सब्सक्राइब करें।",
                      "Devotional Trance Beats is a Hindi devotional channel: daily mantras, bhajans and Purana stories.")

SPECS: dict[str, RequestShort] = {s.slug: s for s in (NARASIMHA, SHANI_TE, SHANI_HI, ATLA_TE, ATLA_HI, ATLA_HI_TB)}
