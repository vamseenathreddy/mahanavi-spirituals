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
    beeja_mantram: str            # seed syllable(s) -- see per-deity notes below on confidence
    telugu_hashtags: list[str] = field(default_factory=list)
    english_keywords: list[str] = field(default_factory=list)


DEITY_CONTENT: dict[Deity, DeityContent] = {
    Deity.SHIVA: DeityContent(
        telugu_name="శివుడు",
        blessing_phrase="ఓం నమః శివాయ 🙏",
        mantra="ఓం నమః శివాయ",
        beeja_mantram="ఓం హౌం నమః శివాయ",  # Haum + the core mantra, fuller than a bare syllable
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
        beeja_mantram="ఓం హ్రాం హనుమతే నమః",  # Hraam + full mantra, fuller than a bare syllable
        telugu_hashtags=["#హనుమంతుడు", "#ఆంజనేయస్వామి", "#మంగళవారం_ప్రత్యేకం"],
        english_keywords=[
            "Lord Hanuman", "Hanuman Panchangam today", "Tuesday Hanuman special",
            "Jai Hanuman", "Hanuman devotional", "Telugu panchangam",
        ],
    ),
    Deity.GANESHA: DeityContent(
        telugu_name="గణేశుడు",
        blessing_phrase="ఓం గణ గణపతయే నమః 🙏",
        mantra="వక్రతుండ మహాకాయ సూర్యకోటి సమప్రభ నిర్విఘ్నం కురు మే దేవ సర్వ కార్యేషు సర్వదా",
        beeja_mantram="ఓం గం గణపతయే నమః",  # full traditional Ganesha bija mantra (Om Gam Ganapataye Namaha)
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
        # Sai Baba is a 19th/20th-century saint, not a Puranic deity with a
        # classical Vedic bija syllable -- using the standard short chant
        # itself here rather than fabricating a beeja that doesn't
        # traditionally exist.
        beeja_mantram="ఓం సాయి రాం",
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
        beeja_mantram="ఓం శ్రీం నమః",  # Shreem + namah, fuller than a bare syllable, kept distinct from the main mantra above
        telugu_hashtags=["#లక్ష్మీదేవి", "#మహాలక్ష్మి", "#శుక్రవారం_ప్రత్యేకం"],
        english_keywords=[
            "Goddess Lakshmi", "Lakshmi Panchangam today", "Friday Lakshmi special",
            "Mahalakshmi devotional", "Telugu panchangam", "wealth goddess blessings",
        ],
    ),
    Deity.VENKATESWARA: DeityContent(
        telugu_name="వేంకటేశ్వర స్వామి",
        blessing_phrase="ఓం నమో వేంకటేశాయ 🙏",
        mantra="గోవిందా గోవిందా",
        # Less standardized across traditions than Ganesha/Lakshmi's bija --
        # worth a native speaker's confirmation before treating as final.
        beeja_mantram="ఓం క్లీం వేంకటేశాయ నమః",
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
        beeja_mantram="ఓం హ్రాం సూర్యాయ నమః",  # Hraam + full mantra, fuller than a bare syllable
        telugu_hashtags=["#సూర్యభగవానుడు", "#ఆదిత్యహృదయం", "#ఆదివారం_ప్రత్యేకం"],
        english_keywords=[
            "Lord Surya", "Surya Panchangam today", "Sunday Surya special",
            "Surya Namaskar devotional", "Aditya Hrudayam", "Telugu panchangam",
        ],
    ),
}

# Which deity corresponds to which weekday -- matches
# config.WEEKDAY_FOLDER_MAP's day assignments (Python's date.weekday():
# Monday=0 ... Sunday=6). Used by anything that needs "today's deity"
# without also needing an actual selected image (e.g. the alert Shorts,
# which have no deity image of their own but still want today's mantra).
WEEKDAY_DEITY_MAP: dict[int, Deity] = {
    0: Deity.SHIVA,
    1: Deity.HANUMAN,
    2: Deity.GANESHA,
    3: Deity.SAI,
    4: Deity.LAKSHMI,
    5: Deity.VENKATESWARA,
    6: Deity.SURYA,
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
