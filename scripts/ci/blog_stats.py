#!/usr/bin/env python3
"""Daily check of the Mahanavi blog: page views (7 / 30 days / all time), articles live and waiting, progress to the target.
Target lives in content/blog/target.json {"monthly_pageviews": N}. Prints a report (also written to the job summary)."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from blog_daily import DAILY_LABEL, ROOT  # noqa: E402


VIDEO_RE = re.compile(r"(?:i\.ytimg\.com/vi(?:_webp)?/|youtube(?:-nocookie)?\.com/embed/|watch\?v=)([A-Za-z0-9_-]{11})")


def duplicate_groups(posts: list[dict]) -> list[list[dict]]:
    """Posts (not the daily articles) that embed the same YouTube video: the second one is a duplicate, usually made by the
    old IFTTT applet. Returns groups of 2 or more."""
    by_video: dict[str, list[dict]] = {}
    for p in posts:
        if DAILY_LABEL in (p.get("labels") or []):
            continue
        for vid in set(VIDEO_RE.findall(p.get("content", ""))):
            by_video.setdefault(vid, []).append(p)
    return [g for g in by_video.values() if len(g) > 1]


def main() -> int:
    from mahanavi.config import get_settings
    from mahanavi.publishers import blogger_publisher as bp
    st = get_settings()
    blog = bp._build_service(st)  # noqa: SLF001
    bid = st.blogger_blog_id
    info = blog.blogs().get(blogId=bid).execute()
    pv = blog.pageViews().get(blogId=bid, range=["7DAYS", "30DAYS", "all"]).execute()
    views = {c["timeRange"]: int(c["count"]) for c in pv.get("counts", [])}
    live = sched = 0
    latest = []
    for status in ("LIVE", "SCHEDULED"):
        tok = None
        while True:
            r = blog.posts().list(blogId=bid, maxResults=50, pageToken=tok, status=[status], fetchBodies=False, fetchImages=False).execute()
            for p in r.get("items", []):
                if DAILY_LABEL in (p.get("labels") or []):
                    if status == "LIVE":
                        live += 1; latest.append((p["published"][:16], p["title"]))
                    else:
                        sched += 1
            tok = r.get("nextPageToken")
            if not tok:
                break
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent, tok = [], None
    while True:
        r = blog.posts().list(blogId=bid, maxResults=50, pageToken=tok, status=["LIVE"], startDate=since, fetchBodies=True, fetchImages=False).execute()
        recent += r.get("items", [])
        tok = r.get("nextPageToken")
        if not tok:
            break
    dups = duplicate_groups(recent)
    tgt = 0
    tf = ROOT / "content" / "blog" / "target.json"
    if tf.exists():
        tgt = int(json.loads(tf.read_text()).get("monthly_pageviews", 0))
    m30 = views.get("THIRTY_DAYS", 0); d7 = views.get("SEVEN_DAYS", 0)
    lines = [f"## Mahanavi blog report {dt.date.today()}", f"Blog: {info.get('name')} ({info.get('url')})",
             f"- Page views: last 7 days {d7} (about {d7 / 7:.0f}/day), last 30 days {m30}, all time {views.get('ALL_TIME', 0)}",
             f"- Daily articles: {live} live, {sched} scheduled"]
    if tgt:
        lines.append(f"- Target {tgt}/month: {m30 / tgt * 100:.0f}% reached; needs {tgt / 30:.0f}/day, now {d7 / 7:.0f}/day "
                     f"({'on track' if d7 / 7 >= tgt / 30 else 'behind'})")
    if dups:
        lines.append(f"- DUPLICATES: {len(dups)} video(s) in the last 3 days have 2+ blog posts (the old IFTTT applet is probably still on):")
        for g in dups[:8]:
            lines.append("    " + " / ".join(f"{p['published'][:16]} {p['title'][:40]}" for p in sorted(g, key=lambda x: x['published'])))
    else:
        lines.append("- Duplicates in the last 3 days: none")
    lines.append("- Latest articles: " + "; ".join(f"{d} {t[:50]}" for d, t in sorted(latest)[-3:]))
    if sched < 6:
        lines.append(f"- ACTION: only {sched} scheduled articles left. Add more to content/blog/posts/.")
    out = "\n".join(lines)
    print(out)
    sm = os.environ.get("GITHUB_STEP_SUMMARY")
    if sm:
        Path(sm).write_text(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
