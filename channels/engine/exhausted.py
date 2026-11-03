"""One shared way to stop a series that has run out of NEW content.

Owner rule (2026-11-03): if a channel has no fresh content for a Short, never repeat an old one. Stop, post nothing, and tell
the owner on Telegram. stop() prints a clear message, sends one Telegram alert and returns 0, so the calling script ends with
exit code 0 (the workflow's "mark today done" step then keeps the other pings of the same window from alerting again).

Stdlib only; secrets come from the environment (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, or the MAHANAVI_ prefixed names).
Never raises: an alert problem must not break a pipeline."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def stop(slot: str, what: str) -> int:
    msg = f"NO NEW CONTENT for {slot}: {what}. Nothing was posted (old content is never repeated). Add new content to resume."
    print(f"::error title=No new content ({slot})::{msg}")
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("MAHANAVI_TELEGRAM_BOT_TOKEN") or ""
    chat = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("MAHANAVI_TELEGRAM_CHAT_ID") or ""
    if token and chat:
        try:
            data = urllib.parse.urlencode({"chat_id": chat, "text": msg}).encode()
            urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=15).read()
            print("Telegram alert sent.")
        except Exception as exc:  # noqa: BLE001
            print(f"Telegram alert failed: {type(exc).__name__}: {exc}")
    else:
        print("Telegram secrets not set in this step, alert not sent.")
    return 0
