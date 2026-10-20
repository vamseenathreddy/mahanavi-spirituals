"""Song-clip Shorts: a sung line (9-14.5 s, cut from the owner's own full songs by scripts/slice_song_clips.py)
over a deity card. One Short per day; the clip rotates through every song so neighbouring days differ.
Clips live in assets/songs/<slug>/<slug>_NN.mp3 with a manifest.json beside them."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from mahanavi.config import PROJECT_ROOT
from mahanavi.content.alert_seo import _CHANNEL_FOOTER_EN, _CHANNEL_FOOTER_TE
from mahanavi.content.request_shorts import RequestShort, Slide

SONGS_DIR = PROJECT_ROOT / "assets" / "songs"
_SUB = "ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు"
_PLAYLIST_LINE = "పూర్తి పాట మా ఛానల్‌లో ఉంది, డిస్క్రిప్షన్ చూడండి"

_WARM = ((92, 28, 12), (62, 18, 8), (30, 8, 4), (214, 150, 40))
_SAFFRON = ((120, 52, 8), (80, 32, 6), (36, 14, 3), (230, 160, 40))
_BLUE = ((22, 36, 84), (14, 24, 60), (6, 10, 28), (120, 150, 230))


@dataclass(frozen=True)
class Song:
    slug: str
    te: str
    en: str
    key: str                 # English tag word
    image: str               # file under assets/images/
    palette: tuple


SONGS: tuple[Song, ...] = (
    Song("ayyappa_bhajan", "అయ్యప్ప భజన", "Ayyappa Bhajan", "ayyappa", "deities/ayyappa_n1.jpg", _BLUE),
    Song("shivoham_chant", "శివోహం", "Shivoham Chant", "shiva", "deities/shiva_n1.jpg", _BLUE),
    Song("kaalabhairava_ashtakam", "శ్రీ కాలభైరవ అష్టకం", "Kaalabhairava Ashtakam", "kalabhairava", "deities/shiva_n2.jpg", _WARM),
    Song("subrahmanya_ashtakam", "శ్రీ సుబ్రహ్మణ్య అష్టకం", "Subrahmanya Ashtakam", "subrahmanya", "deities/murugan_g1.jpg", _SAFFRON),
    Song("panchamukha_hanuman_kavacham", "పంచముఖ ఆంజనేయ కవచం", "Panchamukha Hanuman Kavacham", "hanuman", "deities/hanuman_g1.jpg", _SAFFRON),
    Song("chandrashekhara_ashtakam", "శ్రీ చంద్రశేఖర అష్టకం", "Chandrashekhara Ashtakam", "shiva", "deities/shiva_n3.jpg", _BLUE),
    Song("jogulamba_ashtakam", "శ్రీ జోగులాంబ అష్టకం", "Sri Jogulamba Ashtakam", "jogulamba", "deities/durga_g1.jpg", _WARM),
    Song("dhanvantari_mantra", "ధన్వంతరి మంత్రం", "Dhanvantari Mantra", "dhanvantari", "deities/vishnu_g1.jpg", _SAFFRON),
    Song("dayananda_saraswati", "శ్రీ దయానంద సరస్వతి కృతి", "Sri Dayananda Saraswati Composition", "shiva", "deities/shiva_n4.jpg", _BLUE),
    Song("divine_musical_experience", "దివ్య సంగీత అనుభవం", "A Divine Musical Experience", "devotional", "deities/shivafamily_n1.jpg", _WARM),
)


def clips_for(song: Song) -> list[tuple[Path, float]]:
    manifest = SONGS_DIR / song.slug / "manifest.json"
    if not manifest.exists():
        return []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return [(manifest.parent / c["file"], float(c["seconds"])) for c in data["clips"]]


def pick(d: date, offset: int = 0) -> tuple[Song, Path, float, int]:
    """Day n -> song n % 10, and that song's clip (n // 10) % its clip count: every clip is used before any repeats."""
    n = d.toordinal() + offset
    song = SONGS[n % len(SONGS)]
    clips = clips_for(song)
    if not clips:
        raise FileNotFoundError(f"no clips for {song.slug}; run scripts/slice_song_clips.py")
    idx = (n // len(SONGS)) % len(clips)
    path, secs = clips[idx]
    return song, path, secs, idx + 1


def build(d: date, offset: int = 0) -> tuple[RequestShort, Path]:
    song, clip, secs, number = pick(d, offset)
    title = f"{song.te} | భక్తి గీతం | {song.en} #Shorts"
    desc_te = (f"🙏 {song.te}\nమా ఛానల్ పాట నుంచి ఒక భాగం (భాగం {number}).\n"
               "పూర్తి పాటను ఛానల్‌లో వినండి, ఇష్టమైతే లైక్ చేసి మీ కుటుంబంతో షేర్ చేయండి.")
    desc_en = (f"{song.en}: a short clip from our own devotional song (part {number}). "
               "Listen to the full song on the channel, like it and share it with your family.")
    hashtags = ["#Shorts", "#Devotional", "#TeluguDevotional", f"#{song.key.title()}", "#Bhajan"]
    tags = [song.te, song.en.lower(), f"{song.key} song", f"{song.key} bhajan", "telugu devotional songs",
            "devotional shorts", "bhakti songs", "mahanavi spirituals", "shorts"]
    spec = RequestShort(
        slug=f"song_{song.slug}_{number:02d}", handle="", comment_id="", deity_te=song.te,
        bg_top=song.palette[0], bg_mid=song.palette[1], bg_bottom=song.palette[2], glow=song.palette[3],
        slides=(Slide("mantra", secs, "భక్తి గీతం", song.te, song.en, ""),),
        title=title[:100], title_en=f"{song.en} | Telugu Devotional Song #Shorts",
        description_te=desc_te, description_en=desc_en, hashtags=hashtags, tags=tags,
        header="మహానవి స్పిరిచువల్స్", tag_footer=_SUB, cta_lines=(_SUB,), playlist_line="",
        footer_main=_CHANNEL_FOOTER_TE, footer_en=_CHANNEL_FOOTER_EN, bg_image=song.image,
    )
    return spec, clip
