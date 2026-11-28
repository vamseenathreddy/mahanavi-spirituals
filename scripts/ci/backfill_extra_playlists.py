"""Create a series' extra playlists and copy the videos already in its main playlist into them (idempotent).
Usage: python scripts/ci/backfill_extra_playlists.py SERIES [MAX_ADDS]   (SERIES: vishnu_te, vedas_hi, lakshmi_te, ...)"""
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

    key = sys.argv[1]
    max_adds = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    lang = ep.CHANNELS[key][1]
    if key.startswith("lakshmi"):
        hi = key.endswith("_hi")
        title, desc = (ln.PLAYLIST_TITLE_HI, ln.PLAYLIST_DESC_HI) if hi else (ln.PLAYLIST_TITLE, ln.PLAYLIST_DESC)
    else:
        title, desc = pv.PLAYLISTS[key]
    yt = YouTubeShortsUploader(get_settings())._build_service()  # noqa: SLF001
    n = ep.backfill(yt, key, title, desc, lang, max_adds)
    print(f"{key}: added {n} videos to the extra playlists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
