#!/usr/bin/env python3
"""Daily blog article for the Mahanavi Blogger blog (a long story, sloka explainer or a money / home guide), separate
from the per-video blog entries. Articles live in content/blog/posts/NNN.json; this schedules the next ones, one per day.

  python scripts/ci/blog_daily.py --preview out.html [--id 3]     # build one article locally, no API
  python scripts/ci/blog_daily.py --days 7 [--apply]               # schedule the next unpublished articles, 3 a day at random times

AdSense: set MAHANAVI_ADSENSE_CLIENT (ca-pub-...) and MAHANAVI_ADSENSE_SLOT (the in-article ad unit id). One in-article
unit is placed in the middle of the text. Without them the article is built with no ad (a warning is printed)."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "content" / "blog" / "posts"
RAW = "https://raw.githubusercontent.com/vamseenathreddy/mahanavi-spirituals/main/assets/blog/"
IST = ZoneInfo("Asia/Kolkata")
DAILY_LABEL = "Daily Article"
AD_MARK = "<!--mahanavi-ad-slot-->"
PER_DAY = 3
# one random minute inside each window (IST), so posting times differ day to day: morning / afternoon / evening
WINDOWS = [((5, 30), (9, 30)), ((12, 0), (16, 0)), ((18, 30), (22, 30))]


def day_slots(day: dt.date) -> list[dt.datetime]:
    import random
    rng = random.Random(f"mahanavi-blog-{day.isoformat()}")
    out = []
    for (h0, m0), (h1, m1) in WINDOWS[:PER_DAY]:
        lo, hi = h0 * 60 + m0, h1 * 60 + m1
        t = rng.randint(lo, hi)
        out.append(dt.datetime.combine(day, dt.time(t // 60, t % 60), IST))
    return out


def load_posts() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(POSTS.glob("*.json"))]


def _inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s.replace("\n", "<br>")


def adsense_block(client: str, slot: str) -> str:
    if not client or not slot:
        return AD_MARK  # placeholder so the ad can be patched into already scheduled posts later
    return (
        '<div class="mahanavi-ad" style="margin:28px 0;text-align:center;">'
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client}" crossorigin="anonymous"></script>'
        f'<ins class="adsbygoogle" style="display:block;text-align:center;" data-ad-layout="in-article" data-ad-format="fluid" '
        f'data-ad-client="{client}" data-ad-slot="{slot}"></ins>'
        "<script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>"
    )


def build_html(post: dict, client: str = "", slot: str = "", blog_url: str = "") -> str:
    secs = post["sections"]
    mid = max(0, (len(secs) + 1) // 2 - 1)  # ad goes after this section, i.e. in the middle of the text
    out = [f'<div class="mahanavi-article">']
    out.append(f'<p><img src="{RAW}{post["hero"]}" alt="{html.escape(post["alt"], quote=True)}" style="width:100%;max-width:900px;height:auto;border-radius:10px;"/></p>')
    out.append(f"<p>{_inline(post['intro'])}</p>")
    for i, s in enumerate(secs):
        out.append(f"<h2>{html.escape(s['h'])}</h2>")
        for para in s["p"]:
            out.append(f"<p>{_inline(para)}</p>")
        if i == mid:
            out.append(adsense_block(client, slot))
    if post.get("video"):
        out.append(f'<h2>Watch the video</h2><p><iframe width="560" height="315" src="https://www.youtube.com/embed/{post["video"]}" '
                   'title="YouTube video" frameborder="0" allowfullscreen style="max-width:100%"></iframe></p>')
    if post.get("faq"):
        out.append("<h2>Frequently asked questions</h2>")
        for f in post["faq"]:
            out.append(f"<h3>{html.escape(f['q'])}</h3><p>{_inline(f['a'])}</p>")
    if post.get("disclaimer"):
        out.append(f'<p><i>{_inline(post["disclaimer"])}</i></p>')
    if blog_url:
        from urllib.parse import quote
        links = " | ".join(f'<a href="{blog_url.rstrip("/")}/search/label/{quote(l)}">More: {html.escape(l)}</a>' for l in post["labels"])
        out.append(f"<p><b>Related reading:</b> {links} | <a href=\"{blog_url}\">All articles</a></p>")
    out.append("<p>Daily Telugu devotional videos and Shorts are on the Mahanavi Spirituals YouTube channel. Subscribe so you do not miss the next one.</p></div>")
    return "\n".join(x for x in out if x)


def _service():
    from mahanavi.config import get_settings
    from mahanavi.publishers import blogger_publisher as bp
    st = get_settings()
    return st, bp._build_service(st)  # noqa: SLF001


def existing(blog, blog_id: str) -> tuple[set[str], list[dt.datetime]]:
    titles, dates, tok = set(), [], None
    while True:
        r = blog.posts().list(blogId=blog_id, maxResults=50, pageToken=tok, fetchBodies=False, fetchImages=False,
                              status=["LIVE", "DRAFT", "SCHEDULED"]).execute()
        for p in r.get("items", []):
            titles.add(p["title"])
            if DAILY_LABEL in (p.get("labels") or []):
                dates.append(dt.datetime.fromisoformat(p["published"]).astimezone(IST))
        tok = r.get("nextPageToken")
        if not tok:
            return titles, dates


def patch_ads(blog, blog_id: str, block: str, apply: bool) -> int:
    """Put the AdSense block into already scheduled/live daily articles that still carry the placeholder comment."""
    n, tok = 0, None
    while True:
        r = blog.posts().list(blogId=blog_id, maxResults=50, pageToken=tok, fetchBodies=True, fetchImages=False,
                              status=["LIVE", "SCHEDULED"]).execute()
        for p in r.get("items", []):
            if AD_MARK in p.get("content", ""):
                n += 1
                print(("patching" if apply else "would patch"), p["title"])
                if apply:
                    blog.posts().patch(blogId=blog_id, postId=p["id"], body={"content": p["content"].replace(AD_MARK, block)}).execute()
                    time.sleep(3)
        tok = r.get("nextPageToken")
        if not tok:
            break
    print(f"{n} post(s) {'patched' if apply else 'need the ad block'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch-ads", action="store_true")
    ap.add_argument("--preview")
    ap.add_argument("--id", type=int)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    client = os.environ.get("MAHANAVI_ADSENSE_CLIENT", "").strip() or "ca-pub-7766198162235124"  # publisher id is public (it is in every page that shows ads)
    slot = os.environ.get("MAHANAVI_ADSENSE_SLOT", "").strip() or "1048682654"
    if a.patch_ads:
        st, blog = _service()
        return patch_ads(blog, st.blogger_blog_id, adsense_block(client, slot), a.apply)
    posts = load_posts()
    if a.preview:
        p = next(x for x in posts if x["id"] == (a.id or posts[0]["id"]))
        body = build_html(p, client or "ca-pub-XXXXXXXXXXXXXXXX", slot or "0000000000")
        Path(a.preview).write_text(f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                                   f'<body style="max-width:760px;margin:20px auto;font-family:sans-serif;line-height:1.7;padding:0 14px">'
                                   f'<h1>{html.escape(p["title"])}</h1>{body}</body>', encoding="utf-8")
        print("wrote", a.preview)
        return 0
    if not (client and slot):
        print("::warning::MAHANAVI_ADSENSE_CLIENT / MAHANAVI_ADSENSE_SLOT not set: articles are built WITHOUT an ad block")
    st, blog = _service()
    if not st.blogger_blog_id:
        print("::error::MAHANAVI_BLOGGER_BLOG_ID is not set")
        return 1
    titles, dates = existing(blog, st.blogger_blog_id)
    try:
        blog_url = blog.blogs().get(blogId=st.blogger_blog_id).execute().get("url", "")
    except Exception:
        blog_url = ""
    now = dt.datetime.now(IST)
    taken = {d.replace(second=0, microsecond=0) for d in dates}
    horizon = (now + dt.timedelta(days=a.days)).date()
    todo = [p for p in posts if p["title"] not in titles]
    made, day = 0, now.date()
    while todo and day <= horizon:
        for slot_t in day_slots(day):
            if not todo:
                break
            if slot_t <= now + dt.timedelta(minutes=20) or slot_t in taken or sum(1 for d in taken if d.date() == day) >= PER_DAY:
                continue
            p = todo.pop(0)
            when = slot_t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"{'POST' if a.apply else 'would post'} #{p['id']} {slot_t:%Y-%m-%d %H:%M} IST {p['title'][:60]}")
            if a.apply:
                body = {"title": p["title"], "content": build_html(p, client, slot, blog_url), "published": when,
                        "labels": [DAILY_LABEL] + p["labels"]}
                ok = False
                for attempt in range(4):
                    try:
                        blog.posts().insert(blogId=st.blogger_blog_id, body=body).execute()
                        ok = True
                        break
                    except Exception as e:  # noqa: BLE001
                        if "429" in str(e) or "rateLimit" in str(e):
                            print(f"::warning::Blogger rate limit, waiting {60 * (attempt + 1)}s")
                            time.sleep(60 * (attempt + 1))
                        else:
                            raise
                if not ok:
                    print("::warning::Blogger quota still exhausted: stopping, the next run continues")
                    return 0
                time.sleep(8)
            taken.add(slot_t); made += 1
        day += dt.timedelta(days=1)
    print(f"::notice::{made} article(s) {'scheduled' if a.apply else 'listed'}; {len(todo)} still waiting in the bank")
    if len(todo) < PER_DAY * 7:
        print(f"::warning::only {len(todo)} unscheduled articles left in the bank: add more content/blog/posts/NNN.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
