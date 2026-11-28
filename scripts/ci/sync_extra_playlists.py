"""Daily top-up of the extra playlists of every series of one channel (idempotent, quota-safe).
Usage: python scripts/ci/sync_extra_playlists.py TOKEN_FILE_NAME [BUDGET]"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> int:
    from channels import extra_playlists as ep
    from mahanavi.config import get_settings
    from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader
    from mahanavi.scripts import post_lakshmi_name as ln
    from mahanavi.scripts import post_verse_series as pv

    token, budget = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 30
    for k, (title, _d) in pv.PLAYLISTS.items():
        ep.MAIN_TITLES[k] = title
    ep.MAIN_TITLES["lakshmi_te"], ep.MAIN_TITLES["lakshmi_hi"] = ln.PLAYLIST_TITLE, ln.PLAYLIST_TITLE_HI
    keys = [k for k, v in {**ep.CHANNELS, **ep.SYNC_ONLY}.items() if v[0] == token and k in ep.EXTRA]
    yt = YouTubeShortsUploader(get_settings())._build_service()  # noqa: SLF001
    left = budget
    for k in keys:
        if left <= 0:
            break
        n = ep.sync(yt, k, left)
        left -= n
        print(f"{k}: added {n}")
    print(f"done, {budget - left} additions (budget {budget})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
