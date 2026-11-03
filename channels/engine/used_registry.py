"""Used-content registry: a Drive-synced JSON list of ids of content already published, per series.

Owner rule (2026-11-03): never repeat content. Before publishing, the poster checks the id here (plus the channel's own uploads);
after a successful upload it adds the id. Stdlib only. The file must exist in the Drive state folder (pre-created, see
drive_state_sync.py) so it survives between runs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

DATA_DIR = Path("data")


def content_id(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]


def load(name: str) -> set[str]:
    try:
        data = json.loads((DATA_DIR / name).read_text(encoding="utf-8"))
        return {str(x) for x in data} if isinstance(data, list) else set()
    except (OSError, ValueError):
        return set()


def add(name: str, cid: str) -> None:
    used = load(name)
    used.add(cid)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / name).write_text(json.dumps(sorted(used)), encoding="utf-8")
