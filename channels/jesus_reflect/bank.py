"""Telugu 'Vamsee reflection' scripts for Jesus Worship Waves: a Bible quote, a short illustrative story, the owner's
opinion, a prayer, and the signature. Posted Wednesday and Sunday, in order (state key 'reflect_idx')."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "reflections.json"


def load() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))["items"]


def pick(index: int) -> tuple[int, dict]:
    items = load()
    return index, items[index % len(items)]
