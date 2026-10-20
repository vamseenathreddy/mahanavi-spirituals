"""SEO for the long Bible-verse videos: a search-style title, chapters (one per verse), tags, a short pinned comment.
The channel's standing rule applies: subscribe reminders only, no requests for comments."""
from __future__ import annotations

from channels.jesus_long.bank import load

PLAYLIST = "Bible Verses with Worship Music | Jesus Worship Waves"


def _ts(sec: int) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


TITLES = [  # rotated by ISO week so a theme that comes round again each week never repeats last week's title
    "{n} Bible Verses for {t} | Calming Scripture Reading with Soft Worship Music",
    "Bible Verses for {t} | {n} Scriptures Read Slowly with Peaceful Worship Music",
    "{n} Bible Verses for {t} | Daily Devotion with Gentle Worship Music",
    "Read the Word: {n} Bible Verses for {t} | Quiet Prayer Time with Worship Music",
]


def title(theme: dict, day=None) -> str:
    n = len(theme["verses"])
    week = day.isocalendar()[1] if day is not None else 0
    t = TITLES[week % len(TITLES)].format(n=n, t=theme["title"])
    return t if len(t) <= 100 else f"{n} Bible Verses for {theme['title']} | Scripture Reading with Worship Music"[:100]


def description(theme: dict, chapters: list[tuple[int, str]], day=None) -> str:
    n = len(theme["verses"])
    stamp = f"{day.day} {day.strftime('%B %Y')}: " if day is not None else ""
    lines = [f"{stamp}{n} Bible verses for {theme['phrase']}, read slowly with soft worship music. Sit back, breathe, and let the word of God settle your heart. "
             "Good for prayer time, morning devotion, or winding down at night.",
             "", "Chapters (each verse):"]
    lines += [f"{_ts(s)} {label}" for s, label in chapters]
    lines += ["", f"Scripture is read from the {load()['translation']}. The worship music is original, created for this channel.",
              "", "Subscribe to Jesus Worship Waves for a new Bible verse reading every day.",
              "", f"#BibleVerses #{theme['title'].split()[0]} #Scripture #Jesus #WorshipMusic"]
    return "\n".join(lines)


def tags(theme: dict) -> list[str]:
    base = [f"bible verses for {theme['phrase']}", "bible verses", "scripture reading", "bible reading with music", "worship music",
            "calming scripture", "morning devotion", "bible verses for sleep", f"{theme['phrase']} bible verses", "bible verses with music", "christian worship music", "scriptures for peace", "kjv bible verses", "christian meditation",
            "prayer", "jesus", "daily bible verse", "Jesus Worship Waves"]
    out, n = [], 0
    for t in base:
        if n + len(t) + 1 > 480:
            break
        out.append(t)
        n += len(t) + 1
    return out


def comment(theme: dict) -> str:
    return f"All {len(theme['verses'])} verses are listed with their references in the description. Scripture: {load()['translation']}."
