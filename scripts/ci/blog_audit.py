#!/usr/bin/env python3
"""Read-only audit of the Mahanavi blog: which posts were made by the old IFTTT applet (no labels / no image / no AdSense)."""
import collections
import re

from mahanavi.config import get_settings
from mahanavi.publishers import blogger_publisher as bp

BLOG = "4824099583660261070"
svc = bp._build_service(get_settings())  # noqa: SLF001
items, tok = [], None
while True:
    r = svc.posts().list(blogId=BLOG, maxResults=100, pageToken=tok, fetchBodies=True, status=["LIVE", "SCHEDULED", "DRAFT"]).execute()
    items += r.get("items", [])
    tok = r.get("nextPageToken")
    if not tok:
        break
print(f"TOTAL posts: {len(items)}")
kinds = collections.Counter()
odd = []
for p in items:
    c = p.get("content", "")
    ours = "hqdefault.jpg" in c or "article-body" in c or "mahanavi-ad" in c or "Daily Article" in (p.get("labels") or [])
    feats = dict(img=("<img" in c), labels=bool(p.get("labels")), ad=("adsbygoogle" in c), iframe=("<iframe" in c))
    kinds[("ours" if ours else "other", p["status"], feats["img"], feats["labels"], feats["ad"])] += 1
    if not ours:
        odd.append(p)
for k, v in sorted(kinds.items(), key=lambda x: -x[1]):
    print(v, "(kind, status, img, labels, ad) =", k)
print(f"NOT-OURS (likely IFTTT) posts: {len(odd)}")
for p in odd[:6]:
    print("---", p["id"], p["status"], p["published"][:16], "|", p["title"][:90], "| labels:", p.get("labels"))
    print(re.sub(r"\s+", " ", p.get("content", ""))[:600])
for p in odd[6:60]:
    print("-", p["id"], p["status"], p["published"][:16], p["title"][:70], "| labels:", p.get("labels"))
