"""
post_lakshmi_name.py: the "Sri Lakshmi Devi 108 Names" Shorts series on Mahanavi Spirituals.

  * one name a day, in order 1..108, from SERIES_START (Fri 6 Nov 2026) to Sun 21 Feb 2027, evening
  * a Friday recap Short (the 7 names of the week before), morning, from Fri 13 Nov 2026

Stateless plan: the name number is (today - SERIES_START) + 1, so no counter can drift or repeat. The "already
posted today" marker lives in data/beej_state_mahanavi.json under POST_SLOT (lakshmi / lakshmi_recap).
The posting minute is day-seeded random inside a window (channels/engine/gate.py) and a day-seeded 0-59 s pause
is added before the upload, so the time is never the same two days running.

Usage:
    python -m mahanavi.scripts.post_lakshmi_name --kind name  --gate        # writes post=true/false for the workflow
    python -m mahanavi.scripts.post_lakshmi_name --kind name  --dry-run --date 2026-11-06
    python -m mahanavi.scripts.post_lakshmi_name --kind recap --dry-run --date 2026-11-13
    python -m mahanavi.scripts.post_lakshmi_name --kind name --public       # real upload
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path

from channels.engine import state as state_mod
from mahanavi.config import get_settings
from mahanavi.content.branding import brand_tags, brand_title
from mahanavi.content.lakshmi108 import NAMES, SOURCES, STOTRA_SOURCE
from mahanavi.content.links import strip_links
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.publishers import post_ledger

from channels.lakshmi108_plan import (FINAL_RECAP, FIRST_RECAP, IST, LAST_DAY, SERIES_START, SLOTS, WINDOWS,  # noqa: F401
                                      gate, jitter_seconds, plan)

PLAYLIST_TITLE = "శ్రీ లక్ష్మీ దేవి 108 నామాలు | వివరణ మరియు అర్థాలు | Lakshmi Devi 108 Names Meaning"
PLAYLIST_DESC = ("శ్రీ లక్ష్మీ అష్టోత్తర శతనామాలు: ప్రతి నామం యొక్క అర్థం, ఆ నామం ఎలా వచ్చిందో కథ లేదా అమ్మవారి రూపం, "
                 "మరియు పురాణ ఆధారం. 1 నుంచి 108 వరకు వరుసగా.\n"
                 "Sri Lakshmi Devi 108 names in order, with the meaning of each name and the story or form behind it, "
                 "with the Purana source where there is one. Start from name 1.")

def metadata(kind: str, first_or_n: int) -> tuple[str, str, list[str], str, str]:
    """(title, description, tags, title_en, description_en); no links anywhere."""
    tags = ["Lakshmi Devi", "Lakshmi 108 names", "Ashtottara Shatanamavali", "Lakshmi Ashtottara", "లక్ష్మీ దేవి",
            "లక్ష్మీ అష్టోత్తర శతనామావళి", "108 నామాలు", "Telugu devotional", "Shorts"]
    tagline = "శ్రీ లక్ష్మీ దేవి 108 నామాలు: ప్రతిరోజు ఒక నామం యొక్క అర్థం. ఇంకా చూడని వారు ప్లేలిస్ట్‌లో 1వ నామం నుంచి చూడండి.\n" \
              "Sri Lakshmi Devi 108 names, one name and its meaning every day. New here? Start from name 1 in our playlist."
    hashtags = "#LakshmiDevi #Lakshmi108Names #లక్ష్మీదేవి #Shorts"
    if kind == "name":
        n = first_or_n
        te, tr, mean, l1, l_en, l2, src = NAMES[n - 1]
        title = f"లక్ష్మీ దేవి 108 నామాలు {n}/108 | {tr} - {mean}"
        title_en = f"Lakshmi Devi 108 Names {n}/108 | {tr}: {mean}"
        srcs = f"{SOURCES[src]}\n" if SOURCES[src] else ""
        body = (f"{n}/108: ఓం {te} నమః\n{tr} = {mean}\n\n{l1}\n{l_en}\n{l2}\n\n{srcs}{STOTRA_SOURCE}\n\n{tagline}\n\n{hashtags}")
        return (title, body, tags + [tr], title_en, body)
    first = first_or_n
    last = min(first + 6, 108)
    rows = "\n".join(f"{n}. {NAMES[n - 1][1]} = {NAMES[n - 1][2]}" for n in range(first, last + 1))
    title = f"ఈ వారం మీరు తెలుసుకున్న లక్ష్మీ నామాలు {first}-{last} | {last}/108"
    title_en = f"Lakshmi Devi names you learned this week: {first} to {last} ({last}/108)"
    body = f"{title_en}\n\n{rows}\n\n{tagline}\n\n{hashtags}"
    return (title, body, tags, title_en, body)


def render_video(kind: str, num: int, out: Path) -> Path:
    from mahanavi.video import lakshmi_name_short as lk

    if kind == "name":
        return lk.render(num, out)
    return lk.render(num, out, layers=lk.recap_layers(num))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", choices=["name", "recap"], required=True)
    ap.add_argument("--gate", action="store_true", help="Only decide whether to post now (writes GITHUB_OUTPUT).")
    ap.add_argument("--now", default="", help="IST time for --gate testing, e.g. 2026-11-06T18:30:00")
    ap.add_argument("--public", action="store_true", help="Upload public (default unlisted).")
    ap.add_argument("--dry-run", action="store_true", help="Render the video and print the metadata; no upload.")
    ap.add_argument("--date", default="", help="ISO date override (testing).")
    args = ap.parse_args(argv)

    if args.gate:
        now = dt.datetime.fromisoformat(args.now).replace(tzinfo=IST) if args.now else dt.datetime.now(IST)
        return gate(args.kind, now)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    num = plan(args.kind, today)
    if num is None:
        print(f"Nothing to post for {args.kind} on {today}.")
        return 0
    try:
        title, desc, tags, title_en, desc_en = metadata(args.kind, num)
        title, desc, desc_en = brand_title(title), strip_links(desc), strip_links(desc_en)
        print(f"{today} {args.kind} #{num}\nTITLE: {title}\n{desc}\n")
        out_dir = settings.output_dir / "lakshmi108"
        video = render_video(args.kind, num, out_dir / f"{args.kind}_{num:03d}.mp4")
        print(f"Rendered: {video}")
        if args.dry_run:
            return 0

        from googleapiclient.http import MediaFileUpload

        from mahanavi.publishers.youtube_shorts_uploader import DEFAULT_CATEGORY_ID, YouTubeShortsUploader

        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if "mahanavi" not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected Mahanavi Spirituals.")
        post_ledger.check(settings.youtube_token_file, title, desc)
        time.sleep(jitter_seconds(args.kind, today))     # day-seeded 0-59 s so the second is never the same either
        body = {
            "snippet": {"title": title, "description": desc, "tags": brand_tags(tags), "categoryId": DEFAULT_CATEGORY_ID,
                        "defaultLanguage": "te", "defaultAudioLanguage": "te"},
            "status": {"privacyStatus": "public" if args.public else "unlisted", "selfDeclaredMadeForKids": False},
            "localizations": {"en": {"title": title_en[:100], "description": desc_en}},
        }
        media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
        video_id = str(youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media).execute()["id"])
        print(f"Channel: {got}\nUploaded: https://www.youtube.com/watch?v={video_id}")
        post_ledger.record(settings.youtube_token_file, title, desc, video_id)
        state = state_mod.load()
        state_mod.mark_posted(state, today.isoformat(), f"lakshmi_{args.kind}_{num}", video_id, True, dt.datetime.now(IST).isoformat())
        state_mod.save(state)
        if args.kind == "name":    # the series playlist (find-or-create, add once); a failure here must never lose the upload
            try:
                from channels.beej import playlists as pl
                from channels.engine import upload

                pid = upload.find_or_create_playlist(youtube, PLAYLIST_TITLE, PLAYLIST_DESC, "te")
                print(f"Playlist: {'added' if pl.add_once(youtube, video_id, pid) else 'already listed'}")
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING: could not add to the Lakshmi playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
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
