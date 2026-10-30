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
