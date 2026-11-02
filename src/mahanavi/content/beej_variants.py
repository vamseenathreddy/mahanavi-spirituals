"""More mantras per deity for the daily 6 AM mantra Short, so the same card is never shown twice.

Index 0 of every deity is the ORIGINAL mantra in beej_mantras.DEITIES (already posted before 3 Nov 2026).
These are the extra ones. kind: beej / moola (short name mantra or chant) / gayatri / shloka (a verse).
Each carries a one-line meaning (te, hi) shown in the video description.
All texts are standard, widely chanted mantras and verses; Telugu spelling should be proofread by the owner.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mantra:
    kind: str
    te: str
    hi: str
    translit: str
    mean_te: str
    mean_hi: str


def _m(kind, te, hi, translit, mean_te, mean_hi):
    return Mantra(kind, te, hi, translit, mean_te, mean_hi)


_GAY = "గాయత్రీ మంత్రం, ధ్యానం చేస్తూ బుద్ధిని ప్రేరేపించమని ప్రార్థన"
_GAY_HI = "गायत्री मंत्र: ध्यान करते हुए बुद्धि को प्रेरित करने की प्रार्थना"

VARIANTS: dict[str, tuple[Mantra, ...]] = {
    "ganesha": (
        _m("gayatri", "ఓం ఏకదంతాయ విద్మహే వక్రతుండాయ ధీమహి తన్నో దంతిః ప్రచోదయాత్",
           "ॐ एकदंताय विद्महे वक्रतुण्डाय धीमहि तन्नो दन्तिः प्रचोदयात्",
           "Om Ekadantaya Vidmahe Vakratundaya Dhimahi Tanno Dantih Prachodayat", _GAY, _GAY_HI),
        _m("shloka", "వక్రతుండ మహాకాయ సూర్యకోటి సమప్రభ నిర్విఘ్నం కురు మే దేవ సర్వకార్యేషు సర్వదా",
           "वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ। निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा॥",
           "Vakratunda Mahakaya Suryakoti Samaprabha, Nirvighnam Kuru Me Deva Sarvakaryeshu Sarvada",
           "అన్ని పనుల్లో ఆటంకాలు లేకుండా చూడమని గణపతికి ప్రార్థన", "सभी कार्यों में बाधा न आए, गणपति से यही प्रार्थना"),
        _m("moola", "ఓం శ్రీ గణేశాయ నమః", "ॐ श्री गणेशाय नमः", "Om Shri Ganeshaya Namah",
           "ప్రతి మంచి పనికి ముందు గణపతి స్మరణ", "हर शुभ कार्य से पहले गणपति का स्मरण"),
        _m("shloka", "శుక్లాంబరధరం విష్ణుం శశివర్ణం చతుర్భుజం ప్రసన్నవదనం ధ్యాయేత్ సర్వవిఘ్నోపశాంతయే",
           "शुक्लाम्बरधरं विष्णुं शशिवर्णं चतुर्भुजम्। प्रसन्नवदनं ध्यायेत् सर्वविघ्नोपशान्तये॥",
           "Shuklambaradharam Vishnum Shashivarnam Chaturbhujam, Prasannavadanam Dhyayet Sarvavighnopashantaye",
           "తెల్లని వస్త్రాలు ధరించిన ప్రసన్న ముఖుని విఘ్న శాంతి కోసం ధ్యానిస్తాం",
           "श्वेत वस्त्रधारी प्रसन्न मुख का विघ्न शांति के लिए ध्यान"),
    ),
    "shiva": (
        _m("shloka", "ఓం త్ర్యంబకం యజామహే సుగంధిం పుష్టివర్ధనం ఉర్వారుకమివ బంధనాన్ మృత్యోర్ముక్షీయ మామృతాత్",
           "ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्। उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय माऽमृतात्॥",
           "Om Tryambakam Yajamahe Sugandhim Pushtivardhanam, Urvarukamiva Bandhanan Mrityor Mukshiya Mamritat",
           "మహా మృత్యుంజయ మంత్రం: ఆరోగ్యం, భయ నివారణ కోసం శివ ప్రార్థన", "महामृत्युंजय मंत्र: आरोग्य और भय निवारण के लिए शिव प्रार्थना"),
        _m("gayatri", "ఓం తత్పురుషాయ విద్మహే మహాదేవాయ ధీమహి తన్నో రుద్రః ప్రచోదయాత్",
           "ॐ तत्पुरुषाय विद्महे महादेवाय धीमहि तन्नो रुद्रः प्रचोदयात्",
           "Om Tatpurushaya Vidmahe Mahadevaya Dhimahi Tanno Rudrah Prachodayat", _GAY, _GAY_HI),
        _m("moola", "ఓం నమో భగవతే రుద్రాయ", "ॐ नमो भगवते रुद्राय", "Om Namo Bhagavate Rudraya",
           "రుద్రునికి నమస్కారం, శివ భక్తులు తరచుగా జపించే మంత్రం", "रुद्र को नमन, शिवभक्तों द्वारा बार-बार जपा जाने वाला मंत्र"),
        _m("shloka", "కర్పూరగౌరం కరుణావతారం సంసారసారం భుజగేంద్రహారం", "कर्पूरगौरं करुणावतारं संसारसारं भुजगेन्द्रहारम्",
           "Karpuragauram Karunavataram Samsarasaram Bhujagendraharam",
           "కర్పూరం వంటి తెల్లని, కరుణామూర్తి అయిన శివునికి ప్రణామం", "कर्पूर के समान गौर, करुणा के अवतार शिव को प्रणाम"),
        _m("shloka", "నాగేంద్రహారాయ త్రిలోచనాయ భస్మాంగరాగాయ మహేశ్వరాయ", "नागेन्द्रहाराय त्रिलोचनाय भस्माङ्गरागाय महेश्वराय",
           "Nagendraharaya Trilochanaya Bhasmangaragaya Maheshvaraya",
           "శివ పంచాక్షరి స్తోత్రం ప్రారంభ పాదం", "शिव पंचाक्षरी स्तोत्र का प्रारंभिक चरण"),
        _m("moola", "శివ శివ శంకర హర హర శంభో", "शिव शिव शंकर हर हर शम्भो", "Shiva Shiva Shankara Hara Hara Shambho",
           "శివ నామ సంకీర్తన", "शिव नाम संकीर्तन"),
        _m("beej", "ఓం హౌం జూం సః", "ॐ हौं जूं सः", "Om Haum Joom Sah",
           "మృత్యుంజయ బీజ మంత్రం", "मृत्युंजय बीज मंत्र"),
        _m("moola", "ఓం మహాదేవాయ నమః", "ॐ महादेवाय नमः", "Om Mahadevaya Namah",
           "మహాదేవునికి నమస్కారం", "महादेव को नमन"),
        _m("shloka", "ఓం నమః శివాయ శాంతాయ కారణత్రయహేతవే నివేదయామి చాత్మానం త్వం గతిః పరమేశ్వర",
           "ॐ नमः शिवाय शान्ताय कारणत्रयहेतवे। निवेदयामि चात्मानं त्वं गतिः परमेश्वर॥",
           "Om Namah Shivaya Shantaya Karanatraya Hetave, Nivedayami Chatmanam Tvam Gatih Parameshvara",
           "శాంత శివునికి ఆత్మ సమర్పణ ప్రార్థన", "शांत शिव को आत्म समर्पण की प्रार्थना"),
    ),
    "vishnu": (
        _m("moola", "ఓం నమో భగవతే వాసుదేవాయ", "ॐ नमो भगवते वासुदेवाय", "Om Namo Bhagavate Vasudevaya",
           "ద్వాదశాక్షరి మంత్రం, వాసుదేవునికి నమస్కారం", "द्वादशाक्षरी मंत्र, वासुदेव को नमन"),
        _m("gayatri", "ఓం నారాయణాయ విద్మహే వాసుదేవాయ ధీమహి తన్నో విష్ణుః ప్రచోదయాత్",
           "ॐ नारायणाय विद्महे वासुदेवाय धीमहि तन्नो विष्णुः प्रचोदयात्",
           "Om Narayanaya Vidmahe Vasudevaya Dhimahi Tanno Vishnuh Prachodayat", _GAY, _GAY_HI),
        _m("shloka", "శాంతాకారం భుజగశయనం పద్మనాభం సురేశం", "शान्ताकारं भुजगशयनं पद्मनाभं सुरेशम्",
           "Shantakaram Bhujagashayanam Padmanabham Suresham",
           "శాంత స్వరూపుడైన శేషశయన విష్ణువుకు ప్రణామం", "शांत स्वरूप शेषशायी विष्णु को प्रणाम"),
        _m("moola", "ఓం శ్రీ మహావిష్ణవే నమః", "ॐ श्री महाविष्णवे नमः", "Om Shri Mahavishnave Namah",
           "మహావిష్ణువుకు నమస్కారం", "महाविष्णु को नमन"),
        _m("shloka", "అచ్యుతం కేశవం రామనారాయణం కృష్ణదామోదరం వాసుదేవం హరిం",
           "अच्युतं केशवं रामनारायणं कृष्णदामोदरं वासुदेवं हरिम्",
           "Achyutam Keshavam Rama Narayanam Krishna Damodaram Vasudevam Harim",
           "అచ్యుతాష్టకం ప్రారంభ పాదం, విష్ణు నామ స్మరణ", "अच्युताष्टक का प्रारंभिक चरण, विष्णु नाम स्मरण"),
    ),
    "krishna": (
        _m("moola", "హరే కృష్ణ హరే కృష్ణ కృష్ణ కృష్ణ హరే హరే హరే రామ హరే రామ రామ రామ హరే హరే",
           "हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे। हरे राम हरे राम राम राम हरे हरे॥",
           "Hare Krishna Hare Krishna Krishna Krishna Hare Hare, Hare Rama Hare Rama Rama Rama Hare Hare",
           "హరే కృష్ణ మహామంత్రం, నామస్మరణ", "हरे कृष्ण महामंत्र, नाम स्मरण"),
        _m("gayatri", "ఓం దేవకీనందనాయ విద్మహే వాసుదేవాయ ధీమహి తన్నః కృష్ణః ప్రచోదయాత్",
           "ॐ देवकीनन्दनाय विद्महे वासुदेवाय धीमहि तन्नः कृष्णः प्रचोदयात्",
           "Om Devakinandanaya Vidmahe Vasudevaya Dhimahi Tannah Krishnah Prachodayat", _GAY, _GAY_HI),
        _m("shloka", "కృష్ణాయ వాసుదేవాయ హరయే పరమాత్మనే ప్రణతః క్లేశనాశాయ గోవిందాయ నమో నమః",
           "कृष्णाय वासुदेवाय हरये परमात्मने। प्रणतः क्लेशनाशाय गोविन्दाय नमो नमः॥",
           "Krishnaya Vasudevaya Haraye Paramatmane, Pranatah Kleshanashaya Govindaya Namo Namah",
           "బాధలను తొలగించే గోవిందునికి ప్రణామం", "क्लेश हरने वाले गोविन्द को प्रणाम"),
    ),
    "rama": (
        _m("shloka", "శ్రీ రామ రామ రామేతి రమే రామే మనోరమే సహస్రనామ తత్తుల్యం రామనామ వరాననే",
           "श्री राम राम रामेति रमे रामे मनोरमे। सहस्रनाम तत्तुल्यं रामनाम वरानने॥",
           "Shri Rama Rama Rameti Rame Rame Manorame, Sahasranama Tattulyam Ramanama Varanane",
           "రామ నామం వెయ్యి నామాలకు సమానమని చెప్పే శ్లోకం", "राम नाम को हज़ार नामों के समान बताने वाला श्लोक"),
        _m("gayatri", "ఓం దాశరథాయ విద్మహే సీతావల్లభాయ ధీమహి తన్నో రామః ప్రచోదయాత్",
           "ॐ दाशरथाय विद्महे सीतावल्लभाय धीमहि तन्नो रामः प्रचोदयात्",
           "Om Dasharathaya Vidmahe Sitavallabhaya Dhimahi Tanno Ramah Prachodayat", _GAY, _GAY_HI),
        _m("moola", "శ్రీ రామ జయ రామ జయ జయ రామ", "श्री राम जय राम जय जय राम", "Shri Ram Jai Ram Jai Jai Ram",
           "రామనామ సంకీర్తన, విజయం కోసం స్మరణ", "राम नाम संकीर्तन"),
    ),
    "hanuman": (
        _m("gayatri", "ఓం ఆంజనేయాయ విద్మహే వాయుపుత్రాయ ధీమహి తన్నో హనుమత్ ప్రచోదయాత్",
           "ॐ आञ्जनेयाय विद्महे वायुपुत्राय धीमहि तन्नो हनुमत् प्रचोदयात्",
           "Om Anjaneyaya Vidmahe Vayuputraya Dhimahi Tanno Hanumat Prachodayat", _GAY, _GAY_HI),
        _m("shloka", "మనోజవం మారుతతుల్యవేగం జితేంద్రియం బుద్ధిమతాం వరిష్ఠం",
           "मनोजवं मारुततुल्यवेगं जितेन्द्रियं बुद्धिमतां वरिष्ठम्",
           "Manojavam Marutatulyavegam Jitendriyam Buddhimatam Varishtham",
           "మనోవేగం, వాయువేగం కలిగిన ఇంద్రియ జయుడు, బుద్ధిమంతులలో శ్రేష్ఠునికి నమస్కారం",
           "मन और वायु के समान वेग वाले, जितेंद्रिय, बुद्धिमानों में श्रेष्ठ को नमन"),
        _m("moola", "ఓం శ్రీ ఆంజనేయాయ నమః", "ॐ श्री आञ्जनेयाय नमः", "Om Shri Anjaneyaya Namah",
           "ఆంజనేయ స్వామికి నమస్కారం", "आंजनेय स्वामी को नमन"),
    ),
    "subrahmanya": (
        _m("gayatri", "ఓం తత్పురుషాయ విద్మహే మహాసేనాయ ధీమహి తన్నః షణ్ముఖః ప్రచోదయాత్",
           "ॐ तत्पुरुषाय विद्महे महासेनाय धीमहि तन्नः षण्मुखः प्रचोदयात्",
           "Om Tatpurushaya Vidmahe Mahasenaya Dhimahi Tannah Shanmukhah Prachodayat", _GAY, _GAY_HI),
        _m("moola", "ఓం సుబ్రహ్మణ్యాయ నమః", "ॐ सुब्रह्मण्याय नमः", "Om Subrahmanyaya Namah",
           "సుబ్రహ్మణ్య స్వామికి నమస్కారం", "सुब्रह्मण्य स्वामी को नमन"),
        _m("moola", "ఓం శ్రీ వల్లీదేవసేనా సమేత సుబ్రహ్మణ్య స్వామినే నమః",
           "ॐ श्री वल्लीदेवसेना समेत सुब्रह्मण्य स्वामिने नमः", "Om Shri Valli Devasena Sameta Subrahmanya Swamine Namah",
           "వల్లీ దేవసేనా సహిత సుబ్రహ్మణ్యునికి నమస్కారం", "वल्ली और देवसेना सहित सुब्रह्मण्य को नमन"),
    ),
    "durga": (
        _m("shloka", "యా దేవీ సర్వభూతేషు శక్తిరూపేణ సంస్థితా నమస్తస్యై నమస్తస్యై నమస్తస్యై నమో నమః",
           "या देवी सर्वभूतेषु शक्तिरूपेण संस्थिता। नमस्तस्यै नमस्तस्यै नमस्तस्यै नमो नमः॥",
           "Ya Devi Sarvabhuteshu Shaktirupena Samsthita, Namastasyai Namastasyai Namastasyai Namo Namah",
           "అన్ని ప్రాణుల్లో శక్తి రూపంలో ఉన్న దేవికి నమస్కారం", "सभी प्राणियों में शक्ति रूप से स्थित देवी को नमन"),
        _m("shloka", "సర్వమంగళమాంగళ్యే శివే సర్వార్థసాధికే శరణ్యే త్ర్యంబకే గౌరి నారాయణి నమోఽస్తు తే",
           "सर्वमङ्गलमाङ्गल्ये शिवे सर्वार्थसाधिके। शरण्ये त्र्यम्बके गौरि नारायणि नमोऽस्तु ते॥",
           "Sarvamangala Mangalye Shive Sarvartha Sadhike, Sharanye Tryambake Gauri Narayani Namostu Te",
           "శుభాలన్నిటికీ శుభమైన శరణ్య దేవికి నమస్కారం", "सब मंगलों की मंगल, शरण देने वाली देवी को नमन"),
        _m("beej", "ఓం ఐం హ్రీం క్లీం చాముండాయై విచ్చే", "ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे",
           "Om Aim Hreem Kleem Chamundayai Vichche", "నవార్ణ మంత్రం, చాముండా దేవి ఆరాధన", "नवार्ण मंत्र, चामुंडा देवी की उपासना"),
    ),
    "lakshmi": (
        _m("gayatri", "ఓం మహాలక్ష్మ్యై చ విద్మహే విష్ణుపత్న్యై చ ధీమహి తన్నో లక్ష్మీః ప్రచోదయాత్",
           "ॐ महालक्ष्म्यै च विद्महे विष्णुपत्न्यै च धीमहि तन्नो लक्ष्मीः प्रचोदयात्",
           "Om Mahalakshmyai Cha Vidmahe Vishnupatnyai Cha Dhimahi Tanno Lakshmih Prachodayat", _GAY, _GAY_HI),
        _m("shloka", "నమస్తేఽస్తు మహామాయే శ్రీపీఠే సురపూజితే శంఖచక్రగదాహస్తే మహాలక్ష్మి నమోఽస్తు తే",
           "नमस्तेऽस्तु महामाये श्रीपीठे सुरपूजिते। शङ्खचक्रगदाहस्ते महालक्ष्मि नमोऽस्तु ते॥",
           "Namastestu Mahamaye Shripithe Surapujite, Shankhachakra Gadahaste Mahalakshmi Namostu Te",
           "మహాలక్ష్మికి నమస్కారం (మహాలక్ష్మ్యష్టకం)", "महालक्ष्मी को नमन (महालक्ष्म्यष्टक)"),
        _m("beej", "ఓం శ్రీం హ్రీం క్లీం మహాలక్ష్మ్యై నమః", "ॐ श्रीं ह्रीं क्लीं महालक्ष्म्यै नमः",
           "Om Shreem Hreem Kleem Mahalakshmyai Namah", "శ్రీ బీజాలతో మహాలక్ష్మి ఆరాధన", "श्री बीजों के साथ महालक्ष्मी की उपासना"),
    ),
    "kali": (
        _m("shloka", "జయంతీ మంగళా కాళీ భద్రకాళీ కపాలినీ దుర్గా క్షమా శివా ధాత్రీ స్వాహా స్వధా నమోఽస్తు తే",
           "जयन्ती मङ्गला काली भद्रकाली कपालिनी। दुर्गा क्षमा शिवा धात्री स्वाहा स्वधा नमोऽस्तु ते॥",
           "Jayanti Mangala Kali Bhadrakali Kapalini, Durga Kshama Shiva Dhatri Svaha Svadha Namostu Te",
           "దేవి నామాల స్మరణ (దేవీ మాహాత్మ్యం, అర్గళ స్తోత్రం)", "देवी के नामों का स्मरण (देवी माहात्म्य, अर्गला स्तोत्र)"),
        _m("gayatri", "ఓం కాళికాయై విద్మహే శ్మశానవాసిన్యై ధీమహి తన్నో ఘోరా ప్రచోదయాత్",
           "ॐ कालिकायै विद्महे श्मशानवासिन्यै धीमहि तन्नो घोरा प्रचोदयात्",
           "Om Kalikayai Vidmahe Shmashanavasinyai Dhimahi Tanno Ghora Prachodayat", _GAY, _GAY_HI),
        _m("moola", "ఓం శ్రీ భద్రకాళ్యై నమః", "ॐ श्री भद्रकाल्यै नमः", "Om Shri Bhadrakalyai Namah",
           "భద్రకాళి అమ్మవారికి నమస్కారం", "भद्रकाली माँ को नमन"),
    ),
    "dattatreya": (
        _m("moola", "దిగంబరా దిగంబరా శ్రీపాదవల్లభ దిగంబరా", "दिगम्बरा दिगम्बरा श्रीपादवल्लभ दिगम्बरा",
           "Digambara Digambara Shripada Vallabha Digambara", "దత్త నామ స్మరణ", "दत्त नाम स्मरण"),
        _m("gayatri", "ఓం దిగంబరాయ విద్మహే అవధూతాయ ధీమహి తన్నో దత్తః ప్రచోదయాత్",
           "ॐ दिगम्बराय विद्महे अवधूताय धीमहि तन्नो दत्तः प्रचोदयात्",
           "Om Digambaraya Vidmahe Avadhutaya Dhimahi Tanno Dattah Prachodayat", _GAY, _GAY_HI),
        _m("moola", "ఓం శ్రీ గురుదేవ దత్త", "ॐ श्री गुरुदेव दत्त", "Om Shri Gurudeva Datta",
           "గురుదేవ దత్తునికి నమస్కారం", "गुरुदेव दत्त को नमन"),
    ),
    "surya": (
        _m("gayatri", "ఓం భాస్కరాయ విద్మహే మహాద్యుతికరాయ ధీమహి తన్నో ఆదిత్యః ప్రచోదయాత్",
           "ॐ भास्कराय विद्महे महाद्युतिकराय धीमहि तन्नो आदित्यः प्रचोदयात्",
           "Om Bhaskaraya Vidmahe Mahadyutikaraya Dhimahi Tanno Adityah Prachodayat", _GAY, _GAY_HI),
        _m("moola", "ఓం ఆదిత్యాయ నమః", "ॐ आदित्याय नमः", "Om Adityaya Namah",
           "సూర్య భగవానునికి నమస్కారం", "सूर्य भगवान को नमन"),
        _m("shloka", "జపాకుసుమసంకాశం కాశ్యపేయం మహాద్యుతిం తమోఽరిం సర్వపాపఘ్నం ప్రణతోఽస్మి దివాకరం",
           "जपाकुसुमसंकाशं काश्यपेयं महाद्युतिम्। तमोऽरिं सर्वपापघ्नं प्रणतोऽस्मि दिवाकरम्॥",
           "Japakusuma Sankasham Kashyapeyam Mahadyutim, Tamorim Sarvapapaghnam Pranatosmi Divakaram",
           "జపాకుసుమం వంటి కాంతి గల దివాకరునికి ప్రణామం", "जपाकुसुम के समान कांति वाले दिवाकर को प्रणाम"),
    ),
    "shani": (
        _m("beej", "ఓం శం శనైశ్చరాయ నమః", "ॐ शं शनैश्चराय नमः", "Om Sham Shanaishcharaya Namah",
           "శనైశ్చరునికి నమస్కారం", "शनैश्चर को नमन"),
        _m("shloka", "నీలాంజనసమాభాసం రవిపుత్రం యమాగ్రజం ఛాయామార్తాండసంభూతం తం నమామి శనైశ్చరం",
           "नीलाञ्जनसमाभासं रविपुत्रं यमाग्रजम्। छायामार्तण्डसम्भूतं तं नमामि शनैश्चरम्॥",
           "Nilanjana Samabhasam Raviputram Yamagrajam, Chhaya Martanda Sambhutam Tam Namami Shanaishcharam",
           "శని దేవుని నవగ్రహ ధ్యాన శ్లోకం", "शनिदेव का नवग्रह ध्यान श्लोक"),
        _m("gayatri", "ఓం శనైశ్చరాయ విద్మహే సూర్యపుత్రాయ ధీమహి తన్నో మందః ప్రచోదయాత్",
           "ॐ शनैश्चराय विद्महे सूर्यपुत्राय धीमहि तन्नो मन्दः प्रचोदयात्",
           "Om Shanaishcharaya Vidmahe Suryaputraya Dhimahi Tanno Mandah Prachodayat", _GAY, _GAY_HI),
    ),
    "narasimha": (
        _m("shloka", "ఉగ్రం వీరం మహావిష్ణుం జ్వలంతం సర్వతోముఖం నృసింహం భీషణం భద్రం మృత్యుమృత్యుం నమామ్యహం",
           "उग्रं वीरं महाविष्णुं ज्वलन्तं सर्वतोमुखम्। नृसिंहं भीषणं भद्रं मृत्युमृत्युं नमाम्यहम्॥",
           "Ugram Viram Mahavishnum Jvalantam Sarvatomukham, Nrisimham Bhishanam Bhadram Mrityumrityum Namamyaham",
           "నృసింహ మంత్ర రాజ శ్లోకం, భయ నివారణ ప్రార్థన", "नृसिंह मंत्रराज श्लोक, भय निवारण की प्रार्थना"),
        _m("gayatri", "ఓం వజ్రనఖాయ విద్మహే తీక్ష్ణదంష్ట్రాయ ధీమహి తన్నో నారసింహః ప్రచోదయాత్",
           "ॐ वज्रनखाय विद्महे तीक्ष्णदंष्ट्राय धीमहि तन्नो नारसिंहः प्रचोदयात्",
           "Om Vajranakhaya Vidmahe Tikshnadamshtraya Dhimahi Tanno Narasimhah Prachodayat", _GAY, _GAY_HI),
        _m("moola", "ఓం నమో నారసింహాయ", "ॐ नमो नारसिंहाय", "Om Namo Narasimhaya",
           "నరసింహ స్వామికి నమస్కారం", "नरसिंह स्वामी को नमन"),
    ),
    "saraswati": (
        _m("shloka", "సరస్వతి నమస్తుభ్యం వరదే కామరూపిణి విద్యారంభం కరిష్యామి సిద్ధిర్భవతు మే సదా",
           "सरस्वति नमस्तुभ्यं वरदे कामरूपिणि। विद्यारम्भं करिष्यामि सिद्धिर्भवतु मे सदा॥",
           "Sarasvati Namastubhyam Varade Kamarupini, Vidyarambham Karishyami Siddhirbhavatu Me Sada",
           "చదువు మొదలుపెట్టే ముందు సరస్వతికి ప్రార్థన", "पढ़ाई शुरू करने से पहले सरस्वती से प्रार्थना"),
        _m("gayatri", "ఓం వాగ్దేవ్యై చ విద్మహే కామరాజాయ ధీమహి తన్నో దేవీ ప్రచోదయాత్",
           "ॐ वाग्देव्यै च विद्महे कामराजाय धीमहि तन्नो देवी प्रचोदयात्",
           "Om Vagdevyai Cha Vidmahe Kamarajaya Dhimahi Tanno Devi Prachodayat", _GAY, _GAY_HI),
    ),
    "gayatri": (
        _m("gayatri", "ఓం భూర్భువః స్వః తత్సవితుర్వరేణ్యం భర్గో దేవస్య ధీమహి ధియో యో నః ప్రచోదయాత్",
           "ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात्",
           "Om Bhur Bhuvah Svah Tat Savitur Varenyam Bhargo Devasya Dhimahi Dhiyo Yo Nah Prachodayat",
           "గాయత్రీ మహామంత్రం: మన బుద్ధిని ప్రేరేపించమని ప్రార్థన", "गायत्री महामंत्र: हमारी बुद्धि को प्रेरित करने की प्रार्थना"),
    ),
    "annapurna": (
        _m("shloka", "అన్నపూర్ణే సదాపూర్ణే శంకరప్రాణవల్లభే జ్ఞానవైరాగ్యసిద్ధ్యర్థం భిక్షాం దేహి చ పార్వతి",
           "अन्नपूर्णे सदापूर्णे शङ्करप्राणवल्लभे। ज्ञानवैराग्यसिद्ध्यर्थं भिक्षां देहि च पार्वति॥",
           "Annapurne Sadapurne Shankara Pranavallabhe, Jnana Vairagya Siddhyartham Bhikshaam Dehi Cha Parvati",
           "అన్నం, జ్ఞానం, వైరాగ్యం ప్రసాదించమని అన్నపూర్ణకు ప్రార్థన", "अन्न, ज्ञान और वैराग्य देने के लिए अन्नपूर्णा से प्रार्थना"),
    ),
    # new deities (original mantra in beej_mantras.DEITIES, photo families exist in images/deity_bg)
    "dakshinamurthy": (
        _m("shloka", "గురవే సర్వలోకానాం భిషజే భవరోగిణాం నిధయే సర్వవిద్యానాం దక్షిణామూర్తయే నమః",
           "गुरवे सर्वलोकानां भिषजे भवरोगिणाम्। निधये सर्वविद्यानां दक्षिणामूर्तये नमः॥",
           "Gurave Sarvalokanam Bhishaje Bhavaroginam, Nidhaye Sarvavidyanam Dakshinamurtaye Namah",
           "లోక గురువు, సంసార రోగాలకు వైద్యుడు, విద్యలన్నిటి నిధి అయిన దక్షిణామూర్తికి నమస్కారం",
           "सब लोकों के गुरु, भवरोग के वैद्य, सब विद्याओं के निधि दक्षिणामूर्ति को नमन"),
        _m("shloka", "గురుర్బ్రహ్మా గురుర్విష్ణుః గురుర్దేవో మహేశ్వరః గురుః సాక్షాత్ పరబ్రహ్మ తస్మై శ్రీ గురవే నమః",
           "गुरुर्ब्रह्मा गुरुर्विष्णुः गुरुर्देवो महेश्वरः। गुरुः साक्षात् परब्रह्म तस्मै श्री गुरवे नमः॥",
           "Gurur Brahma Gurur Vishnu Gurur Devo Maheshwarah, Guruh Sakshat Parabrahma Tasmai Shri Gurave Namah",
           "గురువు బ్రహ్మ, విష్ణు, మహేశ్వరులతో సమానమని చెప్పే శ్లోకం", "गुरु को ब्रह्मा, विष्णु, महेश्वर के समान बताने वाला श्लोक"),
    ),
    "venkateswara": (
        _m("moola", "ఓం నమో వేంకటేశాయ", "ॐ नमो वेङ्कटेशाय", "Om Namo Venkateshaya",
           "తిరుమల వేంకటేశ్వర స్వామికి నమస్కారం", "तिरुमला वेंकटेश्वर स्वामी को नमन"),
        _m("moola", "గోవిందా హరి గోవిందా వేంకటరమణా గోవిందా", "गोविन्दा हरि गोविन्दा वेंकटरमणा गोविन्दा",
           "Govinda Hari Govinda Venkataramana Govinda", "వేంకటేశ్వర నామ సంకీర్తన", "वेंकटेश्वर नाम संकीर्तन"),
    ),
    "ayyappa": (
        _m("moola", "స్వామియే శరణం అయ్యప్ప", "स्वामिये शरणम् अय्यप्पा", "Swamiye Sharanam Ayyappa",
           "అయ్యప్ప స్వామి శరణు ఘోష", "अय्यप्पा स्वामी की शरण पुकार"),
        _m("moola", "ఓం శ్రీ ధర్మశాస్త్రే నమః", "ॐ श्री धर्मशास्त्रे नमः", "Om Shri Dharma Shastre Namah",
           "ధర్మ శాస్తా అయ్యప్పకు నమస్కారం", "धर्मशास्ता अय्यप्पा को नमन"),
    ),
}
