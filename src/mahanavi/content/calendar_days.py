"""Calendar-style Telugu Shorts for Mahanavi: "tomorrow's special" (do / don't), the monthly festival list
and the monthly vrata calendar (Ekadashi, Pradosham, Sankashti ...).

Dates: curated festivals (FESTIVALS, refresh yearly; a warning is printed once the list runs out) plus vratas
computed from the real Swiss-Ephemeris tithi at Hyderabad (sunrise for Ekadashi / Amavasya / Purnima / Ashtami /
Shashthi / Chaturthi, evening for Pradosham / Sankashti / Masa Shivaratri). Built as `RequestShort`
(points slides), so the existing renderer, assembler and uploader are reused.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from functools import lru_cache

from mahanavi.content.alert_seo import _CHANNEL_FOOTER_EN, _CHANNEL_FOOTER_TE
from mahanavi.content.beej_mantras import DEITIES, MONTH_NAME, WEEKDAY_NAME
from mahanavi.content.request_shorts import RequestShort, Slide
from mahanavi.panchang.local_provider import HYDERABAD, LocalPanchangProvider

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
CATEGORIES = ("tomorrow", "festivals", "vratas", "tips")
SPECIAL_KINDS = CATEGORIES + ("today",)   # "today": the same-day morning post (5-6 AM), reuses the tomorrow playlist


@dataclass(frozen=True)
class Obs:
    key: str
    te: str
    en: str
    god: str            # beej_mantras.DEITIES key (palette) and photo family
    photo: str          # deity_bg photo family
    why: str            # one Telugu line: what the day is
    dos: tuple[str, str, str]
    donts: tuple[str, str, str]
    tags: tuple[str, ...] = ()   # extra SEO tags (search-trend terms)


OBS: dict[str, Obs] = {o.key: o for o in (
    Obs("ekadashi", "ఏకాదశి", "Ekadashi", "vishnu", "vishnu", "శ్రీ మహావిష్ణువుకు ప్రీతికరమైన ఏకాదశి వ్రతం",
        ("ఉపవాసం లేదా ఫలహారం చేయండి", "విష్ణు సహస్రనామం పఠించండి", "తులసి దళాలతో విష్ణువును పూజించండి"),
        ("అన్నం, ధాన్యాలు తినకండి", "పగటిపూట నిద్రపోకండి", "ఉల్లి, వెల్లుల్లి, మాంసాహారం వద్దు"),
        ("ekadashi vratham", "vishnu sahasranamam", "ekadashi telugu")),
    Obs("pradosham", "ప్రదోషం", "Pradosham", "shiva", "shiva", "సాయంత్రం శివారాధనకు విశేషమైన ప్రదోష కాలం",
        ("సాయంత్రం శివాలయ దర్శనం చేయండి", "శివుడికి అభిషేకం, బిల్వ దళాలు సమర్పించండి", "ఓం నమః శివాయ జపం చేయండి"),
        ("సంధ్యా సమయంలో నిద్రపోకండి", "మాంసాహారం, మద్యం వద్దు", "కోపం, కలహాలు వద్దు"),
        ("pradosham", "lord shiva songs", "shiva stotram telugu")),
    Obs("sankashti", "సంకష్టహర చతుర్థి", "Sankashti Chaturthi", "ganesha", "ganesha", "గణపతికి ప్రీతికరమైన సంకష్టహర చతుర్థి",
        ("గణపతికి గరిక, ఎర్ర పూలు సమర్పించండి", "సంకష్టహర గణపతి స్తోత్రం పఠించండి", "చంద్రోదయం తర్వాత పూజ చేసి ఉపవాసం విరమించండి"),
        ("చంద్రోదయానికి ముందు భోజనం వద్దు", "ఉల్లి, వెల్లుల్లి వద్దు", "మాంసాహారం వద్దు"),
        ("sankashtahara ganapati stotram", "sankashti chaturthi", "ganapati stotram telugu")),
    Obs("shivaratri", "మాస శివరాత్రి", "Masa Shivaratri", "shiva", "shiva", "ప్రతి నెలా వచ్చే శివరాత్రి వ్రతం",
        ("శివుడికి అభిషేకం చేయండి", "బిల్వార్చన చేయండి", "రాత్రి శివ నామ స్మరణ చేయండి"),
        ("మాంసాహారం, మద్యం వద్దు", "వృథా కాలక్షేపం వద్దు", "కోపం, కలహాలు వద్దు"),
        ("masa shivaratri", "lord shiva songs", "om namah shivaya")),
    Obs("purnima", "పౌర్ణమి", "Pournami", "lakshmi", "lakshmi", "సత్యనారాయణ వ్రతానికి శుభప్రదమైన పౌర్ణమి",
        ("సత్యనారాయణ స్వామి వ్రతం చేయండి", "చంద్రుడికి నమస్కరించి పాలు నివేదించండి", "దానధర్మాలు చేయండి"),
        ("మాంసాహారం, మద్యం వద్దు", "ఎవరినీ దూషించకండి", "తామసిక ఆహారం వద్దు"),
        ("pournami", "satyanarayana vratham", "lakshmi devi songs")),
    Obs("amavasya", "అమావాస్య", "Amavasya", "shiva", "shiva", "పితృ దేవతలను స్మరించే అమావాస్య",
        ("పితృ తర్పణం ఇవ్వండి", "పేదలకు అన్నదానం చేయండి", "ఇంట్లో దీపం వెలిగించండి"),
        ("కొత్త పనులు ప్రారంభించకండి", "జుట్టు, గోళ్లు కత్తిరించకండి", "మాంసాహారం వద్దు"),
        ("amavasya", "pitru tarpanam", "amavasya telugu")),
    Obs("bhairava", "కాలభైరవ అష్టమి", "Kalabhairava Ashtami", "shiva", "shiva", "కాలభైరవ స్వామిని ఆరాధించే అష్టమి",
        ("కాలభైరవ అష్టకం పఠించండి", "ఆవనూనె దీపం వెలిగించండి", "కుక్కలకు ఆహారం పెట్టండి"),
        ("మాంసాహారం, మద్యం వద్దు", "అబద్ధాలు, అహంకారం వద్దు", "బలహీనులను బాధపెట్టకండి"),
        ("kalabhairava ashtakam", "bhairava", "lord shiva songs")),
    Obs("shashthi", "సుబ్రహ్మణ్య షష్ఠి", "Subramanya Shashthi", "subrahmanya", "murugan", "కుమార స్వామి ఆరాధనకు విశేషమైన షష్ఠి",
        ("సుబ్రహ్మణ్య స్వామికి అభిషేకం చేయండి", "సుబ్రహ్మణ్య భుజంగం పఠించండి", "పాలు, పండ్లు నివేదించండి"),
        ("మాంసాహారం వద్దు", "మద్యం వద్దు", "అబద్ధాలు ఆడకండి"),
        ("subramanya shashti", "subramanya bhujangam", "murugan songs telugu")),
    Obs("vinayaka", "వినాయక చవితి (నెలవారీ)", "Vinayaka Chaturthi", "ganesha", "ganesha", "గణపతి ఆరాధనకు శుక్ల చతుర్థి",
        ("గణపతికి గరిక, మోదకాలు సమర్పించండి", "ఓం గం గణపతయే నమః జపం చేయండి", "గణేశ అష్టోత్తరం పఠించండి"),
        ("తులసి దళాలతో గణపతిని పూజించకండి", "మాంసాహారం వద్దు", "పూజలో తొందర వద్దు"),
        ("vinayaka chaturthi", "ganesha songs telugu", "ganapati stotram telugu")),
    # curated festivals
    Obs("diwali", "దీపావళి", "Deepavali", "lakshmi", "lakshmi", "దీపాల పండుగ, లక్ష్మీ పూజ",
        ("సాయంత్రం లక్ష్మీ పూజ చేసి దీపాలు వెలిగించండి", "ఇల్లు శుభ్రం చేసి ముగ్గు వేయండి", "పెద్దలకు నమస్కరించి స్వీట్లు పంచండి"),
        ("సాయంత్రం ఇంట్లో చీకటి ఉంచకండి", "టపాసులు జాగ్రత్తగా కాల్చండి", "అప్పులు ఇచ్చి పుచ్చుకోవడం వద్దు (సంప్రదాయం)"),
        ("diwali lakshmi puja", "lakshmi devi songs", "deepavali telugu")),
    Obs("karwa_chauth", "కర్వా చౌత్", "Karwa Chauth", "shiva", "parvati", "భర్త దీర్ఘాయుష్షు కోసం సుమంగళులు చంద్రోదయం వరకు చేసే ఉత్తర భారత వ్రతం",
        ("సూర్యోదయానికి ముందు సర్గి భోజనం చేయండి", "సాయంత్రం గౌరీ పూజ చేసి కర్వా చౌత్ కథ వినండి", "చంద్రుడికి అర్ఘ్యం ఇచ్చి, జల్లెడలో నుంచి భర్తను చూసి ఉపవాసం విడవండి"),
        ("సంప్రదాయం ప్రకారం చంద్రోదయం వరకు అన్నం, నీరు తీసుకోకండి", "ఉపవాస సమయంలో వాదనలు వద్దు", "పూజలో తొందర వద్దు"),
        ("karwa chauth", "karwa chauth 2026", "karwa chauth telugu")),
    Obs("bhagini_hastha", "భగినీ హస్త భోజనం", "Bhagini Hastha Bhojanam", "shiva", "shiva", "అన్నదమ్ములు అక్క చెల్లెళ్ల ఇంట భోజనం చేసే కార్తీక శుక్ల విదియ",
        ("అక్క లేదా చెల్లెలి ఇంట భోజనం చేయండి", "సోదరికి కానుక ఇవ్వండి", "ఇంటి పెద్దలకు నమస్కరించండి"),
        ("సోదరీమణులను నొప్పించకండి", "కోపతాపాలు వద్దు", "ఆహారాన్ని వృథా చేయకండి"),
        ("bhagini hastha bhojanam", "bhai dooj telugu", "yama dwitiya")),
    Obs("nagula_chavithi", "నాగుల చవితి", "Nagula Chavithi", "subrahmanya", "murugan", "నాగదేవతలను, సుబ్రహ్మణ్య స్వామిని పూజించే కార్తీక శుద్ధ చవితి",
        ("పుట్ట వద్ద పాలు పోసి నాగదేవతను పూజించండి", "చిమ్మిలి, చలిమిడి నైవేద్యం పెట్టండి", "సుబ్రహ్మణ్య స్వామిని స్మరించండి"),
        ("పుట్టను పాడు చేయకండి", "పాములను హింసించకండి", "ఉపవాస నియమం ఉంటే భంగం చేయకండి"),
        ("nagula chavithi", "nagula chavithi 2026", "naga devatha puja")),
    Obs("prabodhini", "ప్రబోధిని ఏకాదశి", "Prabodhini Ekadashi", "vishnu", "vishnu", "చాతుర్మాస్య వ్రతం ముగిసి శ్రీ మహావిష్ణువు మేల్కొనే రోజు",
        ("ఉపవాసం ఉండి విష్ణు సహస్రనామం పఠించండి", "సాయంత్రం తులసి వద్ద దీపం వెలిగించండి", "విష్ణు ఆలయ దర్శనం చేయండి"),
        ("అన్నం, ధాన్యాలు తినకండి", "పగటి నిద్ర వద్దు", "ఉల్లి, వెల్లుల్లి, మాంసాహారం వద్దు"),
        ("prabodhini ekadashi", "prabodhini ekadashi 2026", "vishnu sahasranamam telugu")),
    Obs("tulasi_vivaham", "క్షీరాబ్ధి ద్వాదశి (తులసి వివాహం)", "Kshirabdhi Dwadashi / Tulasi Vivaham", "vishnu", "vishnu", "తులసి దేవికి శ్రీ మహావిష్ణువుతో వివాహం జరిపించే పవిత్రమైన రోజు",
        ("తులసి కోటను ముగ్గులతో, పూలతో అలంకరించండి", "ఉసిరి కొమ్మను పెట్టి దీపాలు వెలిగించండి", "తులసి కల్యాణం చేసి నైవేద్యం పెట్టండి"),
        ("తులసి ఆకులు అనవసరంగా తెంపకండి", "మాంసాహారం వద్దు", "పూజలో తొందర వద్దు"),
        ("tulasi vivaham", "tulasi kalyanam", "kshirabdhi dwadashi")),
    Obs("margasira", "మార్గశిర మాసం ప్రారంభం", "Margashira Masam begins", "vishnu", "vishnu", "శ్రీ మహావిష్ణువుకు, లక్ష్మీదేవికి ప్రీతికరమైన మార్గశిర మాసం",
        ("ఉదయాన్నే స్నానం చేసి దీపం వెలిగించండి", "విష్ణు సహస్రనామం పఠించండి", "గురువారాల్లో లక్ష్మీ పూజ చేయండి"),
        ("మాంసాహారం, మద్యం వద్దు", "పగటి నిద్ర వద్దు", "ఇంట్లో అశుభ్రత వద్దు"),
        ("margasira masam", "margasira masam 2026", "lakshmi vratam")),
    Obs("margasira_lakshmivaram", "మార్గశిర లక్ష్మీవారం", "Margashira Lakshmivaram", "lakshmi", "lakshmi", "మార్గశిర మాసంలో లక్ష్మీదేవిని పూజించే గురువారం",
        ("ఇల్లు శుభ్రం చేసి ముగ్గు వేయండి", "లక్ష్మీ అష్టోత్తరం పఠించండి", "పసుపు కుంకుమలతో పూజ చేసి నైవేద్యం పెట్టండి"),
        ("సాయంత్రం ఇంట్లో చీకటి ఉంచకండి", "మాంసాహారం వద్దు", "గొడవలు, కోపం వద్దు"),
        ("margasira lakshmivaram", "margasira guruvaram", "lakshmi devi songs")),
    Obs("dhanurmasam", "ధనుర్మాసం ప్రారంభం", "Dhanurmasam begins", "vishnu", "vishnu", "తిరుప్పావై పఠనంతో శ్రీ మహావిష్ణువును ఆరాధించే ధనుర్మాసం",
        ("తెల్లవారుజామునే లేచి ఇంటి ముందు ముగ్గు వేయండి", "తిరుప్పావై పాశురాలు పఠించండి", "విష్ణు ఆలయ దర్శనం చేయండి"),
        ("పగటి నిద్ర వద్దు", "మాంసాహారం, మద్యం వద్దు", "ఆలస్యంగా నిద్ర లేవకండి"),
        ("dhanurmasam", "dhanurmasam 2026", "tiruppavai telugu")),
    Obs("mukkoti", "ముక్కోటి ఏకాదశి · గీతా జయంతి", "Mukkoti Ekadashi / Gita Jayanti", "vishnu", "vishnu", "వైకుంఠ ద్వార దర్శనం, భగవద్గీత పుట్టిన రోజు",
        ("ఉపవాసం ఉండి విష్ణు ఆలయ ఉత్తర ద్వార దర్శనం చేయండి", "భగవద్గీత శ్లోకాలు పఠించండి", "రాత్రి జాగరణ చేసి విష్ణు నామ స్మరణ చేయండి"),
        ("అన్నం, ధాన్యాలు తినకండి", "పగటి నిద్ర వద్దు", "ఉల్లి, వెల్లుల్లి, మాంసాహారం వద్దు"),
        ("mukkoti ekadashi", "vaikuntha ekadashi", "gita jayanti")),
    Obs("datta_jayanti", "దత్త జయంతి", "Datta Jayanti", "dattatreya", "dattatreya", "శ్రీ దత్తాత్రేయ స్వామి అవతరించిన మార్గశిర పౌర్ణమి",
        ("దత్తాత్రేయ స్వామిని పూజించి దత్త స్తోత్రం పఠించండి", "గురుచరిత్ర పారాయణ చేయండి", "అన్నదానం చేయండి"),
        ("మాంసాహారం, మద్యం వద్దు", "గురువులను, పెద్దలను అవమానించకండి", "పూజలో తొందర వద్దు"),
        ("datta jayanti", "datta jayanti 2026", "dattatreya swamy")),
    Obs("karthika", "కార్తీక మాసం ప్రారంభం", "Karthika Masam begins", "shiva", "shiva", "శివారాధనకు అత్యంత పవిత్రమైన కార్తీక మాసం",
        ("తెల్లవారుజామున స్నానం చేసి దీపం వెలిగించండి", "ఉసిరి చెట్టు కింద దీపారాధన చేయండి", "శివాలయంలో దీపదానం చేయండి"),
        ("మాంసాహారం, మద్యం వద్దు", "ఉల్లి, వెల్లుల్లి వద్దు", "దీపారాధన మానకండి"),
        ("karthika masam", "karthika deepam", "lord shiva songs")),
    Obs("karthika_somavaram", "కార్తీక సోమవారం", "Karthika Somavaram", "shiva", "shiva", "కార్తీక మాసంలో శివుడికి ప్రీతికరమైన సోమవారం",
        ("శివుడికి అభిషేకం, బిల్వార్చన చేయండి", "ఉపవాసం ఉండి సాయంత్రం దీపం వెలిగించండి", "శివ పంచాక్షరి జపం చేయండి"),
        ("మాంసాహారం, ఉల్లి, వెల్లుల్లి వద్దు", "పగటి నిద్ర వద్దు", "మద్యం, పొగాకు వద్దు"),
        ("karthika somavaram", "lord shiva songs", "shiva abhishekam")),
    Obs("karthika_pournami", "కార్తీక పౌర్ణమి", "Karthika Pournami", "shiva", "shiva", "కార్తీక మాసంలో అత్యంత పవిత్రమైన పౌర్ణమి",
        ("నదీ స్నానం చేసి దీపదానం చేయండి", "శివాలయంలో దీపాలు వెలిగించండి", "సత్యనారాయణ వ్రతం చేయండి"),
        ("మాంసాహారం, మద్యం వద్దు", "పగటి నిద్ర వద్దు", "ఎవరినీ దూషించకండి"),
        ("karthika pournami", "karthika deepam", "lord shiva songs")),
)}

# curated 2026 festival dates -> Obs key (extend each year; a warning is printed when this list runs out)
FESTIVALS: dict[dt.date, str] = {
    dt.date(2026, 10, 29): "karwa_chauth",
    dt.date(2026, 11, 8): "diwali",
    dt.date(2026, 11, 11): "bhagini_hastha",
    dt.date(2026, 11, 13): "nagula_chavithi",
    dt.date(2026, 11, 20): "prabodhini",
    dt.date(2026, 11, 21): "tulasi_vivaham",
    dt.date(2026, 12, 9): "margasira",
    dt.date(2026, 12, 10): "margasira_lakshmivaram",
    dt.date(2026, 12, 16): "dhanurmasam",
    dt.date(2026, 12, 17): "margasira_lakshmivaram",
    dt.date(2026, 12, 20): "mukkoti",
    dt.date(2026, 12, 23): "datta_jayanti",
    dt.date(2026, 12, 24): "margasira_lakshmivaram",
    dt.date(2026, 12, 31): "margasira_lakshmivaram",
    dt.date(2026, 11, 10): "karthika",
    dt.date(2026, 11, 16): "karthika_somavaram",
    dt.date(2026, 11, 23): "karthika_somavaram",
    dt.date(2026, 11, 24): "karthika_pournami",
    dt.date(2026, 11, 30): "karthika_somavaram",
    dt.date(2026, 12, 7): "karthika_somavaram",
}
FESTIVALS_END = max(FESTIVALS)
PRIORITY = ["karwa_chauth", "bhagini_hastha", "nagula_chavithi", "prabodhini", "tulasi_vivaham", "margasira", "dhanurmasam",
            "mukkoti", "datta_jayanti", "margasira_lakshmivaram", "diwali", "karthika", "karthika_somavaram", "karthika_pournami", "ekadashi", "pradosham", "sankashti",
            "shivaratri", "purnima", "amavasya", "bhairava", "shashthi", "vinayaka"]
VRATAS = ("ekadashi", "pradosham", "sankashti", "shivaratri", "purnima", "amavasya")

_prov = LocalPanchangProvider(*HYDERABAD)


def _tithi_no(t: dt.datetime) -> int:
    sun, moon = _prov._longitudes(t)  # noqa: SLF001
    return int(((moon - sun) % 360) // 12) + 1   # 1..30 (15 purnima, 30 amavasya)


@lru_cache(maxsize=1024)
def computed(d: dt.date) -> tuple[str, ...]:
    """Vrata keys that fall on this date from the real tithi (Hyderabad)."""
    import swisseph as swe

    rise = _prov._rise_set(d, swe.CALC_RISE)  # noqa: SLF001
    set_ = _prov._rise_set(d, swe.CALC_SET)  # noqa: SLF001
    sr = _tithi_no(rise)
    ev = _tithi_no(set_ + dt.timedelta(minutes=30))     # pradosham: trayodashi in the evening
    night = _tithi_no(set_ + dt.timedelta(hours=3))     # moonrise / night tithi
    out: list[str] = []
    if sr in (11, 26):
        out.append("ekadashi")
    if sr == 15:
        out.append("purnima")
    if sr == 30:
        out.append("amavasya")
    if sr == 23:
        out.append("bhairava")
    if sr == 6:
        out.append("shashthi")
    if sr == 4:
        out.append("vinayaka")
    if ev in (13, 28):
        out.append("pradosham")
    if night == 19:
        out.append("sankashti")
    if _tithi_no(set_ + dt.timedelta(hours=5)) == 29 and night in (28, 29):
        out.append("shivaratri")
    return tuple(out)


def _dedupe_spans(d: dt.date, keys: list[str]) -> list[str]:
    """A tithi that spans two sunrises/evenings would repeat on the next day: keep only the first day."""
    prev = set(computed(d - dt.timedelta(days=1)))
    return [k for k in keys if k not in prev]


# A curated festival replaces the computed vrata it coincides with; some computed vratas are dropped on the day the
# curated (Smarta / pradosha-based) date differs from the sunrise tithi (Prabodhini Ekadashi 20 Nov, Datta Jayanti 23 Dec).
_REPLACES = {"nagula_chavithi": ("vinayaka",), "prabodhini": ("ekadashi",), "mukkoti": ("ekadashi",),
             "datta_jayanti": ("purnima",), "tulasi_vivaham": ("ekadashi",)}
_SUPPRESS: dict[dt.date, tuple[str, ...]] = {dt.date(2026, 11, 21): ("ekadashi",), dt.date(2026, 12, 24): ("purnima",)}


def observances(d: dt.date) -> list[str]:
    keys = [FESTIVALS[d]] if d in FESTIVALS else []
    keys += _dedupe_spans(d, [k for k in computed(d)])
    if d in FESTIVALS:  # a curated day replaces the generic one it coincides with (Diwali amavasya, Karthika purnima)
        keys = [k for k in keys if k not in ("amavasya", "purnima") + _REPLACES.get(FESTIVALS[d], ())]
    keys = [k for k in keys if k not in _SUPPRESS.get(d, ())]
    return sorted(dict.fromkeys(keys), key=PRIORITY.index)


def stale(d: dt.date) -> bool:
    return d > FESTIVALS_END


def next_special(after: dt.date, horizon: int = 10) -> tuple[dt.date, list[str]] | None:
    """Tomorrow-type post for the day after `after` only (None when it is an ordinary day)."""
    day = after + dt.timedelta(days=1)
    obs = observances(day)
    return (day, obs) if obs else None


def month_items(year: int, month: int, kinds: tuple[str, ...]) -> list[tuple[dt.date, str]]:
    d = dt.date(year, month, 1)
    out: list[tuple[dt.date, str]] = []
    while d.month == month:
        for k in observances(d):
            if k in kinds:
                out.append((d, k))
        d += dt.timedelta(days=1)
    return out


# ---------------------------------------------------------------------------------------------------- building
def _short_date(d: dt.date) -> str:
    return f"{d.day} {MONTH_NAME[d.month - 1][0]}"


def _long_date(d: dt.date) -> str:
    return f"{WEEKDAY_NAME[d.weekday()][0]} · {d.day} {MONTH_NAME[d.month - 1][0]} {d.year}"


CTA = ("ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు", "ప్రతి పండుగ, వ్రతం ముందే తెలుసుకోండి - సబ్‌స్క్రైబ్ చేయండి")
PLAYLIST_TITLES = {
    "tomorrow": ("రేపు విశేషం | చేయవలసినవి, చేయకూడనివి | Telugu Festival Do's and Don'ts",
                 "రేపు వచ్చే పండుగ, వ్రతం ఏమిటి? ఏం చేయాలి, ఏం చేయకూడదు? ప్రతి ప్రత్యేక రోజుకు ముందు రోజు సాయంత్రం.\n"
                 "Tomorrow's festival or vratam in Telugu, with simple do's and don'ts: Ekadashi, Pradosham, Sankashti, Pournami, Amavasya."),
    "festivals": ("పండుగల క్యాలెండర్ | Telugu Festival Calendar 2026",
                  "ప్రతి నెలలో వచ్చే పండుగలు, ముఖ్యమైన తేదీలు ముందే తెలుసుకోండి.\nMonth-wise Telugu festival dates, Karthika Masam, Diwali, Shivaratri and more."),
    "tips": ("పూజా నియమాలు | Pooja Rules and Tips in Telugu",
             "పూజ ఎలా చేయాలి, ఏం చేయకూడదు? తులసి, దీపారాధన, నైవేద్యం, ప్రదక్షిణ నియమాలు.\nSimple pooja rules, do's and don'ts in Telugu: tulasi, deepam, naivedyam, pradakshina."),
    "vratas": ("ఏకాదశి ప్రదోషం సంకష్టహర చతుర్థి క్యాలెండర్ | Telugu Vrata Calendar",
               "ప్రతి నెలా ఏకాదశి, ప్రదోషం, సంకష్టహర చతుర్థి, పౌర్ణమి, అమావాస్య తేదీలు.\nMonthly Ekadashi, Pradosham, Sankashti Chaturthi, Pournami and Amavasya dates in Telugu."),
}
PLAYLIST_LABELS = {"tips": "పూజా నియమాలు", "tomorrow": "రేపు విశేషం", "festivals": "పండుగల క్యాలెండర్", "vratas": "వ్రతాల క్యాలెండర్"}
PLAYLIST_LINES = {
    "tips": "ఇలాంటి పూజా నియమాలన్నీ ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి",
    "tomorrow": "ఇలాంటి రేపటి విశేషాలన్నీ ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి",
    "festivals": "అన్ని పండుగల తేదీలు ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి",
    "vratas": "అన్ని వ్రతాల తేదీలు ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్\nఇచ్చాం, దయచేసి చదవండి",
}
BASE_TAGS = ["telugu panchangam", "telugu calendar", "telugu festivals", "telugu devotional", "devotional songs telugu",
             "spiritual mantras meditation", "powerful god mantras telugu", "hindu festivals", "sanatana dharma",
             "తెలుగు పంచాంగం", "పండుగలు", "వ్రతం", "shorts"]
DISCLAIMER_TE = "తేదీలు హైదరాబాద్ సూర్యోదయ పంచాంగం ప్రకారం. స్థానిక పంచాంగం, పండితుల సలహా కూడా చూడండి 🙏"
DISCLAIMER_EN = "Dates follow the Hyderabad sunrise panchang. Please also check your local panchangam or priest."


def _common(slug: str, obs_key, slides: tuple[Slide, ...], title: str, title_en: str, desc_te: str, desc_en: str,
            tags: list[str], hashtags: list[str], header: str, category: str, photo_day: dt.date) -> RequestShort:
    from mahanavi.images import deity_bg

    o = obs_key if isinstance(obs_key, Obs) else OBS[obs_key]
    dei = DEITIES[o.god]
    top, mid, bottom, glow = dei.palette
    path = deity_bg.pick(o.photo, photo_day)
    tags = [t for t in dict.fromkeys(tags + BASE_TAGS) if len(t) <= 30]   # YouTube: each tag <= 30 chars
    while sum(len(t) + (2 if " " in t else 0) + 1 for t in tags) > 440:      # and ~500 total, spaced tags are quoted
        tags.pop(-2)
    return RequestShort(
        slug=slug, handle="", comment_id="", deity_te=o.te, bg_top=top, bg_mid=mid, bg_bottom=bottom, glow=glow,
        slides=slides, title=title[:99] + ("…" if len(title) > 100 else ""), title_en=title_en[:100],
        description_te=desc_te, description_en=desc_en, hashtags=hashtags, tags=tags,
        bg_image=f"deities/{path.name}" if path else "", header=header, tag_footer=CTA[0], cta_lines=CTA,
        playlist_line=PLAYLIST_LINES[category], footer_main=_CHANNEL_FOOTER_TE, footer_en=_CHANNEL_FOOTER_EN)


def build_today(day: dt.date, keys: list[str]) -> RequestShort:
    """Same-day morning version of build_tomorrow ("ఈరోజు ..."), posted 5-6 AM IST."""
    import dataclasses

    spec = build_tomorrow(day, keys)
    o = OBS[keys[0]]
    others = [OBS[k].te for k in keys[1:]]
    name = o.te + (f" + {', '.join(others)}" if others else "")
    en = o.en + (f" + {', '.join(OBS[k].en for k in keys[1:])}" if others else "")
    slides = tuple(dataclasses.replace(sl, label=sl.label.replace("రేపు విశేషం", "ఈరోజు విశేషం")) for sl in spec.slides)
    return dataclasses.replace(
        spec, slug=f"cal_today_{day.isoformat()}", slides=slides,
        title=f"ఈరోజు {name} | {_short_date(day)}: చేయవలసినవి, చేయకూడనివి"[:99],
        title_en=f"Today {en} ({day.day} {day.strftime('%b')}): Do's and Don'ts"[:100],
        description_te=spec.description_te.replace("🙏 రేపు (", "🙏 ఈరోజు (", 1),
        description_en=spec.description_en.replace("Tomorrow, ", "Today, ", 1))


def build_tomorrow(day: dt.date, keys: list[str]) -> RequestShort:
    o = OBS[keys[0]]
    others = [OBS[k].te for k in keys[1:]]
    name = o.te + (f" + {', '.join(others)}" if others else "")
    en = o.en + (f" + {', '.join(OBS[k].en for k in keys[1:])}" if others else "")
    head = _long_date(day)
    body = [name, o.why, *(f"చేయండి: {x}" for x in o.dos), *(f"వద్దు: {x}" for x in o.donts)]
    slides = (Slide("points", 16.0, f"రేపు విశేషం · {_short_date(day)}", "\n".join(body)),)   # one card
    title = f"రేపు {name} | {_short_date(day)}: చేయవలసినవి, చేయకూడనివి"
    title_en = f"Tomorrow {en} ({day.day} {day.strftime('%b')}): Do's and Don'ts"
    desc_te = (f"🙏 రేపు ({head}): {name}\n{o.why}\n\n✅ చేయవలసినవి:\n" + "\n".join(f"• {x}" for x in o.dos)
               + "\n\n❌ చేయకూడనివి:\n" + "\n".join(f"• {x}" for x in o.donts) + f"\n\n{DISCLAIMER_TE}")
    desc_en = f"Tomorrow, {day.strftime('%A %d %B %Y')}: {en}. Simple do's and don'ts in Telugu.\n{DISCLAIMER_EN}"
    tags = [f"{o.en.lower()}", f"{o.en.lower()} {day.year}", f"{o.en.lower()} date", f"{o.en.lower()} telugu", *o.tags, o.te]
    hashtags = ["#Shorts", f"#{o.en.split()[0]}", "#TeluguPanchangam", "#Devotional", "#Telugu"]
    return _common(f"cal_tomorrow_{day.isoformat()}", keys[0], slides, title, title_en, desc_te, desc_en, tags, hashtags,
                   head, "tomorrow", day)


def _chunks(items: list[str], size: int = 5) -> list[list[str]]:
    n = max(1, -(-len(items) // size))
    per = -(-len(items) // n)
    return [items[i:i + per] for i in range(0, len(items), per)]


def _list_post(year: int, month: int, kinds: tuple[str, ...], category: str, heading: str, cover: str, en: str,
               override: list[str] | None = None) -> RequestShort:
    items = month_items(year, month, kinds)
    mname = MONTH_NAME[month - 1][0]
    lines = []
    for d, k in items:
        wd = WEEKDAY_NAME[d.weekday()][0].removesuffix("వారం")
        lines.append(f"{d.day} {mname} ({wd}) · {OBS[k].te}")
    if override:
        lines = list(override)
    # one card for the whole list (2026-10-22: no 1/2, 2/2 split, no separate outro card)
    slides = (Slide("points", 14.0, f"{mname} {year} {heading}", "\n".join(lines) if lines else "ఈ నెలలో ప్రత్యేక తేదీలు లేవు"),)
    title = f"{mname} {year} {heading} | {en}"
    title_en = f"{en} - {dt.date(year, month, 1).strftime('%B %Y')} Telugu Calendar"
    desc_te = (f"🙏 {mname} {year} {heading}:\n\n" + "\n".join(f"• {ln}" for ln in lines) + f"\n\n{DISCLAIMER_TE}")
    desc_en = f"{en} for {dt.date(year, month, 1).strftime('%B %Y')} in Telugu.\n{DISCLAIMER_EN}"
    tags = [en.lower(), f"{en.lower()} {year}", f"{mname} {year}", f"{dt.date(year, month, 1).strftime('%B').lower()} {year} festivals",
            "telugu calendar 2026", "ekadashi dates", "pradosham dates", "sankashti dates", "karthika masam"]
    hashtags = ["#Shorts", "#TeluguCalendar", f"#{en.split()[0]}", "#Panchangam", "#Telugu"]
    return _common(f"cal_{category}_{year}-{month:02d}", cover, slides, title, title_en, desc_te, desc_en, tags, hashtags,
                   f"{mname} {year}", category, dt.date(year, month, 1))


# The whole month on one card: festivals and the main vratas (owner request 2026-10-23). Curated per month because
# several days (Naraka Chaturdashi, Bhagini Hastha Bhojanam, Nagula Chavithi, Prabodhini Ekadashi, Kshirabdhi Dwadashi)
# are not computed vratas. A month without an entry falls back to the computed festival list. Prabodhini Ekadashi
# follows the Smarta day (Nov 20), Kshirabdhi Dwadashi / Tulasi Vivaham Nov 21.
FULL_MONTH: dict[tuple[int, int], list[str]] = {
    (2026, 11): [
        "5 నవంబర్ · రమా ఏకాదశి",
        "6 నవంబర్ · ధనత్రయోదశి",
        "7 నవంబర్ · మాస శివరాత్రి",
        "8 నవంబర్ · నరక చతుర్దశి, దీపావళి",
        "9 నవంబర్ · అమావాస్య",
        "10 నవంబర్ · కార్తీక మాసం ప్రారంభం",
        "11 నవంబర్ · భగినీ హస్త భోజనం",
        "13 నవంబర్ · నాగుల చవితి",
        "15 నవంబర్ · స్కంద షష్ఠి",
        "16, 23, 30 నవంబర్ · కార్తీక సోమవారం",
        "20 నవంబర్ · ప్రబోధిని ఏకాదశి",
        "21 నవంబర్ · క్షీరాబ్ధి ద్వాదశి (తులసి వివాహం)",
        "24 నవంబర్ · కార్తీక పౌర్ణమి (జ్వాలా తోరణం)",
        "27 నవంబర్ · సంకటహర చతుర్థి",
    ],
    (2026, 12): [
        "1 డిసెంబర్ · కాలభైరవ అష్టమి",
        "4 డిసెంబర్ · ఉత్పన్న ఏకాదశి",
        "7 డిసెంబర్ · కార్తీక సోమవారం, మాస శివరాత్రి",
        "8 డిసెంబర్ · కార్తీక అమావాస్య (కార్తీక మాసం ముగింపు)",
        "9 డిసెంబర్ · మార్గశిర మాసం ప్రారంభం",
        "10, 17, 24, 31 డిసెంబర్ · మార్గశిర లక్ష్మీవారం",
        "15 డిసెంబర్ · సుబ్రహ్మణ్య షష్ఠి",
        "16 డిసెంబర్ · ధనుర్మాసం ప్రారంభం",
        "20 డిసెంబర్ · ముక్కోటి ఏకాదశి, గీతా జయంతి",
        "23 డిసెంబర్ · దత్త జయంతి",
        "26 డిసెంబర్ · సంకటహర చతుర్థి",
    ],
}


def build_festivals(year: int, month: int) -> RequestShort:
    kinds = ("diwali", "karthika", "karthika_somavaram", "karthika_pournami", "nagula_chavithi", "prabodhini", "tulasi_vivaham",
             "margasira", "dhanurmasam", "mukkoti", "datta_jayanti", "margasira_lakshmivaram")
    items = month_items(year, month, kinds)
    cover = items[0][1] if items else "karthika"
    return _list_post(year, month, kinds, "festivals", "పండుగలు", cover, "Festivals List", FULL_MONTH.get((year, month)))


def build_vratas(year: int, month: int) -> RequestShort:
    return _list_post(year, month, VRATAS, "vratas", "వ్రత తేదీలు", "ekadashi", "Ekadashi Pradosham Sankashti Dates")


def playlist_ids(youtube) -> dict[str, str]:
    from channels.engine import upload

    return {cat: upload.find_or_create_playlist(youtube, t, d, "te") for cat, (t, d) in PLAYLIST_TITLES.items()}


def playlist_block(youtube, current: str) -> str:
    try:
        ids = playlist_ids(youtube)
    except Exception:  # noqa: BLE001
        return ""
    order = [current] + [c for c in CATEGORIES if c != current]
    return "▶ ప్లేలిస్ట్‌లు (Playlists):\n" + "\n".join(
        f"{'▶' if c == current else '•'} {PLAYLIST_LABELS[c]}: https://www.youtube.com/playlist?list={ids[c]}" for c in order if c in ids)


# ---------------------------------------------------------------------------------------------------- pooja tips
@dataclass(frozen=True)
class Tip:
    title: str
    points: tuple[str, ...]
    god: str
    photo: str
    tags: tuple[str, ...]


TIPS: tuple[Tip, ...] = (
    Tip("తులసి చెట్టును తాకకూడని సమయాలు",
        ("రాత్రి సమయంలో తాకకూడదు", "ఆదివారం, అమావాస్య, ద్వాదశి రోజున ఆకులు కోయకూడదు", "స్నానం చేయకముందు తాకకూడదు",
         "సాయంత్రం తర్వాత ఆకులు కోయకూడదు", "కోపంతో, నిర్లక్ష్యంగా తాకకూడదు"), "vishnu", "vishnu", ("tulasi rules", "tulasi plant telugu")),
    Tip("పూజకు పూలు లేనప్పుడు ఏం చేయాలి",
        ("అక్షతలతో పూజ చేయవచ్చు", "పూలను చించి అక్షతల్లో కలపకండి", "ఒకటి రెండు పూలు ఉంటే దేవుడి చిత్రపటానికి సమర్పించండి",
         "నామాలు చదువుతూ అక్షతలు సమర్పించవచ్చు", "భక్తి, శుద్ధమైన మనసు ముఖ్యం"), "lakshmi", "lakshmi", ("pooja without flowers", "akshatalu")),
    Tip("దీపారాధన నియమాలు",
        ("దీపం తూర్పు లేదా ఉత్తరం వైపు వెలిగించండి", "దీపాన్ని నోటితో ఊది ఆర్పకూడదు", "శుభ్రమైన నూనె, కొత్త వత్తులు వాడండి",
         "సంధ్యా సమయంలో తప్పక దీపం వెలిగించండి", "దీపం కొండెక్కిన తర్వాత నమస్కరించండి"), "lakshmi", "lakshmi", ("deepam rules", "deeparadhana")),
    Tip("శివుడికి సమర్పించకూడనివి",
        ("తులసి దళాలు సమర్పించకూడదు", "మొగలి పువ్వు (కేతకి) వద్దు", "పసుపు, కుంకుమ లింగానికి వద్దు",
         "బిల్వ దళాలు, తెల్లని పూలు ప్రీతికరం", "శుద్ధ జలం, పాలతో అభిషేకం చేయండి"), "shiva", "shiva", ("shiva pooja rules", "lord shiva songs")),
    Tip("గణపతికి ఏవి సమర్పించాలి",
        ("గరిక (దూర్వా) గణపతికి అతి ప్రీతి", "ఎర్రని పూలు సమర్పించండి", "తులసి దళాలు గణపతికి వద్దు",
         "మోదకాలు, ఉండ్రాళ్లు నివేదించండి", "ఓం గం గణపతయే నమః జపించండి"), "ganesha", "ganesha", ("ganesha pooja", "ganapati stotram telugu")),
    Tip("హనుమంతుడికి ప్రీతికరమైనవి",
        ("సింధూరం సమర్పించండి", "తమలపాకుల మాల వేయండి", "మంగళవారం, శనివారం విశేషం",
         "హనుమాన్ చాలీసా పఠించండి", "శుభ్రంగా, నియమంగా పూజ చేయండి"), "hanuman", "hanuman", ("hanuman pooja", "hanuman chalisa telugu")),
    Tip("ఇంటి గడప నియమాలు",
        ("ఉదయం గడపకు పసుపు, కుంకుమ పెట్టండి", "గుమ్మం ముందు ముగ్గు వేయండి", "గడప మీద కూర్చోకూడదు",
         "గడపపై నిలబడి మాట్లాడకూడదు", "సాయంత్రం గుమ్మం దగ్గర దీపం వెలిగించండి"), "lakshmi", "lakshmi", ("home vastu telugu", "gadapa pooja")),
    Tip("సంధ్యా సమయంలో చేయకూడనివి",
        ("నిద్రపోకూడదు", "భోజనం చేయకూడదు", "ఇల్లు ఊడ్చకూడదు", "గోళ్లు, జుట్టు కత్తిరించకూడదు", "కోపం, గొడవలు వద్దు, దీపం పెట్టి దేవుని స్మరించండి"),
        "lakshmi", "lakshmi", ("sandhya samayam", "evening pooja rules")),
    Tip("శనివారం చేయవలసినవి",
        ("శనికి నువ్వుల నూనెతో దీపం వెలిగించండి", "నల్ల నువ్వులు దానం చేయండి", "హనుమాన్ చాలీసా పఠించండి",
         "పేదలకు అన్నదానం చేయండి", "రావి చెట్టుకు ప్రదక్షిణ చేయండి"), "shani", "shani", ("saturday pooja", "shani pooja telugu")),
    Tip("పూజకు ముందు పాటించాల్సినవి",
        ("స్నానం చేసి శుభ్రమైన వస్త్రాలు ధరించండి", "తూర్పు లేదా ఉత్తరం వైపు కూర్చోండి", "ఆసనం మీద కూర్చుని పూజ చేయండి",
         "సంకల్పం చెప్పుకోండి", "పూజ గదిని శుభ్రంగా ఉంచండి"), "ganesha", "ganesha", ("pooja vidhanam", "pooja rules telugu")),
    Tip("నైవేద్యం పెట్టేటప్పుడు గుర్తుంచుకోండి",
        ("నైవేద్యం తాజాగా వండి శుభ్రంగా సిద్ధం చేయండి", "వండేటప్పుడు రుచి చూడకూడదు", "ఉల్లి, వెల్లుల్లి లేకుండా చేయండి",
         "తులసి దళం వేసి నివేదించండి", "నివేదన తర్వాత ప్రసాదంగా స్వీకరించండి"), "lakshmi", "lakshmi", ("naivedyam rules", "prasadam telugu")),
    Tip("ప్రదక్షిణల సంఖ్య",
        ("గణపతికి 1 లేదా 3 ప్రదక్షిణలు", "ఆంజనేయుడికి 11 ప్రదక్షిణలు", "నవగ్రహాలకు 9 ప్రదక్షిణలు",
         "శివాలయంలో సోమసూత్ర ప్రదక్షిణ చేయాలి", "ప్రదక్షిణ చేసేటప్పుడు నామస్మరణ చేయండి"), "shiva", "shiva", ("pradakshina rules", "temple rules telugu")),
    Tip("ఉదయం లేవగానే చేయవలసినది",
        ("కళ్లు తెరవగానే అరచేతులు చూడండి", "కరాగ్రే వసతే లక్ష్మీ శ్లోకం చదవండి", "భూమాతకు నమస్కరించి కాలు పెట్టండి",
         "ఇష్ట దైవాన్ని స్మరించండి", "కొద్దిసేపు ప్రశాంతంగా కూర్చోండి"), "lakshmi", "lakshmi", ("morning slokas telugu", "karagre vasate lakshmi")),
    Tip("కార్తీక మాసంలో చేయవలసినవి",
        ("తెల్లవారుజామున స్నానం చేసి దీపం వెలిగించండి", "ఉసిరి చెట్టు కింద దీపారాధన చేయండి", "తులసి కోట దగ్గర రోజూ దీపం పెట్టండి",
         "శివాలయంలో దీపదానం చేయండి", "సోమవారాల్లో శివుడికి అభిషేకం చేయండి"), "shiva", "shiva", ("karthika masam", "karthika deepam")),
    Tip("శుక్రవారం లక్ష్మీ పూజ",
        ("ఇంటిని శుభ్రం చేసి ముగ్గు వేయండి", "లక్ష్మీదేవికి ఎర్రని పూలు సమర్పించండి", "సాయంత్రం దీపం వెలిగించండి",
         "లక్ష్మీ అష్టోత్తరం పఠించండి", "పాయసం లేదా పండ్లు నివేదించండి"), "lakshmi", "lakshmi", ("friday lakshmi pooja", "lakshmi devi songs")),
    Tip("శంఖం, గంట వాడే నియమాలు",
        ("పూజ ప్రారంభంలో గంట మోగించండి", "శంఖాన్ని నేలపై నేరుగా పెట్టకూడదు", "శంఖాన్ని శుభ్రంగా కడిగి ఉంచండి",
         "శంఖ జలాన్ని పూజ తర్వాత చల్లుకోండి", "గంటను నిర్లక్ష్యంగా మోగించకండి"), "vishnu", "vishnu", ("shankham rules", "pooja items telugu")),
)


def tip_for(day: dt.date) -> Tip:
    return TIPS[day.toordinal() % len(TIPS)]


def build_tip(day: dt.date) -> RequestShort:
    t = tip_for(day)
    o = Obs("tip", "పూజా నియమాలు", "Pooja Rules", t.god, t.photo, t.title, ("", "", ""), ("", "", ""), t.tags)
    slides = (Slide("points", 16.0, t.title, "\n".join(t.points)),)   # one card
    title = f"{t.title} | పూజా నియమాలు"
    title_en = f"{t.tags[0].title()} | Pooja Rules in Telugu"
    desc_te = f"🙏 {t.title}\n\n" + "\n".join(f"• {p}" for p in t.points) + "\n\nఇవి సంప్రదాయ నమ్మకాలు. మీ కుటుంబ ఆచారం, పండితుల సలహా కూడా పాటించండి 🙏"
    desc_en = f"{t.tags[0].title()}: simple pooja rules in Telugu, as traditionally followed. Follow your family custom and priest's advice."
    tags = [*t.tags, "pooja rules telugu", "pooja niyamalu", "పూజా నియమాలు", "devotional tips telugu"]
    hashtags = ["#Shorts", "#PoojaRules", "#Devotional", "#Telugu", "#SanatanaDharma"]
    return _common(f"cal_tips_{day.isoformat()}", o, slides, title, title_en, desc_te, desc_en, tags, hashtags,
                   _long_date(day), "tips", day)
