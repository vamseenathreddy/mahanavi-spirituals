"""A short random pause right before an upload, so the second a Short goes live is never the same two days running.

Every posting job already picks a day-seeded random MINUTE inside its window (channels/engine/gate.py); this adds a random 0-59 SECOND
on top (owner request 2026-11-02, all channels). The repo is public, so the extra runner time is free. POST_JITTER=off skips it (tests).
"""
from __future__ import annotations

import os
import random
import time


def pause(label: str = "") -> int:
    """Sleep a random 0-59 s (SystemRandom, so two jobs in the same second still differ) and return the seconds slept."""
    if os.environ.get("POST_JITTER", "").lower() in ("off", "0", "false", "no"):
        return 0
    secs = random.SystemRandom().randint(0, 59)
    print(f"Random posting second: waiting {secs}s before the upload{' (' + label + ')' if label else ''}.", flush=True)
    time.sleep(secs)
    return secs
