#!/usr/bin/env python3
"""Move the scheduled Telugu posts (content/sites/mahanavi_te) to given IST times. Usage: --apply 'id=YYYY-MM-DDTHH:MM' ..."""
import argparse, datetime as dt, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import blog_daily as bd  # noqa: E402
ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("slots", nargs="+"); a = ap.parse_args()
st, blog = bd._service()  # noqa: SLF001
bid = os.environ["MAHANAVI_BLOGGER_BLOG_ID"]
posts = {json.loads(p.read_text(encoding="utf-8"))["id"]: json.loads(p.read_text(encoding="utf-8"))["title"] for p in (Path(__file__).resolve().parents[2] / "content/sites/mahanavi_te/posts").glob("*.json")}
want = {int(s.split("=")[0]): dt.datetime.fromisoformat(s.split("=")[1]).replace(tzinfo=bd.IST) for s in a.slots}
tok, items = None, []
while True:
    r = blog.posts().list(blogId=bid, maxResults=50, pageToken=tok, fetchBodies=False, fetchImages=False, status=["LIVE", "SCHEDULED"]).execute()
    items += r.get("items", []); tok = r.get("nextPageToken")
    if not tok: break
byt = {p["title"]: p for p in items}
for i, when in sorted(want.items()):
    p = byt.get(posts[i])
    if not p: print("missing", i); continue
    iso = when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(("SET" if a.apply else "would set"), i, when, p["title"][:40])
    if a.apply: blog.posts().patch(blogId=bid, postId=p["id"], body={"published": iso}).execute()
