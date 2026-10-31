"""Scrolling-lyrics Shorts: a long devotional text scrolls slowly over a deity photo (owner request 2026-10-28, modelled
on a popular "Hanuman Chalisa Telugu" scrolling Short). Add a spec to SCROLL to make the next one.

The Hanuman Chalisa is a 16th-century public-domain text (Tulsidas); this is the standard text in Telugu script."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScrollShort:
    slug: str
    photo: str                  # file under assets/images/deities
    lines: tuple[str, ...]      # "" = a blank gap between verses
    seconds: float
    title: str
    title_en: str
    description: str
    description_en: str
    hashtags: list[str]
    tags: list[str]
    lang: str = "te"
    token_file: str = "youtube_token.json"
    expected_channel: str = "Mahanavi"
    gold_lines: int = 0         # the first N non-blank blocks are drawn gold (invocation / dohas)
    dim: float = 0.45           # darkness of the photo behind the text (0-1)
    heading: tuple[str, ...] = field(default_factory=tuple)
    bg: str = ""                # "news:<person>" = gradient + faded portrait instead of a deity photo
    music: str = ""             # optional music file relative to the repo root


def _v(*couplets: str) -> tuple[str, ...]:
    out: list[str] = []
    for c in couplets:
        out += c.split("\n") + [""]
    return tuple(out)


_DOHA_OPEN = (
    "శ్రీ గురు చరణ సరోజ రజ నిజ మన ముకుర సుధారి ।\nబరనఉం రఘుబర బిమల జసు జో దాయకు ఫల చారి ॥",
    "బుద్ధిహీన తను జానికే సుమిరౌ పవన కుమార ।\nబల బుద్ధి విద్యా దేహు మోహి హరహు కలేశ వికార ॥",
)
_CHAUPAI = (
    "జయ హనుమాన జ్ఞాన గుణ సాగర ।\nజయ కపీశ తిహు లోక ఉజాగర ॥ 1 ॥",
    "రామదూత అతులిత బల ధామా ।\nఅంజని పుత్ర పవనసుత నామా ॥ 2 ॥",
    "మహావీర విక్రమ బజరంగీ ।\nకుమతి నివార సుమతి కే సంగీ ॥ 3 ॥",
    "కంచన వరణ విరాజ సువేశా ।\nకానన కుండల కుంచిత కేశా ॥ 4 ॥",
    "హాథ వజ్ర ఔ ధ్వజా విరాజై ।\nకాంధే మూంజ జనేవూ సాజై ॥ 5 ॥",
    "శంకర సువన కేసరీ నందన ।\nతేజ ప్రతాప మహా జగ వందన ॥ 6 ॥",
    "విద్యావాన గుణీ అతి చాతుర ।\nరామ కాజ కరివే కో ఆతుర ॥ 7 ॥",
    "ప్రభు చరిత్ర సునివే కో రసియా ।\nరామ లఖన సీతా మన బసియా ॥ 8 ॥",
    "సూక్ష్మ రూప ధరి సియహిం దిఖావా ।\nవికట రూప ధరి లంక జరావా ॥ 9 ॥",
    "భీమ రూప ధరి అసుర సంహారే ।\nరామచంద్ర కే కాజ సంవారే ॥ 10 ॥",
    "లాయ సంజీవన లఖన జియాయే ।\nశ్రీ రఘువీర హరషి ఉర లాయే ॥ 11 ॥",
    "రఘుపతి కీన్హీ బహుత బడాఈ ।\nతుమ మమ ప్రియ భరతహి సమ భాఈ ॥ 12 ॥",
    "సహస బదన తుమ్హరో జస గావైం ।\nఅస కహి శ్రీపతి కంఠ లగావైం ॥ 13 ॥",
    "సనకాదిక బ్రహ్మాది మునీశా ।\nనారద శారద సహిత అహీశా ॥ 14 ॥",
    "జమ కుబేర దిగపాల జహాం తే ।\nకవి కోవిద కహి సకే కహాం తే ॥ 15 ॥",
    "తుమ ఉపకార సుగ్రీవహిం కీన్హా ।\nరామ మిలాయ రాజపద దీన్హా ॥ 16 ॥",
    "తుమ్హరో మంత్ర విభీషణ మానా ।\nలంకేశ్వర భే సబ జగ జానా ॥ 17 ॥",
    "జుగ సహస్ర జోజన పర భానూ ।\nలీల్యో తాహి మధుర ఫల జానూ ॥ 18 ॥",
    "ప్రభు ముద్రికా మేలి ముఖ మాహీం ।\nజలధి లాంఘి గయే అచరజ నాహీం ॥ 19 ॥",
    "దుర్గమ కాజ జగత కే జేతే ।\nసుగమ అనుగ్రహ తుమ్హరే తేతే ॥ 20 ॥",
    "రామ దుఆరే తుమ రఖవారే ।\nహోత న ఆజ్ఞా బిను పైసారే ॥ 21 ॥",
    "సబ సుఖ లహై తుమ్హారీ శరనా ।\nతుమ రక్షక కాహూ కో డర నా ॥ 22 ॥",
    "ఆపన తేజ సంహారో ఆపై ।\nతీనోం లోక హాంక తే కాంపై ॥ 23 ॥",
    "భూత పిశాచ నికట నహిం ఆవై ।\nమహావీర జబ నామ సునావై ॥ 24 ॥",
    "నాసై రోగ హరై సబ పీరా ।\nజపత నిరంతర హనుమత బీరా ॥ 25 ॥",
    "సంకట తే హనుమాన ఛుడావై ।\nమన క్రమ వచన ధ్యాన జో లావై ॥ 26 ॥",
    "సబ పర రామ తపస్వీ రాజా ।\nతిన కే కాజ సకల తుమ సాజా ॥ 27 ॥",
    "ఔర మనోరథ జో కోఇ లావై ।\nసోఇ అమిత జీవన ఫల పావై ॥ 28 ॥",
    "చారో జుగ పరతాప తుమ్హారా ।\nహై పరసిద్ధ జగత ఉజియారా ॥ 29 ॥",
    "సాధు సంత కే తుమ రఖవారే ।\nఅసుర నికందన రామ దులారే ॥ 30 ॥",
    "అష్ట సిద్ధి నౌ నిధి కే దాతా ।\nఅస బర దీన జానకీ మాతా ॥ 31 ॥",
    "రామ రసాయన తుమ్హరే పాసా ।\nసదా రహో రఘుపతి కే దాసా ॥ 32 ॥",
    "తుమ్హరే భజన రామ కో పావై ।\nజనమ జనమ కే దుఖ బిసరావై ॥ 33 ॥",
    "అంత కాల రఘుబర పుర జాఈ ।\nజహాం జన్మ హరి భక్త కహాఈ ॥ 34 ॥",
    "ఔర దేవతా చిత్త న ధరఈ ।\nహనుమత సేఇ సర్వ సుఖ కరఈ ॥ 35 ॥",
    "సంకట కటై మిటై సబ పీరా ।\nజో సుమిరై హనుమత బలబీరా ॥ 36 ॥",
    "జై జై జై హనుమాన గోసాఈం ।\nకృపా కరహు గురు దేవ కీ నాఈం ॥ 37 ॥",
    "జో శత బార పాఠ కర కోఈ ।\nఛూటహి బంది మహా సుఖ హోఈ ॥ 38 ॥",
    "జో యహ పడ్హై హనుమాన చాలీసా ।\nహోయ సిద్ధి సాఖీ గౌరీసా ॥ 39 ॥",
    "తులసీదాస సదా హరి చేరా ।\nకీజై నాథ హృదయ మహం డేరా ॥ 40 ॥",
)
_DOHA_CLOSE = ("పవన తనయ సంకట హరన మంగల మూరతి రూప ।\nరామ లఖన సీతా సహిత హృదయ బసహు సుర భూప ॥",)

_DESC_VERSES = "\n".join(ln for ln in _v(*_DOHA_OPEN, *_CHAUPAI, *_DOHA_CLOSE))

HANUMAN_CHALISA = ScrollShort(
    slug="hanuman_chalisa_scroll", photo="hanuman_1.jpg",
    lines=("శ్రీ హనుమాన్ చాలీసా", "") + _v(*_DOHA_OPEN, *_CHAUPAI, *_DOHA_CLOSE),
    seconds=172.0, gold_lines=3,
    title="హనుమాన్ చాలీసా తెలుగులో | పూర్తి సాహిత్యం | Hanuman Chalisa Telugu Lyrics",
    title_en="Hanuman Chalisa in Telugu: Full Lyrics Scrolling (40 Verses)",
    description=("🙏 శ్రీ హనుమాన్ చాలీసా (తులసీదాస కృతం), తెలుగు లిపిలో పూర్తి సాహిత్యం. చదువుతూ, పాడుతూ ఆంజనేయ స్వామిని స్మరించండి. "
                 "మంగళవారం, శనివారం పఠించడం శుభప్రదమని సంప్రదాయం.\n\n" + _DESC_VERSES
                 + "\nజై హనుమాన్ 🙏\n\nఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు."),
    description_en=("Hanuman Chalisa by Tulsidas, full lyrics in Telugu script, scrolling over the image of Lord Hanuman. "
                    "Reading it on Tuesdays and Saturdays is traditionally considered auspicious. Jai Hanuman."),
    hashtags=["#Shorts", "#HanumanChalisa", "#హనుమాన్చాలీసా", "#Hanuman", "#Devotional"],
    tags=["hanuman chalisa", "hanuman chalisa telugu", "hanuman chalisa lyrics", "hanuman chalisa telugu lyrics",
          "హనుమాన్ చాలీసా", "హనుమాన్ చాలీసా తెలుగు", "anjaneya swamy", "ఆంజనేయ స్వామి", "tuesday hanuman",
          "telugu devotional", "mahanavi spirituals", "shorts"],
)


# ---------------------------------------------------------------- Hindi (Devanagari) for the two Hindi channels
_HI_DOHA_OPEN = (
    "श्रीगुरु चरन सरोज रज, निज मनु मुकुरु सुधारि ।\nबरनउँ रघुबर बिमल जसु, जो दायकु फल चारि ॥",
    "बुद्धिहीन तनु जानिके, सुमिरौं पवन-कुमार ।\nबल बुधि बिद्या देहु मोहिं, हरहु कलेस बिकार ॥",
)
_HI_CHAUPAI = (
    "जय हनुमान ज्ञान गुन सागर ।\nजय कपीस तिहुँ लोक उजागर ॥ 1 ॥",
    "राम दूत अतुलित बल धामा ।\nअंजनि-पुत्र पवनसुत नामा ॥ 2 ॥",
    "महाबीर बिक्रम बजरंगी ।\nकुमति निवार सुमति के संगी ॥ 3 ॥",
    "कंचन बरन बिराज सुबेसा ।\nकानन कुंडल कुंचित केसा ॥ 4 ॥",
    "हाथ बज्र औ ध्वजा बिराजै ।\nकाँधे मूँज जनेऊ साजै ॥ 5 ॥",
    "संकर सुवन केसरी नंदन ।\nतेज प्रताप महा जग बंदन ॥ 6 ॥",
    "बिद्यावान गुनी अति चातुर ।\nराम काज करिबे को आतुर ॥ 7 ॥",
    "प्रभु चरित्र सुनिबे को रसिया ।\nराम लखन सीता मन बसिया ॥ 8 ॥",
    "सूक्ष्म रूप धरि सियहिं दिखावा ।\nबिकट रूप धरि लंक जरावा ॥ 9 ॥",
    "भीम रूप धरि असुर सँहारे ।\nरामचंद्र के काज सँवारे ॥ 10 ॥",
    "लाय सजीवन लखन जियाये ।\nश्रीरघुबीर हरषि उर लाये ॥ 11 ॥",
    "रघुपति कीन्ही बहुत बड़ाई ।\nतुम मम प्रिय भरतहि सम भाई ॥ 12 ॥",
    "सहस बदन तुम्हरो जस गावैं ।\nअस कहि श्रीपति कंठ लगावैं ॥ 13 ॥",
    "सनकादिक ब्रह्मादि मुनीसा ।\nनारद सारद सहित अहीसा ॥ 14 ॥",
    "जम कुबेर दिगपाल जहाँ ते ।\nकबि कोबिद कहि सके कहाँ ते ॥ 15 ॥",
    "तुम उपकार सुग्रीवहिं कीन्हा ।\nराम मिलाय राज पद दीन्हा ॥ 16 ॥",
    "तुम्हरो मंत्र बिभीषन माना ।\nलंकेस्वर भए सब जग जाना ॥ 17 ॥",
    "जुग सहस्र जोजन पर भानू ।\nलील्यो ताहि मधुर फल जानू ॥ 18 ॥",
    "प्रभु मुद्रिका मेलि मुख माहीं ।\nजलधि लाँघि गये अचरज नाहीं ॥ 19 ॥",
    "दुर्गम काज जगत के जेते ।\nसुगम अनुग्रह तुम्हरे तेते ॥ 20 ॥",
    "राम दुआरे तुम रखवारे ।\nहोत न आज्ञा बिनु पैसारे ॥ 21 ॥",
    "सब सुख लहै तुम्हारी सरना ।\nतुम रच्छक काहू को डर ना ॥ 22 ॥",
    "आपन तेज सम्हारो आपै ।\nतीनों लोक हाँक तें काँपै ॥ 23 ॥",
    "भूत पिसाच निकट नहिं आवै ।\nमहाबीर जब नाम सुनावै ॥ 24 ॥",
    "नासै रोग हरै सब पीरा ।\nजपत निरंतर हनुमत बीरा ॥ 25 ॥",
    "संकट तें हनुमान छुड़ावै ।\nमन क्रम बचन ध्यान जो लावै ॥ 26 ॥",
    "सब पर राम तपस्वी राजा ।\nतिन के काज सकल तुम साजा ॥ 27 ॥",
    "और मनोरथ जो कोई लावै ।\nसोइ अमित जीवन फल पावै ॥ 28 ॥",
    "चारों जुग परताप तुम्हारा ।\nहै परसिद्ध जगत उजियारा ॥ 29 ॥",
    "साधु-संत के तुम रखवारे ।\nअसुर निकंदन राम दुलारे ॥ 30 ॥",
    "अष्ट सिद्धि नौ निधि के दाता ।\nअस बर दीन जानकी माता ॥ 31 ॥",
    "राम रसायन तुम्हरे पासा ।\nसदा रहो रघुपति के दासा ॥ 32 ॥",
    "तुम्हरे भजन राम को पावै ।\nजनम-जनम के दुख बिसरावै ॥ 33 ॥",
    "अंत काल रघुबर पुर जाई ।\nजहाँ जन्म हरि-भक्त कहाई ॥ 34 ॥",
    "और देवता चित्त न धरई ।\nहनुमत सेइ सर्ब सुख करई ॥ 35 ॥",
    "संकट कटै मिटै सब पीरा ।\nजो सुमिरै हनुमत बलबीरा ॥ 36 ॥",
    "जै जै जै हनुमान गोसाईं ।\nकृपा करहु गुरु देव की नाईं ॥ 37 ॥",
    "जो सत बार पाठ कर कोई ।\nछूटहि बंदि महा सुख होई ॥ 38 ॥",
    "जो यह पढ़ै हनुमान चलीसा ।\nहोय सिद्धि साखी गौरीसा ॥ 39 ॥",
    "तुलसीदास सदा हरि चेरा ।\nकीजै नाथ हृदय मँह डेरा ॥ 40 ॥",
)
_HI_DOHA_CLOSE = ("पवनतनय संकट हरन, मंगल मूरति रूप ।\nराम लखन सीता सहित, हृदय बसहु सुर भूप ॥",)
_HI_VERSES = "\n".join(_v(*_HI_DOHA_OPEN, *_HI_CHAUPAI, *_HI_DOHA_CLOSE))
_HI_FOOT = "अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे 🙏"


def _hi(slug, token_file, expected, title, title_en, lead, tags, footer) -> ScrollShort:
    return ScrollShort(
        slug=slug, photo="hanuman_1.jpg", lines=("श्री हनुमान चालीसा", "") + _v(*_HI_DOHA_OPEN, *_HI_CHAUPAI, *_HI_DOHA_CLOSE),
        seconds=172.0, gold_lines=3, lang="hi", token_file=token_file, expected_channel=expected, title=title, title_en=title_en,
        description=f"🙏 {lead}\n\n{_HI_VERSES}\nजय हनुमान 🙏\n\n{_HI_FOOT}\n\n{footer}",
        description_en=("Hanuman Chalisa by Tulsidas, full lyrics in Hindi (Devanagari), scrolling over the image of Lord Hanuman. "
                        "Reading it on Tuesdays and Saturdays is traditionally considered auspicious. Jai Hanuman."),
        hashtags=["#Shorts", "#HanumanChalisa", "#हनुमानचालीसा", "#Hanuman", "#Devotional"], tags=tags)


_TAGS_HI = ["hanuman chalisa", "hanuman chalisa lyrics", "hanuman chalisa hindi", "hanuman chalisa lyrics in hindi",
            "हनुमान चालीसा", "हनुमान चालीसा लिरिक्स", "bajrangbali", "tuesday hanuman", "hindi devotional", "shorts"]
HANUMAN_CHALISA_HI = _hi(
    "hanuman_chalisa_scroll_hi", "youtube_token_mantra_sangam.json", "Mantra Sangam",
    "हनुमान चालीसा हिंदी लिरिक्स | पूरा पाठ | Hanuman Chalisa", "Hanuman Chalisa in Hindi: Full Lyrics Scrolling (40 Chaupai)",
    "श्री हनुमान चालीसा (तुलसीदास कृत), पूरे लिरिक्स हिंदी में। साथ में पढ़ें और बजरंगबली को याद करें। मंगलवार और शनिवार को पाठ करना शुभ माना जाता है।",
    _TAGS_HI + ["divine mantra sangam"], "दिव्य मंत्र संगम - हिंदी भक्ति चैनल। रोज़ राहु काल, शुभ मुहूर्त, मंत्र और पौराणिक कथाएं।")
HANUMAN_CHALISA_HI_TB = _hi(
    "hanuman_chalisa_scroll_hi_tb", "youtube_token_trance_beats.json", "Trance Beats",
    "श्री हनुमान चालीसा | मंगलवार विशेष पाठ | Bajrangbali Lyrics", "Shree Hanuman Chalisa Lyrics (Tuesday Special Path)",
    "मंगलवार विशेष: श्री हनुमान चालीसा के पूरे बोल। संकट मोचन हनुमान जी का स्मरण करें।",
    _TAGS_HI + ["devotional trance beats", "sankat mochan"], "Devotional Trance Beats: हिंदी भक्ति मंत्र, भजन और कीर्तन। चैनल को सब्सक्राइब करें।")


# ---- news explainer (owner supplies the points; posted manually on Pulse TDP Fans) ----
ARNAB_RELIEF = ScrollShort(
    slug="arnab_tufan_relief", photo="", bg="news:cbn", music="channels/trending/assets/music/approved/002.mp3", seconds=125.0,
    lang="te", token_file="youtube_token_pulse_boosting.json", expected_channel="Pulse", gold_lines=2, dim=0.0,
    title="ఆర్నబ్ తుఫాన్ బాధితులకు సీఎం చంద్రబాబు భారీ ఊరట | పరిహారం వివరాలు",
    title_en="Cyclone Arnab Relief: CM Chandrababu Announces Compensation (Full List)",
    description=("ఆర్నబ్ తుఫాన్ బాధితులకు సీఎం చంద్రబాబు నాయుడు ప్రకటించిన పరిహారం వివరాలు. మత్స్యకారులు, రైతులు, పశుపోషకులకు ఇచ్చే సాయం పూర్తి జాబితా.\n\n"
                 "అందరికీ తెలియాలంటే షేర్ చేయండి. ఇలాంటి వార్తల కోసం ఛానల్‌ను సబ్‌స్క్రైబ్ చేయండి."),
    description_en="Compensation announced by Andhra Pradesh CM N. Chandrababu Naidu for Cyclone Arnab victims: fishermen, farmers and livestock owners.",
    hashtags=["#Shorts", "#ChandrababuNaidu", "#TDP", "#AndhraPradesh", "#ArnabTufan", "#PulseTDPFans"],
    tags=["chandrababu naidu", "arnab tufan", "cyclone relief andhra pradesh", "tufan pariharam", "ap cm announcement", "tdp", "shorts"],
    lines=(
        "తుఫాన్ బాధితులకు సీఎం ప్రకటించిన పరిహారం", "",
        "మత్స్యకారులకు, చేపల చెరువులకు సాయం", "",
        "దెబ్బతిన్న వల మరమ్మతులకు రూ.5 వేల సాయం", "",
        "కొత్త వలల కొనుగోలుకు రూ.10 వేల పరిహారం", "",
        "వలలతో సహా పూర్తిగా దెబ్బతిన్న మోటారు లేని పడవలకు రూ.27 వేల సాయం", "",
        "వలలతో సహా పూర్తిగా దెబ్బతిన్న ఫిషింగ్ బోట్లకు రూ.25 వేల పరిహారం", "",
        "చేపల చెరువుల పునరుద్ధరణకు రూ.17 వేల సాయం", "",
        "దెబ్బతిన్న షెడ్లకు రూ.25 వేల పరిహారం", "",
        "పశుసంపద, కోళ్ల పెంపకానికి పరిహారం", "",
        "ఆవు మృతిచెందితే రూ.50 వేల పరిహారం", "",
        "గేదె మృతికి రూ.40 వేల సాయం", "",
        "దూడ మృతికి రూ.25 వేల పరిహారం", "",
        "గొర్రె, మేక మృతికి రూ.7,500 సాయం", "",
        "కోళ్లు మృతిచెందితే ఒక్కోదానికి రూ.100 చొప్పున పరిహారం", "",
        "కోళ్లకు సంబంధించి ఒక్కో లబ్ధిదారుకు గరిష్ఠంగా రూ.10 వేల సాయం", "",
        "దెబ్బతిన్న క్యాటరింగ్ షెడ్లకు రూ.5 వేల పరిహారం", "",
        "బ్యాటరీ షెడ్ల నష్టానికి రూ.500 సాయం", "",
        "పంటలకు హెక్టారుకు పరిహారం", "",
        "పలు పంటలకు నష్టం ఆధారంగా హెక్టారుకు రూ.15 వేల నుంచి రూ.25 వేల వరకు పరిహారం", "",
        "అరటి, పసుపు, యామ్ వంటి పంటలకు హెక్టారుకు రూ.35 వేల సాయం", "",
        "తమలపాకుల తోటలకు హెక్టారుకు రూ.75 వేల పరిహారం", "",
        "మిరప, బొప్పాయి, టమాటా, ఉల్లి పంటలకు హెక్టారుకు రూ.25 వేల నుంచి రూ.35 వేల వరకు సాయం", "",
        "మామిడి, నిమ్మ, దానిమ్మ, సపోటా, జీడిమామిడి తోటలకు హెక్టారుకు రూ.35 వేల సాయం", "",
        "కాఫీ, డ్రాగన్ ఫ్రూట్ తోటలకు హెక్టారుకు రూ.35 వేల సాయం", "",
        "కూరగాయలు, పుచ్చకాయలు, నర్సరీలకు హెక్టారుకు రూ.25 వేల పరిహారం", "",
        "టపియోకా పంటకు హెక్టారుకు రూ.10 వేల సాయం", "",
        "ఆయిల్ పామ్, కొబ్బరి చెట్ల నష్టానికి ఒక్కో చెట్టుకు రూ.15 వేల పరిహారం", "",
        "పంటలు, వృత్తులు, ఆస్తుల నష్టాలకు పరిహారం అందించేలా ప్రభుత్వం నిర్ణయం", "",
        "పరిహారం పంపిణీలో అధికారులు పారదర్శకత పాటించాలని సీఎం చంద్రబాబు స్పష్టం చేశారు", "",
    ),
)

SCROLL: dict[str, ScrollShort] = {s.slug: s for s in (HANUMAN_CHALISA, HANUMAN_CHALISA_HI, HANUMAN_CHALISA_HI_TB, ARNAB_RELIEF)}


# ---- Friday (Lakshmi vara) things not to do: traditional beliefs plus a modern, practical reason for each (2026-10-30) ----
_FRI_TE = [
    ("ఇంటిని మురికిగా ఉంచకూడదు", "శుభ్రత ఉన్నచోటే లక్ష్మీదేవి నివసిస్తుందని నమ్మకం.", "శుభ్రమైన ఇల్లు ఆరోగ్యాన్ని, మనశ్శాంతిని కూడా ఇస్తుంది."),
    ("అప్పు ఇవ్వడం, తీసుకోవడం చేయకూడదు", "శుక్రవారం డబ్బు లావాదేవీలు లక్ష్మీదేవికి ఇష్టం ఉండవని విశ్వాసం.", "తొందరపాటు ఆర్థిక నిర్ణయాలు ఎప్పుడూ మంచివి కావు."),
    ("గొడవలు, కోపం వద్దు", "కలహాలున్న ఇంట్లో సిరిసంపదలు నిలవవని పెద్దల మాట.", "ప్రశాంత మనసుతోనే మంచి నిర్ణయాలు వస్తాయి."),
    ("స్త్రీలను అవమానించకూడదు", "స్త్రీ లక్ష్మీ స్వరూపమని శాస్త్రాలు చెబుతాయి.", "తల్లి, భార్య, కోడలు, కూతురిని గౌరవించడమే గొప్ప పూజ."),
    ("పెద్దలను, గురువులను, పేదలను నొప్పించకూడదు", "వారిని అవమానిస్తే లక్ష్మీదేవి కోపిస్తుందని నమ్మకం.", "గౌరవం ఇస్తే ఆశీస్సులు దక్కుతాయి."),
    ("మాంసం, మద్యం మానండి", "శుక్రవారం సాత్విక జీవనానికి మంచి రోజు.", "తేలికైన ఆహారం ఆరోగ్యానికీ మేలు చేస్తుంది."),
    ("మురికి బట్టలు ధరించకూడదు", "స్నానం చేసి శుభ్రమైన బట్టలు వేసుకోవడం శుభమని సంప్రదాయం.", "శుచి, శుభ్రత మనలో ఉత్సాహాన్ని పెంచుతాయి."),
    ("సోమరితనం వద్దు", "శ్రమించేవారిపైనే లక్ష్మీ కటాక్షం ఉంటుందని చెబుతారు.", "ఉదయాన్నే లేవడం రోజంతా చురుకుగా ఉంచుతుంది."),
    ("పూజా సామగ్రిని నేల మీద పెట్టకూడదు", "పళ్లెంలో ఉంచి భక్తితో సమర్పించాలి.", "పూజలో క్రమశిక్షణ, గౌరవం ముఖ్యం."),
    ("ద్వేషం, చెడు ఆలోచనలు వద్దు", "మనసును కూడా శరీరంలా శుభ్రంగా ఉంచుకోవాలి.", "సానుకూల ఆలోచనే నిజమైన సంపదకు మొదటి అడుగు."),
]
_FRI_HI = [
    ("घर को गंदा न रखें", "मान्यता है कि माँ लक्ष्मी स्वच्छ घर में ही वास करती हैं।", "साफ़ घर सेहत और मन की शांति भी देता है।"),
    ("उधार का लेन-देन न करें", "शुक्रवार को पैसों का लेन-देन लक्ष्मी जी को अप्रसन्न करता है, ऐसा माना जाता है।", "जल्दबाज़ी में पैसों के फ़ैसले वैसे भी ठीक नहीं होते।"),
    ("झगड़ा और क्रोध न करें", "कलह वाले घर में सुख-समृद्धि नहीं टिकती, ऐसा बड़े कहते हैं।", "शांत मन से ही सही फ़ैसले होते हैं।"),
    ("स्त्रियों का अपमान न करें", "शास्त्रों में स्त्री को लक्ष्मी का रूप माना गया है।", "माँ, पत्नी, बहू और बेटी का सम्मान सबसे बड़ा पूजन है।"),
    ("बड़ों, गुरु और ग़रीब को न सताएँ", "इनका अपमान करने से लक्ष्मी जी नाराज़ होती हैं, ऐसी मान्यता है।", "सम्मान देने से आशीर्वाद मिलता है।"),
    ("मांस और शराब से दूर रहें", "शुक्रवार सात्विक जीवन का दिन माना जाता है।", "हल्का भोजन सेहत के लिए भी अच्छा है।"),
    ("गंदे कपड़े न पहनें", "स्नान करके साफ़ कपड़े पहनना शुभ माना गया है।", "स्वच्छता हमारे भीतर उत्साह बढ़ाती है।"),
    ("आलस्य न करें", "परिश्रम करने वालों पर ही लक्ष्मी की कृपा रहती है।", "सुबह जल्दी उठना पूरे दिन को सक्रिय रखता है।"),
    ("पूजा की सामग्री ज़मीन पर न रखें", "थाली में रखकर श्रद्धा से अर्पित करें।", "पूजा में अनुशासन और सम्मान ज़रूरी है।"),
    ("द्वेष और बुरे विचार न रखें", "मन को भी तन की तरह शुद्ध रखना चाहिए।", "सकारात्मक सोच ही असली समृद्धि की पहली सीढ़ी है।"),
]


def _friday_lines(title: str, rows, foot: str) -> tuple[str, ...]:
    out: list[str] = ["§" + title, ""]
    n = 0
    for head, why, modern in rows:
        if why is None:   # a group heading such as "do" / "don't"
            out += ["§" + head, ""]
            continue
        n += 1
        out += [f"§{n}. {head}", why, modern, ""]
    out += [foot, ""]
    return tuple(out)


def _friday(slug, token_file, expected, lang, rows, title, title_en, head, foot, desc, desc_en, tags, extra_footer="",
            photo="lakshmi_g1.jpg") -> ScrollShort:
    return ScrollShort(
        slug=slug, photo=photo, lines=_friday_lines(head, rows, foot), seconds=0.0, gold_lines=0, lang=lang,
        token_file=token_file, expected_channel=expected, title=title, title_en=title_en,
        description=desc + extra_footer, description_en=desc_en,
        hashtags=["#Shorts", "#Friday", "#Lakshmi", "#Devotional"] + (["#శుక్రవారం", "#లక్ష్మీదేవి"] if lang == "te" else ["#शुक्रवार", "#लक्ष्मी"]),
        tags=tags)


_FRI_NOTE_EN = ("These are traditional beliefs about Fridays, the day of Goddess Lakshmi, compiled from popular Dharma Shastra based "
                "sources, each with a practical modern reason. They are shared for devotion and general well-being.")
FRIDAY_TE = _friday(
    "friday_donts_te", "youtube_token.json", "Mahanavi", "te", _FRI_TE,
    "శుక్రవారం చేయకూడని 10 పనులు | లక్ష్మీదేవి కృప కోసం | Friday Do's and Don'ts",
    "10 Things Not to Do on Friday: Lakshmi Devi Traditions and Modern Reasons",
    "శుక్రవారం చేయకూడని 10 పనులు", "ఇవి సంప్రదాయ నమ్మకాలు. శుక్రవారం లక్ష్మీదేవిని భక్తితో స్మరించండి",
    "శుక్రవారం లక్ష్మీదేవికి ప్రీతికరమైన రోజు. ఈ రోజు సంప్రదాయం ప్రకారం చేయకూడని 10 పనులు, వాటి వెనుక ఆధునిక కారణాలతో.\n\n"
    "ఇవి ధర్మశాస్త్ర ఆధారిత ప్రజాదరణ పొందిన నమ్మకాలు. భక్తి, శ్రేయస్సు కోసం పంచుకుంటున్నాం.",
    _FRI_NOTE_EN,
    ["friday dos and donts", "friday lakshmi puja", "శుక్రవారం చేయకూడని పనులు", "లక్ష్మీదేవి", "friday lakshmi devi", "telugu devotional", "shorts"])
_FRI_HI_TAGS = ["शुक्रवार को क्या न करें", "friday lakshmi puja niyam", "shukrawar upay", "माँ लक्ष्मी", "friday dos and donts",
                "hindi devotional", "shorts"]
_FRI_HI_NOTE = "ये शुक्रवार से जुड़ी पारंपरिक मान्यताएँ हैं, भक्ति और सामान्य भलाई के लिए साझा की गई हैं।"
FRIDAY_HI = _friday(
    "friday_donts_hi", "youtube_token_mantra_sangam.json", "Mantra Sangam", "hi", _FRI_HI,
    "शुक्रवार को न करें ये 10 काम | माँ लक्ष्मी की कृपा के लिए | Friday Niyam",
    "10 Things Not to Do on Friday: Maa Lakshmi Traditions", "शुक्रवार को न करें ये 10 काम",
    "ये परंपरागत मान्यताएँ हैं। शुक्रवार को माँ लक्ष्मी का ध्यान करें",
    "शुक्रवार माँ लक्ष्मी का दिन है। जानिए परंपरा के अनुसार इस दिन न करने योग्य 10 काम, और हर बात के पीछे आज का व्यावहारिक कारण।\n\n" + _FRI_HI_NOTE,
    _FRI_NOTE_EN, _FRI_HI_TAGS + ["divine mantra sangam"])
FRIDAY_HI_TB = _friday(
    "friday_donts_hi_tb", "youtube_token_trance_beats.json", "Trance Beats", "hi", _FRI_HI,
    "शुक्रवार को भूलकर भी न करें ये 10 काम | Shukrawar Lakshmi Niyam",
    "10 Friday Rules for Maa Lakshmi's Blessings", "शुक्रवार के 10 नियम: लक्ष्मी कृपा के लिए",
    "ये परंपरागत मान्यताएँ हैं। शुक्रवार को माँ लक्ष्मी का ध्यान करें",
    "शुक्रवार के 10 नियम: माँ लक्ष्मी की कृपा के लिए क्या न करें, और उसका आज का व्यावहारिक कारण।\n\n" + _FRI_HI_NOTE,
    _FRI_NOTE_EN, _FRI_HI_TAGS + ["devotional trance beats"])


# ---- Saturday: Venkateswara Swamy do's and don'ts (owner request 2026-10-31; posted private first for review) ----
_SAT_TE = [
    ("ఇవి చేయండి", None, None),
    ("తెల్లవారుజామున స్నానం చేయండి", "శుచిగా స్వామిని స్మరించడం శనివారం శుభప్రదమని నమ్మకం.", "సుప్రభాతం వింటే రోజు ప్రశాంతంగా మొదలవుతుంది."),
    ("దీపం వెలిగించండి", "నెయ్యి లేదా నూనె దీపం స్వామికి ప్రీతికరమని సంప్రదాయం.", "దీపం ముందు కూర్చుంటే మనసు ఏకాగ్రమవుతుంది."),
    ("తులసి దళాలు సమర్పించండి", "తులసి స్వామికి అత్యంత ప్రియమైనదని చెబుతారు.", "తులసి మొక్క ఇంటికి మంచి వాతావరణాన్ని ఇస్తుంది."),
    ("గోవింద నామాలు జపించండి", "ఓం నమో వేంకటేశాయ అని భక్తితో స్మరించండి.", "నామస్మరణ ఒత్తిడిని తగ్గించి మనసును తేలిక చేస్తుంది."),
    ("సాత్విక ఆహారం తీసుకోండి", "ఉపవాసం ఉండేవారు పండ్లు, పాలు తీసుకుంటారు.", "శక్తి ఉన్నంత వరకే చేయండి, ఆరోగ్యం ముఖ్యం."),
    ("అన్నదానం చేయండి", "ఆకలితో ఉన్నవారికి భోజనం పెట్టడం గొప్ప సేవ.", "ఇచ్చే సంతోషం మనసుకు నిజమైన తృప్తిని ఇస్తుంది."),
    ("ఇవి వద్దు", None, None),
    ("మాంసం, మద్యం, ఉల్లి వెల్లుల్లి వద్దు", "శనివారం స్వామి సేవకు సాత్విక ఆహారం మంచిదని పెద్దల మాట.", "తేలికైన ఆహారం శరీరానికీ మేలు."),
    ("కోపం, గొడవలు వద్దు", "భక్తి నిలవాలంటే మనసు ప్రశాంతంగా ఉండాలి.", "కోపం తగ్గిస్తే మంచి నిర్ణయాలు వస్తాయి."),
    ("వాడిన పూలు, ఎంగిలి నైవేద్యం వద్దు", "స్వామికి తాజా పూలు, శుద్ధమైన నైవేద్యమే సమర్పించాలి.", "శుభ్రత పూజలో ముఖ్యమైన భాగం."),
    ("ఆహారాన్ని వృథా చేయకండి", "అన్నం పరబ్రహ్మ స్వరూపమని పెద్దలు చెబుతారు.", "అవసరమైనంతే వండితే ఖర్చు కూడా తగ్గుతుంది."),
]
SATURDAY_TE = _friday(
    "saturday_venkateswara_te", "youtube_token.json", "Mahanavi", "te", _SAT_TE,
    "శనివారం వేంకటేశ్వర స్వామికి చేయాల్సినవి, చేయకూడనివి | Saturday Do's and Don'ts | Venkateswara",
    "Saturday Do's and Don'ts for Lord Venkateswara: Traditions and Modern Reasons",
    "శనివారం వేంకటేశ్వర స్వామికి చేయాల్సినవి, చేయకూడనివి", "ఇవి సంప్రదాయ నమ్మకాలు. ఓం నమో వేంకటేశాయ",
    "శనివారం వేంకటేశ్వర స్వామికి ప్రీతికరమైన రోజు. ఈ రోజు చేయవలసిన, చేయకూడని పనులు, వాటి వెనుక ఆధునిక కారణాలతో.\n\n"
    "ఇవి సంప్రదాయ నమ్మకాలు. భక్తి, శ్రేయస్సు కోసం పంచుకుంటున్నాం.",
    "Traditional Saturday observances for Lord Venkateswara (Balaji), each with a practical modern reason, shared for devotion and general well-being.",
    ["saturday venkateswara", "venkateswara swamy saturday", "శనివారం వేంకటేశ్వర స్వామి", "govinda namalu", "saturday dos and donts",
     "telugu devotional", "shorts"], photo="venkateswara_n1.jpg")


def news_spec(payload: dict) -> ScrollShort:
    """A one-off news scroll Short built from a JSON payload (the scheduled news task writes it each morning and evening).
    payload: title, title_en, lines (list of str, blank string = gap), person (cbn|lokesh|pawan, default cbn), sources (str),
    description (optional), tags (optional list). seconds is computed from the amount of text."""
    import datetime as dt
    import glob

    lines = [str(x).strip() for x in payload["lines"]]
    out: list[str] = []
    for ln in lines:
        if ln:
            out += [ln, ""]
    music = sorted(glob.glob("channels/trending/assets/music/approved/*.mp3"))
    pick = music[dt.date.today().toordinal() % len(music)] if music else ""
    src = payload.get("sources", "Andhra Jyothy, Eenadu")
    desc = payload.get("description") or payload["title"]
    return ScrollShort(
        slug="news_custom", photo="", bg=f"news:{payload.get('person', 'cbn')}", music=pick, seconds=0.0, lang="te",
        token_file="youtube_token_pulse_boosting.json", expected_channel="Pulse", gold_lines=1, dim=0.0,
        title=payload["title"][:98], title_en=payload.get("title_en", payload["title"])[:98], lines=tuple(out),
        description=f"{desc}\n\nవార్తా మూలాలు / Sources: {src}\n\nఇలాంటి వార్తల కోసం ఛానల్‌ను సబ్‌స్క్రైబ్ చేయండి.",
        description_en=payload.get("description_en", payload.get("title_en", "")),
        hashtags=["#Shorts", "#ChandrababuNaidu", "#TDP", "#AndhraPradesh", "#PulseTDPFans"],
        tags=list(payload.get("tags", [])) + ["chandrababu naidu", "andhra pradesh news", "tdp", "shorts"])


import dataclasses as _dc

SATURDAY_TE = _dc.replace(SATURDAY_TE, dim=0.58)   # the sharp temple photo is busy: darker so the text stays readable
SCROLL.update({x.slug: x for x in (FRIDAY_TE, FRIDAY_HI, FRIDAY_HI_TB, SATURDAY_TE)})
