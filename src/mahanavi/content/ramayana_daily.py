"""Mahanavi: 10 daily Ramayana story Shorts (owner request 2026-11-06), riding the release of Ramayana Part 1 (5 Nov 2026).

One short Ramayana story per day, one movie line per day (facts from the Great Andhra review, paraphrased), tags and hashtags.
Images: put the owner's 10 images at assets/images/ramayana/day01.jpg ... day10.jpg; until a day's image exists, a Rama deity photo is used.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from mahanavi.content.alert_seo import _CHANNEL_FOOTER_EN, _CHANNEL_FOOTER_TE
from mahanavi.content.request_shorts import RequestShort, Slide

START = dt.date(2026, 11, 6)
CATCHUP_DAYS = 5
PLAYLIST_TITLE = "Ramayana Stories | రామాయణ కథలు | Mahanavi Spirituals"
PLAYLIST_DESC = ("Short Ramayana stories, one every day: Shabari, Hanuman, Lakshmana, Jatayu, Bharata, Ahalya, the squirrel at Rama Setu, "
                 "Guha, Vibhishana and the return to Ayodhya.\n\nప్రతిరోజూ ఒక చిన్న రామాయణ కథ.")
SRC = "https://telugu.greatandhra.com/movies/movie-news/ramayana-part-1-movie-review.html"


@dataclass(frozen=True)
class Story:
    n: int
    slug: str
    name_te: str
    name_en: str
    lines: tuple[str, ...]
    movie: str          # one factual line about the film (Telugu)
    moral: str


STORIES: tuple[Story, ...] = (
    Story(1, "shabari", "శబరి భక్తి", "Shabari's Devotion",
          ("శబరి ఏళ్ల తరబడి రాముని రాక కోసం ఎదురుచూసింది",
           "ప్రతి పండును రుచి చూసి, తియ్యనివి మాత్రమే తెచ్చింది",
           "రాముడు ఆమె ఎంగిలి పండ్లను ప్రేమగా స్వీకరించాడు",
           "భక్తికి కులం, వయసు, హోదా అడ్డు కావు"),
          "రామాయణం పార్ట్ 1 నవంబర్ 5న విడుదలైంది, దర్శకుడు నితేష్ తివారీ", "ప్రేమతో ఇచ్చినదే దేవునికి ఇష్టం"),
    Story(2, "hanuman", "హనుమంతుని సాగర లంఘనం", "Hanuman Leaps Across the Ocean",
          ("సీతమ్మ జాడ కోసం వానరులు సముద్ర తీరంలో ఆగిపోయారు",
           "జాంబవంతుడు హనుమంతునికి అతని బలాన్ని గుర్తు చేశాడు",
           "రామ నామం స్మరిస్తూ హనుమ నూరు యోజనాల సముద్రం దాటాడు",
           "నమ్మకం ఉంటే అసాధ్యం కూడా సాధ్యమే"),
          "సినిమా సమీక్ష ప్రకారం హనుమంతుని పాత్ర రెండో భాగంలో వస్తుంది", "నీలోని శక్తిని నమ్ము"),
    Story(3, "lakshmana", "లక్ష్మణుని సేవ", "Lakshmana's Sacrifice",
          ("వనవాసంలో లక్ష్మణుడు రాముని సీతమ్మను పద్నాలుగేళ్లు కాపాడాడు",
           "ఆ ఏళ్లన్నీ అతను నిద్ర, విశ్రాంతి వదులుకున్నాడని చెబుతారు",
           "అతని నిద్రను ఊర్మిళ తీసుకుందని కథ",
           "నిశ్శబ్దంగా చేసే త్యాగాలే గొప్పవి"),
          "సినిమాలో లక్ష్మణుడిగా రవి దూబే నటించారు", "సేవలో గొప్పతనం ఉంది"),
    Story(4, "jatayu", "జటాయువు పోరాటం", "Jatayu Fights Ravana",
          ("రావణుడు సీతమ్మను ఎత్తుకుపోతుంటే ముసలి జటాయువు చూసింది",
           "తన వయసును లెక్క చేయక రావణునితో పోరాడింది",
           "రెక్కలు తెగి నేల కూలి, రామునికి సీత జాడ చెప్పింది",
           "రాముడే స్వయంగా ఆ పక్షికి అంతిమ సంస్కారం చేశాడు"),
          "సినిమా సమీక్షలో విజువల్ ఎఫెక్ట్స్, నిర్మాణ విలువలకు ప్రశంసలు వచ్చాయి", "ధర్మం కోసం నిలబడటమే గొప్ప"),
    Story(5, "bharata", "భరతుని పాదుకలు", "Bharata and the Sandals",
          ("రాముడు వనవాసానికి వెళ్లాడని తెలిసి భరతుడు కన్నీరు పెట్టాడు",
           "అడవికి వెళ్లి అన్నను తిరిగి రమ్మని వేడుకున్నాడు",
           "రాముడు ఒప్పుకోకపోవడంతో పాదుకలను తెచ్చి సింహాసనంపై ఉంచాడు",
           "పద్నాలుగేళ్లు రాజు కాకుండా సేవకుడిలా పాలించాడు"),
          "సమీక్ష ప్రకారం రాముని పాత్రలో రణబీర్ కపూర్ ప్రశాంతతను చూపించారు", "అధికారం కన్నా అనుబంధం గొప్పది"),
    Story(6, "ahalya", "అహల్య శాపవిమోచనం", "Ahalya Is Freed",
          ("గౌతమ మహర్షి శాపంతో అహల్య రాయిలా మిగిలిపోయింది",
           "విశ్వామిత్రుడు రామలక్ష్మణులను ఆ ఆశ్రమానికి తీసుకెళ్లాడు",
           "రాముని పాద స్పర్శతో అహల్యకు శాపం తొలగింది",
           "పశ్చాత్తాపానికి ఎప్పుడూ క్షమ ఉంటుంది"),
          "సినిమాలో సీతగా సాయి పల్లవి హుందాగా కనిపించారని సమీక్ష చెబుతోంది", "క్షమించడం గొప్ప గుణం"),
    Story(7, "squirrel", "ఉడుత సేవ", "The Little Squirrel at Rama Setu",
          ("లంకకు వంతెన కడుతుంటే వానరులు పెద్ద బండరాళ్లు తెచ్చారు",
           "ఒక చిన్న ఉడుత ఇసుకలో దొర్లి, రాళ్ల మధ్య దులిపేది",
           "తనకు చేతనైన సాయం చిన్నదైనా అది ఆపలేదు",
           "రాముడు మెచ్చి ప్రేమగా ఉడుత వీపుపై నిమిరాడు, అందుకే ఆ గీతలు"),
          "సినిమాలో రావణుని పాత్రను యష్ పోషించారు", "చిన్న సాయమైనా గొప్పదే"),
    Story(8, "guha", "గుహుని స్నేహం", "Guha, the Boatman Friend",
          ("గంగ ఒడ్డున నిషాద రాజు గుహుడు రాముని కలిశాడు",
           "తన పడవలో రామ సీతా లక్ష్మణులను నది దాటించాడు",
           "రాముడు అతన్ని సొంత సోదరునిలా కౌగిలించుకున్నాడు",
           "స్నేహానికి హోదా ఉండదు"),
          "ఈ సినిమా పార్ట్ 2 వచ్చే ఏడాది లేదా ఆ తర్వాత వస్తుందని సమీక్షలో ఉంది", "నిజమైన స్నేహం అన్నిటినీ దాటుతుంది"),
    Story(9, "vibhishana", "విభీషణ శరణాగతి", "Vibhishana Surrenders",
          ("రావణుని తమ్ముడు విభీషణుడు సీతను తిరిగి ఇవ్వమని చెప్పాడు",
           "రావణుడు అవమానించడంతో అతను రాముని శరణు కోరాడు",
           "శరణు కోరినవారిని రాముడు ఎప్పుడూ వదలనని చెప్పాడు",
           "తరువాత లంకకు విభీషణుడినే రాజును చేశాడు"),
          "సమీక్ష ప్రకారం రావణుని నేపథ్య కథ ఈ సినిమాలో కొత్తగా చూపించారు", "ధర్మం వైపు నిలబడిన వారికి రక్షణ"),
    Story(10, "pattabhishekam", "అయోధ్యకు తిరిగి రాక", "The Return to Ayodhya",
          ("రావణుని ఓడించి రాముడు పద్నాలుగేళ్ల తరువాత అయోధ్యకు వచ్చాడు",
           "ప్రజలు ఇంటింటా దీపాలు వెలిగించి స్వాగతం పలికారు",
           "భరతుడు పాదుకలను రాముని పాదాల వద్ద ఉంచాడు",
           "అలా రామరాజ్యం మొదలైంది, అదే దీపావళి సంప్రదాయం"),
          "సినిమా సంగీతంలో హాన్స్ జిమ్మర్ నేపథ్య సంగీతానికి ప్రశంసలు దక్కాయి", "ధర్మం గెలిచి తీరుతుంది"),
)


def next_story(today: dt.date, done: list[str] | tuple[str, ...] = ()) -> Story | None:
    """The first story not posted yet, one per day from START, with a catch-up window after the tenth day."""
    last = START + dt.timedelta(days=len(STORIES) - 1 + CATCHUP_DAYS)
    if today < START or today > last:
        return None
    for s in STORIES:
        if s.slug not in done:
            return s
    return None


def _bg(s: Story) -> str:
    own = Path(__file__).resolve().parents[3] / "assets" / "images" / "ramayana" / f"day{s.n:02d}.jpg"
    if own.exists():
        return f"ramayana/day{s.n:02d}.jpg"
    return f"deities/rama_n{(s.n - 1) % 10 + 1}.jpg"


def build(s: Story) -> RequestShort:
    story = "\n".join(s.lines)
    body = "\n".join((s.name_te, *s.lines, f"నీతి: {s.moral}"))
    slides = (Slide("points", 10.0, "", body),)   # one card, all the text, 10 seconds
    title = f"రామాయణ కథ {s.n}: {s.name_te} | {s.name_en} | Ramayana Story {s.n}/10"
    title_en = f"Ramayana Story {s.n}/10: {s.name_en}"
    desc = (f"🙏 రామాయణ కథ {s.n}/10: {s.name_te}\n\n" + "\n".join(f"• {x}" for x in s.lines) +
            f"\n\n💡 నీతి: {s.moral}\n\n"
            "ప్రతిరోజూ ఒక చిన్న రామాయణ కథ. ప్లేలిస్ట్ లో 10 కథలూ చూడండి, ఛానల్ ను ఫాలో అవ్వండి.\n"
            "కథలు వాల్మీకి రామాయణం ఆధారంగా సంక్షిప్తంగా చెప్పినవి; ప్రాంతాన్ని బట్టి కొన్ని వివరాలు మారవచ్చు.")
    desc_en = (f"Ramayana story {s.n} of 10: {s.name_en}.\n" + " ".join(s.lines[:0]) +
               "A short Ramayana story every day for 10 days. Stories are told in brief after Valmiki Ramayana; details vary by tradition.")
    tags = ["ramayana", "ramayana stories", "ramayana part 1", "ramayana movie", "ramayana movie telugu", "ramayana 2026",
            "ramayana story in telugu", "ramayana kathalu", "ramayanam", "ramayanam in telugu", "sri rama", "rama", "sita rama",
            "hanuman", "valmiki ramayana", "ramayana short stories", "telugu devotional", "telugu stories", "moral stories telugu",
            "jai shri ram", "jai sri ram", "ramayana telugu", "bhakti", s.name_en.lower(), "shorts"]
    hashtags = ["#Ramayana", "#RamayanaPart1", "#SriRama", "#JaiShriRam", "#RamayanaStory", "#TeluguDevotional", "#Shorts", "#రామాయణం"]
    return RequestShort(
        slug=f"ramayana_{s.n:02d}_{s.slug}", handle="", comment_id="", deity_te="శ్రీరాముడు",
        bg_top=(30, 14, 6), bg_mid=(86, 40, 12), bg_bottom=(14, 8, 4), glow=(255, 190, 80), slides=slides,
        title=title[:100], description_te=desc, description_en=desc_en, title_en=title_en[:100],
        hashtags=hashtags, tags=tags, lang="te", token_file="youtube_token.json", expected_channel="Mahanavi",
        watermark="@MahanaviSpirituals", header="", bg_image=_bg(s), uniform_text=True,
        playlist_line="రామాయణ కథలన్నీ ఒకే చోట!\nడిస్క్రిప్షన్‌లో ప్లేలిస్ట్ లింక్",
        cta_lines=("ప్రతిరోజూ ఒక రామాయణ కథ", "ఛానల్ ను ఫాలో అవ్వండి"), tag_footer="",
        footer_main=_CHANNEL_FOOTER_TE, footer_en=_CHANNEL_FOOTER_EN)
