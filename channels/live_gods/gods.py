"""Day-wise live streams on Mahanavi Spirituals (IST weekday: Monday=0). One unbroken stream 4:00 to 9:55 AM."""
from __future__ import annotations

import importlib

# weekday -> god key. Friday uses the existing Lakshmi video (Revathy VSL); the others use the chant loop built by god_live_build.py.
WEEK = {0: "shiva", 1: "hanuman", 2: "ganesha", 3: "dattatreya", 4: "lakshmi", 5: "venkateswara", 6: "surya"}

GODS = {
    "shiva": dict(te="శివ", en="Lord Shiva", names_te="శివ అష్టోత్తర శతనామావళి", names_en="Shiva Ashtottara Shatanamavali", day_te="సోమవారం", day_en="Monday",
                  photos=["shiva_n1", "shiva_n2", "shiva_n3", "shiva_n4", "shiva_n5", "shiva_n6", "shiva_n7", "shiva_n8", "shiva_n9", "shiva_n10", "shiva_g1", "shiva_g2"],
                  mantra="ఓం నమః శివాయ", tags=["Shiva 108 names", "Shiva Ashtottara", "Om Namah Shivaya", "Monday Shiva puja", "Shiva stotram Telugu", "Lord Shiva songs"]),
    "hanuman": dict(te="హనుమాన్", en="Lord Hanuman", names_te="హనుమాన్ అష్టోత్తర శతనామావళి", names_en="Hanuman Ashtottara Shatanamavali", day_te="మంగళవారం", day_en="Tuesday",
                    photos=["hanuman_1", "hanuman_g1", "hanuman_g2"], mantra="ఓం శ్రీ హనుమతే నమః",
                    tags=["Hanuman 108 names", "Hanuman Ashtottara", "Tuesday Hanuman puja", "Anjaneya stotram Telugu", "Hanuman songs"]),
    "ganesha": dict(te="గణపతి", en="Lord Ganesha", names_te="గణేశ అష్టోత్తర శతనామావళి", names_en="Ganesha Ashtottara Shatanamavali", day_te="బుధవారం", day_en="Wednesday",
                    photos=["ganesha_g1", "ganesha_g2"], mantra="ఓం గం గణపతయే నమః",
                    tags=["Ganesha 108 names", "Ganapati Ashtottara", "Wednesday Ganesh puja", "Vinayaka songs Telugu"]),
    "dattatreya": dict(te="దత్తాత్రేయ", en="Lord Dattatreya", names_te="దత్తాత్రేయ అష్టోత్తర శతనామావళి", names_en="Dattatreya Ashtottara Shatanamavali", day_te="గురువారం", day_en="Thursday",
                       photos=[f"dattatreya_g{i}" for i in range(1, 11)], mantra="ఓం శ్రీ దత్తాత్రేయాయ నమః",
                       tags=["Dattatreya 108 names", "Datta Ashtottara", "Thursday Guru puja", "Datta stotram Telugu"]),
    "lakshmi": dict(te="లక్ష్మీ", en="Goddess Lakshmi", day_te="శుక్రవారం", day_en="Friday", photos=[], tags=[]),
    "venkateswara": dict(te="వేంకటేశ్వర", en="Lord Venkateswara", names_te="శ్రీ వేంకటేశ్వర అష్టోత్తర శతనామావళి", names_en="Venkateswara Ashtottara Shatanamavali", day_te="శనివారం", day_en="Saturday",
                         photos=[f"venkateswara_n{i}" for i in range(1, 10)] + ["venkateswara_g1", "venkateswara_g2"], mantra="ఓం నమో వేంకటేశాయ",
                         tags=["Venkateswara 108 names", "Balaji Ashtottara", "Saturday Venkateswara puja", "Govinda songs Telugu"]),
    "surya": dict(te="సూర్య", en="Lord Surya", names_te="సూర్య అష్టోత్తర శతనామావళి", names_en="Surya Ashtottara Shatanamavali", day_te="ఆదివారం", day_en="Sunday",
                  photos=["graha_surya", "surya_g2"], mantra="ఓం సూర్యాయ నమః",
                  tags=["Surya 108 names", "Surya Ashtottara", "Sunday Surya puja", "Aditya Hrudayam Telugu"]),
}


def names(god: str) -> list[str] | None:
    try:
        return importlib.import_module(f"channels.live_gods.{god}").NAMES
    except ModuleNotFoundError:
        return None


def title(god: str) -> str:
    g = GODS[god]
    return f"LIVE {g['names_te']} | {g['names_en']} | {g['en']} {g['day_en']} Chanting | మహానవి"[:100]


def description(god: str) -> str:
    g = GODS[god]
    return (f"{g['day_te']} ఉదయం {g['te']} 108 నామాలు ప్రశాంతంగా వినండి. ఈ లైవ్‌లో {g['names_te']} తెలుగులో వరుసగా వినిపిస్తుంది.\n"
            f"Listen to the {g['names_en']} (108 names of {g['en']}) in Telugu, chanted in a continuous morning live stream every {g['day_en']}.\n\n"
            "ప్రతి రోజు ఉదయం 4 గంటల నుంచి లైవ్ | Live every morning from 4 AM IST: Mon Shiva, Tue Hanuman, Wed Ganesha, Thu Dattatreya, Fri Lakshmi, Sat Venkateswara, Sun Surya.\n"
            "Channel: Mahanavi Spirituals\n\n"
            "The chanting voice is a synthetic (AI) Telugu voice reading the traditional names, with generated ambient music. "
            "This stream contains altered or synthetic content.\n\n"
            "#" + " #".join(t.replace(" ", "") for t in g["tags"][:3]) + " #MahanaviSpirituals #TeluguDevotional")
