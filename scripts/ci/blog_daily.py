#!/usr/bin/env python3
"""Daily blog article for the Mahanavi Blogger blog (a long story, sloka explainer or a money / home guide), separate
from the per-video blog entries. Articles live in data/blog/posts/NNN.json; this schedules the next ones, one per day.

  python scripts/ci/blog_daily.py --preview out.html [--id 3]     # build one article locally, no API
  python scripts/ci/blog_daily.py --days 7 [--apply]               # schedule the next unpublished articles (07:00 IST each day)

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
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "data" / "blog" / "posts"
RAW = "https://raw.githubusercontent.com/vamseenathreddy/mahanavi-spirituals/main/assets/blog/"
IST = ZoneInfo("Asia/Kolkata")
DAILY_LABEL = "Daily Article"
HOUR_IST = 7


def load_posts() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(POSTS.glob("*.json"))]


def _inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s.replace("\n", "<br>")


def adsense_block(client: str, slot: str) -> str:
    if not client or not slot:
        return ""
    return (
        '<div class="mahanavi-ad" style="margin:28px 0;text-align:center;">'
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client}" crossorigin="anonymous"></script>'
        f'<ins class="adsbygoogle" style="display:block;text-align:center;" data-ad-layout="in-article" data-ad-format="fluid" '
        f'data-ad-client="{client}" data-ad-slot="{slot}"></ins>'
        "<script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>"
    )


def build_html(post: dict, client: str = "", slot: str = "") -> str:
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
    if post.get("faq"):
        out.append("<h2>తరచుగా అడిగే ప్రశ్నలు</h2>")
        for f in post["faq"]:
            out.append(f"<h3>{html.escape(f['q'])}</h3><p>{_inline(f['a'])}</p>")
    if post.get("disclaimer"):
        out.append(f'<p><i>{_inline(post["disclaimer"])}</i></p>')
    out.append("<p>మహానవి స్పిరిచ్యువల్స్ యూట్యూబ్ ఛానెల్‌లో రోజూ కొత్త వీడియోలు, షార్ట్స్ చూడండి.</p></div>")
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    ap.add_argument("--id", type=int)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    client = os.environ.get("MAHANAVI_ADSENSE_CLIENT", "").strip()
    slot = os.environ.get("MAHANAVI_ADSENSE_SLOT", "").strip()
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
    today = dt.datetime.now(IST).date()
    nxt = (max(d.date() for d in dates) + dt.timedelta(days=1)) if dates else today + dt.timedelta(days=1)
    nxt = max(nxt, today + dt.timedelta(days=1))
    horizon = today + dt.timedelta(days=a.days)
    todo = [p for p in posts if p["title"] not in titles]
    made = 0
    for p in todo:
        if nxt > horizon:
            break
        when = dt.datetime.combine(nxt, dt.time(HOUR_IST, 0), IST).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"{'POST' if a.apply else 'would post'} #{p['id']} {nxt} {p['title'][:60]}")
        if a.apply:
            blog.posts().insert(blogId=st.blogger_blog_id, body={
                "title": p["title"], "content": build_html(p, client, slot), "published": when,
                "labels": [DAILY_LABEL] + p["labels"]}).execute()
        made += 1
        nxt += dt.timedelta(days=1)
    print(f"::notice::{made} article(s) {'scheduled' if a.apply else 'listed'}; {max(len(todo) - made, 0)} still waiting in the bank")
    if not todo:
        print("::warning::the article bank is empty: add more data/blog/posts/NNN.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
