"""
post_calendar_short.py: Mahanavi calendar Shorts (content/calendar_days.py).

    python -m mahanavi.scripts.post_calendar_short --kind tomorrow --dry-run [--date 2026-10-28]
    python -m mahanavi.scripts.post_calendar_short --kind festivals --date 2026-10-28 --dry-run
    POST_SLOT=cal_tomorrow STATE_FILE=data/beej_state.json python -m mahanavi.scripts.post_calendar_short --kind tomorrow --public
--date is "today" (the post covers tomorrow / next month). Uploads unlisted unless --public or --private.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.engine import upload as eng_upload
from channels.calendar.gate import next_month
from mahanavi.config import get_settings
from mahanavi.content import calendar_days as cal
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.images.request_card_renderer import RequestCardRenderer
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader
from mahanavi.scripts.post_request_short import assemble, upload

IST = ZoneInfo("Asia/Kolkata")


def build(kind: str, today: dt.date):
    if cal.stale(today):
        print(f"::warning::calendar_days.FESTIVALS ends {cal.FESTIVALS_END}; add next year's festival dates", file=sys.stderr)
    if kind == "tips":
        return cal.build_tip(today)
    if kind == "tomorrow":
        nxt = cal.next_special(today)
        if nxt is None:
            return None
        return cal.build_tomorrow(*nxt)
    y, m = next_month(today)
    return cal.build_festivals(y, m) if kind == "festivals" else cal.build_vratas(y, m)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kind", required=True, choices=cal.CATEGORIES)
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    try:
        spec = build(args.kind, today)
        if spec is None:
            print("nothing special tomorrow: no post")
            return 0
        print(f"{today} -> {spec.slug}: {spec.title}")
        out_dir = settings.output_dir / "calendar" / spec.slug
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
        top = cal.playlist_block(youtube, args.kind)
        if top:
            spec = dataclasses.replace(spec, description_te=f"{top}\n\n{spec.description_te}")
        privacy = "public" if args.public else ("private" if args.private else "unlisted")
        video_id = upload(youtube, spec, video, privacy)
        print(f"Channel: {got}\nUploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        print(f"::notice::calendar short uploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        state = state_mod.load()
        state_mod.mark_posted(state, today.isoformat(), spec.slug, video_id, True, dt.datetime.now(IST).isoformat())
        state_mod.save(state)
        try:
            pid = cal.playlist_ids(youtube)[args.kind]
            eng_upload.add_to_playlist(youtube, video_id, pid)
            print("Playlist: added")
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: could not add to the playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        print(f"::error::calendar short failed: {str(exc)[:400]}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"::error::calendar short failed: {type(exc).__name__}: {str(exc)[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
