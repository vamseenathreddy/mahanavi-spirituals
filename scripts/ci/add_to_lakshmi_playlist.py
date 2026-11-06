"""Add one video to the Lakshmi 108 Names playlist (find-or-create, never lists a video twice).
Usage: python scripts/ci/add_to_lakshmi_playlist.py VIDEO_ID [en|hi]"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> int:
    from channels.beej import playlists as pl
    from channels.engine import upload
    from mahanavi.config import get_settings
    from mahanavi.scripts import post_lakshmi_name as m

    vid = sys.argv[1]
    hi = len(sys.argv) > 2 and sys.argv[2] == "hi"
    from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader
    yt = YouTubeShortsUploader(get_settings())._build_service()  # noqa: SLF001
    pid = upload.find_or_create_playlist(yt, m.PLAYLIST_TITLE_HI if hi else m.PLAYLIST_TITLE, m.PLAYLIST_DESC_HI if hi else m.PLAYLIST_DESC, "hi" if hi else "te")
    print(f"playlist: https://www.youtube.com/playlist?list={pid}")
    print("added" if pl.add_once(yt, vid, pid) else "already listed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
