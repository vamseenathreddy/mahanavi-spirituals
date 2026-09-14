"""
Deity-specific content building blocks used by the SEO/caption generator.

Kept separate from generator.py so a Telugu speaker (or you, later) can
review/tweak the devotional phrasing, mantras, and keyword lists without
touching any generation logic. Add a new deity here and the generator
picks it up automatically — no other code changes needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mahanavi.core.models import Deity


@dataclass(frozen=True, slots=True)
class DeityContent:
    telugu_name: str
    blessing_phrase: str        # short devotional opening line
    mantra: str                  # traditional chant/mantra
    telugu_hashtags: list[str] = field(default_factory=list)
    english_keywords: list[str] = field(default_factory=list)


DEITY_CONTENT: dict[Deity, DeityContent] = {
    Deity.SHIVA: DeityContent(
        telugu_name="శివుడు",
        blessing_phrase="ఓం నమః శివాయ 🙏",
        mantra="ఓం నమః శివాయ",
        telugu_hashtags=["#శివుడు", "#మహాదేవుడు", "#సోమవారం_ప్రత్యేకం"],
        english_keywords=[
            "Lord Shiva", "Shiva Panchangam today", "Monday Shiva special",
            "Om Namah Shivaya", "Shiva devotional", "Telugu panchangam",
        ],
    ),
    Deity.HANUMAN: DeityContent(
        telugu_name="హనుమంతుడు",
        blessing_phrase="జై హనుమాన్ 🙏",
        mantra="ఓం హనుమతే నమః",
        telugu_hashtags=["#హనుమంతుడు", "#ఆంజనేయస్వామి", "#మంగళవారం_ప్రత్యేకం"],
        english_keywords=[
            "Lord Hanuman", "Hanuman Panchangam today", "Tuesday Hanuman special",
            "Jai Hanuman", "Hanuman devotional", "Telugu panchangam",
        ],
    ),
    Deity.GANESHA: DeityContent(
        telugu_name="గణేశుడు",
        blessing_phrase="ఓం గణ గణపతయే నమః 🙏",
        mantra="వక్రతుండ మహాకాయ సూర్యకోటి సమప్రభ",
        telugu_hashtags=["#గణేశుడు", "#వినాయకుడు", "#బుధవారం_ప్రత్యేకం"],
        english_keywords=[
            "Lord Ganesha", "Ganesha Panchangam today", "Wednesday Ganesha special",
            "Vinayaka devotional", "Ganpati", "Telugu panchangam",
        ],
    ),
    Deity.SAI: DeityContent(
        telugu_name="సాయిబాబా",
        blessing_phrase="ఓం సాయి రాం 🙏",
        mantra="శ్రీ సాయినాథాయ నమః",
        telugu_hashtags=["#సాయిబాబా", "#షిర్డీసాయి", "#గురువారం_ప్రత్యేకం"],
        english_keywords=[
            "Shirdi Sai Baba", "Sai Baba Panchangam today", "Thursday Sai special",
            "Om Sai Ram", "Sai devotional", "Telugu panchangam",
        ],
    ),
    Deity.LAKSHMI: DeityContent(
        telugu_name="లక్ష్మీదేవి",
        blessing_phrase="ఓం శ్రీ మహాలక్ష్మ్యై నమః 🙏",
        mantra="ఓం శ్రీం మహాలక్ష్మ్యై నమః",
        telugu_hashtags=["#లక్ష్మీదేవి", "#మహాలక్ష్మి", "#శుక్రవారం_ప్రత్యేకం"],
        english_keywords=[
            "Goddess Lakshmi", "Lakshmi Panchangam today", "Friday Lakshmi special",
            "Mahalakshmi devotional", "Telugu panchangam", "wealth goddess blessings",
        ],
    ),
    Deity.VENKATESWARA: DeityContent(
        telugu_name="వేంకటేశ్వరుడు",
        blessing_phrase="ఓం నమో వేంకటేశాయ 🙏",
        mantra="గోవిందా గోవిందా",
        telugu_hashtags=["#వేంకటేశ్వరుడు", "#తిరుమల", "#శనివారం_ప్రత్యేకం"],
        english_keywords=[
            "Lord Venkateswara", "Venkateswara Panchangam today", "Saturday Balaji special",
            "Tirumala Tirupati", "Govinda Govinda", "Telugu panchangam",
        ],
    ),
    Deity.SURYA: DeityContent(
        telugu_name="సూర్యభగవానుడు",
        blessing_phrase="ఓం సూర్యాయ నమః 🙏",
        mantra="ఓం ఘృణి సూర్యాయ నమః",
        telugu_hashtags=["#సూర్యభగవానుడు", "#ఆదిత్యహృదయం", "#ఆదివారం_ప్రత్యేకం"],
        english_keywords=[
            "Lord Surya", "Surya Panchangam today", "Sunday Surya special",
            "Surya Namaskar devotional", "Aditya Hrudayam", "Telugu panchangam",
        ],
    ),
}

# General hashtags applied across every post regardless of deity.
GENERAL_TELUGU_HASHTAGS: list[str] = [
    "#పంచాంగం", "#తెలుగుపంచాంగం", "#భక్తి", "#దైవం", "#మహానవిస్పిరిచువల్స్",
]

# Curated devotional hashtags that tend to have broad reach/trend cyclically.
# Review and refresh this list periodically — hashtag popularity shifts over time.
TRENDING_DEVOTIONAL_HASHTAGS: list[str] = [
    "#Devotional", "#Bhakti", "#TeluguPanchangam", "#DailyPanchangam",
    "#HinduDevotional", "#Spirituality", "#TempleVibes", "#GodBless",
]

GENERAL_ENGLISH_KEYWORDS: list[str] = [
    "Telugu panchangam today", "daily panchangam", "Hindu devotional content",
    "Telugu devotional channel", "today's panchangam", "rahu kalam today",
    "auspicious time today",
]
