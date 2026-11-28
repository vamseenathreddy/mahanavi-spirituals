#!/usr/bin/env python3
"""Write blog post JSONs (content/sites/<site>/posts/NNN.json) from the verse databanks, in English (purana) and Hindi (purana_hi).
Each post is original prose around the verse: keyword-first title, text, meaning, how it is used, FAQ. Idempotent: skips titles already present.
  python scripts/ci/blog_gen.py --site purana [--dry]"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from mahanavi.content import chanakya_neeti as ch  # noqa: E402
from mahanavi.content import lakshmi108 as lk  # noqa: E402
from mahanavi.content import lakshmi108_hi as lkh  # noqa: E402
from mahanavi.content import shiva_te as sv  # noqa: E402
from mahanavi.content import vedas  # noqa: E402
from mahanavi.content import vishnu_sahasra as vs  # noqa: E402

HERO = {"vishnu": "hero_vishnu.jpg", "shiva": "hero_shiva.jpg", "lakshmi": "hero_lakshmi.jpg", "veda": "hero_surya.jpg", "chanakya": "hero_saraswati.jpg"}
EN = {
    "vishnu": dict(god="vishnu", label="Vishnu Sahasranamam"), "shiva": dict(god="shiva", label="Shiva Stotram"),
    "lakshmi": dict(god="lakshmi", label="Lakshmi 108 Names"), "veda": dict(god="surya", label="Vedas"),
}


def vlines(sa: str) -> str:
    return "\n".join(f"> {x}" for x in sa.split("\n"))


def en_vishnu(i: int) -> dict:
    a, b = 2 * i, min(2 * i + 2, len(vs.SA))
    sa = " ".join(vs.SA[a:b]).replace("\n", " ")
    first = vs.SA[a].split("\n")[0].split(" ।")[0].strip()
    mean = " ".join(vs.EN_MEAN[a:b])
    title = f"Vishnu Sahasranamam Lyrics with Meaning: Verses {a + 1}-{b}"
    verse = " ".join(f"**{x.replace(chr(10), ' ')}**" for x in vs.SA[a:b])
    return dict(
        title=title, hero="vishnu", god="vishnu",
        desc=f"Vishnu Sahasranamam verses {a + 1} to {b} in Sanskrit with a simple English meaning and how to chant them: '{first}'.",
        labels=["Vishnu Sahasranamam", "Vishnu Sahasranama meaning", "Vishnu stotram", "Thursday prayers", "Hindu mantras"],
        hero_title=f"Vishnu Sahasranamam {a + 1}-{b}", alt=f"Lord Vishnu, Vishnu Sahasranamam verses {a + 1} to {b} with meaning",
        caption=f"Vishnu Sahasranamam, verses {a + 1} to {b}.",
        intro=f"**Vishnu Sahasranamam** is the thousand names of Lord Vishnu, taught by Bhishma to Yudhishthira in the Mahabharata. This post gives **verses {a + 1} to {b}** with the Sanskrit text and a plain English meaning, so you can chant with understanding.",
        takeaways=[f"The verses here open with **{first}**.", "Read the Sanskrit slowly, then the meaning, then chant once more.",
                   "Thursday and Ekadashi are the days most families keep for Vishnu Sahasranamam.", "A short daily portion is better than a rushed full reading."],
        sections=[
            {"h": f"Vishnu Sahasranamam verses {a + 1}-{b} in Sanskrit", "p": ["Read the lines aloud, one breath for each half of a verse:", verse]},
            {"h": "Meaning in simple English", "p": [mean]},
            {"h": "How to use these verses", "p": ["Light a lamp, sit facing east and chant these verses once, then read the meaning silently. Many families take two verses a day and finish the full text in a little under two months.",
                                                  "The names do not need a long ritual. What matters is steady practice, a clear pronunciation and a calm mind."]},
            {"h": "When to chant", "ul": ["Thursdays, the day of Vishnu and the planet Jupiter.", "Ekadashi, twice a month.", "Early morning after a bath, or in the evening at the lamp."]},
        ],
        faq=[{"q": f"What do Vishnu Sahasranamam verses {a + 1} to {b} mean?", "a": mean},
             {"q": "Who taught the Vishnu Sahasranamam?", "a": "**Bhishma** taught it to Yudhishthira on the field of Kurukshetra, as told in the Anushasana Parva of the Mahabharata."},
             {"q": "Can I chant a few verses a day instead of the whole text?", "a": "Yes. A small daily portion with the meaning understood is a common and accepted way to learn it."}],
        note="The Sanskrit is the traditional text. The English is our own plain rendering of the meaning.")


def en_lakshmi(i: int) -> dict:
    rows = lk.NAMES[4 * i:4 * i + 4]
    lo, hi = 4 * i + 1, 4 * i + len(rows)
    names = ", ".join(r[1] for r in rows)
    return dict(
        title=f"Lakshmi Ashtottara Shatanamavali Meaning: Names {lo}-{hi} ({names})", hero="lakshmi", god="lakshmi",
        desc=f"Meaning of Goddess Lakshmi's 108 names, numbers {lo} to {hi}: {names}, with a short note on each.",
        labels=["Lakshmi 108 names", "Lakshmi Ashtottara", "Goddess Lakshmi", "Friday prayers", "Hindu mantras"],
        hero_title=f"Lakshmi 108 Names {lo}-{hi}", alt=f"Goddess Lakshmi, 108 names {lo} to {hi} with meaning", caption=f"Names {lo} to {hi} of the 108 names of Lakshmi.",
        intro=f"The **108 names of Goddess Lakshmi (Ashtottara Shatanamavali)** are chanted on Fridays and at Diwali and Varalakshmi Vratham. This post explains **names {lo} to {hi}**: **{names}**.",
        takeaways=[f"Each name describes one quality of Lakshmi: {names}.", "Fridays are the traditional day for Lakshmi names.", "Say each name with 'Om' before and 'Namah' after."],
        sections=[{"h": f"{r[1]}: {r[2]}", "p": [f"**{r[1]}** means **{r[2]}**. {r[4]}"] } for r in rows] + [
            {"h": "How to chant the 108 names", "p": ["Offer flowers or kumkum at each name if you can, saying 'Om', the name, then 'Namah'. If time is short, chant a few names a day and complete the 108 over the week."]}],
        faq=[{"q": "How many names does Lakshmi Ashtottara have?", "a": "**108** names, which is why it is called Ashtottara Shatanamavali."},
             {"q": "Which day is best for Lakshmi names?", "a": "**Friday**, and festival days like Diwali and Varalakshmi Vratham."}],
        note="Written in our own words from the traditional list of names.")


def en_shiva(i: int) -> dict:
    sa = sv.SA[i]
    day = sv.HEADS[i]
    stot = "Shiva Panchakshara Stotram" if "పంచాక్షర" in day else "Lingashtakam"
    mean = sv.EN_MEAN[i]
    return dict(
        title=f"{stot} Lyrics with Meaning in English: Verse {1 + i if stot[0] == 'S' else i - 5}", hero="shiva", god="shiva",
        desc=f"{stot} verse with Sanskrit text and a simple English meaning. Chant on Mondays and Maha Shivaratri.",
        labels=[stot, "Shiva stotram", "Om Namah Shivaya", "Monday prayers", "Hindu mantras"],
        hero_title=stot, alt=f"Lord Shiva, {stot} with English meaning", caption=f"{stot}: one verse with its meaning.",
        intro=f"**{stot}** is among the most loved Shiva hymns. This post gives one verse in Sanskrit with its **meaning in simple English**.",
        takeaways=["Mondays and Pradosham are the usual days for Shiva stotras.", "Bilva leaves, water and a lamp are the simple offerings.", "Understand the meaning and the chant becomes prayer."],
        sections=[{"h": "The verse in Sanskrit", "p": [" ".join(f"**{x}**" for x in sa.split("\n"))]}, {"h": "Meaning", "p": [mean]},
                  {"h": "How to chant it", "p": ["Sit quietly, take three slow breaths and chant the verse once aloud, then once in the mind. Do the whole hymn on Mondays, one verse on other days."]}],
        faq=[{"q": f"What is the meaning of this {stot} verse?", "a": mean}, {"q": "When should I chant Shiva stotras?", "a": "**Mondays**, **Pradosham** and **Maha Shivaratri** are the traditional times."}],
        note="The Sanskrit is the traditional text. The English is our own plain rendering.")


def en_veda(i: int) -> dict:
    m = vedas.MANTRAS[i]
    return dict(
        title=f"{m.title_en}", hero="veda", god="surya",
        desc=f"{m.ref_en}: the mantra in Sanskrit with a simple English meaning and how it is used.",
        labels=[vedas.HEAD_EN[m.veda], "Vedic mantras", "Veda mantra meaning", "Sanatana Dharma", "Hindu mantras"],
        hero_title=m.title_en.split("|")[0].strip(), alt=f"{vedas.HEAD_EN[m.veda]} mantra with English meaning", caption=m.ref_en,
        intro=f"This is a mantra from the **{vedas.HEAD_EN[m.veda]}** ({m.ref_en}). Below are the Sanskrit text and a **plain English meaning**.",
        takeaways=[f"Source: {m.ref_en}.", "The four Vedas are Rigveda, Yajurveda, Samaveda and Atharvaveda.", "Vedic mantras are learned by listening and repeating."],
        sections=[{"h": "The mantra in Sanskrit", "p": [f"**{m.sa.replace(chr(10), ' ')}**"]}, {"h": "Meaning in simple English", "p": [m.en_mean]},
                  {"h": "About the " + vedas.HEAD_EN[m.veda], "p": [f"The {vedas.HEAD_EN[m.veda]} is one of the four Vedas, the oldest scriptures of Sanatana Dharma, handed down by voice for thousands of years."]}],
        faq=[{"q": "What does this mantra mean?", "a": m.en_mean}, {"q": "How many Vedas are there?", "a": "There are **four**: Rig, Yajur, Sama and Atharva."}],
        note="The Sanskrit is the traditional text. The English is our own plain rendering.")


def hi_vishnu(i: int) -> dict:
    a, b = 2 * i, min(2 * i + 2, len(vs.SA))
    first = vs.SA[a].split("\n")[0].split(" ।")[0].strip()
    mean = " ".join(vs.HI_MEAN[a:b])
    verse = " ".join(f"**{x.replace(chr(10), ' ')}**" for x in vs.SA[a:b])
    return dict(
        title=f"विष्णु सहस्रनाम अर्थ सहित: श्लोक {a + 1}-{b}", hero="vishnu", god="vishnu",
        desc=f"विष्णु सहस्रनाम के श्लोक {a + 1} से {b} संस्कृत पाठ और सरल हिंदी अर्थ के साथ: '{first}'।",
        labels=["विष्णु सहस्रनाम", "विष्णु सहस्रनाम अर्थ", "विष्णु स्तोत्र", "गुरुवार पूजा", "Vishnu Sahasranamam"],
        hero_title=f"विष्णु सहस्रनाम {a + 1}-{b}", alt=f"भगवान विष्णु, विष्णु सहस्रनाम श्लोक {a + 1} से {b} अर्थ सहित", caption=f"विष्णु सहस्रनाम, श्लोक {a + 1} से {b}।",
        intro=f"**विष्णु सहस्रनाम** भगवान विष्णु के हज़ार नाम हैं, जिन्हें भीष्म पितामह ने युधिष्ठिर को महाभारत में सुनाया। इस लेख में **श्लोक {a + 1} से {b}** संस्कृत पाठ और सरल हिंदी अर्थ के साथ हैं।",
        takeaways=[f"इन श्लोकों की शुरुआत **{first}** से होती है।", "पहले संस्कृत धीरे पढ़ें, फिर अर्थ, फिर एक बार और जपें।", "गुरुवार और एकादशी विष्णु सहस्रनाम के लिए सबसे उत्तम दिन माने जाते हैं।", "रोज़ थोड़ा पाठ, जल्दबाज़ी में पूरा पाठ करने से बेहतर है।"],
        sections=[{"h": f"विष्णु सहस्रनाम श्लोक {a + 1}-{b} संस्कृत में", "p": ["श्लोक को धीरे और साफ़ उच्चारण के साथ पढ़ें:", verse]},
                  {"h": "सरल हिंदी अर्थ", "p": [mean]},
                  {"h": "पाठ कैसे करें", "p": ["दीपक जलाकर पूर्व की ओर मुख करके बैठें। श्लोक एक बार बोलकर पढ़ें, फिर अर्थ मन में दोहराएँ। कई परिवार रोज़ दो श्लोक पढ़कर लगभग दो महीने में पूरा पाठ कर लेते हैं।"]},
                  {"h": "किस दिन पढ़ें", "ul": ["गुरुवार, विष्णु और बृहस्पति का दिन।", "एकादशी, महीने में दो बार।", "सुबह स्नान के बाद या शाम को दीपक के पास।"]}],
        faq=[{"q": f"विष्णु सहस्रनाम के श्लोक {a + 1} से {b} का अर्थ क्या है?", "a": mean},
             {"q": "विष्णु सहस्रनाम किसने सुनाया?", "a": "**भीष्म पितामह** ने कुरुक्षेत्र में युधिष्ठिर को सुनाया, यह महाभारत के अनुशासन पर्व में आता है।"},
             {"q": "क्या रोज़ कुछ श्लोक पढ़ना ठीक है?", "a": "हाँ, अर्थ समझकर रोज़ थोड़ा पाठ करना सामान्य और मान्य तरीका है।"}],
        note="संस्कृत पाठ परंपरागत है। हिंदी अर्थ हमारे अपने सरल शब्दों में है।")


def hi_lakshmi(i: int) -> dict:
    rows = list(zip(lk.NAMES, lkh.HI))[4 * i:4 * i + 4]
    lo, hi = 4 * i + 1, 4 * i + len(rows)
    names = ", ".join(r[1][0] for r in rows)
    return dict(
        title=f"लक्ष्मी अष्टोत्तर शतनामावली अर्थ सहित: नाम {lo}-{hi} ({names})", hero="lakshmi", god="lakshmi",
        desc=f"माँ लक्ष्मी के 108 नामों में से नाम {lo} से {hi}: {names}, हर नाम का सरल अर्थ।",
        labels=["लक्ष्मी 108 नाम", "लक्ष्मी अष्टोत्तर", "माँ लक्ष्मी", "शुक्रवार पूजा", "Lakshmi 108 names"],
        hero_title=f"लक्ष्मी 108 नाम {lo}-{hi}", alt=f"माँ लक्ष्मी, 108 नाम {lo} से {hi} अर्थ सहित", caption=f"माँ लक्ष्मी के 108 नामों में से {lo} से {hi}।",
        intro=f"**माँ लक्ष्मी के 108 नाम (अष्टोत्तर शतनामावली)** शुक्रवार, दीवाली और वरलक्ष्मी व्रत पर पढ़े जाते हैं। इस लेख में **नाम {lo} से {hi}** का अर्थ है: **{names}**।",
        takeaways=[f"हर नाम लक्ष्मी जी का एक गुण बताता है: {names}।", "शुक्रवार लक्ष्मी नामों के लिए परंपरागत दिन है।", "हर नाम से पहले 'ॐ' और बाद में 'नमः' बोलें।"],
        sections=[{"h": f"{r[1][0]}: {r[0][1]}", "p": [f"**{r[1][0]}** ({r[0][1]}) का भाव: {r[1][1]} {r[1][2]}"]} for r in rows]
        + [{"h": "108 नाम कैसे जपें", "p": ["हर नाम पर फूल या कुमकुम चढ़ाते हुए 'ॐ', नाम और 'नमः' बोलें। समय कम हो तो रोज़ कुछ नाम पढ़कर सप्ताह में 108 पूरे करें।"]}],
        faq=[{"q": "लक्ष्मी अष्टोत्तर में कितने नाम हैं?", "a": "**108** नाम, इसीलिए इसे अष्टोत्तर शतनामावली कहते हैं।"},
             {"q": "लक्ष्मी नाम पढ़ने का सबसे अच्छा दिन कौन सा है?", "a": "**शुक्रवार**, और दीवाली व वरलक्ष्मी व्रत जैसे पर्व।"}],
        note="पारंपरिक नामों की सूची पर हमारे अपने शब्दों में लिखा गया।")


def hi_veda(i: int) -> dict:
    m = vedas.MANTRAS[i]
    h = vedas.HEAD_HI[m.veda]
    return dict(
        title=m.title_hi, hero="veda", god="surya",
        desc=f"{m.ref_hi}: मंत्र संस्कृत में, सरल हिंदी अर्थ और उपयोग के साथ।", labels=[h, "वैदिक मंत्र", "वेद मंत्र अर्थ", "सनातन धर्म", "Vedic mantras"],
        hero_title=m.title_hi.split("|")[0].strip(), alt=f"{h} का मंत्र हिंदी अर्थ सहित", caption=m.ref_hi,
        intro=f"यह **{h}** ({m.ref_hi}) का मंत्र है। नीचे संस्कृत पाठ और **सरल हिंदी अर्थ** है।",
        takeaways=[f"स्रोत: {m.ref_hi}।", "चार वेद हैं: ऋग्वेद, यजुर्वेद, सामवेद और अथर्ववेद।", "वैदिक मंत्र सुनकर और दोहराकर सीखे जाते हैं।"],
        sections=[{"h": "संस्कृत मंत्र", "p": [f"**{m.sa.replace(chr(10), ' ')}**"]}, {"h": "सरल हिंदी अर्थ", "p": [m.hi_mean]},
                  {"h": f"{h} के बारे में", "p": [f"{h} चार वेदों में से एक है, सनातन धर्म के सबसे प्राचीन ग्रंथ, जो हज़ारों वर्षों तक वाणी से आगे बढ़ते रहे।"]}],
        faq=[{"q": "इस मंत्र का अर्थ क्या है?", "a": m.hi_mean}, {"q": "वेद कितने हैं?", "a": "**चार**: ऋग्, यजुः, साम और अथर्व।"}],
        note="संस्कृत पाठ परंपरागत है। हिंदी अर्थ हमारे अपने सरल शब्दों में है।")


def hi_chanakya(i: int) -> dict:
    rows = list(zip(ch.SUTRAS, ch.EXAMPLES))[3 * i:3 * i + 3]
    first = rows[0][0][0]
    return dict(
        title=f"चाणक्य नीति के 3 सूत्र अर्थ सहित: {first.rstrip('।')}", hero="chanakya", god="saraswati",
        desc="चाणक्य नीति के तीन सूत्र हिंदी अर्थ और आज के जीवन के उदाहरण के साथ: पैसा, रिश्ते और सफलता पर चाणक्य की सीख।",
        labels=["चाणक्य नीति", "चाणक्य के विचार", "चाणक्य सूत्र", "जीवन की सीख", "Chanakya Neeti"],
        hero_title="चाणक्य नीति के सूत्र", alt="चाणक्य नीति के सूत्र हिंदी अर्थ सहित", caption="चाणक्य नीति: आज के जीवन के लिए तीन सूत्र।",
        intro="**चाणक्य नीति** आचार्य चाणक्य की जीवन, धन और व्यवहार पर सीख है। इस लेख में **तीन सूत्र** हैं, हर एक के साथ आज के जीवन का छोटा उदाहरण।",
        takeaways=[r[0][0] for r in rows],
        sections=[{"h": f"सूत्र {k + 1}", "p": [f"**{r[0][0]}**", f"उदाहरण: {r[1][0]}"]} for k, r in enumerate(rows)],
        faq=[{"q": "चाणक्य नीति क्या है?", "a": "**चाणक्य नीति** आचार्य चाणक्य के जीवन, राजनीति, धन और व्यवहार पर सूत्रों का संग्रह है।"}],
        note="सूत्र चाणक्य की परंपरागत शिक्षा पर आधारित हमारे अपने शब्द हैं।")


PLAN = {
    "purana": [("vishnu", en_vishnu, 54), ("shiva", en_shiva, 15), ("lakshmi", en_lakshmi, 27), ("veda", en_veda, 10)],
    "purana_hi": [("vishnu", hi_vishnu, 54), ("lakshmi", hi_lakshmi, 27), ("chanakya", hi_chanakya, 35), ("veda", hi_veda, 10)],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    d = ROOT / "content" / "sites" / a.site
    posts = d / "posts"
    have = {json.loads(p.read_text(encoding="utf-8"))["title"] for p in posts.glob("*.json")}
    nxt = max(int(p.stem) for p in posts.glob("*.json")) + 1
    cfg = json.loads((d / "site.json").read_text(encoding="utf-8"))
    hero_out = ROOT / "assets" / "blog" / cfg["hero_dir"]
    # interleave the topics so the blog mixes Vishnu, Shiva, Lakshmi and Veda posts day to day
    queues = [[(k, fn, i) for i in range(n)] for k, fn, n in PLAN[a.site]]
    order = []
    while any(queues):
        for q in queues:
            if q:
                order.append(q.pop(0))
    made = 0
    for k, fn, i in order:
        p = fn(i)
        if p["title"] in have:
            continue
        hero = HERO[p["hero"]]
        p["hero"] = hero
        p["id"] = nxt
        if not a.dry:
            shutil.copy(ROOT / "assets" / "blog" / hero, hero_out / hero)
            (posts / f"{nxt:03d}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
        nxt += 1
        made += 1
    print(f"{a.site}: {made} new posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
