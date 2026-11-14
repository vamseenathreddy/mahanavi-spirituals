#!/usr/bin/env python3
"""Repair posts made by the old IFTTT applet, IN PLACE (PATCH only: nothing is deleted, unpublished or re-dated):
  1. broken thumbnail (IFTTT left the literal text ***Url?split('v=')[1]*** in the image link) -> real YouTube thumbnail
  2. the same 11 unrelated labels on every post (Ayyappa Devotional, Holi, Dewali ...) -> topic labels from the title
Posts whose image is fine and labels are already specific are left alone.
  python scripts/ci/blog_repair.py [--apply] [--limit N]"""
import argparse
import html
import re
import time

from mahanavi.config import get_settings
from mahanavi.publishers import blogger_publisher as bp
from mahanavi.publishers.blog_labels import labels_for

BLOG = "4824099583660261070"
GENERIC = {"Ayyappa Devotional", "Bhakti", "Devotional Lyrics", "Dewali", "Holi", "Karthika Maasam", "Sankranti", "Telugu Songs",
           "Videos", "Vinayaka", "YouTube"}
# IFTTT left an unresolved template (the log shows it as ***Url?split('v=')[1]***) in the image link, whatever the brackets are
BROKEN = re.compile(r"https://i\.ytimg\.com/vi_webp/[^\"\s]*split\('v='\)[^\"\s]*?/maxresdefault\.webp")
VID = re.compile(r"youtube(?:-nocookie)?\.com/(?:watch\?v=|embed/)([A-Za-z0-9_-]{11})")

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
todo, words = [], []
for p in items:
    c = p.get("content", "")
    labels = set(p.get("labels") or [])
    fix_img = bool(BROKEN.search(c))
    fix_lab = labels == GENERIC or (labels and labels <= GENERIC and len(labels) >= 8)
    if not (fix_img or fix_lab):
        continue
    m = VID.search(c)
    vid = m.group(1) if m else None
    new_c = c
    if fix_img:
        if not vid:
            fix_img = False
        else:
            new_c = BROKEN.sub(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", c)
    new_labels = labels_for(html.unescape(p["title"])) if fix_lab else None
    if not (fix_img or fix_lab):
        continue
    words.append(len(re.sub(r"<[^>]+>", " ", c).split()))
    todo.append((p, new_c if fix_img else None, new_labels))
print(f"LIVE posts: {len(items)}; to repair: {len(todo)} (broken image: {sum(1 for t in todo if t[1])}, generic labels: {sum(1 for t in todo if t[2])})")
if words:
    words.sort()
    print(f"text words per post (min/median/max): {words[0]}/{words[len(words)//2]}/{words[-1]}")
if todo:
    p, nc, nl = todo[0]
    print("SAMPLE:", p["title"][:80], "| new labels:", nl)
    print("BEFORE:", re.sub(r"\s+", " ", p["content"])[:1500])
    if nc:
        print("AFTER img:", re.search(r'<img src="([^"]+)"', nc).group(1))
done = 0
for p, nc, nl in todo[: a.limit]:
    body = {}
    if nc:
        body["content"] = nc
    if nl is not None:
        body["labels"] = nl
    if not a.apply:
        continue
    for attempt in range(5):
        try:
            svc.posts().patch(blogId=BLOG, postId=p["id"], body=body).execute()
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
