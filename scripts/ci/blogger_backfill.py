"""Post recent public uploads of the main channel to the main Blogger blog, skipping any whose title is already
on the blog. Without --apply it only lists what it would post.

  python scripts/ci/blogger_backfill.py --since 2026-11-06T00:00:00Z [--limit 30] [--apply]"""
from __future__ import annotations

import argparse
import sys
import time

from mahanavi.config import get_settings
from mahanavi.publishers import blogger_publisher as bp
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    st = get_settings()
    if not st.blogger_blog_id:
        print("::error::MAHANAVI_BLOGGER_BLOG_ID is not set")
        return 1
    yt = YouTubeShortsUploader(st)._build_service()  # noqa: SLF001
    up = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = []
    r = yt.playlistItems().list(part="contentDetails", playlistId=up, maxResults=50).execute()
    ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
    vids = []
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,status", id=",".join(ids[k:k + 50])).execute().get("items", []):
            if v["status"]["privacyStatus"] == "public" and v["snippet"]["publishedAt"] >= a.since:
                vids.append(v)
    vids.sort(key=lambda v: v["snippet"]["publishedAt"])
    blog = bp._build_service(st)  # noqa: SLF001
    have, tok = set(), None
    while True:
        r = blog.posts().list(blogId=st.blogger_blog_id, maxResults=50, pageToken=tok, fetchBodies=False, status=["LIVE", "DRAFT"]).execute()
        have |= {p["title"].strip() for p in r.get("items", [])}
        tok = r.get("nextPageToken")
        if not tok or len(have) > 400:
            break
    todo = [v for v in vids if v["snippet"]["title"].strip() not in have][: a.limit]
    print(f"::notice::{len(vids)} public uploads since {a.since}, {len(todo)} not on the blog yet")
    done = 0
    for v in todo:
        sn = v["snippet"]
        print(f"  {v['id']} {sn['publishedAt']} {sn['title'][:70]}")
        if a.apply:
            desc = sn.get("description", "")[:1500]
            ok = bool(bp.post_to_blogger(st, v["id"], sn["title"], desc))
            if not ok:  # Blogger rate limit (429): wait and try once more
                time.sleep(120)
                ok = bool(bp.post_to_blogger(st, v["id"], sn["title"], desc))
            done += ok
            time.sleep(75)
    if a.apply:
        print(f"::notice::posted {done} of {len(todo)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
