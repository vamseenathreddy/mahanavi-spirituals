#!/usr/bin/env python3
"""Weekly content stock check: how many NEW posts are left in every series that draws from a finite list, so you can ask for
a refill before a series runs dry (a dry series stops and alerts, it never repeats old content).

Reads the Drive-synced state in data/ (run drive_state_sync.py pull first). Sends ONE Telegram message listing any series with
LOW_DAYS posts or fewer left (or a full table with --always). Never raises over a missing file.

    python scripts/ci/content_stock.py [--always] [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

IST = ZoneInfo("Asia/Kolkata")
DATA = Path("data")
LOW_DAYS = 14          # warn when this many posts (days) or fewer are left


def gita() -> tuple[int, int]:
    from mahanavi.content.bhagavad_gita_slokas import GITA_SLOKAS
    f = DATA / "last_gita_sloka_index.txt"
    idx = 0
    if f.exists():
        raw = f.read_text().strip().partition(":")[2] or f.read_text().strip()
        idx = int(raw) if raw.isdigit() else 0
    left = max(0, len(GITA_SLOKAS) - idx)
    return left * 2, len(GITA_SLOKAS)         # a verse day then a skipped quiz day: about 2 days per verse


def concepts() -> tuple[int, int]:
    from channels.engine import used_registry
    from mahanavi.content.purana_concept_shorts import PURANA_CONCEPT_SHORTS as C, is_paused
    from mahanavi.scripts.post_concept_short import concept_id
    used = used_registry.load("purana_concept_used.json")
    live = [c for c in C if not is_paused(c)]
    left = sum(1 for c in live if concept_id(c) not in used)
    return left * 2, len(live)         # one concept every other day


def temples() -> tuple[int, int]:
    from mahanavi.content import temple_secrets as ts
    f = DATA / "mahanavi_temple_secrets_state.json"
    try:
        used = json.loads(f.read_text()).get("used_ids", [])
    except (OSError, ValueError):
        used = []
    return ts.left(used) * 7, len(ts.TEMPLES)     # one temple a week


def chanakya() -> tuple[int, int]:
    from channels import chanakya_plan as p
    today = dt.datetime.now(IST).date()
    n = max(0, (today - p.SERIES_START).days) // p.STEP + 1
    total = p.cn.days()
    return max(0, total - n) * p.STEP, total


def lakshmi() -> tuple[int, int]:
    from channels import lakshmi108_plan as p
    today = dt.datetime.now(IST).date()
    return max(0, (p.LAST_DAY - today).days), 108


SERIES = [("Gita verse Shorts", gita), ("Purana Concept Shorts", concepts), ("Temple Secrets", temples),
          ("Chanakya Neeti", chanakya), ("Lakshmi 108 Names", lakshmi)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--always", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    rows, low = [], []
    for name, fn in SERIES:
        try:
            days, total = fn()
        except Exception as exc:  # noqa: BLE001
            rows.append(f"{name}: could not read ({type(exc).__name__})")
            continue
        rows.append(f"{name}: about {days} days of new content left (list size {total})")
        if days <= LOW_DAYS:
            low.append(f"{name}: only about {days} days left")
    text = "CONTENT STOCK\n" + "\n".join(rows)
    print(text)
    if low:
        text = "CONTENT RUNNING LOW, ask for a refill:\n" + "\n".join(low) + "\n\n" + text
    if (low or a.always) and not a.dry_run:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat = os.environ.get("TELEGRAM_CHAT_ID", "")
        if token and chat:
            data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
            try:
                urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=15).read()
                print("Telegram sent.")
            except Exception as exc:  # noqa: BLE001
                print(f"Telegram failed: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
