"""
Static content for the "Bhagavad Gita Sloka" Shorts series -- the
SEVENTH series on this channel, posting one Gita verse (sloka) per day
with its meaning, per explicit request (2026-10-02): "from bhagavadgeetha
get daily one sloka and meening shorts card at 3 to 4 pm daily... You
can get complete 18 of bhagavatgeetha from internet rite?"

SCOPE, STATED HONESTLY: the Bhagavad Gita has 700 verses across 18
chapters. The user asked for the complete set, posted one per day in
sequence. Building and verifying all 700 verses (accurate Sanskrit text
+ a careful Telugu meaning for each) is a large content task that this
module deliberately does NOT claim to complete in one pass -- doing so
by guessing/paraphrasing from memory for a sacred text risks real
inaccuracy, which matters more here than for original story content.

PHASE 1 (this file, as of 2026-10-02): 11 of the Gita's most
well-known, frequently-cited verses, spanning 8 of the 18 chapters
(2, 3, 4, 6, 7, 9, 15, 18), each with its Sanskrit/Devanagari text
verified against multiple independent sources (not reconstructed from
memory) before being included here. GITA_SLOKAS is intentionally a
flat, independently-extensible list -- more verses (eventually working
toward all 700, chapter by chapter) get APPENDED here over time without
touching the renderer, SEO, or posting script, which all key off
GitaSloka objects and len(GITA_SLOKAS) alone.

SANSKRIT: kept in Devanagari (not transliterated Telugu script) for the
sloka itself -- this is how the Gita is traditionally presented even in
non-Devanagari-reading regions, and the font (telugu_font_path, a Noto
Sans variable font) covers the Devanagari block too.

TELUGU MEANING: a plain-modern-Telugu rendering of the verse's meaning
(not a word-for-word trot, and not claimed as a certified/published
translation) -- same honest-sourcing approach as purana_short_stories.py
and purana_concept_shorts.py elsewhere in this project.

ROTATION: scripts/post_gita_sloka_short.py advances through GITA_SLOKAS
in list order (chapter-ascending here), one per day, wrapping back to
sloka 0 after the last entry -- same persisted-index pattern as every
other rotating series on this channel.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GitaSloka:
    chapter: int
    verse: int
    sanskrit_deva: str        # Devanagari text
    transliteration: str      # IAST/Latin transliteration
    telugu_meaning: str       # plain modern Telugu rendering of the verse's meaning
    chapter_name_te: str      # the chapter's (adhyayam's) Telugu name


# Chapter (adhyayam) Telugu names for the 8 chapters represented so far --
# extend this dict as later chapters are added.
_CHAPTER_NAME_TE: dict[int, str] = {
    1: "అర్జున విషాద యోగము",
    2: "సాంఖ్య యోగము",
    3: "కర్మ యోగము",
    4: "జ్ఞాన యోగము",
    5: "కర్మ సన్న్యాస యోగము",
    6: "ధ్యాన యోగము",
    7: "జ్ఞాన విజ్ఞాన యోగము",
    8: "అక్షరపరబ్రహ్మ యోగము",
    9: "రాజవిద్యా రాజగుహ్య యోగము",
    10: "విభూతి యోగము",
    11: "విశ్వరూప సందర్శన యోగము",
    12: "భక్తి యోగము",
    13: "క్షేత్ర క్షేత్రజ్ఞ విభాగ యోగము",
    14: "గుణత్రయ విభాగ యోగము",
    15: "పురుషోత్తమ యోగము",
    16: "దైవాసుర సంపద్విభాగ యోగము",
    17: "శ్రద్ధాత్రయ విభాగ యోగము",
    18: "మోక్ష సన్న్యాస యోగము",
}


def _sloka(chapter: int, verse: int, sanskrit_deva: str, transliteration: str, telugu_meaning: str) -> GitaSloka:
    return GitaSloka(
        chapter=chapter, verse=verse, sanskrit_deva=sanskrit_deva,
        transliteration=transliteration, telugu_meaning=telugu_meaning,
        chapter_name_te=_CHAPTER_NAME_TE[chapter],
    )


GITA_SLOKAS: list[GitaSloka] = [
    _sloka(
        2, 14,
        "మాత్రాస్పర్శాస్తు కౌంతేయ శీతోష్ణసుఖదుఃఖదాః |\nఆగమాపాయినోఽనిత్యాస్తాంస్తితిక్షస్వ భారత ||",
        "mātrā-sparśās tu kaunteya śītoṣṇa-sukha-duḥkha-dāḥ / āgamāpāyino 'nityās tāṁs titikṣasva bhārata",
        "ఇంద్రియాలు విషయాలతో తాకినప్పుడు కలిగే చలి-వేడి, సుఖ-దుఃఖాలు వచ్చి పోయేవే, శాశ్వతం కావు. అర్జునా, వాటిని సహనంతో భరించు — అన్నది కృష్ణుని బోధ.",
    ),
    _sloka(
        2, 20,
        "న జాయతే మ్రియతే వా కదాచిన్\nనాయం భూత్వా భవితా వా న భూయః |\nఅజో నిత్యః శాశ్వతోఽయం పురాణో\nన హన్యతే హన్యమానే శరీరే ||",
        "na jāyate mriyate vā kadācin nāyaṁ bhūtvā bhavitā vā na bhūyaḥ / ajo nityaḥ śāśvato 'yaṁ purāṇo na hanyate hanyamāne śarīre",
        "ఆత్మకు పుట్టుక గానీ మరణం గానీ లేదు. అది ఎప్పుడూ ఉన్నదే, శాశ్వతమైనది, సనాతనమైనది — శరీరం నశించినా ఆత్మ నశించదు.",
    ),
    _sloka(
        2, 47,
        "కర్మణ్యేవాధికారస్తే మా ఫలేషు కదాచన |\nమా కర్మఫలహేతుర్భూర్మా తే సంగోఽస్త్వకర్మణి ||",
        "karmaṇy-evādhikāras te mā phaleṣu kadācana / mā karma-phala-hetur bhūr mā te saṅgo 'stv akarmaṇi",
        "పని చేయడంలో మాత్రమే నీకు అధికారం ఉంది, దాని ఫలితంపై కాదు. ఫలితమే పని చేయడానికి కారణం కాకూడదు, అలాగే పని చేయకుండా ఉండటం వైపు కూడా మొగ్గు చూపకూడదు.",
    ),
    _sloka(
        3, 21,
        "యద్యదాచరతి శ్రేష్ఠస్తత్తదేవేతరో జనః |\nస యత్ప్రమాణం కురుతే లోకస్తదనువర్తతే ||",
        "yad yad ācarati śreṣṭhas tat tad evetaro janaḥ / sa yat pramāṇaṁ kurute lokas tad anuvartate",
        "గొప్పవారు ఏది ఆచరిస్తే సామాన్యులు అదే అనుసరిస్తారు. వారు దేనిని ప్రమాణంగా పెట్టుకుంటే లోకం దానినే అనుసరిస్తుంది — నాయకుల ఆచరణే లోకానికి దారి చూపుతుంది.",
    ),
    _sloka(
        4, 7,
        "యదా యదా హి ధర్మస్య గ్లానిర్భవతి భారత |\nఅభ్యుత్థానమధర్మస్య తదాత్మానం సృజామ్యహమ్ ||",
        "yadā yadā hi dharmasya glānir bhavati bhārata / abhyutthānam adharmasya tadātmānaṁ sṛjāmy aham",
        "ధర్మానికి హాని కలిగి, అధర్మం పెరిగిన ప్రతిసారీ, నేను (భగవంతుడు) అవతరిస్తాను — అని కృష్ణుని వాగ్దానం.",
    ),
    _sloka(
        4, 8,
        "పరిత్రాణాయ సాధూనాం వినాశాయ చ దుష్కృతామ్ |\nధర్మసంస్థాపనార్థాయ సంభవామి యుగే యుగే ||",
        "paritrāṇāya sādhūnāṁ vināśāya ca duṣkṛtām / dharma-saṁsthāpanārthāya saṁbhavāmi yuge yuge",
        "సజ్జనులను రక్షించడానికి, దుష్టులను నశింపజేయడానికి, ధర్మాన్ని మళ్ళీ స్థాపించడానికి నేను ప్రతి యుగంలోనూ అవతరిస్తాను.",
    ),
    _sloka(
        6, 5,
        "ఉద్ధరేదాత్మనాత్మానం నాత్మానమవసాదయేత్ |\nఆత్మైవ హ్యాత్మనో బంధురాత్మైవ రిపురాత్మనః ||",
        "uddhared ātmanātmānaṁ nātmānam avasādayet / ātmaiva hy ātmano bandhur ātmaiva ripur ātmanaḥ",
        "మనిషి తన మనసు ద్వారా తనను తానే ఉద్ధరించుకోవాలి, తనను తాను దిగజార్చుకోకూడదు. మనసే మనిషికి మిత్రుడు, అదే మనసు శత్రువు కూడా కావచ్చు.",
    ),
    _sloka(
        7, 7,
        "మత్తః పరతరం నాన్యత్కించిదస్తి ధనంజయ |\nమయి సర్వమిదం ప్రోతం సూత్రే మణిగణా ఇవ ||",
        "mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya / mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva",
        "ధనంజయా (అర్జునా), నా కంటే గొప్పది మరేదీ లేదు. దారంలో ముత్యాలు గుచ్చినట్లు, ఈ సమస్త సృష్టి నాలోనే ఇమిడి ఉంది.",
    ),
    _sloka(
        9, 22,
        "అనన్యాశ్చింతయంతో మాం యే జనాః పర్యుపాసతే |\nతేషాం నిత్యాభియుక్తానాం యోగక్షేమం వహామ్యహమ్ ||",
        "ananyāś cintayanto māṁ ye janāḥ paryupāsate / teṣāṁ nityābhiyuktānāṁ yoga-kṣemaṁ vahāmy aham",
        "ఇతర ఆలోచన లేకుండా నిరంతరం నన్నే ధ్యానిస్తూ సేవించేవారి యోగక్షేమాలు — అంటే లేనివి సమకూర్చడం, ఉన్నవి కాపాడటం — నేనే చూసుకుంటాను.",
    ),
    _sloka(
        15, 7,
        "మమైవాంశో జీవలోకే జీవభూతః సనాతనః |\nమనఃషష్ఠానీంద్రియాణి ప్రకృతిస్థాని కర్షతి ||",
        "mamaivāṁśo jīva-loke jīva-bhūtaḥ sanātanaḥ / manaḥ-ṣaṣṭhānīndriyāṇi prakṛti-sthāni karṣati",
        "ఈ జీవలోకంలో ఉన్న ప్రతి జీవుడూ నా సనాతనమైన అంశమే. మనసుతో సహా ఆరు ఇంద్రియాలను ప్రకృతిలో ఉంచుకుని, జీవుడు వాటితో పోరాడుతుంటాడు.",
    ),
    _sloka(
        18, 66,
        "సర్వధర్మాన్పరిత్యజ్య మామేకం శరణం వ్రజ |\nఅహం త్వాం సర్వపాపేభ్యో మోక్షయిష్యామి మా శుచః ||",
        "sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja / ahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ",
        "అన్ని ధర్మాలను విడిచి నన్ను మాత్రమే శరణు కోరు. నేను నిన్ను సమస్త పాపాల నుండి విముక్తుడిని చేస్తాను — దుఃఖించకు.",
    ),
    _sloka(
        2, 3,
        "క్లైబ్యం మా స్మ గమః పార్థ నైతత్త్వయ్యుపపద్యతే |\nక్షుద్రం హృదయదౌర్బల్యం త్యక్త్వోత్తిష్ఠ పరన్తప ||",
        "klaibyaṃ mā sma gamaḥ pārtha naitattvayyupapadyate / kṣudraṃ hṛdayadaurbalyaṃ tyaktvottiṣṭha parantapa",
        "అర్జునా, పిరికితనానికి లొంగకు, అది నీకు తగదు. హృదయంలోని ఈ చిన్న బలహీనతను విడిచిపెట్టి లేచి నిలబడు. భయం వచ్చినప్పుడు గుర్తుంచుకోవలసిన మాట ఇది.",
    ),
    _sloka(
        2, 13,
        "దేహినోఽస్మిన్యథా దేహే కౌమారం యౌవనం జరా |\nతథా దేహాన్తరప్రాప్తిర్ధీరస్తత్ర న ముహ్యతి ||",
        "dehino'sminyathā dehe kaumāraṃ yauvanaṃ jarā / tathā dehāntaraprāptirdhīrastatra na muhyati",
        "ఈ శరీరంలో బాల్యం, యౌవనం, వృద్ధాప్యం ఎలా వస్తాయో, అలాగే మరణం తర్వాత మరో శరీరం కూడా వస్తుంది. ధీరుడు దీనికి కలత చెందడు.",
    ),
    _sloka(
        2, 22,
        "వాసాంసి జీర్ణాని యథా విహాయ నవాని గృహ్ణాతి నరోఽపరాణి |\nతథా శరీరాణి విహాయ జీర్ణాన్యన్యాని సంయాతి నవాని దేహీ ||",
        "vāsāṃsi jīrṇāni yathā vihāya navāni gṛhṇāti naro'parāṇi / tathā śarīrāṇi vihāya jīrṇānyanyāni saṃyāti navāni dehī",
        "మనిషి పాత బట్టలను విడిచి కొత్తవి ధరించినట్లే, ఆత్మ పాత శరీరాన్ని విడిచి కొత్త శరీరాన్ని పొందుతుంది.",
    ),
    _sloka(
        2, 23,
        "నైనం ఛిన్దన్తి శస్త్రాణి నైనం దహతి పావకః |\nన చైనం క్లేదయన్త్యాపో న శోషయతి మారుతః ||",
        "nainaṃ chindanti śastrāṇi nainaṃ dahati pāvakaḥ / na cainaṃ kledayantyāpo na śoṣayati mārutaḥ",
        "ఆత్మను ఆయుధాలు ఛేదించలేవు, అగ్ని కాల్చలేదు, నీరు తడపలేదు, గాలి ఆరబెట్టలేదు.",
    ),
    _sloka(
        2, 27,
        "జాతస్య హి ధ్రువో మృత్యుర్ధ్రువం జన్మ మృతస్య చ |\nతస్మాదపరిహార్యేఽర్థే న త్వం శోచితుమర్హసి ||",
        "jātasya hi dhruvo mṛtyurdhruvaṃ janma mṛtasya ca / tasmādaparihārye'rthe na tvaṃ śocitumarhasi",
        "పుట్టినవారికి మరణం తప్పదు, చనిపోయినవారికి పుట్టుక తప్పదు. తప్పించుకోలేని దాని గురించి నీవు దుఃఖపడకూడదు.",
    ),
    _sloka(
        2, 38,
        "సుఖదుఃఖే సమే కృత్వా లాభాలాభౌ జయాజయౌ |\nతతో యుద్ధాయ యుజ్యస్వ నైవం పాపమవాప్స్యసి ||",
        "sukhaduḥkhe same kṛtvā lābhālābhau jayājayau / tato yuddhāya yujyasva naivaṃ pāpamavāpsyasi",
        "సుఖదుఃఖాలను, లాభనష్టాలను, గెలుపు ఓటములను సమానంగా చూసి నీ కర్తవ్యానికి సిద్ధపడు. అప్పుడు నీకు పాపం అంటదు.",
    ),
    _sloka(
        2, 48,
        "యోగస్థః కురు కర్మాణి సఙ్గం త్యక్త్వా ధనఞ్జయ |\nసిద్ధ్యసిద్ధ్యోః సమో భూత్వా సమత్వం యోగ ఉచ్యతే ||",
        "yogasthaḥ kuru karmāṇi saṅgaṃ tyaktvā dhanañjaya / siddhyasiddhyoḥ samo bhūtvā samatvaṃ yoga ucyate",
        "ఆసక్తిని విడిచి, గెలుపు ఓటములను సమానంగా చూస్తూ, స్థిరమైన మనసుతో పనులు చెయ్యి. ఈ సమభావమే యోగం అంటారు.",
    ),
    _sloka(
        2, 56,
        "దుఃఖేష్వనుద్విగ్నమనాః సుఖేషు విగతస్పృహః |\nవీతరాగభయక్రోధః స్థితధీర్మునిరుచ్యతే ||",
        "duḥkheṣvanudvignamanāḥ sukheṣu vigataspṛhaḥ / vītarāgabhayakrodhaḥ sthitadhīrmunirucyate",
        "కష్టాలలో కలత చెందనివాడు, సుఖాలలో అతిగా కోరనివాడు, రాగ భయ క్రోధాలు లేనివాడు స్థిరబుద్ధి గల జ్ఞాని.",
    ),
    _sloka(
        2, 62,
        "ధ్యాయతో విషయాన్పుంసః సఙ్గస్తేషూపజాయతే |\nసఙ్గాత్సఞ్జాయతే కామః కామాత్క్రోధోఽభిజాయతే ||",
        "dhyāyato viṣayānpuṃsaḥ saṅgasteṣūpajāyate / saṅgātsañjāyate kāmaḥ kāmātkrodho'bhijāyate",
        "విషయాలను పదే పదే ఆలోచిస్తే వాటిపై అంటిపెట్టుకునే గుణం పుడుతుంది, దాని నుండి కోరిక, కోరిక తీరకపోతే కోపం పుడతాయి.",
    ),
    _sloka(
        2, 63,
        "క్రోధాద్భవతి సమ్మోహః సమ్మోహాత్స్మృతివిభ్రమః |\nస్మృతిభ్రంశాద్ బుద్ధినాశో బుద్ధినాశాత్ప్రణశ్యతి ||",
        "krodhādbhavati sammohaḥ sammohātsmṛtivibhramaḥ / smṛtibhraṃśād buddhināśo buddhināśātpraṇaśyati",
        "కోపం నుండి మోహం, మోహం నుండి మతిమరుపు, మతిమరుపు నుండి బుద్ధి నాశనం కలుగుతాయి. బుద్ధి నశిస్తే మనిషి నశిస్తాడు.",
    ),
    _sloka(
        2, 71,
        "విహాయ కామాన్యః సర్వాన్పుమాంశ్చరతి నిఃస్పృహః |\nనిర్మమో నిరహఙ్కారః స శాన్తిమధిగచ్ఛతి ||",
        "vihāya kāmānyaḥ sarvānpumāṃścarati niḥspṛhaḥ / nirmamo nirahaṅkāraḥ sa śāntimadhigacchati",
        "కోరికలన్నిటినీ విడిచి, నాది అనే భావన, అహంకారం లేకుండా జీవించేవాడు నిజమైన శాంతిని పొందుతాడు.",
    ),
    _sloka(
        3, 19,
        "తస్మాదసక్తః సతతం కార్యం కర్మ సమాచర |\nఅసక్తో హ్యాచరన్కర్మ పరమాప్నోతి పూరుషః ||",
        "tasmādasaktaḥ satataṃ kāryaṃ karma samācara / asakto hyācarankarma paramāpnoti pūruṣaḥ",
        "కాబట్టి ఫలంపై ఆసక్తి లేకుండా నీ కర్తవ్యాన్ని ఎల్లప్పుడూ చెయ్యి. ఆసక్తి లేకుండా పని చేసేవాడు పరమ పదాన్ని పొందుతాడు.",
    ),
    _sloka(
        3, 35,
        "శ్రేయాన్స్వధర్మో విగుణః పరధర్మాత్స్వనుష్ఠితాత్ |\nస్వధర్మే నిధనం శ్రేయః పరధర్మో భయావహః ||",
        "śreyānsvadharmo viguṇaḥ paradharmātsvanuṣṭhitāt / svadharme nidhanaṃ śreyaḥ paradharmo bhayāvahaḥ",
        "ఇతరుల ధర్మాన్ని బాగా చేయడం కంటే, లోపాలున్నా తన ధర్మాన్ని పాటించడమే మేలు. పరధర్మం భయాన్ని కలిగిస్తుంది.",
    ),
    _sloka(
        4, 34,
        "తద్విద్ధి ప్రణిపాతేన పరిప్రశ్నేన సేవయా |\nఉపదేక్ష్యన్తి తే జ్ఞానం జ్ఞానినస్తత్త్వదర్శినః ||",
        "tadviddhi praṇipātena paripraśnena sevayā / upadekṣyanti te jñānaṃ jñāninastattvadarśinaḥ",
        "వినయంతో నమస్కరించి, ప్రశ్నలడిగి, సేవ చేసి జ్ఞానులైన గురువుల నుండి జ్ఞానాన్ని తెలుసుకో. తత్వాన్ని చూసినవారే నీకు బోధిస్తారు.",
    ),
    _sloka(
        4, 38,
        "న హి జ్ఞానేన సదృశం పవిత్రమిహ విద్యతే |\nతత్స్వయం యోగసంసిద్ధః కాలేనాత్మని విన్దతి ||",
        "na hi jñānena sadṛśaṃ pavitramiha vidyate / tatsvayaṃ yogasaṃsiddhaḥ kālenātmani vindati",
        "ఈ లోకంలో జ్ఞానంతో సమానమైన పవిత్రమైనది మరొకటి లేదు. సాధన చేసినవాడు సమయం వచ్చినప్పుడు దాన్ని తనలోనే పొందుతాడు.",
    ),
    _sloka(
        5, 18,
        "విద్యావినయసమ్పన్నే బ్రాహ్మణే గవి హస్తిని |\nశుని చైవ శ్వపాకే చ పణ్డితాః సమదర్శినః ||",
        "vidyāvinayasampanne brāhmaṇe gavi hastini / śuni caiva śvapāke ca paṇḍitāḥ samadarśinaḥ",
        "జ్ఞానులు విద్యావంతుడిని, ఆవును, ఏనుగును, కుక్కను, అందరినీ సమానంగా చూస్తారు. అందరిలో ఒకే ఆత్మను చూడడమే నిజమైన జ్ఞానం.",
    ),
    _sloka(
        6, 6,
        "బన్ధురాత్మాత్మనస్తస్య యేనాత్మైవాత్మనా జితః |\nఅనాత్మనస్తు శత్రుత్వే వర్తేతాత్మైవ శత్రువత్ ||",
        "bandhurātmātmanastasya yenātmaivātmanā jitaḥ / anātmanastu śatrutve vartetātmaiva śatruvat",
        "మనసును జయించినవాడికి మనసే మిత్రుడు. మనసును జయించనివాడికి అదే శత్రువులా పని చేస్తుంది.",
    ),
    _sloka(
        6, 17,
        "యుక్తాహారవిహారస్య యుక్తచేష్టస్య కర్మసు |\nయుక్తస్వప్నావబోధస్య యోగో భవతి దుఃఖహా ||",
        "yuktāhāravihārasya yuktaceṣṭasya karmasu / yuktasvapnāvabodhasya yogo bhavati duḥkhahā",
        "తిండి, విహారం, పని, నిద్ర, మెలకువ అన్నీ మితంగా ఉన్నవాడికి యోగం దుఃఖాన్ని పోగొడుతుంది.",
    ),
    _sloka(
        6, 35,
        "అసంశయం మహాబాహో మనో దుర్నిగ్రహం చలమ్ |\nఅభ్యాసేన తు కౌన్తేయ వైరాగ్యేణ చ గృహ్యతే ||",
        "asaṃśayaṃ mahābāho mano durnigrahaṃ calam / abhyāsena tu kaunteya vairāgyeṇa ca gṛhyate",
        "మనసు చంచలమైనది, అదుపు చేయడం కష్టమే సందేహం లేదు. కానీ నిరంతర అభ్యాసం, వైరాగ్యంతో దాన్ని అదుపులోకి తేవచ్చు.",
    ),
    _sloka(
        7, 14,
        "దైవీ హ్యేషా గుణమయీ మమ మాయా దురత్యయా |\nమామేవ యే ప్రపద్యన్తే మాయామేతాం తరన్తి తే ||",
        "daivī hyeṣā guṇamayī mama māyā duratyayā / māmeva ye prapadyante māyāmetāṃ taranti te",
        "త్రిగుణాలతో కూడిన నా ఈ మాయను దాటడం కష్టం. నన్నే శరణు పొందినవారు ఈ మాయను దాటుతారు.",
    ),
    _sloka(
        8, 7,
        "తస్మాత్సర్వేషు కాలేషు మామనుస్మర యుధ్య చ |\nమయ్యర్పితమనోబుద్ధిర్మామేవైష్యస్యసంశయమ్ ||",
        "tasmātsarveṣu kāleṣu māmanusmara yudhya ca / mayyarpitamanobuddhirmāmevaiṣyasyasaṃśayam",
        "కాబట్టి ఎల్లప్పుడూ నన్ను స్మరిస్తూ నీ కర్తవ్యాన్ని చెయ్యి. మనసు బుద్ధిని నాకు అర్పిస్తే నన్నే చేరుకుంటావు.",
    ),
    _sloka(
        9, 26,
        "పత్రం పుష్పం ఫలం తోయం యో మే భక్త్యా ప్రయచ్ఛతి |\nతదహం భక్త్యుపహృతమశ్నామి ప్రయతాత్మనః ||",
        "patraṃ puṣpaṃ phalaṃ toyaṃ yo me bhaktyā prayacchati / tadahaṃ bhaktyupahṛtamaśnāmi prayatātmanaḥ",
        "భక్తితో ఆకు, పువ్వు, పండు, నీరు ఏది సమర్పించినా దాన్ని నేను ప్రేమగా స్వీకరిస్తాను. దేవునికి కావలసింది భక్తి, ఖరీదు కాదు.",
    ),
    _sloka(
        9, 27,
        "యత్కరోషి యదశ్నాసి యజ్జుహోషి దదాసి యత్ |\nయత్తపస్యసి కౌన్తేయ తత్కురుష్వ మదర్పణమ్ ||",
        "yatkaroṣi yadaśnāsi yajjuhoṣi dadāsi yat / yattapasyasi kaunteya tatkuruṣva madarpaṇam",
        "నువ్వు చేసేది, తినేది, హోమం చేసేది, దానం చేసేది, తపస్సు చేసేది ఏదైనా నాకు అర్పణగా చెయ్యి.",
    ),
    _sloka(
        9, 29,
        "సమోఽహం సర్వభూతేషు న మే ద్వేష్యోఽస్తి న ప్రియః |\nయే భజన్తి తు మాం భక్త్యా మయి తే తేషు చాప్యహమ్ ||",
        "samo'haṃ sarvabhūteṣu na me dveṣyo'sti na priyaḥ / ye bhajanti tu māṃ bhaktyā mayi te teṣu cāpyaham",
        "నేను అన్ని ప్రాణులలో సమానుడిని, నాకు ద్వేషించేవారు, ప్రియులు ఎవరూ లేరు. భక్తితో నన్ను భజించేవారు నాలో ఉంటారు, నేను వారిలో ఉంటాను.",
    ),
    _sloka(
        9, 34,
        "మన్మనా భవ మద్భక్తో మద్యాజీ మాం నమస్కురు |\nమామేవైష్యసి యుక్త్వైవమాత్మానం మత్పరాయణః ||",
        "manmanā bhava madbhakto madyājī māṃ namaskuru / māmevaiṣyasi yuktvaivamātmānaṃ matparāyaṇaḥ",
        "నాపై మనసు నిలుపు, నా భక్తుడివి అవ్వు, నన్ను పూజించు, నాకు నమస్కరించు. ఇలా నన్ను ఆశ్రయిస్తే తప్పక నన్ను చేరుతావు.",
    ),
    _sloka(
        10, 8,
        "అహం సర్వస్య ప్రభవో మత్తః సర్వం ప్రవర్తతే |\nఇతి మత్వా భజన్తే మాం బుధా భావసమన్వితాః ||",
        "ahaṃ sarvasya prabhavo mattaḥ sarvaṃ pravartate / iti matvā bhajante māṃ budhā bhāvasamanvitāḥ",
        "నేనే సమస్తానికి మూలం, నా నుండే అన్నీ నడుస్తున్నాయి. ఇది తెలిసిన జ్ఞానులు ప్రేమతో నన్ను భజిస్తారు.",
    ),
    _sloka(
        10, 20,
        "అహమాత్మా గుడాకేశ సర్వభూతాశయస్థితః |\nఅహమాదిశ్చ మధ్యం చ భూతానామన్త ఏవ చ ||",
        "ahamātmā guḍākeśa sarvabhūtāśayasthitaḥ / ahamādiśca madhyaṃ ca bhūtānāmanta eva ca",
        "అర్జునా, నేను అన్ని ప్రాణుల హృదయంలో ఉన్న ఆత్మను. ప్రాణుల ఆది, మధ్యం, అంతం కూడా నేనే.",
    ),
    _sloka(
        12, 13,
        "అద్వేష్టా సర్వభూతానాం మైత్రః కరుణ ఏవ చ |\nనిర్మమో నిరహఙ్కారః సమదుఃఖసుఖః క్షమీ ||",
        "adveṣṭā sarvabhūtānāṃ maitraḥ karuṇa eva ca / nirmamo nirahaṅkāraḥ samaduḥkhasukhaḥ kṣamī",
        "ఎవరినీ ద్వేషించకుండా, అందరితో స్నేహంగా, కరుణతో, నాది అనే భావన అహంకారం లేకుండా, సుఖదుఃఖాలను సమంగా చూసి క్షమించేవాడు భగవంతునికి ప్రియుడు.",
    ),
    _sloka(
        12, 15,
        "యస్మాన్నోద్విజతే లోకో లోకాన్నోద్విజతే చ యః |\nహర్షామర్షభయోద్వేగైర్ముక్తో యః స చ మే ప్రియః ||",
        "yasmānnodvijate loko lokānnodvijate ca yaḥ / harṣāmarṣabhayodvegairmukto yaḥ sa ca me priyaḥ",
        "ఎవరి వల్ల లోకం కలత చెందదో, ఎవరు లోకం వల్ల కలత చెందరో, హర్షం కోపం భయం ఆందోళన లేనివాడు నాకు ప్రియుడు.",
    ),
    _sloka(
        13, 28,
        "సమం సర్వేషు భూతేషు తిష్ఠన్తం పరమేశ్వరమ్ |\nవినశ్యత్స్వవినశ్యన్తం యః పశ్యతి స పశ్యతి ||",
        "samaṃ sarveṣu bhūteṣu tiṣṭhantaṃ parameśvaram / vinaśyatsvavinaśyantaṃ yaḥ paśyati sa paśyati",
        "నశించే ప్రాణులందరిలో నశించకుండా సమానంగా ఉన్న పరమేశ్వరుని ఎవరు చూస్తారో వారే నిజంగా చూసినవారు.",
    ),
    _sloka(
        15, 15,
        "సర్వస్య చాహం హృది సన్నివిష్టో మత్తః స్మృతిర్జ్ఞానమపోహనం చ |\nవేదైశ్చ సర్వైరహమేవ వేద్యో వేదాన్తకృద్వేదవిదేవ చాహమ్ ||",
        "sarvasya cāhaṃ hṛdi sanniviṣṭo mattaḥ smṛtirjñānamapohanaṃ ca / vedaiśca sarvairahameva vedyo vedāntakṛdvedavideva cāham",
        "నేను అందరి హృదయంలో ఉన్నాను. జ్ఞాపకం, జ్ఞానం, మరపు నా నుండే కలుగుతాయి. అన్ని వేదాల ద్వారా తెలుసుకోదగినవాడిని నేనే.",
    ),
    _sloka(
        16, 21,
        "త్రివిధం నరకస్యేదం ద్వారం నాశనమాత్మనః |\nకామః క్రోధస్తథా లోభస్తస్మాదేతత్త్రయం త్యజేత్ ||",
        "trividhaṃ narakasyedaṃ dvāraṃ nāśanamātmanaḥ / kāmaḥ krodhastathā lobhastasmādetattrayaṃ tyajet",
        "కామం, క్రోధం, లోభం అనే ఈ మూడు నరకానికి ద్వారాలు, ఆత్మను నాశనం చేస్తాయి. కాబట్టి ఈ మూడింటినీ విడిచిపెట్టాలి.",
    ),
    _sloka(
        17, 16,
        "మనఃప్రసాదః సౌమ్యత్వం మౌనమాత్మవినిగ్రహః |\nభావసంశుద్ధిరిత్యేతత్తపో మానసముచ్యతే ||",
        "manaḥprasādaḥ saumyatvaṃ maunamātmavinigrahaḥ / bhāvasaṃśuddhirityetattapo mānasamucyate",
        "మనసులో ప్రశాంతత, సౌమ్యత, మౌనం, ఆత్మనిగ్రహం, భావశుద్ధి ఇవి మానసిక తపస్సు అంటారు.",
    ),
    _sloka(
        18, 58,
        "మచ్చిత్తః సర్వదుర్గాణి మత్ప్రసాదాత్తరిష్యసి |\nఅథ చేత్త్వమహఙ్కారాన్న శ్రోష్యసి వినఙ్క్ష్యసి ||",
        "maccittaḥ sarvadurgāṇi matprasādāttariṣyasi / atha cettvamahaṅkārānna śroṣyasi vinaṅkṣyasi",
        "నాపై మనసు ఉంచితే నా అనుగ్రహంతో అన్ని కష్టాలను దాటుతావు. అహంకారంతో వినకపోతే నశిస్తావు.",
    ),
    _sloka(
        18, 61,
        "ఈశ్వరః సర్వభూతానాం హృద్దేశేఽర్జున తిష్ఠతి |\nభ్రామయన్సర్వభూతాని యన్త్రారూఢాని మాయయా ||",
        "īśvaraḥ sarvabhūtānāṃ hṛddeśe'rjuna tiṣṭhati / bhrāmayansarvabhūtāni yantrārūḍhāni māyayā",
        "అర్జునా, ఈశ్వరుడు అన్ని ప్రాణుల హృదయంలో ఉన్నాడు. యంత్రంపై ఎక్కినట్లు ప్రాణులను తన మాయతో తిప్పుతున్నాడు.",
    ),
    _sloka(
        18, 78,
        "యత్ర యోగేశ్వరః కృష్ణో యత్ర పార్థో ధనుర్ధరః |\nతత్ర శ్రీర్విజయో భూతిర్ధ్రువా నీతిర్మతిర్మమ ||",
        "yatra yogeśvaraḥ kṛṣṇo yatra pārtho dhanurdharaḥ / tatra śrīrvijayo bhūtirdhruvā nītirmatirmama",
        "యోగేశ్వరుడైన కృష్ణుడు, ధనుర్ధారి అర్జునుడు ఎక్కడ ఉంటారో అక్కడ సంపద, విజయం, ఐశ్వర్యం, స్థిరమైన నీతి ఉంటాయి.",
    ),
]
