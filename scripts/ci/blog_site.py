#!/usr/bin/env python3
"""SEO-formatted articles for the extra Blogger sites (PuranaKnowledge, later the Hindi and niche blogs).

Each site lives in content/sites/<site>/ : site.json (blog id, names, ad slot) and posts/NNN.json.

  python scripts/ci/blog_site.py --site purana --preview out.html [--id 2]   # build one article locally, no API
  python scripts/ci/blog_site.py --site purana --days 7 [--apply]            # schedule next unpublished posts, 3 a day
  python scripts/ci/blog_site.py --site purana --relink [--apply]            # fill the Related reading block with real post URLs

SEO per article: keyword-first title, bold keywords, key-takeaways box, contents list with anchors, one H1 (Blogger title),
H2/H3 outline, hero image with alt + title + caption, mid-article AdSense, FAQ with FAQPage JSON-LD, Article JSON-LD,
related-reading links (same-label posts) and labels as tags."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blog_daily as bd  # noqa: E402  (slot times, ad block, service helper)

ROOT = bd.ROOT
RELATED_MARK = "<!--related-posts-->"
RAW = "https://raw.githubusercontent.com/vamseenathreddy/mahanavi-spirituals/main/assets/blog/"


def site_dir(site: str) -> Path:
    return ROOT / "content" / "sites" / site


def load_site(site: str) -> tuple[dict, list[dict]]:
    d = site_dir(site)
    cfg = json.loads((d / "site.json").read_text(encoding="utf-8"))
    posts = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((d / "posts").glob("*.json"))]
    return cfg, posts


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s


def anchor(i: int) -> str:
    return f"s{i + 1}"


def build_html(cfg: dict, post: dict, client: str, slot: str) -> str:
    secs = post["sections"]
    mid = max(0, (len(secs) + 1) // 2 - 1)
    alt = html.escape(post["alt"], quote=True)
    img = f'{RAW}{cfg["hero_dir"]}/{post["hero"]}'
    o = ['<div class="article-body">']
    o.append(f'<p><img src="{img}" alt="{alt}" title="{alt}" width="1200" height="630" '
             f'style="width:100%;max-width:900px;height:auto;border-radius:10px;"/><br/><small><i>{html.escape(post.get("caption", post["alt"]))}</i></small></p>')
    o.append(f'<p>{inline(post["intro"])}</p>')
    if post.get("takeaways"):
        o.append('<div style="background:#fff7e6;border-left:5px solid #e08a00;padding:12px 16px;margin:18px 0;border-radius:6px;">'
                 "<p><b>Key takeaways</b></p><ul>" + "".join(f"<li>{inline(t)}</li>" for t in post["takeaways"]) + "</ul></div>")
    heads = [(i, s) for i, s in enumerate(secs) if s.get("h")]
    if len(heads) >= 3:
        o.append("<p><b>In this article</b></p><ol>" + "".join(f'<li><a href="#{anchor(i)}">{html.escape(s["h"])}</a></li>' for i, s in heads)
                 + ('<li><a href="#faq">Frequently asked questions</a></li>' if post.get("faq") else "") + "</ol>")
    for i, s in enumerate(secs):
        if s.get("h"):
            o.append(f'<h2 id="{anchor(i)}">{html.escape(s["h"])}</h2>')
        for para in s.get("p", []):
            o.append(f"<p>{inline(para)}</p>")
        for sub in s.get("sub", []):
            o.append(f'<h3>{html.escape(sub["h"])}</h3>')
            for para in sub.get("p", []):
                o.append(f"<p>{inline(para)}</p>")
        if s.get("ul"):
            o.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in s["ul"]) + "</ul>")
        if s.get("ol"):
            o.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in s["ol"]) + "</ol>")
        if i == mid:
            o.append(bd.adsense_block(client, slot))
    if post.get("video"):
        o.append(f'<h2>Watch the video</h2><p><iframe width="560" height="315" src="https://www.youtube.com/embed/{post["video"]}" '
                 'title="YouTube video" frameborder="0" allowfullscreen style="max-width:100%"></iframe></p>')
    if post.get("faq"):
        o.append('<h2 id="faq">Frequently asked questions</h2>')
        for f in post["faq"]:
            o.append(f"<h3>{html.escape(f['q'])}</h3><p>{inline(f['a'])}</p>")
    if post.get("note"):
        o.append(f'<p><i>{inline(post["note"])}</i></p>')
    o.append(RELATED_MARK)
    labels = " | ".join(f'<a href="{cfg["url"]}/search/label/{quote(l)}">{html.escape(l)}</a>' for l in post["labels"])
    o.append(f'<p><b>Topics:</b> {labels} | <a href="{cfg["url"]}">Home</a></p>')
    if cfg.get("youtube_url"):
        o.append(f'<p>{html.escape(cfg["cta"])} <a href="{cfg["youtube_url"]}">{html.escape(cfg["youtube_name"])} on YouTube</a>.</p>')
    o.append(jsonld(cfg, post, img))
    o.append("</div>")
    return "\n".join(x for x in o if x)


def jsonld(cfg: dict, post: dict, img: str) -> str:
    art = {"@context": "https://schema.org", "@type": "Article", "headline": post["title"], "image": img,
           "description": post["desc"], "inLanguage": cfg.get("lang", "en"),
           "author": {"@type": "Organization", "name": cfg["name"]}, "publisher": {"@type": "Organization", "name": cfg["name"]}}
    blocks = [art]
    if post.get("faq"):
        blocks.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\*\*", "", f["a"])}} for f in post["faq"]]})
    return "".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in blocks)


def related_html(post: dict, others: list[dict]) -> str:
    mine = set(post["labels"])
    scored = sorted((o for o in others if o["title"] != post["title"]), key=lambda o: -len(mine & set(o["labels"])))
    pick = scored[:3]
    if not pick:
        return ""
    return "<p><b>Related reading:</b></p><ul>" + "".join(f'<li><a href="{o["url"]}">{html.escape(o["title"])}</a></li>' for o in pick) + "</ul>"


def relink(blog, blog_id: str, apply: bool) -> int:
    items, tok = [], None
    while True:
        r = blog.posts().list(blogId=blog_id, maxResults=50, pageToken=tok, fetchBodies=True, fetchImages=False,
                              status=["LIVE", "SCHEDULED"]).execute()
        items += r.get("items", [])
        tok = r.get("nextPageToken")
        if not tok:
            break
    n = 0
    for p in items:
        if RELATED_MARK not in p.get("content", ""):
            continue
        block = related_html({"title": p["title"], "labels": p.get("labels") or []},
                             [{"title": x["title"], "labels": x.get("labels") or [], "url": x["url"]} for x in items])
        if not block:
            continue
        n += 1
        print(("linking" if apply else "would link"), p["title"])
        if apply:
            blog.posts().patch(blogId=blog_id, postId=p["id"], body={"content": p["content"].replace(RELATED_MARK, block)}).execute()
            time.sleep(3)
    print(f"{n} post(s) {'linked' if apply else 'need links'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--preview")
    ap.add_argument("--id", type=int)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--relink", action="store_true")
    ap.add_argument("--per-day", type=int, default=0)
    a = ap.parse_args()
    cfg, posts = load_site(a.site)
    client, slot = cfg["adsense_client"], cfg["adsense_slot"]
    if a.preview:
        p = next(x for x in posts if x["id"] == (a.id or posts[0]["id"]))
        body = build_html(cfg, p, client, slot)
        Path(a.preview).write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                                   f'<body style="max-width:760px;margin:20px auto;font-family:Georgia,serif;line-height:1.7;padding:0 14px">'
                                   f'<h1>{html.escape(p["title"])}</h1>{body}</body>', encoding="utf-8")
        print("wrote", a.preview)
        return 0
    st, blog = bd._service()  # noqa: SLF001
    blog_id = cfg["blog_id"]
    if a.relink:
        return relink(blog, blog_id, a.apply)
    per_day = a.per_day or cfg.get("per_day", 3)
    existing_titles = set()
    tok = None
    taken = set()
    while True:
        r = blog.posts().list(blogId=blog_id, maxResults=50, pageToken=tok, fetchBodies=False, fetchImages=False,
                              status=["LIVE", "DRAFT", "SCHEDULED"]).execute()
        for p in r.get("items", []):
            existing_titles.add(p["title"])
            taken.add(dt.datetime.fromisoformat(p["published"]).astimezone(bd.IST).replace(second=0, microsecond=0))
        tok = r.get("nextPageToken")
        if not tok:
            break
    now = dt.datetime.now(bd.IST)
    horizon = (now + dt.timedelta(days=a.days)).date()
    todo = [p for p in posts if p["title"] not in existing_titles]
    made, day = 0, now.date()
    while todo and day <= horizon:
        for slot_t in bd.day_slots(day)[:per_day]:
            if not todo:
                break
            if slot_t <= now + dt.timedelta(minutes=20) or slot_t in taken or sum(1 for d in taken if d.date() == day) >= per_day:
                continue
            p = todo.pop(0)
            when = slot_t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"{'POST' if a.apply else 'would post'} #{p['id']} {slot_t:%Y-%m-%d %H:%M} IST {p['title']}")
            if a.apply:
                body = {"title": p["title"], "content": build_html(cfg, p, client, slot), "published": when, "labels": p["labels"]}
                for attempt in range(4):
                    try:
                        blog.posts().insert(blogId=blog_id, body=body).execute()
                        break
                    except Exception as e:  # noqa: BLE001
                        if ("429" in str(e) or "rateLimit" in str(e)) and attempt < 3:
                            time.sleep(60 * (attempt + 1))
                        else:
                            raise
                time.sleep(8)
            taken.add(slot_t)
            made += 1
        day += dt.timedelta(days=1)
    print(f"::notice::{made} post(s) {'scheduled' if a.apply else 'listed'}; {len(todo)} still waiting")
    return 0


if __name__ == "__main__":
    sys.exit(main())
