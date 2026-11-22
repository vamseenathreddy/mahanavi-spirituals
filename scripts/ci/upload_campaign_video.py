#!/usr/bin/env python3
"""Upload a finished campaign video (long or Short) with Telugu + English SEO metadata to the channel the token belongs to.

Usage: upload_campaign_video.py VIDEO META.json [--thumb thumb.jpg] [--privacy public] [--short]
Refuses to upload if the token's channel title does not contain meta['expected_channel'].
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from mahanavi.config import get_settings
from mahanavi.content.links import strip_links
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("meta")
    ap.add_argument("--thumb", default=""); ap.add_argument("--privacy", default="public", choices=["private", "unlisted", "public"])
    ap.add_argument("--publish-at", default="", help="RFC3339 time; forces privacy=private until then")
    a = ap.parse_args()
    from googleapiclient.http import MediaFileUpload

    m = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    yt = YouTubeShortsUploader(get_settings())._build_service()  # noqa: SLF001
    got = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
    if m["expected_channel"].lower() not in got.lower():
        print(f"::error::NOT posting: token acts as '{got}', expected '{m['expected_channel']}'")
        return 1
    status = {"privacyStatus": a.privacy, "selfDeclaredMadeForKids": False}
    if a.publish_at:
        status = {"privacyStatus": "private", "publishAt": a.publish_at, "selfDeclaredMadeForKids": False}
    body = {"snippet": {"title": m["title"], "description": strip_links(m["description"]), "tags": m["tags"],
                        "categoryId": m.get("category", "25"), "defaultLanguage": m.get("lang", "te"),
                        "defaultAudioLanguage": m.get("lang", "te")},
            "status": status,
            "localizations": {"en": {"title": m["title_en"], "description": strip_links(m["description_en"])}}}
    media = MediaFileUpload(a.video, mimetype="video/mp4", chunksize=-1, resumable=True)
    vid = yt.videos().insert(part="snippet,status,localizations", body=body, media_body=media).execute()["id"]
    print(f"Channel: {got}\nUploaded ({a.privacy}): https://www.youtube.com/watch?v={vid}")
    if a.thumb and Path(a.thumb).exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumb, mimetype="image/jpeg")).execute()
            print("Thumbnail set")
        except Exception as exc:  # noqa: BLE001
            print(f"::warning::thumbnail not set: {type(exc).__name__}: {str(exc)[:200]}")
    for _ in range(9):
        try:
            st = yt.videos().list(part="processingDetails", id=vid).execute()["items"][0].get("processingDetails", {}).get("processingStatus")
            if st in ("succeeded", "failed", "terminated"):
                print(f"::notice::processing {st}"); break
        except Exception:  # noqa: BLE001
            break
        time.sleep(10)
    print(f"::notice::campaign video uploaded: https://www.youtube.com/watch?v={vid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
