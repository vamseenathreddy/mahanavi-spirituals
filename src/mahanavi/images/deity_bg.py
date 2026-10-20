"""Deity photo behind Telugu cards, matched to the mantra / story (owner request 2026-10-20). Photos live in
assets/images/deities and rotate by date. Rashi uses the ruling planet's god, Purana the god the story is about."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

DEITIES = Path(__file__).resolve().parents[3] / "assets" / "images" / "deities"
PHOTOS = {
    "kurma": ["puranic_kurma", "puranic_manthan"], "manthan": ["puranic_manthan"], "varaha": ["puranic_varaha"],
    "dashavatara": ["puranic_dashavatara"], "garuda": ["puranic_garuda"], "dakshinamurthy": ["puranic_dakshinamurthy"],
    "sheshashayi": ["puranic_sheshashayi"],
    "g_surya": ["graha_surya"], "g_chandra": ["graha_chandra"], "g_mangala": ["graha_mangala"], "g_budha": ["graha_budha"],
    "g_guru": ["graha_guru"], "g_shukra": ["graha_shukra"], "g_shani": ["graha_shani"], "g_rahu": ["graha_rahu"],
    "g_ketu": ["graha_ketu"],
    "ayyappa": ['ayyappa_n1', 'ayyappa_n2', 'ayyappa_n3'],
    "annapurna": ['annapurna_n1', 'annapurna_n2'],
    "gita": ['gita_n1', 'gita_n2', 'gita_n3', 'gita_n4', 'gita_n5', 'gita_n6', 'gita_n7', 'gita_n8', 'gita_n9', 'gita_n10'],

    "shiva": ["shiva_g1", "shiva_g2", "shivafamily_n1", "shivafamily_n2", "shiva_n1", "shiva_n2", "shiva_n3", "shiva_n4", "shiva_n5", "shiva_n6", "shiva_n7", "shiva_n8", "shiva_n9", "shiva_n10"], "hanuman": ["hanuman_g1", "hanuman_g2"], "ganesha": ["ganesha_g1", "ganesha_g2"],
    "vishnu": ["vishnu_g1", "vishnu_g3", "vishnu_g5", "vishnu_g2"], "lakshmi": ["lakshmi_g1", "lakshmi_g2"],
    "shani": ["shani_g1", "shani_g3", "shani_g5"], "surya": ["surya_g2"], "durga": ["durga_g1", "durga_g2", "durga_n1", "durga_n2", "durga_n3", "durga_n4", "durga_n5", "durga_n6", "durga_n7", "durga_n8", "durga_n9", "durga_n10"],
    "krishna": ["krishna_g1", "krishna_n1", "krishna_n2", "krishna_n3", "krishna_n4", "krishna_n5", "krishna_n6", "krishna_n7", "krishna_n8", "krishna_n9", "krishna_n10"], "rama": ["rama_g1", "rama_g2", "rama_n1", "rama_n2", "rama_n3", "rama_n4", "rama_n5", "rama_n6", "rama_n7", "rama_n8", "rama_n9", "rama_n10"], "narasimha": ["narasimha_g1", "narasimha_g2", "narasimha_n1", "narasimha_n2", "narasimha_n3"],
    "saraswati": ["saraswati_g2", "saraswati_n1", "saraswati_n2", "saraswati_n3", "saraswati_n4", "saraswati_n5", "saraswati_n6", "saraswati_n7", "saraswati_n8", "saraswati_n9", "saraswati_n10"], "murugan": ["murugan_g1", "murugan_g2"], "parvati": ["parvati_g2"],
    "dattatreya": ["dattatreya_g1", "dattatreya_g3", "dattatreya_g5"], "venkateswara": ["venkateswara_g1"],
}
# Mesha, Vrishabha, Mithuna, Karka, Simha, Kanya, Tula, Vrischika, Dhanus, Makara, Kumbha, Meena
RASHI_GOD = ["g_mangala", "g_shukra", "g_budha", "g_chandra", "g_surya", "g_budha", "g_shukra", "g_mangala", "g_guru",
             "g_shani", "g_shani", "g_guru"]
KEYWORDS = [
    ("కూర్మ", "kurma"), ("సముద్ర మథన", "manthan"), ("క్షీరసాగర", "manthan"), ("వరాహ", "varaha"), ("దశావతార", "dashavatara"), ("గరుడ", "garuda"), ("దక్షిణామూర్తి", "dakshinamurthy"), ("శేషశయన", "sheshashayi"), ("అనంతశయన", "sheshashayi"),
    ("అయ్యప్ప", "ayyappa"), ("అన్నపూర్ణ", "annapurna"),  # first match wins
    ("నరసింహ", "narasimha"), ("హనుమ", "hanuman"), ("ఆంజనేయ", "hanuman"), ("గణేశ", "ganesha"), ("గణపతి", "ganesha"),
    ("సరస్వతి", "saraswati"), ("లక్ష్మి", "lakshmi"), ("దుర్గ", "durga"), ("పార్వతి", "parvati"),
    ("సుబ్రహ్మణ్య", "murugan"), ("కార్తికేయ", "murugan"), ("కృష్ణ", "krishna"), ("రామ", "rama"), ("శివ", "shiva"),
    ("శని", "shani"), ("సూర్య", "surya"), ("వేంకటేశ్వర", "venkateswara"), ("దత్తాత్రేయ", "dattatreya"),
    ("విష్ణు", "vishnu"), ("నారాయణ", "vishnu"), ("హరి", "vishnu"), ("వామన", "vishnu"), ("వరాహ", "vishnu"),
    ("కూర్మ", "vishnu"), ("మత్స్య", "vishnu"), ("దేవి", "durga"),
]
WEEKDAY = ["shiva", "hanuman", "ganesha", "vishnu", "lakshmi", "shani", "surya"]

import re as _re

EN_RULES = [  # English title keywords, first match wins (the English title names the story's main deity most reliably)
    ("narasimha", "narasimha"), ("kurma", "kurma"), ("varaha", "varaha"), ("dattatreya", "dattatreya"),
    ("venkateswara", "venkateswara"), ("annapurna", "annapurna"), ("ayyappa", "ayyappa"), ("kartikeya", "murugan"),
    ("hanuman", "hanuman"), ("ganesha", "ganesha"), ("lakshmi", "lakshmi"), ("deepavali", "lakshmi"),
    ("savitri", "lakshmi"), ("krishna", "krishna"), ("kaliya", "krishna"), ("rukmini", "krishna"), ("sudama", "krishna"),
    ("draupadi", "krishna"), ("rama", "rama"), ("shabari", "rama"), ("jatayu", "rama"), ("ahalya", "rama"),
    ("vibhishana", "rama"), ("saraswati", "saraswati"), ("gayatri", "surya"), ("surya", "surya"), ("shani", "shani"),
    ("parvati", "parvati"), ("kedara gauri", "parvati"), ("durga", "durga"), ("devi", "durga"), ("goddess", "durga"),
    ("kali", "durga"), ("lalita", "durga"), ("chamunda", "durga"), ("shami", "durga"), ("shiva", "shiva"),
    ("shivaratri", "shiva"), ("pradosham", "shiva"), ("kannappa", "shiva"), ("lingodbhava", "shiva"),
    ("kamadahana", "shiva"), ("atmalinga", "shiva"), ("tripura", "shiva"), ("somnath", "shiva"), ("bhairava", "shiva"),
    ("bhagiratha", "shiva"), ("markandeya", "shiva"), ("meenakshi", "shiva"), ("vishnu", "vishnu"), ("hayagriva", "vishnu"),
    ("ekadashi", "vishnu"), ("gajendra", "vishnu"), ("vamana", "vishnu"), ("matsya", "vishnu"), ("tulasi", "vishnu"),
]


def god_for_title_en(title_en: str) -> str | None:
    t = (title_en or "").lower()
    for word, god in EN_RULES:
        if _re.search(r"\b" + _re.escape(word), t):
            return god
    return None


def pick(god: str, day: dt.date) -> Path | None:
    files = [DEITIES / f"{n}.jpg" for n in PHOTOS.get(god, []) if (DEITIES / f"{n}.jpg").exists()]
    return files[day.toordinal() % len(files)] if files else None


def god_for_text(*texts: str) -> str | None:
    for text in texts:
        for word, god in KEYWORDS:
            if word in (text or ""):
                return god
    return None


def photo_for_rashi(rashi_index: int, day: dt.date) -> Path | None:
    return pick(RASHI_GOD[rashi_index % 12], day)


def photo_for_story(day: dt.date, *texts: str, title_en: str = "") -> Path | None:
    return pick(god_for_title_en(title_en) or god_for_text(*texts) or WEEKDAY[day.weekday()], day)


def with_photo(base: Image.Image, path: Path | None, mix: float = 0.55, dim: int = 70) -> Image.Image:
    """Photo cover-filled behind the card (tinted by the card's own colour and dimmed so text stays readable);
    returns base unchanged if the photo is missing."""
    if path is None:
        return base
    try:
        with Image.open(path) as raw:
            src = raw.convert("RGB")
    except OSError:
        return base
    w, h = base.size
    if src.width > src.height:  # landscape scene: blurred cover fill plus the sharp scene fitted to the width
        back = ImageOps.fit(src, (w, h), method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(30))
        if src.width / src.height < 2.2:  # single-subject scene: crop to the centre so the deity fills the width
            cx, cw = src.width // 2, int(src.width * 0.62)
            src = src.crop((cx - cw // 2, 0, cx + cw // 2, src.height))
        fg = src.resize((w, int(src.height * w / src.width)), Image.Resampling.LANCZOS)
        fm = Image.new("L", fg.size, 255)
        fd = ImageDraw.Draw(fm)
        for i in range(40):
            fd.line((0, i, w, i), fill=int(255 * i / 40))
            fd.line((0, fg.height - 1 - i, w, fg.height - 1 - i), fill=int(255 * i / 40))
        back.paste(fg, (0, int(h * 0.40 - fg.height / 2)), fm)
        photo = back
    else:
        photo = None
    photo = photo if photo is not None else ImageOps.fit(src, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.3)).filter(ImageFilter.GaussianBlur(3))
    tinted = Image.blend(photo.convert("RGBA"), base.convert("RGBA"), mix)
    shade = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(shade)
    for y in range(h):  # a little lighter at the top so the face shows, darker toward the text-heavy lower part
        sd.line((0, y, w, y), fill=int(dim + 90 * (y / h)))
    return Image.composite(Image.new("RGBA", (w, h), (10, 4, 4, 255)), tinted, shade)
