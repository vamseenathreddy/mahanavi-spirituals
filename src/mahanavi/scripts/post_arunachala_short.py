"""Ramana Maharshi TV: the "upcoming at Arunachala" Short, 20 days before each event (content/arunachala_events.py).

    python -m mahanavi.scripts.post_arunachala_short --dry-run --date 2026-11-04
    STATE_FILE=data/ramana_arunachala_state.json POST_SLOT=ramana_arunachala python -m mahanavi.scripts.post_arunachala_short --public
Each event is posted once (its slug goes into state["used_ids"]); the video joins the Arunachala playlist and the main Ramana playlist.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.engine import upload as eng_upload
from mahanavi.config import PROJECT_ROOT, get_settings
from mahanavi.content import arunachala_events as ev
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
    ap.add_argument("--event", default="", help="force an event slug (testing)")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    try:
        st = state_mod.load()
        if ev.stale(today):
            print("::warning::arunachala_events.EVENTS ends within 60 days; add the next events", file=sys.stderr)
        event = next((e for e in ev.EVENTS if e.slug == args.event), None) if args.event else ev.due(today, st["used_ids"])
        if event is None:
            print("no Arunachala event is 20 days away: no post")
            return 0
        spec = ev.build(event, today)
        print(f"{today} -> {spec.slug}: {spec.title}")
        out_dir = settings.output_dir / "arunachala" / spec.slug
        slides = RequestCardRenderer(settings).render_all(spec, out_dir)
        music = sorted((PROJECT_ROOT / "ramana" / "assets").glob("om_0*.mp3"))
        if not music:
            raise MahanaviError("Ramana Om music clips missing under ramana/assets")
        video = assemble(spec, [s.path for s in slides], music[today.toordinal() % len(music)], out_dir / f"{spec.slug}.mp4")
        print(f"Assembled: {video} ({spec.total_seconds:.1f}s)")
        if args.dry_run:
            return 0
        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if spec.expected_channel.lower() not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected '{spec.expected_channel}'.")
        arun = eng_upload.find_or_create_playlist(youtube, ev.PLAYLIST_TITLE, ev.PLAYLIST_DESC, "te")
        spec = dataclasses.replace(spec, description_te=(
            f"▶ అరుణాచల విశేషాల ప్లేలిస్ట్: https://www.youtube.com/playlist?list={arun}\n\n{spec.description_te}"))
        privacy = "private" if args.private else "public"
        video_id = upload(youtube, spec, video, privacy)
        print(f"Channel: {got}\nUploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        print(f"::notice::arunachala short uploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        state_mod.mark_posted(st, today.isoformat(), spec.slug, video_id, True, dt.datetime.now(IST).isoformat())
        if event.slug not in st["used_ids"]:
            st["used_ids"].append(event.slug)
        state_mod.save(st)
        for label, pid in (("Arunachala playlist", arun),
                           ("main Ramana playlist", settings.ramana_playlist_id or eng_upload.find_or_create_playlist(
                               youtube, ev.MAIN_PLAYLIST_TITLE, "", "en"))):
            try:
                eng_upload.add_to_playlist(youtube, video_id, pid)
                print(f"Playlist: added to {label}")
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING: could not add to {label}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"::error::arunachala short failed: {str(exc)[:400]}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"::error::arunachala short failed: {type(exc).__name__}: {str(exc)[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
