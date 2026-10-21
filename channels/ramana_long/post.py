"""Builds (and uploads) the Self-enquiry long video for Ramana Maharshi TV. Private by default (the channel's draft rule);
pass --public after review. One-off: python -m channels.ramana_long.post [--dry-run] [--public] [--fake-voice]."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from channels.ramana_long import metadata, video


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--fake-voice", action="store_true", help="offline layout test: silent narration")
    ap.add_argument("--out", default="out_ramana_long")
    args = ap.parse_args(argv)

    out = Path(args.out)
    info = video.build(out, out / "long.mp4", fake_voice=args.fake_voice)
    video.thumbnail(out / "thumb.png")
    meta = {"title": metadata.title(), "description": metadata.description(info["chapters"]), "tags": metadata.tags(),
            "comment": metadata.comment()}
    (out / "meta.json").write_text(json.dumps({**meta, "render": info}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"::notice title=ramana long::{info['duration']} s | {meta['title']}")
    if args.dry_run:
        return 0

    from googleapiclient.http import MediaFileUpload

    from channels.engine import upload
    from mahanavi.config import get_settings
    from mahanavi.publishers.post_ledger import DuplicatePost

    settings = get_settings()
    yt = upload.service(settings.ramana_youtube_token_file)
    got = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
    if "ramana" not in got.lower():
        raise SystemExit(f"::error::NOT posting: the saved token acts as channel '{got}', not Ramana Maharshi TV.")
    privacy = "public" if args.public else "private"
    try:
        video_id = upload.upload_video(yt, str(out / "long.mp4"), meta["title"], meta["description"], meta["tags"], None,
                                       privacy_status=privacy, language="en", category_id="27")
    except DuplicatePost as dup:
        print(f"::warning::DUPLICATE BLOCKED, nothing uploaded: {dup}")
        return 0
    print(f"UPLOADED ({privacy}) https://www.youtube.com/watch?v={video_id}")
    print(f"::notice title=uploaded::{privacy} https://www.youtube.com/watch?v={video_id}")
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(out / "thumb.png"), mimetype="image/png")).execute()
        print("thumbnail set")
    except Exception as exc:  # noqa: BLE001 - needs a verified channel
        print(f"::warning::thumbnail failed: {str(exc)[:160]}")
    try:
        pl = upload.find_or_create_playlist(yt, metadata.PLAYLIST, "Ramana Maharshi meditation, self-enquiry and teachings.", "en")
        upload.add_to_playlist(yt, video_id, pl)
        print("added to playlist")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::playlist failed: {str(exc)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
