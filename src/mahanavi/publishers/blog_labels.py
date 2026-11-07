"""Blogger labels for a video post, from its title. They match the category buttons in the blog theme."""
from __future__ import annotations

RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Muhurta", ("రాహు కాలం", "దుర్ముహూర్త", "శుభ ఘడియ", "శుభ సమయం", "ముహూర్త", "rahu", "muhurt", "शुभ", "राहु")),
    ("Mantras", ("మంత్రం", "mantra", "मंत्र")),
    ("Shlokas", ("శ్లోకం", "shloka", "gita", "గీతా", "श्लोक")),
    ("Ramayana", ("రామాయణ", "ramayana")),
    ("Chanakya Neethi", ("చాణక్య", "chanakya")),
    ("Purana Stories", ("purana", "పురాణ", "పురాణం")),
    ("Lakshmi", ("లక్ష్మీ", "lakshmi")),
    ("Festivals & Vratas", ("ప్రదోషం", "శివరాత్రి", "ఏకాదశి", "పండుగ", "వ్రత", "pradosh", "ekadashi", "festival", "vrat")),
    ("Pooja Rules", ("పూజా నియమాలు", "pooja rules", "puja")),
]


def labels_for(title: str) -> list[str]:
    low = title.lower()
    out = [name for name, keys in RULES if any(k.lower() in low for k in keys)]
    return out + ["Shorts"]
