"""One Vedic mantra a day, rotating Rigveda, Yajurveda, Samaveda, Atharvaveda (10 topics, approved by the owner on 2026-11-25).

Mantra text is the standard published Sanskrit; the Telugu and Hindi meanings are plain renderings written for these channels.
Every entry: Devanagari mantra (SA), the same mantra in Telugu script (TE_READ), Telugu meaning, Hindi meaning, English meaning,
and the titles. No numbering anywhere (owner rule 2026-11-06). Refs are Veda + verse, shown as the card's second line.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mantra:
    veda: str            # rig | yajur | sama | atharva
    ref_te: str
    ref_hi: str
    ref_en: str
    sa: str
    te_read: str
    te_mean: str
    hi_mean: str
    en_mean: str
    title_te: str
    title_hi: str
    title_en: str


HEAD_TE = {"rig": "ఋగ్వేదం", "yajur": "యజుర్వేదం", "sama": "సామవేదం", "atharva": "అథర్వవేదం"}
HEAD_HI = {"rig": "ऋग्वेद", "yajur": "यजुर्वेद", "sama": "सामवेद", "atharva": "अथर्ववेद"}
HEAD_EN = {"rig": "Rigveda", "yajur": "Yajurveda", "sama": "Samaveda", "atharva": "Atharvaveda"}

MANTRAS: list[Mantra] = [
    Mantra(
        "rig", "ఋగ్వేదం 1.1.1 · మొదటి మంత్రం", "ऋग्वेद 1.1.1 · पहला मंत्र", "Rigveda 1.1.1, Agni Sukta",
        "अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम् । होतारं रत्नधातमम् ॥",
        "అగ్నిమీళే పురోహితం యజ్ఞస్య దేవమృత్విజమ్ । హోతారం రత్నధాతమమ్ ॥",
        "యజ్ఞానికి పురోహితుడు, దేవుడు, ఋత్విజుడు, దేవతలను పిలిచేవాడు, గొప్ప సంపదలను ఇచ్చేవాడు అయిన అగ్నిని నేను స్తుతిస్తున్నాను.",
        "मैं अग्निदेव की स्तुति करता हूँ, जो यज्ञ के पुरोहित, देव, ऋत्विज, देवताओं को बुलाने वाले और सबसे बड़े रत्नदाता हैं।",
        "I praise Agni, the priest of the sacrifice, the divine minister, the invoker, the greatest giver of treasure.",
        "ఋగ్వేదంలోని మొదటి మంత్రం | First Mantra of the Rigveda | Agni Sukta",
        "ऋग्वेद का पहला मंत्र | अग्नि सूक्त अर्थ सहित | First Mantra of the Rigveda",
        "First Mantra of the Rigveda | Agni Sukta with meaning",
    ),
    Mantra(
        "yajur", "యజుర్వేదం · పూర్ణమదః శాంతి మంత్రం", "यजुर्वेद · पूर्णमदः शांति मंत्र", "Yajurveda, Purnamadah (Isha Upanishad invocation)",
        "ॐ पूर्णमदः पूर्णमिदं पूर्णात्पूर्णमुदच्यते । पूर्णस्य पूर्णमादाय पूर्णमेवावशिष्यते ॥ ॐ शान्तिः शान्तिः शान्तिः ॥",
        "ఓం పూర్ణమదః పూర్ణమిదం పూర్ణాత్ పూర్ణముదచ్యతే । పూర్ణస్య పూర్ణమాదాయ పూర్ణమేవావశిష్యతే ॥ ఓం శాంతిః శాంతిః శాంతిః ॥",
        "అది పూర్ణం, ఇది పూర్ణం. పూర్ణం నుండి పూర్ణమే పుడుతుంది. పూర్ణం నుండి పూర్ణాన్ని తీసినా పూర్ణమే మిగులుతుంది.",
        "वह (परब्रह्म) पूर्ण है, यह (जगत्) पूर्ण है। पूर्ण से पूर्ण ही उत्पन्न होता है, पूर्ण में से पूर्ण निकालने पर भी पूर्ण ही शेष रहता है।",
        "That is whole, this is whole. From the whole the whole arises. Take the whole from the whole and the whole remains.",
        "యజుర్వేద పూర్ణమదః మంత్రం | Purnamadah Mantra | Yajurveda Shanti Mantra",
        "यजुर्वेद का पूर्णमदः मंत्र | अर्थ सहित | Purnamadah Mantra",
        "Purnamadah Mantra | Yajurveda Shanti Mantra with meaning",
    ),
    Mantra(
        "sama", "సామవేదం 1.1 · మొదటి మంత్రం", "सामवेद 1.1 · पहला मंत्र", "Samaveda 1.1 (same verse as Rigveda 6.16.10)",
        "अग्न आ याहि वीतये गृणानो हव्यदातये । नि होता सत्सि बर्हिषि ॥",
        "అగ్న ఆ యాహి వీతయే గృణానో హవ్యదాతయే । ని హోతా సత్సి బర్హిషి ॥",
        "అగ్నీ, స్తుతింపబడినవాడివై హవిస్సు స్వీకరించడానికి రా. హోతవై యజ్ఞ దర్భాసనం మీద కూర్చో.",
        "हे अग्नि, स्तुति सुनकर हवि लेने आओ। होता बनकर यज्ञ के कुशासन पर बैठो।",
        "Come, Agni, praised, to partake of the offering. Sit down as priest on the sacred grass.",
        "సామవేదంలోని మొదటి మంత్రం | First Mantra of the Samaveda",
        "सामवेद का पहला मंत्र | अर्थ सहित | First Mantra of the Samaveda",
        "First Mantra of the Samaveda with meaning",
    ),
    Mantra(
        "atharva", "అథర్వవేదం 12.1.12 · భూమి సూక్తం", "अथर्ववेद 12.1.12 · भूमि सूक्त", "Atharvaveda 12.1.12, Prithvi Sukta",
        "यत्ते मध्यं पृथिवि यच्च नभ्यं यास्त ऊर्जस्तन्वः संबभूवुः । तासु नो धेह्यभि नः पवस्व माता भूमिः पुत्रो अहं पृथिव्याः । पर्जन्यः पिता स उ नः पिपर्तु ॥",
        "యత్తే మధ్యం పృథివి యచ్చ నభ్యం యాస్త ఊర్జస్తన్వః సంబభూవుః । తాసు నో ధేహ్యభి నః పవస్వ మాతా భూమిః పుత్రో అహం పృథివ్యాః । పర్జన్యః పితా స ఉ నః పిపర్తు ॥",
        "భూమీ, నీ మధ్యలో, నీ నాభిలో నుండి వెలువడిన శక్తులను మాకు ప్రసాదించు, మమ్మల్ని పవిత్రం చెయ్యి. భూమి నా తల్లి, నేను భూమి పుత్రుడిని. మేఘుడు నా తండ్రి, ఆయన మమ్మల్ని పోషించుగాక.",
        "हे भूमि, तेरे मध्य और नाभि से जो शक्तियाँ प्रकट हुईं, उनमें हमें स्थापित करो और पवित्र करो। भूमि मेरी माता है, मैं पृथ्वी का पुत्र हूँ; पर्जन्य (मेघ) मेरे पिता हैं, वे हमें पुष्ट करें।",
        "Earth, set us among the forces that rise from your centre and navel. Earth is my mother, I am her son. May Parjanya, the rain, my father, nourish me.",
        "అథర్వవేదం: భూమి నా తల్లి | Prithvi Sukta | Atharvaveda",
        "अथर्ववेद: भूमि मेरी माता है | पृथ्वी सूक्त अर्थ सहित | Prithvi Sukta",
        "Prithvi Sukta | Atharvaveda, Earth is my mother",
    ),
    Mantra(
        "rig", "ఋగ్వేదం 3.62.10 · గాయత్రీ మంత్రం", "ऋग्वेद 3.62.10 · गायत्री मंत्र", "Rigveda 3.62.10, Gayatri",
        "तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि । धियो यो नः प्रचोदयात् ॥",
        "తత్సవితుర్వరేణ్యం భర్గో దేవస్య ధీమహి । ధియో యో నః ప్రచోదయాత్ ॥",
        "సవితృ దేవుని శ్రేష్ఠమైన తేజస్సును ధ్యానిస్తున్నాము. ఆయన మా బుద్ధులను ప్రేరేపించుగాక.",
        "हम सविता देव के श्रेष्ठ तेज का ध्यान करते हैं; वह हमारी बुद्धियों को प्रेरित करे।",
        "We meditate on the excellent light of the divine Savitr. May he inspire our minds.",
        "ఋగ్వేదంలో గాయత్రీ మంత్రం | Gayatri Mantra in the Rigveda",
        "ऋग्वेद में गायत्री मंत्र | अर्थ सहित | Gayatri Mantra in the Rigveda",
        "Gayatri Mantra in the Rigveda with meaning",
    ),
    Mantra(
        "yajur", "యజుర్వేదం · శ్రీ రుద్రం మొదటి మంత్రం", "यजुर्वेद · श्री रुद्रम् का पहला मंत्र", "Yajurveda, Taittiriya Samhita 4.5.1, Sri Rudram",
        "नमस्ते रुद्र मन्यव उतो त इषवे नमः । नमस्ते अस्तु धन्वने बाहुभ्यामुत ते नमः ॥",
        "నమస్తే రుద్ర మన్యవ ఉతో త ఇషవే నమః । నమస్తే అస్తు ధన్వనే బాహుభ్యాముత తే నమః ॥",
        "రుద్రా, నీ కోపానికి నమస్కారం, నీ బాణానికి నమస్కారం, నీ ధనుస్సుకు నమస్కారం, నీ బాహువులకు నమస్కారం.",
        "हे रुद्र, तेरे क्रोध को नमन, तेरे बाण को नमन, तेरे धनुष को नमन, तेरी भुजाओं को नमन।",
        "Salutations to your fury, Rudra, to your arrow, to your bow, and to your arms.",
        "శ్రీ రుద్రం మొదటి మంత్రం | Sri Rudram Namakam | Yajurveda",
        "श्री रुद्रम् का पहला मंत्र | अर्थ सहित | Sri Rudram Namakam",
        "Sri Rudram Namakam, first mantra | Yajurveda",
    ),
    Mantra(
        "sama", "సామవేదం · శాంతి మంత్రం", "सामवेद · शांति मंत्र", "Samaveda tradition, Kena Upanishad invocation",
        "ॐ आप्यायन्तु ममाङ्गानि वाक्प्राणश्चक्षुः श्रोत्रमथो बलमिन्द्रियाणि च सर्वाणि ॥",
        "ఓం ఆప్యాయంతు మమాంగాని వాక్ప్రాణశ్చక్షుః శ్రోత్రమథో బలమింద్రియాణి చ సర్వాణి ॥",
        "నా అవయవాలన్నీ పుష్టి పొందుగాక: వాక్కు, ప్రాణం, కన్ను, చెవి, బలం, అన్ని ఇంద్రియాలు.",
        "मेरे सभी अंग पुष्ट हों: वाणी, प्राण, नेत्र, कान, बल और सभी इंद्रियाँ।",
        "May all my limbs grow strong: speech, breath, eye, ear, strength and all the senses.",
        "సామవేద శాంతి మంత్రం | Samaveda Shanti Mantra",
        "सामवेद का शांति मंत्र | अर्थ सहित | Samaveda Shanti Mantra",
        "Samaveda Shanti Mantra with meaning",
    ),
    Mantra(
        "atharva", "అథర్వవేదం 1.6.1 · జల మంత్రం", "अथर्ववेद 1.6.1 · जल मंत्र", "Atharvaveda 1.6.1, the water mantra",
        "ॐ शं नो देवीरभिष्टय आपो भवन्तु पीतये । शं योरभि स्रवन्तु नः ॥",
        "ఓం శం నో దేవీరభిష్టయ ఆపో భవంతు పీతయే । శం యోరభి స్రవంతు నః ॥",
        "దివ్యమైన జలాలు మాకు శుభం కలిగించి, తాగడానికి ఆరోగ్యకరంగా ఉండుగాక. మాకు సుఖం, ఆరోగ్యం కలిగేలా ప్రవహించుగాక.",
        "दिव्य जल हमारे लिए कल्याणकारी हों, इच्छाएँ पूरी करें और पीने के लिए सुखद हों; हमें सुख और आरोग्य देते हुए बहें।",
        "May the divine waters be good for us, for our wishes and for drinking. May they flow to us with health and joy.",
        "అథర్వవేద జల మంత్రం | Water Mantra | Atharvaveda",
        "अथर्ववेद का जल मंत्र | अर्थ सहित | Water Mantra",
        "Water Mantra | Atharvaveda with meaning",
    ),
    Mantra(
        "rig", "ఋగ్వేదం 10.129.1 · నాసదీయ సూక్తం", "ऋग्वेद 10.129.1 · नासदीय सूक्त", "Rigveda 10.129.1, Nasadiya Sukta",
        "नासदासीन्नो सदासीत्तदानीं नासीद्रजो नो व्योमा परो यत् । किमावरीवः कुह कस्य शर्मन्नम्भः किमासीद्गहनं गभीरम् ॥",
        "నాసదాసీన్నో సదాసీత్తదానీం నాసీద్రజో నో వ్యోమా పరో యత్ । కిమావరీవః కుహ కస్య శర్మన్నమ్భః కిమాసీద్గహనం గభీరమ్ ॥",
        "అప్పుడు సత్తు లేదు, అసత్తు లేదు. లోకాలు లేవు, వాటిపైన ఆకాశమూ లేదు. ఏది కప్పింది, ఎక్కడ, ఎవరి ఆశ్రయంలో? లోతైన అగాధ జలమే ఉందా?",
        "तब न सत् था न असत्; न लोक थे, न उनके परे आकाश। किसने ढका, कहाँ, किसके आश्रय में? क्या अथाह गहरा जल था?",
        "Then there was neither being nor non-being, no realm of space, no sky beyond. What covered it, where, in whose keeping? Was there deep, unfathomable water?",
        "సృష్టికి ముందు ఏముంది? ఋగ్వేద నాసదీయ సూక్తం | Nasadiya Sukta",
        "सृष्टि से पहले क्या था? ऋग्वेद का नासदीय सूक्त | Nasadiya Sukta",
        "What existed before creation? Nasadiya Sukta | Rigveda",
    ),
    Mantra(
        "yajur", "యజుర్వేదం · బృహదారణ్యక ఉపనిషత్తు 1.3.28", "यजुर्वेद · बृहदारण्यक उपनिषद् 1.3.28", "Yajurveda, Brihadaranyaka Upanishad 1.3.28",
        "असतो मा सद्गमय । तमसो मा ज्योतिर्गमय । मृत्योर्मा अमृतं गमय ॥ ॐ शान्तिः शान्तिः शान्तिः ॥",
        "అసతో మా సద్గమయ । తమసో మా జ్యోతిర్గమయ । మృత్యోర్మా అమృతం గమయ ॥ ఓం శాంతిః శాంతిః శాంతిః ॥",
        "అసత్యం నుండి సత్యానికి నన్ను నడిపించు. చీకటి నుండి వెలుగుకు నడిపించు. మృత్యువు నుండి అమరత్వానికి నడిపించు.",
        "मुझे असत्य से सत्य की ओर, अंधकार से प्रकाश की ओर, मृत्यु से अमरत्व की ओर ले चलो।",
        "Lead me from the unreal to the real, from darkness to light, from death to immortality.",
        "అసతో మా సద్గమయ | Yajurveda Mantra Meaning",
        "असतो मा सद्गमय | यजुर्वेद मंत्र अर्थ सहित | Asato Ma Sadgamaya",
        "Asato Ma Sadgamaya | Yajurveda mantra with meaning",
    ),
]
