#!/usr/bin/env python3
"""daily_digest.py: one Telegram digest per channel, every morning, from the YouTube Analytics + Data APIs.

For each channel token it reports: subscribers (total, 7-day net, yesterday), views / watch time / likes /
comments / shares for the latest full day and the last 7 days (with % change against the 7 days before),
a 7-day views sparkline, the top videos (with views, likes, avg % viewed and subscribers gained), where
views come from (Shorts feed, search, subscribers, ...), top countries and a couple of plain-language takeaways.
A first message summarises all channels side by side.

Needs the yt-analytics.readonly scope on each token; a channel without it gets one clear line instead of a crash.

Usage: python scripts/ci/daily_digest.py [--days 7] [--only ramana,jesus] [--dry-run]
Env:   MAHANAVI_TELEGRAM_BOT_TOKEN / MAHANAVI_TELEGRAM_CHAT_ID, tokens in ./data/ (restored from Drive).
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
DATA = Path("data")
CHANNELS = [  # (key, label, token file)
    ("mahanavi", "Mahanavi Spirituals", "youtube_token.json"),
    ("mantra_sangam", "Divine Mantra Sangam", "youtube_token_mantra_sangam.json"),
    ("trance", "Devotional Trance Beats", "youtube_token_trance_beats.json"),
    ("jesus", "Jesus Worship Waves", "youtube_token_jesus.json"),
    ("ramana", "Ramana Maharshi TV", "youtube_token_ramana.json"),
    ("pulse", "Pulse Boosting", "youtube_token_pulse_boosting.json"),
]
SOURCE_NAMES = {
    "SHORTS": "Shorts feed", "YT_SEARCH": "YouTube search", "SUBSCRIBER": "Subscribers", "RELATED_VIDEO": "Suggested",
    "YT_CHANNEL": "Channel page", "BROWSE": "Home/Browse", "EXT_URL": "External links", "NOTIFICATION": "Notifications",
    "PLAYLIST": "Playlists", "NO_LINK_OTHER": "Direct/other", "YT_OTHER_PAGE": "Other YouTube", "END_SCREEN": "End screens",
}
BARS = "▁▂▃▄▅▆▇█"


# ---------------------------------------------------------------- pure formatting helpers (unit tested)
def fmt_num(n: float) -> str:
    n = float(n)
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if abs(n) >= 10_000:
        return f"{n / 1000:.1f}K"
    return f"{int(round(n)):,}"


def pct_change(now: float, before: float) -> str:
    if before <= 0:
        return "new" if now > 0 else "flat"
    ch = 100 * (now - before) / before
    arrow = "▲" if ch > 0.5 else ("▼" if ch < -0.5 else "►")
    return f"{arrow}{abs(ch):.0f}%"


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    hi, lo = max(values), min(values)
    if hi == lo:
        return BARS[0] * len(values) if hi == 0 else BARS[3] * len(values)
    return "".join(BARS[int((v - lo) / (hi - lo) * (len(BARS) - 1))] for v in values)


def minutes_to_text(m: float) -> str:
    h = m / 60
    return f"{h:,.0f} h" if h >= 10 else f"{m:,.0f} min"


def build_channel_message(label: str, d: dict, today: dt.date, days: int) -> str:
    """d keys: subs, total_views, videos, daily[list of {day, views, minutes, likes, comments, shares, gained, lost}],
    prev[dict totals], top[list], sources[list of (name, views)], countries[list], uploads_yesterday."""
    daily = sorted(d["daily"], key=lambda r: r["day"])
    last7 = daily[-days:]
    tot = {k: sum(r[k] for r in last7) for k in ("views", "minutes", "likes", "comments", "shares", "gained", "lost")}
    prev = d.get("prev", {})
    latest = daily[-1] if daily else None
    lines = [f"📺 {label}   {today:%a %d %b %Y}"]
    lines.append(f"👥 Subscribers: {fmt_num(d['subs'])}   7-day net {tot['gained'] - tot['lost']:+d} (+{tot['gained']} / -{tot['lost']})")
    if latest:
        lines.append(f"📅 Latest day ({latest['day']}): {fmt_num(latest['views'])} views, {latest['likes']} likes, "
                     f"{latest['comments']} comments, {latest['gained'] - latest['lost']:+d} subs")
    lines.append(f"📈 Last {days} days: {fmt_num(tot['views'])} views {pct_change(tot['views'], prev.get('views', 0))} vs previous {days}")
    lines.append(f"   ⏱ watch time {minutes_to_text(tot['minutes'])} {pct_change(tot['minutes'], prev.get('minutes', 0))}   "
                 f"👍 {tot['likes']} {pct_change(tot['likes'], prev.get('likes', 0))}   "
                 f"💬 {tot['comments']}   ↗ {tot['shares']} shares")
    if tot["views"]:
        lines.append(f"   subscribers per 1,000 views: {1000 * tot['gained'] / tot['views']:.1f}   likes per 100 views: {100 * tot['likes'] / tot['views']:.1f}")
    lines.append(f"   views by day: {sparkline([r['views'] for r in last7])}  ({', '.join(fmt_num(r['views']) for r in last7)})")
    lines.append(f"🎬 All-time: {fmt_num(d['total_views'])} views, {d['videos']} videos"
                 + (f"; {d['uploads_yesterday']} uploaded yesterday" if d.get("uploads_yesterday") is not None else ""))
    if d.get("top"):
        lines.append(f"\n🏆 Top videos ({days} days)")
        for i, v in enumerate(d["top"], 1):
            lines.append(f"{i}. {v['title'][:60]}\n   {fmt_num(v['views'])} views, {v['likes']} likes, {v['avg_pct']:.0f}% viewed, {v['gained']:+d} subs")
    if d.get("weak"):
        w = d["weak"]
        lines.append(f"🔻 Weakest recent: {w['title'][:55]} ({fmt_num(w['views'])} views)")
    if d.get("sources"):
        tv = sum(v for _n, v in d["sources"]) or 1
        lines.append("\n🧭 Where views come from: " + ", ".join(f"{n} {100 * v / tv:.0f}%" for n, v in d["sources"][:4]))
    if d.get("countries"):
        tv = tot["views"] or sum(v for _c, v in d["countries"]) or 1
        lines.append("🌍 Top countries: " + ", ".join(f"{c} {100 * v / tv:.0f}%" for c, v in d["countries"][:4]))
    take = takeaways(d, tot, prev, last7, days)
    if take:
        lines.append("\n💡 " + "\n💡 ".join(take))
    return "\n".join(lines)


def takeaways(d: dict, tot: dict, prev: dict, last7: list[dict], days: int) -> list[str]:
    out = []
    if last7 and tot["views"]:
        best = max(last7, key=lambda r: r["views"])
        out.append(f"Best day was {best['day']} with {fmt_num(best['views'])} views.")
    if prev.get("views", 0) > 0 and tot["views"] < 0.8 * prev["views"]:
        out.append("Views are down more than 20% on the previous week; check the weakest videos and the posting times.")
    elif prev.get("views", 0) > 0 and tot["views"] > 1.2 * prev["views"]:
        out.append("Views are up more than 20% on the previous week; repeat what the top videos did.")
    if d.get("top") and tot["views"]:
        share = 100 * d["top"][0]["views"] / tot["views"]
        if share >= 40:
            out.append(f"One video gives {share:.0f}% of the views; a similar topic is worth posting again.")
    if tot["gained"] == 0 and tot["views"] > 500:
        out.append("Views but no new subscribers: the subscribe reminder may need to be stronger.")
    return out[:3]


def build_summary(rows: list[tuple[str, dict | None, str]], today: dt.date, days: int) -> str:
    lines = [f"📊 Daily channel report   {today:%a %d %b %Y}   (last {days} days)\n"]
    for label, t, note in rows:
        if t is None:
            lines.append(f"• {label}: {note}")
            continue
        lines.append(f"• {label}: {fmt_num(t['views'])} views {pct_change(t['views'], t['prev_views'])}, "
                     f"{t['net']:+d} subs ({fmt_num(t['subs'])} total), {fmt_num(t['likes'])} likes")
    ok = [t for _l, t, _n in rows if t]
    if ok:
        lines.append(f"\nAll channels: {fmt_num(sum(t['views'] for t in ok))} views, {sum(t['net'] for t in ok):+d} subscribers")
    return "\n".join(lines)


# ---------------------------------------------------------------- API access
def _creds(token_file: Path):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    c = Credentials.from_authorized_user_file(str(token_file))
    if c.expired and c.refresh_token:
        c.refresh(Request())
        token_file.write_text(c.to_json(), encoding="utf-8")
    return c


def collect(token_file: Path, today: dt.date, days: int) -> dict:
    from googleapiclient.discovery import build
    creds = _creds(token_file)
    yt = build("youtube", "v3", credentials=creds)
    an = build("youtubeAnalytics", "v2", credentials=creds)
    ch = yt.channels().list(part="snippet,statistics", mine=True).execute()["items"][0]
    st = ch["statistics"]
    end = today - dt.timedelta(days=1)
    start = end - dt.timedelta(days=2 * days - 1)
    base = dict(ids="channel==MINE")
    r = an.reports().query(**base, startDate=start.isoformat(), endDate=end.isoformat(), dimensions="day", sort="day",
                           metrics="views,estimatedMinutesWatched,likes,comments,shares,subscribersGained,subscribersLost").execute()
    allrows = [dict(zip(("day", "views", "minutes", "likes", "comments", "shares", "gained", "lost"), row)) for row in r.get("rows", [])]
    for row in allrows:
        for k in row:
            if k != "day":
                row[k] = int(row[k])
    # drop trailing days YouTube has not filled in yet (all zeros after the last day with data)
    while allrows and allrows[-1]["views"] == 0 and len(allrows) > days:
        allrows.pop()
    cur, before = allrows[-days:], allrows[-2 * days:-days]
    prev = {k: sum(x[k] for x in before) for k in ("views", "minutes", "likes", "comments", "shares", "gained", "lost")}
    win_start = (cur[0]["day"] if cur else (end - dt.timedelta(days=days - 1)).isoformat())
    win_end = cur[-1]["day"] if cur else end.isoformat()
    out = {"name": ch["snippet"]["title"], "subs": int(st.get("subscriberCount", 0)), "total_views": int(st.get("viewCount", 0)),
           "videos": int(st.get("videoCount", 0)), "daily": cur, "prev": prev}
    try:
        r = an.reports().query(**base, startDate=win_start, endDate=win_end, dimensions="video", sort="-views", maxResults=10,
                               metrics="views,likes,averageViewPercentage,subscribersGained").execute()
        rows = r.get("rows", [])
        ids = [x[0] for x in rows]
        titles = {}
        for i in range(0, len(ids), 50):
            for v in yt.videos().list(part="snippet,status", id=",".join(ids[i:i + 50])).execute().get("items", []):
                titles[v["id"]] = v["snippet"]["title"]
        vids = [{"id": x[0], "title": titles.get(x[0], x[0]), "views": int(x[1]), "likes": int(x[2]), "avg_pct": float(x[3]), "gained": int(x[4])} for x in rows]
        out["top"] = vids[:3]
        recent = [v for v in vids[3:] if v["views"] >= 0]
        out["weak"] = recent[-1] if len(recent) >= 3 else None
    except Exception:  # noqa: BLE001
        out["top"], out["weak"] = [], None
    try:
        r = an.reports().query(**base, startDate=win_start, endDate=win_end, dimensions="insightTrafficSourceType", sort="-views",
                               metrics="views").execute()
        out["sources"] = [(SOURCE_NAMES.get(a, a.title().replace("_", " ")), int(b)) for a, b in r.get("rows", [])]
    except Exception:  # noqa: BLE001
        out["sources"] = []
    try:
        r = an.reports().query(**base, startDate=win_start, endDate=win_end, dimensions="country", sort="-views", maxResults=4,
                               metrics="views").execute()
        out["countries"] = [(a, int(b)) for a, b in r.get("rows", [])]
    except Exception:  # noqa: BLE001
        out["countries"] = []
    try:
        pl = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        items = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50).execute().get("items", [])
        y = (today - dt.timedelta(days=1))
        n = 0
        for it in items:
            pub = dt.datetime.fromisoformat(it["contentDetails"]["videoPublishedAt"].replace("Z", "+00:00")).astimezone(IST).date()
            n += pub == y
        out["uploads_yesterday"] = n
    except Exception:  # noqa: BLE001
        out["uploads_yesterday"] = None
    return out


def telegram(text: str) -> bool:
    import requests
    tok, chat = os.environ.get("MAHANAVI_TELEGRAM_BOT_TOKEN"), os.environ.get("MAHANAVI_TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("Telegram not configured; message printed only.")
        return False
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                      json={"chat_id": chat, "text": text[:4000], "disable_web_page_preview": True}, timeout=30)
    return r.ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--only", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    today = dt.datetime.now(IST).date()
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    messages, summary_rows = [], []
    for key, label, tf in CHANNELS:
        if only and key not in only:
            continue
        path = DATA / tf
        if not path.exists():
            summary_rows.append((label, None, "token not available"))
            continue
        try:
            d = collect(path, today, a.days)
        except Exception as exc:  # noqa: BLE001
            note = f"no data ({type(exc).__name__}); re-run auth setup with the analytics scope" if "scope" in str(exc).lower() or "403" in str(exc) else f"failed ({type(exc).__name__})"
            print(f"{label}: {str(exc)[:200]}", file=sys.stderr)
            summary_rows.append((label, None, note))
            continue
        cur = d["daily"][-a.days:]
        summary_rows.append((label, {"views": sum(r["views"] for r in cur), "prev_views": d["prev"]["views"],
                                     "net": sum(r["gained"] - r["lost"] for r in cur), "subs": d["subs"],
                                     "likes": sum(r["likes"] for r in cur)}, ""))
        messages.append(build_channel_message(d["name"] or label, d, today, a.days))
    for label, t, note in summary_rows:  # shows up as run annotations, since the Telegram text itself is not visible in the log
        print(f"::notice title=digest::{label}: " + (f"ok, {t['views']} views in window" if t else note))
    out = [build_summary(summary_rows, today, a.days), *messages]
    for m in out:
        print(m + "\n" + "-" * 40)
        if not a.dry_run:
            telegram(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
