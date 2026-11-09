"""Shiv Tandav Stotram (Ravana), 15 verses: Devanagari text and a short Hindi meaning of each, for the verse by verse series.

The meanings are plain Hindi renderings written for this channel (not copied from any publication)."""
from __future__ import annotations

HEAD = "शिव ताण्डव स्तोत्रम्"
HEAD_EN = "Shiv Tandav Stotram"

# (verse, meaning)
VERSES: list[tuple[str, str]] = [
    ("जटाटवीगलज्जलप्रवाहपावितस्थले गलेऽवलम्ब्य लम्बितां भुजङ्गतुङ्गमालिकाम् ।\nडमड्डमड्डमड्डमन्निनादवड्डमर्वयं चकार चण्डताण्डवं तनोतु नः शिवः शिवम् ॥",
     "जटाओं के वन से बहती गंगा की धारा ने जिनका स्थान पवित्र किया, गले में सर्पों की माला है, और डमरू की डम-डम गूंजती है। ऐसे शिव ने प्रचंड ताण्डव किया, वे हमारा कल्याण करें।"),
    ("जटाकटाहसम्भ्रमभ्रमन्निलिम्पनिर्झरी विलोलवीचिवल्लरीविराजमानमूर्धनि ।\nधगद्धगद्धगज्ज्वलल्ललाटपट्टपावके किशोरचन्द्रशेखरे रतिः प्रतिक्षणं मम ॥",
     "जिनके मस्तक पर जटाओं में घूमती गंगा की चंचल लहरें शोभा देती हैं, ललाट पर अग्नि धगधग जल रही है और सिर पर बाल चन्द्रमा है, उन शिव में मेरी प्रीति हर क्षण बनी रहे।"),
    ("धराधरेन्द्रनन्दिनीविलासबन्धुबन्धुर स्फुरद्दिगन्तसन्ततिप्रमोदमानमानसे ।\nकृपाकटाक्षधोरणीनिरुद्धदुर्धरापदि क्वचिद्दिगम्बरे मनो विनोदमेतु वस्तुनि ॥",
     "पर्वतराज की पुत्री पार्वती के साथ आनंद करने वाले, जिनकी कृपा भरी दृष्टि से कठिन से कठिन संकट रुक जाते हैं, उन दिगम्बर शिव में मेरा मन आनंद पाए।"),
    ("जटाभुजङ्गपिङ्गलस्फुरत्फणामणिप्रभा कदम्बकुङ्कुमद्रवप्रलिप्तदिग्वधूमुखे ।\nमदान्धसिन्धुरस्फुरत्त्वगुत्तरीयमेदुरे मनो विनोदमद्भुतं बिभर्तु भूतभर्तरि ॥",
     "जटा के सर्पों के फनों की मणियों की चमक से दिशाओं के मुख कुंकुम से रंगे लगते हैं, मतवाले हाथी की खाल उनका वस्त्र है। ऐसे भूतनाथ शिव में मेरा मन अद्भुत आनंद पाए।"),
    ("सहस्रलोचनप्रभृत्यशेषलेखशेखर प्रसूनधूलिधोरणी विधूसराङ्घ्रिपीठभूः ।\nभुजङ्गराजमालया निबद्धजाटजूटकः श्रियै चिराय जायतां चकोरबन्धुशेखरः ॥",
     "इन्द्र आदि सब देवताओं के सिर के फूलों की धूल से जिनकी चरण-चौकी धूसर है, सर्पराज की माला से जटा बंधी है, वे चन्द्रशेखर शिव हमें चिरकाल तक समृद्धि दें।"),
    ("ललाटचत्वरज्वलद्धनञ्जयस्फुलिङ्गभा निपीतपञ्चसायकं नमन्निलिम्पनायकम् ।\nसुधामयूखलेखया विराजमानशेखरं महाकपालिसम्पदे शिरोजटालमस्तु नः ॥",
     "जिन्होंने ललाट की अग्नि की चिंगारी से कामदेव को भस्म किया, जिन्हें देवराज प्रणाम करते हैं, जिनके मस्तक पर चन्द्रकला सजी है, वे जटाधारी शिव हमें सिद्धि और सम्पदा दें।"),
    ("करालभालपट्टिकाधगद्धगद्धगज्ज्वल द्धनञ्जयाहुतीकृतप्रचण्डपञ्चसायके ।\nधराधरेन्द्रनन्दिनीकुचाग्रचित्रपत्रक प्रकल्पनैकशिल्पिनि त्रिलोचने रतिर्मम ॥",
     "जिनके भयंकर ललाट की अग्नि में कामदेव की आहुति हुई, और जो पार्वती के अंगों पर चित्र रचने के एकमात्र शिल्पी हैं, उन त्रिलोचन शिव में मेरी प्रीति हो।"),
    ("नवीनमेघमण्डली निरुद्धदुर्धरस्फुरत् कुहूनिशीथिनीतमः प्रबन्धबद्धकन्धरः ।\nनिलिम्पनिर्झरीधरस्तनोतु कृत्तिसिन्धुरः कलानिधानबन्धुरः श्रियं जगद्धुरन्धरः ॥",
     "नए बादलों से ढकी अमावस की रात के अंधकार जैसा जिनका कंठ है, जो गंगा और गजचर्म धारण करते हैं, चन्द्रकला के धारक और जगत के आधार हैं, वे शिव हमें सम्पदा दें।"),
    ("प्रफुल्लनीलपङ्कजप्रपञ्चकालिमप्रभा विडम्बिकण्ठकन्धरारुचिप्रबद्धकन्धरम् ।\nस्मरच्छिदं पुरच्छिदं भवच्छिदं मखच्छिदं गजच्छिदान्धकच्छिदं तमन्तकच्छिदं भजे ॥",
     "खिले नीले कमलों की श्याम आभा जैसा जिनका कंठ है, जिन्होंने काम, त्रिपुर, संसार के बंधन, दक्ष के यज्ञ, गजासुर, अंधकासुर और यम का नाश किया, उन शिव को मैं भजता हूँ।"),
    ("अखर्वसर्वमङ्गलाकलाकदम्बमञ्जरी रसप्रवाहमाधुरीविजृम्भणामधुव्रतम् ।\nस्मरान्तकं पुरान्तकं भवान्तकं मखान्तकं गजान्तकान्धकान्तकं तमन्तकान्तकं भजे ॥",
     "जो सब मंगलमयी कलाओं की मंजरी के रस की मधुरता के भौंरे हैं, और जिन्होंने काम, त्रिपुर, भव, यज्ञ, गजासुर, अंधक और स्वयं यम का अंत किया, उन शिव को मैं भजता हूँ।"),
    ("जयत्वदभ्रविभ्रमभ्रमद्भुजङ्गमश्वस द्विनिर्गमत्क्रमस्फुरत्करालभालहव्यवाट् ।\nधिमिद्धिमिद्धिमिध्वनन्मृदङ्गतुङ्गमङ्गल ध्वनिक्रमप्रवर्तितप्रचण्डताण्डवः शिवः ॥",
     "जिनके ललाट की भयंकर अग्नि में सर्पों की फुफकार से लपटें उठती हैं, और मृदंग की धिमिधिमि ध्वनि के क्रम पर जो प्रचंड ताण्डव करते हैं, वे शिव सदा विजयी हों।"),
    ("दृषद्विचित्रतल्पयोर्भुजङ्गमौक्तिकस्रजोर्गरिष्ठरत्नलोष्ठयोः सुहृद्विपक्षपक्षयोः ।\nतृणारविन्दचक्षुषोः प्रजामहीमहेन्द्रयोः समं प्रवर्तयन्मनः कदा सदाशिवं भजे ॥",
     "पत्थर और कोमल शय्या, सर्प और मोतियों की माला, रत्न और मिट्टी, मित्र और शत्रु, तिनका और कमल, प्रजा और राजा, सबको समान देखता हुआ मैं सदाशिव को कब भजूँगा?"),
    ("कदा निलिम्पनिर्झरीनिकुञ्जकोटरे वसन् विमुक्तदुर्मतिः सदा शिरःस्थमञ्जलिं वहन् ।\nविमुक्तलोललोचनो ललामभाललग्नकः शिवेति मन्त्रमुच्चरन् कदा सुखी भवाम्यहम् ॥",
     "मैं कब गंगा तट की कुंज में रहकर, दुर्बुद्धि से मुक्त होकर, सिर पर हाथ जोड़े, चंचल नेत्र शांत करके, \"शिव\" मंत्र का उच्चारण करता हुआ सुखी होऊँगा?"),
    ("इमं हि नित्यमेवमुक्तमुत्तमोत्तमं स्तवं पठन्स्मरन्ब्रुवन्नरो विशुद्धिमेति सन्ततम् ।\nहरे गुरौ सुभक्तिमाशु याति नान्यथा गतिं विमोहनं हि देहिनां सुशङ्करस्य चिन्तनम् ॥",
     "जो मनुष्य इस उत्तम स्तोत्र को नित्य पढ़ता, स्मरण करता या कहता है, वह सदा शुद्ध रहता है और शिव तथा गुरु में शीघ्र दृढ़ भक्ति पाता है। शंकर का चिंतन मोह दूर करता है।"),
    ("पूजावसानसमये दशवक्त्रगीतं यः शम्भुपूजनमिदं पठति प्रदोषे ।\nतस्य स्थिरां रथगजेन्द्रतुरङ्गयुक्तां लक्ष्मीं सदैव सुमुखिं प्रददाति शम्भुः ॥",
     "पूजा के अंत में प्रदोष काल में रावण द्वारा रचित इस शम्भु-स्तोत्र को जो पढ़ता है, उसे शम्भु रथ, हाथी और घोड़ों से युक्त स्थिर लक्ष्मी और सदा प्रसन्न मन देते हैं।"),
]


