"""
post_chanakya.py: the daily Chanakya Neeti Short, ONE static card with 5 teachings (content/chanakya_neeti.py).
Telugu -> Mahanavi Spirituals, Hindi -> Divine Mantra Sangam. Stateless plan (channels/chanakya_plan.py); the "already posted" marker
is the channel's beej state file under POST_SLOT chanakya / chanakya_hi.

    python -m mahanavi.scripts.post_chanakya --lang te --dry-run --date 2026-11-09
    python -m mahanavi.scripts.post_chanakya --lang hi --public
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

from channels.chanakya_plan import SERIES_START, jitter_seconds, plan
from channels.engine import state as state_mod
from mahanavi.config import get_settings
from mahanavi.content import chanakya_neeti as cn
from mahanavi.content.branding import brand_tags, brand_title
from mahanavi.content.links import strip_links
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.publishers import post_ledger

IST = ZoneInfo("Asia/Kolkata")
CHANNEL_WORD = {"te": "mahanavi", "hi": "mantra sangam"}
PLAYLISTS = {
    "te": ("చాణక్య నీతి | ప్రతిరోజు 5 సూత్రాలు | Chanakya Neeti in Telugu",
           "ప్రతిరోజు చాణక్య నీతి నుంచి 5 సూత్రాలు, ఒకటి కూడా మళ్లీ రాదు.\nFive Chanakya Neeti teachings every day in Telugu, none repeated."),
    "hi": ("चाणक्य नीति | रोज़ 5 सूत्र | Chanakya Neeti in Hindi",
           "हर दिन चाणक्य नीति के 5 सूत्र, कोई दोबारा नहीं आता।\nFive Chanakya Neeti teachings every day in Hindi, none repeated."),
}
DISCLAIMER = {"te": "ఇవి చాణక్య నీతి స్ఫూర్తితో సులభ భాషలో ఇచ్చిన బోధలు.", "hi": "ये चाणक्य नीति की सीख सरल भाषा में हैं।"}


def metadata(lang: str, day: int) -> tuple[str, str, list[str], str, str]:
    lines = cn.card(day, lang)
    n = cn.days()
    if lang == "te":
        title = f"చాణక్య నీతి: నేటి 5 సూత్రాలు (రోజు {day + 1}/{n}) | Chanakya Neeti in Telugu"
        head = f"🙏 చాణక్య నీతి, రోజు {day + 1}/{n}"
        tags_x = ["chanakya neeti telugu", "chanakya niti in telugu", "telugu motivation"]
        hashtags = "#ChanakyaNeeti #చాణక్యనీతి #Telugu #Shorts"
    else:
        title = f"चाणक्य नीति: आज के 5 सूत्र (दिन {day + 1}/{n}) | Chanakya Neeti in Hindi"
        head = f"🙏 चाणक्य नीति, दिन {day + 1}/{n}"
        tags_x = ["chanakya neeti hindi", "chanakya niti in hindi", "hindi motivation"]
        hashtags = "#ChanakyaNeeti #चाणक्यनीति #Hindi #Shorts"
    body = head + "\n\n" + "\n".join(f"{i}. {x}" for i, x in enumerate(lines, 1)) + f"\n\n{DISCLAIMER[lang]}\n\n{hashtags}"
    tags = ["chanakya neeti", "chanakya quotes", "chanakya sutras", "chanakya niti", "life lessons", "motivation", "Shorts"] + tags_x
    title_en = f"Chanakya Neeti: 5 teachings for today (day {day + 1} of {n})"
    desc_en = f"Five Chanakya Neeti teachings every day, none repeated. Day {day + 1} of {n}.\n\n{hashtags}"
    return title, body, tags, title_en, desc_en


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lang", choices=["te", "hi"], required=True)
    ap.add_argument("--public", action="store_true", help="Upload public (default unlisted).")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    day = plan(today)
    if day is None:
        print(f"Nothing to post on {today} (series starts {SERIES_START}, {cn.days()} days).")
        return 0
    try:
        title, desc, tags, title_en, desc_en = metadata(args.lang, day)
        if args.lang == "te":
            title = brand_title(title)
        desc, desc_en = strip_links(desc), strip_links(desc_en)
        print(f"{today} {args.lang} day {day + 1}\nTITLE: {title}\n{desc}\n")
        from mahanavi.video import chanakya_short

        music = None
        if args.lang == "hi":
            from mahanavi.scripts.post_beej_mantra import music_for

            music = music_for("mantra_sangam", today, settings.alert_short_music_path)
        video = chanakya_short.render(args.lang, day, settings.output_dir / "chanakya" / f"chanakya_{args.lang}_{day + 1:03d}.mp4", music)
        print(f"Rendered: {video}")
        if args.dry_run:
            return 0

        from googleapiclient.http import MediaFileUpload

        from mahanavi.publishers.youtube_shorts_uploader import DEFAULT_CATEGORY_ID, YouTubeShortsUploader

        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if CHANNEL_WORD[args.lang] not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected the {CHANNEL_WORD[args.lang]} channel.")
        post_ledger.check(settings.youtube_token_file, title, desc)
        time.sleep(jitter_seconds(args.lang, today))     # day-seeded 0-59 s on top of the random minute
        body = {
            "snippet": {"title": title, "description": desc, "tags": [t for t in brand_tags(tags) if t.isascii()],   # ASCII only: YouTube rejects other scripts in tags
                        "categoryId": DEFAULT_CATEGORY_ID, "defaultLanguage": args.lang, "defaultAudioLanguage": args.lang},
            "status": {"privacyStatus": "public" if args.public else "unlisted", "selfDeclaredMadeForKids": False},
            "localizations": {"en": {"title": title_en[:100], "description": desc_en}},
        }
        media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
        video_id = str(youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media).execute()["id"])
        print(f"Channel: {got}\nUploaded: https://www.youtube.com/watch?v={video_id}")
        post_ledger.record(settings.youtube_token_file, title, desc, video_id)
        state = state_mod.load()
        state_mod.mark_posted(state, today.isoformat(), f"chanakya_{args.lang}_{day + 1}", video_id, True, dt.datetime.now(IST).isoformat())
        state_mod.save(state)
        try:
            from channels.beej import playlists as pl
            from channels.engine import upload

            ptitle, pdesc = PLAYLISTS[args.lang]
            pid = upload.find_or_create_playlist(youtube, ptitle, pdesc, args.lang)
            print(f"Playlist: {'added' if pl.add_once(youtube, video_id, pid) else 'already listed'}")
        except Exception as exc:  # noqa: BLE001  a playlist failure must never lose the upload
            print(f"WARNING: could not add to the Chanakya playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0
    except post_ledger.DuplicatePost as dup:
        print(f"SKIP: {dup}")
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
