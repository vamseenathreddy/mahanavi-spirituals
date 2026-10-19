"""Long Bible-verse video for Jesus Worship Waves (English, US audience). State: data/jesus_state.json, key '<date>#long'
(POST_SLOT=long) and 'long_idx' (the next theme), so no new Drive file is needed."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.jesus_long import bank, metadata, video

IST = ZoneInfo("Asia/Kolkata")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--theme")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--out", default="out_long")
    args = ap.parse_args(argv)

    from mahanavi.config import get_settings

    settings = get_settings()
    now = dt.datetime.now(IST)
    today = dt.date.fromisoformat(args.date) if args.date else now.date()
    st = state_mod.load()
    key = state_mod.slot_key(today.isoformat())
    if key in st["posted"] and not args.dry_run and os.environ.get("FORCE_POST") != "true":
        print(f"Already posted for {key}. Nothing to do.")
        return 0
    idx = int(st.get("long_idx", 0))
    theme_key, theme = (args.theme, bank.load()["themes"][args.theme]) if args.theme else bank.theme_for(idx)
    print(f"{key}: theme {theme_key} ({len(theme['verses'])} verses)")
    out = Path(args.out)
    info = video.build(theme_key, theme, out, out / "long.mp4", seed=today.toordinal())
    video.thumbnail(theme, out / "thumb.png", seed=today.toordinal())
    meta = {"title": metadata.title(theme), "description": metadata.description(theme, info["chapters"]),
            "tags": metadata.tags(theme), "comment": metadata.comment(theme)}
    (out / "meta.json").write_text(json.dumps({**meta, "render": info}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"::notice title=long video::{theme_key}: {info['duration']} s, title: {meta['title']}")
    if args.dry_run:
        return 0

    from googleapiclient.http import MediaFileUpload

    from channels.engine import upload
    from mahanavi.publishers.post_ledger import DuplicatePost

    yt = upload.service(settings.jesus_youtube_token_file)
    got = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
    if "jesus" not in got.lower():
        raise SystemExit(f"::error::NOT posting: the saved token acts as channel '{got}', not Jesus Worship Waves.")
    privacy = "public" if args.public else "unlisted"
    try:
        video_id = upload.upload_video(yt, str(out / "long.mp4"), meta["title"], meta["description"], meta["tags"], None,
                                       privacy_status=privacy, language="en", category_id="22")
    except DuplicatePost as dup:
        print(f"::warning::DUPLICATE BLOCKED, nothing uploaded: {dup}")
        return 0
    print(f"UPLOADED ({privacy}) {video_id}\nWatch: https://www.youtube.com/watch?v={video_id}")
    state_mod.mark_posted(st, today.isoformat(), f"long_{theme_key}", video_id, False, now.isoformat(timespec="seconds"))
    if not args.theme:
        st["long_idx"] = idx + 1
    state_mod.save(st)  # saved before the optional extras so a failure there never causes a second upload
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(out / "thumb.png"), mimetype="image/png")).execute()
        print("thumbnail set")
    except Exception as exc:  # noqa: BLE001 - needs a verified channel
        print(f"::warning::thumbnail failed: {str(exc)[:160]}")
    try:
        pl = upload.find_or_create_playlist(yt, metadata.PLAYLIST, "Bible verses read slowly with soft worship music.", "en")
        upload.add_to_playlist(yt, video_id, pl)
        print("playlist added")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::playlist failed: {exc}")
    try:
        upload.add_comment(yt, video_id, meta["comment"])
        print("comment posted")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::comment failed: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
