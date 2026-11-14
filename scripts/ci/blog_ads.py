#!/usr/bin/env python3
"""Add the AdSense in-article block to LIVE Mahanavi blog posts that have none (PATCH of the content only: nothing is
deleted or re-dated). The ad goes right after the embedded video, so it sits between the video and the description.
Posts with fewer than 60 words of text are skipped (too thin for ads).
  python scripts/ci/blog_ads.py [--apply] [--limit N]"""
import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blog_daily as bd  # noqa: E402
from mahanavi.config import get_settings  # noqa: E402
from mahanavi.publishers import blogger_publisher as bp  # noqa: E402

BLOG = "4824099583660261070"
CLIENT = "ca-pub-7766198162235124"
SLOT = "1048682654"
ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true")
ap.add_argument("--limit", type=int, default=400)
a = ap.parse_args()

svc = bp._build_service(get_settings())  # noqa: SLF001
items, tok = [], None
while True:
    r = svc.posts().list(blogId=BLOG, maxResults=100, pageToken=tok, fetchBodies=True, status=["LIVE"]).execute()
    items += r.get("items", [])
    tok = r.get("nextPageToken")
    if not tok:
        break
block = bd.adsense_block(CLIENT, SLOT)
todo, skipped = [], {"has_ad": 0, "no_video": 0, "thin": 0}
for p in items:
    c = p.get("content", "")
    if "adsbygoogle" in c:
        skipped["has_ad"] += 1
        continue
    m = re.search(r"</iframe>\s*(</p>|</div>)?", c, re.I)
    if not m:
        skipped["no_video"] += 1
        continue
    if len(re.sub(r"<[^>]+>", " ", c).split()) < 60:
        skipped["thin"] += 1
        continue
    todo.append((p, c[: m.end()] + block + c[m.end():]))
print(f"LIVE posts: {len(items)}; to add ad: {len(todo)}; skipped: {skipped}")
if todo:
    print("SAMPLE:", todo[0][0]["title"][:80])
    i = todo[0][1].index("mahanavi-ad")
    print(todo[0][1][max(0, i - 260): i + 140].replace("\n", " "))
done = 0
if a.apply:
    for p, nc in todo[: a.limit]:
        for attempt in range(5):
            try:
                svc.posts().patch(blogId=BLOG, postId=p["id"], body={"content": nc}).execute()
                done += 1
                break
            except Exception as exc:  # noqa: BLE001
                if ("429" in str(exc) or "rateLimit" in str(exc) or "quota" in str(exc).lower()) and attempt < 4:
                    time.sleep(60 * (attempt + 1))
                else:
                    print("::warning::failed", p["id"], str(exc)[:160])
                    break
        time.sleep(2)
print(f"{'PATCHED' if a.apply else 'would patch'}: {done if a.apply else min(len(todo), a.limit)}")
