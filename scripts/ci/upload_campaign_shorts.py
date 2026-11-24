#!/usr/bin/env python3
"""Upload the Chatrai campaign Shorts planned for one IST date (content/campaign/shorts_plan.json).

Each Short is scheduled for its slot (private + publishAt); a slot already past (or within 10 minutes) goes public now.
Titles already on the channel's recent uploads are skipped, so a re-run never posts a duplicate.
Usage: upload_campaign_shorts.py ASSETS_DIR [--date YYYY-MM-DD] [--only 1,2]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from mahanavi.config import get_settings
from mahanavi.content.links import strip_links
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader

IST = ZoneInfo("Asia/Kolkata")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("assets"); ap.add_argument("--date", default=""); ap.add_argument("--only", default="")
    a = ap.parse_args()
    from googleapiclient.http import MediaFileUpload

    now = dt.datetime.now(IST)
    day = a.date or now.date().isoformat()
    plan = [e for e in json.loads(Path("content/campaign/shorts_plan.json").read_text(encoding="utf-8")) if e["date"] == day]
    if a.only:
        keep = {int(x) for x in a.only.split(",")}
        plan = [e for e in plan if int(e["file"].rsplit("_s", 1)[1].split(".")[0]) in keep]
    if not plan:
        print(f"nothing planned for {day}"); return 0
    yt = YouTubeShortsUploader(get_settings())._build_service()  # noqa: SLF001
    got = yt.channels().list(part="snippet,contentDetails", mine=True).execute()["items"][0]
    if "pulse" not in got["snippet"]["title"].lower():
        print(f"::error::NOT posting: token acts as '{got['snippet']['title']}', expected Pulse"); return 1
    ups = got["contentDetails"]["relatedPlaylists"]["uploads"]
    have = set()
    nxt = None
    for _ in range(3):
        r = yt.playlistItems().list(part="snippet", playlistId=ups, maxResults=50, pageToken=nxt).execute()
        have |= {i["snippet"]["title"] for i in r["items"]}
        nxt = r.get("nextPageToken")
        if not nxt:
            break
    for e in plan:
        if e["title"] in have:
            print(f"skip (already uploaded): {e['title']}"); continue
        h, m = map(int, e["slot"].split(":"))
        at = dt.datetime.fromisoformat(day).replace(hour=h, minute=m, tzinfo=IST)
        status = {"selfDeclaredMadeForKids": False}
        if at > now + dt.timedelta(minutes=10):
            status.update(privacyStatus="private", publishAt=at.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        else:
            status["privacyStatus"] = "public"
        body = {"snippet": {"title": e["title"], "description": strip_links(e["description"]), "tags": e["tags"], "categoryId": "25",
                            "defaultLanguage": "te", "defaultAudioLanguage": "te"},
                "status": status,
                "localizations": {"en": {"title": e["title_en"], "description": strip_links(e["description_en"])}}}
        media = MediaFileUpload(str(Path(a.assets) / e["file"]), mimetype="video/mp4", chunksize=-1, resumable=True)
        vid = yt.videos().insert(part="snippet,status,localizations", body=body, media_body=media).execute()["id"]
        print(f"::notice::#{e['n']} {e['slot']} IST {status['privacyStatus']}: https://www.youtube.com/shorts/{vid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
