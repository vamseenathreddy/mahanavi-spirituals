#!/usr/bin/env python3
"""weekly_review.py: the weekly health review of every channel, saved to the repo so it can be read and acted on.

For each channel token it collects (reusing daily_digest.collect): subscribers, 7-day and previous-7-day views, net
subscribers, top and weakest videos, traffic sources, and from the Data API the number of uploads and the views of the
posts that are old enough to have settled (2 to 9 days old). It then raises FLAGS (plain-language problems) and writes:

  reports/weekly/<date>.json   the full numbers
  reports/weekly/<date>.md     the human summary, flags first
  reports/history.json         one compact row per channel per week (trend over time)
  reports/LATEST.md            copy of the newest summary

Flags: reach collapse (median views of settled posts under 20), views down 40% or more, no net subscriber gain for two
weeks, posting stalled (no upload in 3 days), a channel that could not be read (token or scope problem).
Usage: python scripts/ci/weekly_review.py [--only ramana,pulse]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import daily_digest as dd  # noqa: E402

IST = dd.IST
OUT = Path("reports")


def settled_posts(token_file: Path, today: dt.date) -> dict:
    from googleapiclient.discovery import build
    creds = dd._creds(token_file)  # noqa: SLF001
    yt = build("youtube", "v3", credentials=creds)
    pl = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    items = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50).execute().get("items", [])
    ids = [i["contentDetails"]["videoId"] for i in items]
    vids = []
    for k in range(0, len(ids), 50):
        vids += yt.videos().list(part="snippet,statistics,status", id=",".join(ids[k:k + 50])).execute().get("items", [])
    posts = []
    for v in vids:
        pub = dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")).astimezone(IST)
        posts.append({"id": v["id"], "title": v["snippet"]["title"], "age": (today - pub.date()).days,
                      "views": int(v["statistics"].get("viewCount", 0)), "privacy": v["status"]["privacyStatus"]})
    pub = [p for p in posts if p["privacy"] == "public"]
    last7 = [p for p in pub if p["age"] <= 7]
    settled = [p for p in pub if 2 <= p["age"] <= 9]
    recent = [p for p in pub if 1 <= p["age"] <= 4]
    last_age = min((p["age"] for p in pub), default=None)
    return {"uploads_7d": len(last7), "settled_n": len(settled),
            "median_settled": statistics.median(p["views"] for p in settled) if settled else None,
            "recent_n": len(recent), "median_recent": statistics.median(p["views"] for p in recent) if recent else None,
            "best_settled": sorted(settled, key=lambda p: -p["views"])[:3], "worst_settled": sorted(settled, key=lambda p: p["views"])[:3],
            "days_since_upload": last_age}


def flags_for(label: str, d: dict, s: dict, hist: list[dict]) -> list[str]:
    out = []
    cur = d["daily"][-7:]
    views, prev = sum(r["views"] for r in cur), d["prev"]["views"]
    net = sum(r["gained"] - r["lost"] for r in cur)
    if s["median_settled"] is not None and s["settled_n"] >= 5 and s["median_settled"] < 20:
        out.append(f"REACH COLLAPSE: median views of {s['settled_n']} settled posts is {s['median_settled']:.0f}")
    if s["median_recent"] is not None and s["recent_n"] >= 5 and s["median_recent"] < 15 and not (s["median_settled"] is not None and s["median_settled"] < 20):
        out.append(f"RECENT REACH COLLAPSE: posts from the last 4 days have a median of {s['median_recent']:.0f} views, while older posts did far better")
    if prev >= 100 and views <= 0.6 * prev:
        out.append(f"VIEWS DOWN {100 - round(100 * views / prev)}%: {views} vs {prev} the week before")
    last = hist[-1] if hist else None
    if net <= 0 and last and last.get("net", 1) <= 0 and views > 0:
        out.append("NO SUBSCRIBER GROWTH for two weeks in a row")
    if s["days_since_upload"] is not None and s["days_since_upload"] >= 3:
        out.append(f"POSTING STALLED: last public upload {s['days_since_upload']} days ago")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    today = dt.datetime.now(IST).date()
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    (OUT / "weekly").mkdir(parents=True, exist_ok=True)
    hist_path = OUT / "history.json"
    history = json.loads(hist_path.read_text()) if hist_path.exists() else {}
    report, md = {}, [f"# Weekly channel review, week ending {today.isoformat()}\n"]
    all_flags = []
    for key, label, tf in dd.CHANNELS:
        if only and key not in only:
            continue
        path = dd.DATA / tf
        if not path.exists():
            all_flags.append(f"{label}: TOKEN FILE MISSING")
            continue
        try:
            d = dd.collect(path, today, 7)
            s = settled_posts(path, today)
        except Exception as exc:  # noqa: BLE001
            all_flags.append(f"{label}: COULD NOT READ ({type(exc).__name__}: {str(exc)[:120]}). Token or analytics scope needs a re-login.")
            continue
        cur = d["daily"][-7:]
        row = {"date": today.isoformat(), "subs": d["subs"], "views": sum(r["views"] for r in cur), "prev_views": d["prev"]["views"],
               "net": sum(r["gained"] - r["lost"] for r in cur), "likes": sum(r["likes"] for r in cur),
               "uploads_7d": s["uploads_7d"], "median_settled": s["median_settled"]}
        hist = history.setdefault(key, [])
        fl = flags_for(label, d, s, hist)
        hist.append(row)
        report[key] = {"label": label, "row": row, "flags": fl, "top": d.get("top"), "sources": d.get("sources"), "settled": s}
        all_flags += [f"{label}: {f}" for f in fl]
        vpp = row["views"] / row["uploads_7d"] if row["uploads_7d"] else 0
        md.append(f"## {label}\n- subscribers {row['subs']} ({row['net']:+d} this week)\n- views {row['views']} (previous week {row['prev_views']}), {row['uploads_7d']} uploads, about {vpp:.0f} views per upload\n"
                  f"- median views of settled posts: {s['median_settled']}\n"
                  + "".join(f"- best: {p['views']} views, {p['title'][:70]}\n" for p in s["best_settled"][:2])
                  + "".join(f"- weakest: {p['views']} views, {p['title'][:70]}\n" for p in s["worst_settled"][:2])
                  + "".join(f"- FLAG: {f}\n" for f in fl))
    md.insert(1, "## Flags\n" + ("".join(f"- {f}\n" for f in all_flags) if all_flags else "- none\n"))
    text = "\n".join(md)
    (OUT / "weekly" / f"{today.isoformat()}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    (OUT / "weekly" / f"{today.isoformat()}.md").write_text(text)
    (OUT / "LATEST.md").write_text(text)
    hist_path.write_text(json.dumps(history, ensure_ascii=False, indent=1))
    print(text)
    for f in all_flags:
        print(f"::warning title=weekly review::{f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
