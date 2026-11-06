"""Mahanavi: the daily Ramayana story Short (content/ramayana_daily.py), 10 days from 2026-11-06.

    python -m mahanavi.scripts.post_ramayana_short --dry-run --story 1
    STATE_FILE=data/mahanavi_ramayana_state.json POST_SLOT=ramayana python -m mahanavi.scripts.post_ramayana_short --public
Each story is posted once (slug in state["used_ids"]); the video joins the Ramayana Stories playlist.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import sys
import time
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.engine import upload as eng_upload
from mahanavi.config import get_settings
from mahanavi.content import ramayana_daily as rd
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.images.request_card_renderer import RequestCardRenderer
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader
from mahanavi.scripts.post_request_short import assemble, upload

IST = ZoneInfo("Asia/Kolkata")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="")
    ap.add_argument("--story", type=int, default=0, help="force story number 1-10 (testing)")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    try:
        st = state_mod.load()
        story = next((s for s in rd.STORIES if s.n == args.story), None) if args.story else rd.next_story(today, st["used_ids"])
        if story is None:
            print("no Ramayana story due: no post")
            return 0
        spec = rd.build(story)
        print(f"{today} -> {spec.slug}: {spec.title}")
        out_dir = settings.output_dir / "ramayana" / spec.slug
        slides = RequestCardRenderer(settings).render_all(spec, out_dir)
        music = settings.alert_short_music_path
        if music is None or not music.exists():
            raise MahanaviError(f"Music file missing: {music}")
        video = assemble(spec, [s.path for s in slides], music, out_dir / f"{spec.slug}.mp4")
        print(f"Assembled: {video} ({spec.total_seconds:.1f}s)")
        if args.dry_run:
            return 0
        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if spec.expected_channel.lower() not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected '{spec.expected_channel}'.")
        pid = eng_upload.find_or_create_playlist(youtube, rd.PLAYLIST_TITLE, rd.PLAYLIST_DESC, "te")
        spec = dataclasses.replace(spec, description_te=(
            f"▶ రామాయణ కథల ప్లేలిస్ట్: https://www.youtube.com/playlist?list={pid}\n\n{spec.description_te}"))
        privacy = "private" if args.private else "public"
        video_id = upload(youtube, spec, video, privacy)
        print(f"Channel: {got}\nUploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        print(f"::notice::ramayana short uploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        state_mod.mark_posted(st, today.isoformat(), spec.slug, video_id, True, dt.datetime.now(IST).isoformat())
        if story.slug not in st["used_ids"]:
            st["used_ids"].append(story.slug)
        state_mod.save(st)
        for attempt in (1, 2):
            try:
                eng_upload.add_to_playlist(youtube, video_id, pid)
                print("Playlist: added to Ramayana Stories")
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    print(f"WARNING: could not add to playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
                else:
                    time.sleep(20)
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"::error::ramayana short failed: {str(exc)[:400]}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"::error::ramayana short failed: {type(exc).__name__}: {str(exc)[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
