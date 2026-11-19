#!/usr/bin/env python3
"""Mahanavi blog cleanup (Telugu only). Dry-run unless --apply.
1) English articles from content/blog/posts/*.json (LIVE or SCHEDULED) are reverted to DRAFT (nothing is deleted).
2) The manual in-article AdSense block (div.mahanavi-ad) is removed from the remaining posts (it leaves an empty gap)."""
import argparse
import glob
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mahanavi.config import get_settings  # noqa: E402
from mahanavi.publishers import blogger_publisher as bp  # noqa: E402

BLOG = "4824099583660261070"
ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true")
a = ap.parse_args()
eng = {json.load(open(f))["title"].strip().lower() for f in glob.glob("content/blog/posts/*.json")}
svc = bp._build_service(get_settings())  # noqa: SLF001
items, tok = [], None
while True:
    r = svc.posts().list(blogId=BLOG, maxResults=100, pageToken=tok, fetchBodies=True, status=["LIVE", "SCHEDULED"]).execute()
    items += r.get("items", [])
    tok = r.get("nextPageToken")
    if not tok:
        break
AD = re.compile(r'<div[^>]*class=["\']mahanavi-ad["\'][^>]*>.*?</ins>.*?</script>\s*</div>', re.S | re.I)
to_draft, to_strip = [], []
for p in items:
    if p["title"].strip().lower() in eng:
        to_draft.append(p)
    elif AD.search(p.get("content", "")):
        to_strip.append((p, AD.sub("", p["content"])))
print(f"posts LIVE/SCHEDULED: {len(items)}; English->draft: {len(to_draft)}; strip ad block: {len(to_strip)}")
for p in to_draft:
    print("  DRAFT:", p["status"], p["title"][:70])
for p, _ in to_strip[:5]:
    print("  STRIP:", p["title"][:70])


def retry(fn):
    for i in range(5):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            if ("429" in str(e) or "rateLimit" in str(e) or "quota" in str(e).lower()) and i < 4:
                time.sleep(60 * (i + 1))
            else:
                print("::warning::failed", str(e)[:160])
                return None


if a.apply:
    for p in to_draft:
        retry(lambda p=p: svc.posts().revert(blogId=BLOG, postId=p["id"]).execute())
        time.sleep(2)
    n = 0
    for p, nc in to_strip:
        if retry(lambda p=p, nc=nc: svc.posts().patch(blogId=BLOG, postId=p["id"], body={"content": nc}).execute()):
            n += 1
        time.sleep(2)
    print(f"DONE: drafted {len(to_draft)}, stripped {n}")
