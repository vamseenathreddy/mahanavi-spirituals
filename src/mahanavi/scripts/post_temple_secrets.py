"""Mahanavi "Temple Secrets" weekly Short (content/temple_secrets.py).

    python -m mahanavi.scripts.post_temple_secrets --dry-run [--temple tirumala]
    STATE_FILE=data/mahanavi_temple_secrets_state.json POST_SLOT=temple_secrets python -m mahanavi.scripts.post_temple_secrets --public
One temple per run, in list order; the slug goes into state["used_ids"] so it never repeats.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.engine import upload as eng_upload
from mahanavi.config import get_settings
from mahanavi.content import temple_secrets as ts
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
    ap.add_argument("--temple", default="", help="force a temple slug (testing)")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    try:
        st = state_mod.load()
        temple = next((t for t in ts.TEMPLES if t.slug == args.temple), None) if args.temple else ts.used_and_next(st["used_ids"])
        if temple is None:
            print("::error::Temple Secrets list is used up: add more temples to content/temple_secrets.py")
            return 1
        if ts.left(st["used_ids"]) <= ts.LOW_STOCK:
            print(f"::warning::only {ts.left(st['used_ids'])} temple(s) left in the Temple Secrets list, add more")
        spec = ts.build(temple, today)
        print(f"{today} -> {spec.slug}: {spec.title}")
        out_dir = settings.output_dir / "temple_secrets" / spec.slug
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
        pid = eng_upload.find_or_create_playlist(youtube, ts.PLAYLIST_TITLE, ts.PLAYLIST_DESC, "te")
        spec = dataclasses.replace(spec, description_te=(
            f"▶ దేవాలయ రహస్యాల ప్లేలిస్ట్: https://www.youtube.com/playlist?list={pid}\n\n{spec.description_te}"))
        privacy = "private" if args.private else "public"
        video_id = upload(youtube, spec, video, privacy)
        print(f"Channel: {got}\nUploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        print(f"::notice::temple secrets short uploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        state_mod.mark_posted(st, today.isoformat(), spec.slug, video_id, True, dt.datetime.now(IST).isoformat())
        if temple.slug not in st["used_ids"]:
            st["used_ids"].append(temple.slug)
        state_mod.save(st)
        try:
            eng_upload.add_to_playlist(youtube, video_id, pid)
            print("Playlist: added")
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: could not add to the playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"::error::temple secrets short failed: {str(exc)[:400]}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"::error::temple secrets short failed: {type(exc).__name__}: {str(exc)[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
