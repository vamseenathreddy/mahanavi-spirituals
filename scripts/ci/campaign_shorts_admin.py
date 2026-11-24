#!/usr/bin/env python3
"""Admin for the campaign Shorts already uploaded: delete some slots of a date and/or refresh descriptions from the plan.

Usage: campaign_shorts_admin.py --date 2026-11-24 [--delete 3,4] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mahanavi.config import get_settings
from mahanavi.content.links import strip_links
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True); ap.add_argument("--delete", default=""); ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--now", default="", help="slot numbers to make public right away")
    ap.add_argument("--at", default="", help="slot=HH:MM IST reschedules, comma separated, e.g. 2=20:00")
    a = ap.parse_args()
    plan = [e for e in json.loads(Path("content/campaign/shorts_plan.json").read_text(encoding="utf-8")) if e["date"] == a.date]
    yt = YouTubeShortsUploader(get_settings())._build_service()  # noqa: SLF001
    got = yt.channels().list(part="snippet,contentDetails", mine=True).execute()["items"][0]
    if "pulse" not in got["snippet"]["title"].lower():
        print("::error::wrong channel"); return 1
    ups = got["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, nxt = {}, None
    for _ in range(3):
        r = yt.playlistItems().list(part="snippet", playlistId=ups, maxResults=50, pageToken=nxt).execute()
        for i in r["items"]:
            ids[i["snippet"]["title"]] = i["snippet"]["resourceId"]["videoId"]
        nxt = r.get("nextPageToken")
        if not nxt:
            break
    dele = {int(x) for x in a.delete.split(",") if x}
    now_slots = {int(x) for x in a.now.split(",") if x}
    at = {int(k): v for k, v in (x.split("=") for x in a.at.split(",") if x)}
    for e in plan:
        slot = int(e["file"].rsplit("_s", 1)[1].split(".")[0]); vid = ids.get(e["title"])
        if not vid:
            print(f"not found: {e['title']}"); continue
        if slot in dele:
            yt.videos().delete(id=vid).execute(); print(f"::notice::deleted #{e['n']} {vid}"); continue
        if slot in now_slots:
            yt.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}).execute()
            print(f"::notice::#{e['n']} public now https://www.youtube.com/shorts/{vid}")
        if slot in at:
            import datetime as dt
            from zoneinfo import ZoneInfo
            h, m = map(int, at[slot].split(":"))
            t = dt.datetime.fromisoformat(a.date).replace(hour=h, minute=m, tzinfo=ZoneInfo("Asia/Kolkata")).astimezone(dt.timezone.utc)
            yt.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": "private", "publishAt": t.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                                                           "selfDeclaredMadeForKids": False}}).execute()
            print(f"::notice::#{e['n']} scheduled {at[slot]} IST")
        if a.refresh:
            cur = yt.videos().list(part="snippet", id=vid).execute()["items"][0]["snippet"]
            cur["description"] = strip_links(e["description"]); cur["tags"] = e["tags"]
            yt.videos().update(part="snippet", body={"id": vid, "snippet": {k: cur[k] for k in ("title", "description", "tags", "categoryId")}}).execute()
            print(f"::notice::refreshed #{e['n']} {vid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
