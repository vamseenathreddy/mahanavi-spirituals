"""Posts ONE Bhavishya Purana story Short per run (11 total, from the 8-minute text video), in order.

Which story is next is decided from the channel itself: the first story whose Telugu title is not yet in a recent upload
title. So a missed day never skips a story and a re-run never duplicates one. Exit code 3 = all 11 are already posted (or
the start date has not come), so the workflow falls back to the normal Purana rotation.

Video files come from the orphan branch assets-bhavishya-shorts (build/bhavishya_shorts/sNN.mp4).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from channels import playlist_links
from mahanavi.config import get_settings
from mahanavi.content.alert_seo import ShortSeoContent
from mahanavi.publishers.blogger_publisher import post_to_blogger
from mahanavi.publishers.recent_titles import is_posted, recent_titles
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader

START_DATE = "2026-11-16"
VIDEO_DIR = Path("build") / "bhavishya_shorts"
TEXT = json.loads((Path(__file__).resolve().parents[3] / "content" / "bhavishya" / "story_text.json").read_text(encoding="utf-8"))

STORIES = [  # (Telugu title, English title)
    ("కళావిదుడి ఐదు రత్నాలు", "Kalavidu's Five Jewels"),
    ("రథసప్తమి", "Ratha Saptami"),
    ("పంచ మహాయజ్ఞాలు", "The Five Maha Yajnas"),
    ("పిప్పలాద మహర్షి", "Pippalada Maharshi"),
    ("రూపసేనుడు, వీరవరుడు", "Roopasena and Veeravara"),
    ("తల్లి, తండ్రి, గురువు", "Mother, Father and Guru"),
    ("దాన విధి", "The Rules of Giving"),
    ("గుణాకరుడి సాధన", "Gunakara's Sadhana"),
    ("ఉద్యానవనాలు, చెరువులు", "Gardens and Ponds"),
    ("కర్మ, మూడు మార్గాలు", "Karma and the Three Paths"),
    ("అక్షయ తృతీయ, అన్నదానం", "Akshaya Tritiya and Annadanam"),
]


def build_seo(i: int) -> ShortSeoContent:
    te, en = STORIES[i]
    take = TEXT["stories"][i]["take"].replace("\n", " ").strip()
    title = f"{te} | Bhavishya Purana Story {i + 1} | భవిష్య పురాణం"
    desc = (
        f"భవిష్య పురాణ కథ {i + 1}/11: {te}. {take}\n\n"
        f"Bhavishya Purana story {i + 1} of 11: {en}. A short life lesson from the Puranas, written in Telugu on screen "
        f"with calm music. No voice, read at your own pace.\n\n"
        "మొత్తం 11 కథలు ఒకే వీడియోలో చూడండి (8 నిమిషాలు): Bhavishya Purana in Telugu, full video on this channel.\n"
        "ప్రతిరోజూ పురాణ కథలు చూడటానికి Mahanavi Spirituals ను Subscribe చేయండి.\n\n"
        "The artwork and music were created with AI-assisted tools. This video contains realistic synthetic visuals.\n\n"
        "Search words: Bhavishya Purana in Telugu, భవిష్య పురాణం, Purana stories in Telugu, life lessons from Puranas, "
        f"{en}, {te}."
    )
    tags = ["#Shorts", "#BhavishyaPurana", "#భవిష్యపురాణం", "#PuranaStories", "#TeluguDevotional",
            "#LifeLessons", "#MahanaviSpirituals"]
    return ShortSeoContent(title=title[:100], description=desc, hashtags=tags)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--story", type=int, default=None, help="force story 1-11 (test; no date gate)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    settings = get_settings()
    today = datetime.now(ZoneInfo(settings.timezone)).date().isoformat()
    uploader = YouTubeShortsUploader(settings)
    if a.story is not None:
        i = a.story - 1
    else:
        if today < START_DATE:
            print(f"Bhavishya Shorts start {START_DATE}; today {today}.")
            return 3
        titles = recent_titles(uploader._build_service())  # noqa: SLF001
        done = [is_posted(titles, f"{te} | Bhavishya Purana Story") for te, _ in STORIES]
        if all(done):
            print("All 11 Bhavishya Shorts are posted.")
            return 3
        i = done.index(False)
    video = VIDEO_DIR / f"s{i:02d}.mp4"
    if not video.exists():
        print(f"FAILED: {video} missing", file=sys.stderr)
        return 1
    seo = build_seo(i)
    print(f"Story {i + 1}: {seo.title}")
    if a.dry_run:
        print(seo.full_caption())
        return 0
    try:
        seo = playlist_links.WithPlaylists(seo, playlist_links.block(uploader._build_service(), settings, "puranas"))  # noqa: SLF001
    except Exception as exc:  # noqa: BLE001
        print(f"Note: playlist links skipped ({type(exc).__name__}).")
    res = uploader.upload(video, seo, privacy_status="public" if a.public else "unlisted")
    if not res.success:
        print(f"Upload FAILED: {res.error_message}", file=sys.stderr)
        return 1
    print(f"Uploaded: {res.post_url}")
    if res.video_id:
        if settings.playlist_id_puranas:
            uploader.add_to_playlist(res.video_id, settings.playlist_id_puranas)
        post_to_blogger(settings, res.video_id, seo.title, seo.full_caption())
    return 0


if __name__ == "__main__":
    sys.exit(main())
