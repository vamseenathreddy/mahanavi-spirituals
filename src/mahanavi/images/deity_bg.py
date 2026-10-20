"""Deity photo behind Telugu cards, matched to the mantra / story (owner request 2026-10-20). Photos live in
assets/images/deities and rotate by date. Rashi uses the ruling planet's god, Purana the god the story is about."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

DEITIES = Path(__file__).resolve().parents[3] / "assets" / "images" / "deities"
PHOTOS = {
    "ayyappa": ['ayyappa_n1', 'ayyappa_n2', 'ayyappa_n3'],
    "annapurna": ['annapurna_n1', 'annapurna_n2'],
    "gita": ['gita_n1', 'gita_n2', 'gita_n3', 'gita_n4', 'gita_n5', 'gita_n6', 'gita_n7', 'gita_n8', 'gita_n9', 'gita_n10'],

    "shiva": ["shiva_g1", "shiva_g2", "shivafamily_n1", "shivafamily_n2"], "hanuman": ["hanuman_g1", "hanuman_g2"], "ganesha": ["ganesha_g1", "ganesha_g2"],
    "vishnu": ["vishnu_g1", "vishnu_g3", "vishnu_g5", "vishnu_g2"], "lakshmi": ["lakshmi_g1", "lakshmi_g2"],
    "shani": ["shani_g1", "shani_g3", "shani_g5"], "surya": ["surya_g2"], "durga": ["durga_g1", "durga_g2", "durga_n1", "durga_n2", "durga_n3", "durga_n4", "durga_n5", "durga_n6", "durga_n7", "durga_n8", "durga_n9", "durga_n10"],
    "krishna": ["krishna_g1", "krishna_n1", "krishna_n2", "krishna_n3", "krishna_n4", "krishna_n5", "krishna_n6", "krishna_n7", "krishna_n8", "krishna_n9", "krishna_n10"], "rama": ["rama_g1", "rama_g2", "rama_n1", "rama_n2", "rama_n3", "rama_n4", "rama_n5", "rama_n6", "rama_n7", "rama_n8", "rama_n9", "rama_n10"], "narasimha": ["narasimha_g1", "narasimha_g2", "narasimha_n1", "narasimha_n2", "narasimha_n3"],
    "saraswati": ["saraswati_g2", "saraswati_n1", "saraswati_n2", "saraswati_n3", "saraswati_n4", "saraswati_n5", "saraswati_n6", "saraswati_n7", "saraswati_n8", "saraswati_n9", "saraswati_n10"], "murugan": ["murugan_g1", "murugan_g2"], "parvati": ["parvati_g2"],
    "dattatreya": ["dattatreya_g1", "dattatreya_g3", "dattatreya_g5"], "venkateswara": ["venkateswara_g1"],
}
# Mesha, Vrishabha, Mithuna, Karka, Simha, Kanya, Tula, Vrischika, Dhanus, Makara, Kumbha, Meena
RASHI_GOD = ["hanuman", "lakshmi", "vishnu", "shiva", "surya", "vishnu", "lakshmi", "hanuman", "dattatreya", "shani",
             "shani", "dattatreya"]
KEYWORDS = [
    ("అయ్యప్ప", "ayyappa"), ("అన్నపూర్ణ", "annapurna"),  # first match wins
    ("నరసింహ", "narasimha"), ("హనుమ", "hanuman"), ("ఆంజనేయ", "hanuman"), ("గణేశ", "ganesha"), ("గణపతి", "ganesha"),
    ("సరస్వతి", "saraswati"), ("లక్ష్మి", "lakshmi"), ("దుర్గ", "durga"), ("పార్వతి", "parvati"),
    ("సుబ్రహ్మణ్య", "murugan"), ("కార్తికేయ", "murugan"), ("కృష్ణ", "krishna"), ("రామ", "rama"), ("శివ", "shiva"),
    ("శని", "shani"), ("సూర్య", "surya"), ("వేంకటేశ్వర", "venkateswara"), ("దత్తాత్రేయ", "dattatreya"),
    ("విష్ణు", "vishnu"), ("నారాయణ", "vishnu"), ("హరి", "vishnu"), ("వామన", "vishnu"), ("వరాహ", "vishnu"),
    ("కూర్మ", "vishnu"), ("మత్స్య", "vishnu"), ("దేవి", "durga"),
]
WEEKDAY = ["shiva", "hanuman", "ganesha", "vishnu", "lakshmi", "shani", "surya"]


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


def photo_for_story(day: dt.date, *texts: str) -> Path | None:
    return pick(god_for_text(*texts) or WEEKDAY[day.weekday()], day)


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
    photo = ImageOps.fit(src, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.3)).filter(ImageFilter.GaussianBlur(3))
    tinted = Image.blend(photo.convert("RGBA"), base.convert("RGBA"), mix)
    shade = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(shade)
    for y in range(h):  # a little lighter at the top so the face shows, darker toward the text-heavy lower part
        sd.line((0, y, w, y), fill=int(dim + 90 * (y / h)))
    return Image.composite(Image.new("RGBA", (w, h), (10, 4, 4, 255)), tinted, shade)