def count() -> int:
    return len(VERSES)


# Short English meaning of each verse (same order as VERSES), shown on the card under the Hindi meaning
MEANING_EN: list[str] = [
    "Shiva, whose matted locks let the Ganga flow down, a serpent garland on his neck, the damaru sounding, performed his fierce dance. May he bless us.",
    "I love Shiva, whose locks hold the restless waves of the Ganga, whose forehead blazes with fire and who wears the crescent moon.",
    "May my mind find joy in Shiva, delighted with Parvati, whose merciful glance removes even the hardest troubles.",
    "May my mind find wonder in Shiva, the lord of beings, clad in an elephant hide, with the gems of his serpents lighting up all directions.",
    "May Shiva, the moon crested one, whose footstool is dusty with flowers from the crowns of the gods, grant us lasting prosperity.",
    "May Shiva, who burned Kama with the spark of his forehead fire and whom Indra bows to, grant us success and wealth.",
    "I love the three eyed Shiva, whose forehead fire consumed Kama and who alone paints designs on Parvati.",
    "May Shiva, whose throat is dark like a new moon night with clouds, who bears the Ganga and the moon, grant us wealth.",
    "I worship Shiva, whose throat is dark like blue lotuses, who destroyed Kama, Tripura, worldly bonds, Daksha's yajna, Gajasura, Andhaka and Yama.",
    "I worship Shiva, the bee at the honey of all auspicious arts, who ended Kama, Tripura, Bhava, the yajna, Gajasura, Andhaka and Yama.",
    "May Shiva, whose forehead fire flares with the hiss of serpents, dancing to the beat of the mridanga, always be victorious.",
    "Seeing stone and soft bed, snake and pearl necklace, friend and foe, king and subject alike, when shall I worship Sadashiva?",
    "When shall I be happy by the Ganga, free of evil thoughts, hands folded, eyes calm, chanting the name of Shiva?",
    "One who reads, recalls or recites this hymn daily stays pure and quickly gains firm devotion to Shiva and the Guru. Thinking of Shankara removes delusion.",
    "One who reads this hymn by Ravana at the end of worship at dusk is given steady wealth, with chariots, elephants and horses, by Shambhu.",
]
