"""Friday video for Pulse Boosting: this week's AP government development actions, dated, scrolling upward.

State: data/trending_state.json (STATE_FILE), key '<date>#weekly' (POST_SLOT=weekly), so no new Drive file is needed."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.weekly_dev import collect, metadata, video

IST = ZoneInfo("Asia/Kolkata")
USED_CAP = 400
SAMPLE = [{"date": "2026-10-19", "headline": "విశాఖలో గూగుల్ ఏఐ హబ్ ఏర్పాటుకు ప్రభుత్వం ఒప్పందం", "publisher": "Eenadu", "link": "x", "key": "a"},
          {"date": "2026-10-21", "headline": "అమరావతి రాజధాని పనులకు కొత్తగా నిధులు మంజూరు", "publisher": "Andhra Jyothy", "link": "x", "key": "b"},
          {"date": "2026-10-22", "headline": "ఐటీ పార్కుకు శంకుస్థాపన చేసిన మంత్రి లోకేశ్", "publisher": "Eenadu", "link": "x", "key": "c"},
          {"date": "2026-10-23", "headline": "కేబినెట్ కీలక నిర్ణయాలు: కొత్త రహదారులకు ఆమోదం", "publisher": "TV9 Telugu", "link": "x", "key": "d"}]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--out", default="out_weekly")
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
    used = set(st.get("weekly_used", []))
    items = SAMPLE if args.sample else collect.collect(today, used)
    print(f"{key}: {len(items)} dated items")
    for it in items:
        print(f"::notice title=week item::{it['date']} | {it['headline'][:100]} | {it['publisher']}")
    if len(items) < collect.MIN_ITEMS:
        print(f"::warning::only {len(items)} usable development stories this week (need {collect.MIN_ITEMS}); no video posted.")
        return 0
    out = Path(args.out)
    info = video.render(items, out / "weekly.mp4", out, music_seed=today.toordinal())
    video.thumbnail(items, out / "thumb.png")
    meta = {"title": metadata.title(items), "description": metadata.description(items), "tags": metadata.tags(items),
            "comment": metadata.comment(items)}
    (out / "meta.json").write_text(json.dumps({**meta, "items": items, "render": info}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Rendered", info, "| title:", meta["title"], f"({len(meta['title'])} chars)")
    if args.dry_run or args.sample:
        return 0

    from googleapiclient.http import MediaFileUpload

    from channels.engine import upload
    from mahanavi.publishers.post_ledger import DuplicatePost

    yt = upload.service(settings.trending_youtube_token_file)
    got = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
    if "pulse" not in got.lower():
        raise SystemExit(f"::error::NOT posting: the saved token acts as channel '{got}', not Pulse Boosting.")
    privacy = "public" if args.public else "unlisted"
    try:
        video_id = upload.upload_video(yt, str(out / "weekly.mp4"), meta["title"], meta["description"], meta["tags"], None,
                                       privacy_status=privacy, language="te", category_id="25")
    except DuplicatePost as dup:
        print(f"::warning::DUPLICATE BLOCKED, nothing uploaded: {dup}")
        return 0
    print(f"UPLOADED ({privacy}) {video_id}\nWatch: https://www.youtube.com/watch?v={video_id}")
    state_mod.mark_posted(st, today.isoformat(), "weekly_dev", video_id, False, now.isoformat(timespec="seconds"))
    st["weekly_used"] = (list(used) + [it["key"] for it in items])[-USED_CAP:]
    state_mod.save(st)  # saved before the optional extras so a failure there never causes a second upload
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(out / "thumb.png"), mimetype="image/png")).execute()
        print("thumbnail set")
    except Exception as exc:  # noqa: BLE001 - needs a verified channel; the video keeps an auto frame otherwise
        print(f"::warning::thumbnail failed: {str(exc)[:160]}")
    try:
        pl = upload.find_or_create_playlist(yt, metadata.PLAYLIST_TITLE, "Every Friday: this week's Andhra Pradesh government development actions, with dates.", "te")
        upload.add_to_playlist(yt, video_id, pl)
        print("playlist added")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::playlist failed: {exc}")
    try:
        upload.add_comment(yt, video_id, meta["comment"])
        print("comment posted")
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::comment failed: {exc}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"video_id={video_id}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
