"""
Static content for the "Purana Concept" Shorts series -- a SECOND new
series alongside the Purana Story Shorts (post_purana_short.py), but a
genuinely different kind of content, per explicit request (2026-10-02:
"i want another concept other than stories from that puranas pdf"). The
full-narrative story format was already covered by the other series;
this one rotates through SIX different, non-story ways to present
material from the Puranas:

  SLOKA          -- a short puranic/dharmic teaching-line with its
                     meaning, not a narrative.
  SACRED_PLACE   -- a tirtha/kshetra's puranic significance (why it's
                     holy, what visiting or performing rites there is
                     said to do).
  VRATHA         -- a specific vow/observance described in the Puranas
                     and its benefit.
  DHARMA_QA      -- a short question-and-answer on a dharma topic, in
                     the question-sage/answer-teacher pattern the
                     Puranas themselves use repeatedly.
  TRIVIA_LIST    -- an enumerated list the Puranas are built around
                     (the ten avatars, the seven sages, the nine
                     planets) -- naturally shareable/saveable content.
  CHARACTER_QUIZ -- a clue-then-reveal guessing format for a
                     well-known Puranic figure.

ROTATION (per explicit request, "lets rotate above 6 concepts daily"):
PURANA_CONCEPT_SHORTS below is a single flat list, but deliberately
INTERLEAVED one-of-each-type-in-turn (sloka, sacred place, vratha,
dharma Q&A, trivia, quiz, then the next entry of each again...) rather
than grouped by type -- so posting one entry per day, in list order,
naturally cycles through all six concepts before any repeat, exactly as
asked. scripts/post_concept_short.py is what actually advances through
this list one entry per run; this module only defines the content.

SOURCING: this channel's existing practice (see purana_short_stories.py)
is well-known material written fresh in plain modern Telugu, cited to
its Purana HONESTLY -- not a verbatim scripture quotation, and not a
hyper-specific chapter/verse citation this project has no way to
independently verify. Where a teaching is a famous, widely-repeated
maxim whose precise originating verse is genuinely disputed across
sources (e.g. "dharmo rakshati rakshitah"), it is cited to the general
Puranic/dharmashastra tradition rather than pinned to one invented
specific citation.

INVOCATION LINE: same per-entry deity salutation pattern as the story
series (invocation_te). Entries not tied to one specific deity (a trivia
list, a general dharma Q&A) use the universal "ఓం నమో భగవతే వాసుదేవాయ"
rather than defaulting to any one deity's mantra.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConceptType(str, Enum):
    SLOKA = "sloka"
    SACRED_PLACE = "sacred_place"
    VRATHA = "vratha"
    DHARMA_QA = "dharma_qa"
    TRIVIA_LIST = "trivia_list"
    CHARACTER_QUIZ = "character_quiz"


# Badge label shown on the card in place of the story series'
# "పురాణ కథ - N" -- names the concept, not a running count (this series
# doesn't carry the "endless episode number" feature the story series
# has; that was a request specific to that series).
CONCEPT_LABEL_TE: dict[ConceptType, str] = {
    ConceptType.SLOKA: "నేటి పురాణ వాక్యం",
    ConceptType.SACRED_PLACE: "పుణ్య క్షేత్రం",
    ConceptType.VRATHA: "వ్రత మహత్యం",
    ConceptType.DHARMA_QA: "ధర్మ సందేహం",
    ConceptType.TRIVIA_LIST: "పురాణ విశేషాలు",
    ConceptType.CHARACTER_QUIZ: "పాత్రను గుర్తించండి",
}

_UNIVERSAL_INVOCATION = "ఓం నమో భగవతే వాసుదేవాయ"


@dataclass(frozen=True, slots=True)
class PuranaConceptShort:
    concept_type: ConceptType
    title_te: str           # card heading
    title_en: str            # transliterated, for filenames/SEO
    invocation_te: str        # this entry's deity salutation (or the universal one)
    body_te: str               # the main content block, already formatted (line breaks where needed)
    purana_name_te: str
    purana_name_en: str


# --- SLOKA -------------------------------------------------------------

_SLOKA_1 = PuranaConceptShort(
    concept_type=ConceptType.SLOKA,
    title_te="ధర్మమే రక్ష", title_en="Dharma Protects",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "ధర్మో రక్షతి రక్షితః — అంటే, మనం ధర్మాన్ని కాపాడితే ధర్మమే మనలను కాపాడుతుంది. "
        "పురాణాలు మళ్ళీ మళ్ళీ చెప్పే సత్యం ఇదే — ధర్మాన్ని వదలకుండా నడుచుకునేవారికి ఎప్పుడూ "
        "రక్షణ ఉంటుంది."
    ),
    purana_name_te="పురాణ ధర్మ బోధన", purana_name_en="Puranic Dharma Teaching",
)

_SLOKA_2 = PuranaConceptShort(
    concept_type=ConceptType.SLOKA,
    title_te="అహింసే పరమ ధర్మం", title_en="Ahimsa Is Supreme Dharma",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "అహింసా పరమో ధర్మః — ఏ జీవికి బాధ కలిగించకపోవడమే అన్నిటికంటే గొప్ప ధర్మం అని పురాణాలు "
        "బోధిస్తాయి. ఆలోచన, మాట, చేత మూడింటిలోనూ అహింసను పాటించాలన్నదే దీని అసలు అర్థం."
    ),
    purana_name_te="పురాణ ధర్మ బోధన", purana_name_en="Puranic Dharma Teaching",
)

_SLOKA_3 = PuranaConceptShort(
    concept_type=ConceptType.SLOKA,
    title_te="పరోపకారమే పుణ్యం", title_en="Helping Others Is Merit",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "పరులకు సాయం చేయడమే అసలైన పుణ్యకార్యం అని పురాణాలు నొక్కి చెబుతాయి. ఒక చిన్న సాయమైనా "
        "నిస్వార్థంగా చేస్తే, అది గొప్ప పుణ్యఫలాన్ని ఇస్తుందని పెద్దల మాట."
    ),
    purana_name_te="పురాణ ధర్మ బోధన", purana_name_en="Puranic Dharma Teaching",
)

# --- SACRED_PLACE --------------------------------------------------------

_PLACE_KASHI = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="కాశీ క్షేత్ర మహాత్మ్యం", title_en="Kashi Kshetra Mahatyam",
    invocation_te="ఓం నమః శివాయ",
    body_te=(
        "కాశీ (వారణాసి) పరమశివుని నివాస క్షేత్రంగా పురాణాలు కొనియాడతాయి. ఇక్కడ మరణించినవారికి "
        "మోక్షం లభిస్తుందని స్కంద పురాణం చెబుతుంది. గంగా నది ఒడ్డున ఉన్న ఈ పుణ్యక్షేత్రాన్ని "
        "సందర్శిస్తే పాపాలు తొలగిపోతాయని నమ్మకం."
    ),
    purana_name_te="స్కంద పురాణం", purana_name_en="Skanda Purana",
)

_PLACE_GAYA = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="గయా క్షేత్ర మహాత్మ్యం", title_en="Gaya Kshetra Mahatyam",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "పితృదేవతలకు పిండప్రదానం చేస్తే మోక్షం లభించే పుణ్యక్షేత్రంగా గయను పురాణాలు కీర్తిస్తాయి. "
        "ఇక్కడ శ్రీమహావిష్ణువు స్వయంగా తన పాదాన్ని నిలిపాడని కథనం — అందుకే దీన్ని 'విష్ణుపాద "
        "క్షేత్రం' అని కూడా పిలుస్తారు."
    ),
    purana_name_te="వాయు పురాణం", purana_name_en="Vayu Purana",
)

_PLACE_PRAYAGA = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="ప్రయాగ త్రివేణీ సంగమం", title_en="Prayaga Triveni Sangam",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "గంగ, యమున, అంతర్వాహినిగా సరస్వతి కలిసే ప్రయాగ త్రివేణీ సంగమాన్ని పురాణాలు అత్యంత "
        "పవిత్ర తీర్థంగా వర్ణిస్తాయి. ఇక్కడ స్నానం చేస్తే పాపాలు తొలగిపోతాయని, అందుకే పన్నెండేళ్ళ "
        "కొకసారి కుంభమేళా ఇక్కడ జరుగుతుందని నమ్మకం."
    ),
    purana_name_te="పద్మ పురాణం", purana_name_en="Padma Purana",
)

# --- VRATHA --------------------------------------------------------------

_VRATHA_EKADASHI = PuranaConceptShort(
    concept_type=ConceptType.VRATHA,
    title_te="ఏకాదశి వ్రత మహత్యం", title_en="Ekadashi Vratha Mahatyam",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "ప్రతి నెలా వచ్చే ఏకాదశి రోజున ఉపవాసం ఉండి శ్రీమహావిష్ణువును పూజించడం వల్ల పాపాలు తొలగి "
        "పుణ్యం లభిస్తుందని పురాణాలు చెబుతాయి. ఈ వ్రతాన్ని శ్రద్ధగా ఆచరించేవారికి మనశ్శాంతి, "
        "ఆరోగ్యం కలుగుతాయని నమ్మకం."
    ),
    purana_name_te="పద్మ పురాణం", purana_name_en="Padma Purana",
)

_VRATHA_SATYANARAYANA = PuranaConceptShort(
    concept_type=ConceptType.VRATHA,
    title_te="సత్యనారాయణ వ్రతం", title_en="Satyanarayana Vratham",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "ఏ శుభకార్యం చేసినా, ఏ కోరిక నెరవేరినా సత్యనారాయణ స్వామి వ్రతం చేయడం తెలుగు ఇళ్ళలో "
        "ఆనవాయితీ. నిజాయితీగా, భక్తితో ఈ వ్రతం చేస్తే కుటుంబంలో సుఖసంతోషాలు నెలకొంటాయని "
        "స్కంద పురాణంలోని కథనం చెబుతుంది."
    ),
    purana_name_te="స్కంద పురాణం", purana_name_en="Skanda Purana",
)

_VRATHA_VARALAKSHMI = PuranaConceptShort(
    concept_type=ConceptType.VRATHA,
    title_te="వరలక్ష్మీ వ్రతం", title_en="Varalakshmi Vratham",
    invocation_te="ఓం శ్రీ మహాలక్ష్మ్యై నమః",
    body_te=(
        "శ్రావణ మాసంలో వచ్చే వరలక్ష్మీ వ్రతం ఆచరిస్తే లక్ష్మీదేవి అనుగ్రహం వల్ల ఐశ్వర్యం, "
        "సౌభాగ్యం లభిస్తాయని పురాణాలు చెబుతాయి. ఇంటిల్లిపాదికీ శుభం కలిగించే ఈ వ్రతాన్ని "
        "స్త్రీలు ప్రత్యేక భక్తితో చేస్తారు."
    ),
    purana_name_te="స్కంద పురాణం", purana_name_en="Skanda Purana",
)

# --- DHARMA_QA -------------------------------------------------------------

_QA_DHARMA = PuranaConceptShort(
    concept_type=ConceptType.DHARMA_QA,
    title_te="ధర్మం అంటే ఏమిటి?", title_en="What Is Dharma?",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "సమాధానం: ఇతరులకు మేలు చేసేది, సత్యానికి కట్టుబడి ఉండేది, తన కర్తవ్యాన్ని నిజాయితీగా "
        "నిర్వర్తించేదే ధర్మం అని పురాణాలు బోధిస్తాయి. ధర్మం పరిస్థితిని బట్టి మారేది కాదు, "
        "అది శాశ్వత సత్యం."
    ),
    purana_name_te="పురాణ ధర్మ బోధన", purana_name_en="Puranic Dharma Teaching",
)

_QA_DANAM = PuranaConceptShort(
    concept_type=ConceptType.DHARMA_QA,
    title_te="దానం ఎందుకు చేయాలి?", title_en="Why Give Charity?",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "సమాధానం: మనకున్నదాంట్లో కొంత ఇతరులకు పంచడం వల్ల మనసు స్వచ్ఛంగా మారుతుందని, "
        "అహంకారం తగ్గుతుందని పురాణాలు చెబుతాయి. నిస్వార్థంగా చేసే దానం అత్యంత పుణ్యప్రదమని "
        "శాస్త్రవచనం."
    ),
    purana_name_te="పురాణ ధర్మ బోధన", purana_name_en="Puranic Dharma Teaching",
)

_QA_KOPAM = PuranaConceptShort(
    concept_type=ConceptType.DHARMA_QA,
    title_te="కోపాన్ని ఎలా జయించాలి?", title_en="How To Conquer Anger?",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "సమాధానం: ఓర్పు, క్షమాగుణం అలవర్చుకోవడమే కోపాన్ని జయించే మార్గమని పురాణాలు బోధిస్తాయి. "
        "కోపం మనిషి వివేకాన్ని నాశనం చేస్తుందని, శాంతమే అసలైన బలమని పెద్దల మాట."
    ),
    purana_name_te="పురాణ ధర్మ బోధన", purana_name_en="Puranic Dharma Teaching",
)

# --- TRIVIA_LIST -----------------------------------------------------------

_TRIVIA_DASHAVATARA = PuranaConceptShort(
    concept_type=ConceptType.TRIVIA_LIST,
    title_te="దశావతారాలు", title_en="The Ten Avatars",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "శ్రీమహావిష్ణువు పది అవతారాలు: మత్స్య, కూర్మ, వరాహ, నరసింహ, వామన, పరశురామ, శ్రీరామ, "
        "బలరామ, శ్రీకృష్ణ, కల్కి. ధర్మాన్ని రక్షించడానికి ఆయా యుగాల్లో ఈ అవతారాలు దాల్చాడని "
        "పురాణాలు చెబుతాయి."
    ),
    purana_name_te="భాగవత పురాణం", purana_name_en="Bhagavata Purana",
)

_TRIVIA_SAPTARISHI = PuranaConceptShort(
    concept_type=ConceptType.TRIVIA_LIST,
    title_te="సప్త ఋషులు", title_en="The Seven Sages",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "పురాణాల్లో ప్రస్తావించే సప్తఋషులు: వశిష్ఠ, విశ్వామిత్ర, కశ్యప, భరద్వాజ, జమదగ్ని, "
        "గౌతమ, అత్రి. వీరు వేదవిద్యకు, సృష్టి పరిరక్షణకు మూలస్తంభాలుగా పురాణాల్లో "
        "కీర్తించబడ్డారు."
    ),
    purana_name_te="మత్స్య పురాణం", purana_name_en="Matsya Purana",
)

_TRIVIA_NAVAGRAHA = PuranaConceptShort(
    concept_type=ConceptType.TRIVIA_LIST,
    title_te="నవగ్రహాలు", title_en="The Nine Planets",
    invocation_te=_UNIVERSAL_INVOCATION,
    body_te=(
        "పురాణాల ప్రకారం నవగ్రహాలు: సూర్య, చంద్ర, కుజ, బుధ, గురు, శుక్ర, శని, రాహు, కేతు. "
        "ఈ తొమ్మిది గ్రహాలు మానవ జీవితాన్ని, కర్మఫలాలను ప్రభావితం చేస్తాయని పురాణ జ్యోతిష "
        "గ్రంథాలు వివరిస్తాయి."
    ),
    purana_name_te="పురాణ జ్యోతిష విజ్ఞానం", purana_name_en="Puranic Astrological Tradition",
)

# --- CHARACTER_QUIZ ----------------------------------------------------------

_QUIZ_HANUMAN = PuranaConceptShort(
    concept_type=ConceptType.CHARACTER_QUIZ,
    title_te="ఈ పాత్రను గుర్తించండి", title_en="Guess This Character",
    invocation_te="ఓం శ్రీ హనుమతే నమః",
    body_te=(
        "క్లూ: ఈయన వాయుదేవుని కుమారుడు. రామభక్తికి మారుపేరు. సంజీవిని పర్వతాన్నే మోసుకొచ్చిన "
        "బలశాలి.\n\nజవాబు: ఈయనే హనుమంతుడు!"
    ),
    purana_name_te="పురాణ పాత్రలు", purana_name_en="Puranic Characters",
)

_QUIZ_NARADA = PuranaConceptShort(
    concept_type=ConceptType.CHARACTER_QUIZ,
    title_te="ఈ పాత్రను గుర్తించండి", title_en="Guess This Character",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "క్లూ: ఈయన బ్రహ్మదేవుని మానసపుత్రుడు. చేతిలో వీణతో 'నారాయణ నారాయణ' అంటూ ముల్లోకాలు "
        "తిరుగుతుంటాడు. కథలను ముందుకు నడిపించే దేవర్షి ఈయనే.\n\nజవాబు: ఈయనే నారద మహర్షి!"
    ),
    purana_name_te="పురాణ పాత్రలు", purana_name_en="Puranic Characters",
)

_QUIZ_GARUDA = PuranaConceptShort(
    concept_type=ConceptType.CHARACTER_QUIZ,
    title_te="ఈ పాత్రను గుర్తించండి", title_en="Guess This Character",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "క్లూ: ఈయన శ్రీమహావిష్ణువు వాహనం. పక్షిరాజుగా పిలువబడతాడు. తల్లి దాస్యవిముక్తి కోసం "
        "అమృతాన్ని తీసుకొచ్చిన పరాక్రమశాలి.\n\nజవాబు: ఈయనే గరుడుడు!"
    ),
    purana_name_te="పురాణ పాత్రలు", purana_name_en="Puranic Characters",
)

# --- 2026-10-24 additions: temple kshetras and the seven Chiranjeevis (YouTube Studio idea evaluation) ---

_PLACE_TIRUMALA = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="తిరుమల శ్రీవారి క్షేత్ర మహాత్మ్యం", title_en="Tirumala Srivari Kshetra Mahatyam",
    invocation_te="ఓం నమో వేంకటేశాయ",
    body_te=(
        "శేషాచలం కొండలపై వెలసిన శ్రీ వేంకటేశ్వరుని క్షేత్రమే తిరుమల. కలియుగంలో భక్తులను కాపాడడానికి శ్రీమహావిష్ణువు ఇక్కడ వెలిశాడని పురాణాలు చెబుతాయి. స్వామివారికి తలనీలాలు సమర్పించడం, వైకుంఠ ఏకాదశి దర్శనం భక్తులకు ఎంతో పవిత్రం."
    ),
    purana_name_te="వరాహ పురాణం", purana_name_en="Varaha Purana",
)

_PLACE_SRISAILAM = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="శ్రీశైల క్షేత్ర మహాత్మ్యం", title_en="Srisailam Kshetra Mahatyam",
    invocation_te="ఓం నమః శివాయ",
    body_te=(
        "నల్లమల కొండలపై, కృష్ణా నది ఒడ్డున ఉన్న శ్రీశైలంలో మల్లికార్జున స్వామి జ్యోతిర్లింగంగా, భ్రమరాంబా దేవి శక్తిపీఠంగా కొలువై ఉన్నారు. పన్నెండు జ్యోతిర్లింగాల్లో, పద్దెనిమిది మహాశక్తి పీఠాల్లో ఈ క్షేత్రం ఒకటి కావడమే దీని ప్రత్యేకత."
    ),
    purana_name_te="స్కంద పురాణం (శ్రీశైల ఖండం)", purana_name_en="Skanda Purana",
)

_PLACE_ARUNACHALAM = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="అరుణాచల క్షేత్ర మహాత్మ్యం", title_en="Arunachalam Kshetra Mahatyam",
    invocation_te="ఓం నమః శివాయ",
    body_te=(
        "తిరువణ్ణామలై అరుణాచలం పంచభూత క్షేత్రాల్లో అగ్ని క్షేత్రం. ఆ కొండే శివలింగ స్వరూపమని భక్తుల నమ్మకం. పౌర్ణమి రోజున గిరి ప్రదక్షిణ, కార్తిక దీపోత్సవం ఇక్కడ ఎంతో ప్రసిద్ధి."
    ),
    purana_name_te="స్కంద పురాణం (అరుణాచల మాహాత్మ్యం)", purana_name_en="Skanda Purana",
)

_PLACE_RAMESWARAM = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="రామేశ్వర క్షేత్ర మహాత్మ్యం", title_en="Rameswaram Kshetra Mahatyam",
    invocation_te="ఓం నమః శివాయ",
    body_te=(
        "లంకకు వెళ్ళే ముందు శ్రీరాముడు సముద్ర తీరంలో శివలింగాన్ని ప్రతిష్ఠించిన క్షేత్రమే రామేశ్వరం అని పురాణ కథనం. ఇది పన్నెండు జ్యోతిర్లింగాల్లో ఒకటి, చార్‌ధామ్ క్షేత్రాల్లో కూడా ఒకటి."
    ),
    purana_name_te="స్కంద పురాణం", purana_name_en="Skanda Purana",
)

_PLACE_PURI = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="పూరీ జగన్నాథ క్షేత్ర మహాత్మ్యం", title_en="Puri Jagannath Kshetra Mahatyam",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "పూరీ జగన్నాథ క్షేత్రం చార్‌ధామ్ క్షేత్రాల్లో ఒకటి. ప్రతి సంవత్సరం జరిగే రథయాత్రలో జగన్నాథుడు, బలభద్రుడు, సుభద్రాదేవి భారీ రథాలపై ఊరేగుతారు. ఆ రథాన్ని లాగడం పుణ్యమని భక్తులు నమ్ముతారు."
    ),
    purana_name_te="స్కంద పురాణం (పురుషోత్తమ క్షేత్రం)", purana_name_en="Skanda Purana",
)

_TRIVIA_CHIRANJEEVI = PuranaConceptShort(
    concept_type=ConceptType.TRIVIA_LIST,
    title_te="ఏడుగురు చిరంజీవులు", title_en="The Seven Chiranjeevis",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "పురాణాలు చెప్పే ఏడుగురు చిరంజీవులు: అశ్వత్థామ, మహాబలి, వ్యాసుడు, హనుమంతుడు, విభీషణుడు, "
        "కృపాచార్యుడు, పరశురాముడు. వీరు ఈ కలియుగంలో కూడా జీవించి ఉన్నారని సంప్రదాయ విశ్వాసం."
    ),
    purana_name_te="పురాణ సంప్రదాయం", purana_name_en="Puranic Tradition",
)

_QUIZ_PARASHURAMA = PuranaConceptShort(
    concept_type=ConceptType.CHARACTER_QUIZ,
    title_te="ఈ చిరంజీవి ఎవరు?", title_en="Guess The Chiranjeevi",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "క్లూ: ఈయన జమదగ్ని మహర్షి కుమారుడు. చేతిలో గండ్రగొడ్డలి ధరించిన విష్ణువు ఆరవ అవతారం. చిరంజీవులలో ఒకరు.\n\nజవాబు: ఈయనే పరశురాముడు!"
    ),
    purana_name_te="పురాణ పాత్రలు", purana_name_en="Puranic Characters",
)

_QUIZ_VIBHISHANA = PuranaConceptShort(
    concept_type=ConceptType.CHARACTER_QUIZ,
    title_te="ఈ చిరంజీవి ఎవరు?", title_en="Guess The Chiranjeevi",
    invocation_te="ఓం శ్రీరామాయ నమః",
    body_te=(
        "క్లూ: ఈయన రావణుని తమ్ముడు అయినా ధర్మం వైపు నిలిచి శ్రీరాముని శరణు కోరాడు. యుద్ధం తర్వాత లంకకు రాజయ్యాడు. చిరంజీవులలో ఒకరు.\n\nజవాబు: ఈయనే విభీషణుడు!"
    ),
    purana_name_te="పురాణ పాత్రలు", purana_name_en="Puranic Characters",
)

_QUIZ_ASHWATTHAMA = PuranaConceptShort(
    concept_type=ConceptType.CHARACTER_QUIZ,
    title_te="ఈ చిరంజీవి ఎవరు?", title_en="Guess The Chiranjeevi",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "క్లూ: ఈయన ద్రోణాచార్యుని కుమారుడు. నుదుటిపై పుట్టుకతోనే మణి ఉంది. కురుక్షేత్ర యుద్ధం తర్వాత శాపం పొందిన చిరంజీవి.\n\nజవాబు: ఈయనే అశ్వత్థామ!"
    ),
    purana_name_te="పురాణ పాత్రలు", purana_name_en="Puranic Characters",
)

_QUIZ_MAHABALI = PuranaConceptShort(
    concept_type=ConceptType.CHARACTER_QUIZ,
    title_te="ఈ చిరంజీవి ఎవరు?", title_en="Guess The Chiranjeevi",
    invocation_te="ఓం నమో నారాయణాయ",
    body_te=(
        "క్లూ: ఈయన ప్రహ్లాదుని మనుమడు, గొప్ప దానశీలి. వామనుడు మూడడుగుల నేల అడిగితే ఇచ్చిన చక్రవర్తి. చిరంజీవులలో ఒకరు.\n\nజవాబు: ఈయనే మహాబలి చక్రవర్తి!"
    ),
    purana_name_te="పురాణ పాత్రలు", purana_name_en="Puranic Characters",
)

# --- Tirumala facts series (2026-10-24): well-known, checkable traditions only; no invented 'secrets' ---

_TIRUMALA_1 = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="తిరుమల ఏడు కొండలు", title_en="Tirumala Seven Hills",
    invocation_te="ఓం నమో వేంకటేశాయ",
    body_te=(
        "శ్రీవారి క్షేత్రం ఏడు కొండలపై ఉంది: శేషాద్రి, నీలాద్రి, గరుడాద్రి, అంజనాద్రి, వృషభాద్రి, నారాయణాద్రి, వేంకటాద్రి. అందుకే స్వామిని ఏడుకొండలవాడు అని పిలుస్తారు. వేంకటాద్రి మీదే ఆలయం ఉంది."
    ),
    purana_name_te="తిరుమల సంప్రదాయం", purana_name_en="Tirumala Tradition",
)

_TIRUMALA_2 = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="తిరుమల తలనీలాలు మొక్కు", title_en="Tirumala Hair Offering",
    invocation_te="ఓం నమో వేంకటేశాయ",
    body_te=(
        "తిరుమలలో భక్తులు మొక్కుగా తలనీలాలు సమర్పించడం ఎంతో ప్రసిద్ధి. అహంకారాన్ని వదిలి స్వామికి శరణాగతి చెందడానికి ఇది ప్రతీక అని భక్తుల నమ్మకం. తిరుమల తిరుపతి దేవస్థానం కళ్యాణకట్టల్లో ఈ సేవ అందుబాటులో ఉంటుంది."
    ),
    purana_name_te="తిరుమల సంప్రదాయం", purana_name_en="Tirumala Tradition",
)

_TIRUMALA_3 = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="తిరుమల శ్రీవారి లడ్డు", title_en="Tirumala Srivari Laddu",
    invocation_te="ఓం నమో వేంకటేశాయ",
    body_te=(
        "తిరుమల లడ్డు ప్రసాదం వందల ఏళ్ల సంప్రదాయం. దీనికి 2009లో భౌగోళిక గుర్తింపు (GI ట్యాగ్) లభించింది. దీన్ని ఆలయం లోపల పోటులో తయారు చేస్తారు. శ్రీవారి దర్శనం తర్వాత భక్తులు దీన్ని ప్రసాదంగా తీసుకుంటారు."
    ),
    purana_name_te="తిరుమల సంప్రదాయం", purana_name_en="Tirumala Tradition",
)

_TIRUMALA_4 = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="తిరుమల సుప్రభాత సేవ", title_en="Tirumala Suprabhatam Seva",
    invocation_te="ఓం నమో వేంకటేశాయ",
    body_te=(
        "తిరుమలలో రోజు ప్రారంభం సుప్రభాత సేవతో అవుతుంది. తెల్లవారుజామున శ్రీవారిని మేల్కొలిపే ఈ సేవలో వేంకటేశ్వర సుప్రభాతం పఠిస్తారు. రాత్రి ఏకాంత సేవతో స్వామివారికి విశ్రాంతి ఇస్తారు."
    ),
    purana_name_te="తిరుమల సంప్రదాయం", purana_name_en="Tirumala Tradition",
)

_TIRUMALA_5 = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="శ్రీవారి బ్రహ్మోత్సవాలు, గరుడ సేవ", title_en="Tirumala Brahmotsavam Garuda Seva",
    invocation_te="ఓం నమో వేంకటేశాయ",
    body_te=(
        "తిరుమలలో ఏటా తొమ్మిది రోజులు బ్రహ్మోత్సవాలు జరుగుతాయి. ఇందులో గరుడ సేవ ఎంతో ప్రధానమైనది: శ్రీవారు గరుడ వాహనంపై మాడ వీధుల్లో ఊరేగుతారు. లక్షలాది మంది భక్తులు ఈ వేడుక చూడటానికి వస్తారు."
    ),
    purana_name_te="తిరుమల సంప్రదాయం", purana_name_en="Tirumala Tradition",
)

_TIRUMALA_6 = PuranaConceptShort(
    concept_type=ConceptType.SACRED_PLACE,
    title_te="తిరుమల అలిపిరి మెట్ల మార్గం", title_en="Tirumala Alipiri Footpath",
    invocation_te="ఓం నమో వేంకటేశాయ",
    body_te=(
        "కొండపైకి నడిచి వెళ్ళే భక్తుల కోసం అలిపిరి మెట్ల మార్గం ఉంది. ఇందులో సుమారు మూడున్నర వేల మెట్లు ఉంటాయి. నడిచి వచ్చి స్వామిని దర్శించుకోవడం గొప్ప మొక్కుగా భక్తులు భావిస్తారు."
    ),
    purana_name_te="తిరుమల సంప్రదాయం", purana_name_en="Tirumala Tradition",
)

# Interleaved one-of-each-type-per-turn (see module docstring) so posting
# in list order cycles through all 6 concepts before any repeat.
PURANA_CONCEPT_SHORTS: list[PuranaConceptShort] = [
    _SLOKA_1, _PLACE_KASHI, _VRATHA_EKADASHI, _QA_DHARMA, _TRIVIA_DASHAVATARA, _QUIZ_HANUMAN,
    _SLOKA_2, _PLACE_GAYA, _VRATHA_SATYANARAYANA, _QA_DANAM, _TRIVIA_SAPTARISHI, _QUIZ_NARADA,
    _SLOKA_3, _PLACE_PRAYAGA, _VRATHA_VARALAKSHMI, _QA_KOPAM, _TRIVIA_NAVAGRAHA, _QUIZ_GARUDA,
    # 2026-10-24: temples (Kashi's 871 views was the best of this series) and the Chiranjeevi quizzes, interleaved with the rest
    _PLACE_TIRUMALA, _PLACE_SRISAILAM, _PLACE_ARUNACHALAM, _TRIVIA_CHIRANJEEVI,
    _PLACE_RAMESWARAM, _PLACE_PURI,
    # Tirumala facts, one a day in a row
    _TIRUMALA_1, _TIRUMALA_2, _TIRUMALA_3, _TIRUMALA_4, _TIRUMALA_5, _TIRUMALA_6,
]
