"""Fill each mantra channel's Gayatri and Shloka playlists with the Shorts already posted, and take those Shorts
out of the main beej playlist so each playlist holds one kind of content.

  python scripts/ci/setup_kind_playlists.py [--apply]    (without --apply it only reports)

Never deletes a video; only removes the playlist ENTRY from the main beej playlist after the video is in its own."""
from __future__ import annotations

import sys
from pathlib import Path

from channels.beej import playlists as bp
from channels.engine import upload
from mahanavi.content import beej_mantras

GAYATRI = ("గాయత్రీ మంత్రం", "गायत्री मंत्र", "gayatri mantra")
SHLOKA = ("శ్లోకం", "श्लोक", "shloka")


def kind_of(title: str) -> str | None:
    low = title.lower()
    if any(m.lower() in low for m in GAYATRI):
        return "gayatri"
    if any(m.lower() in low for m in SHLOKA):
        return "shloka"
    return None


def main() -> int:
    apply = "--apply" in sys.argv
    rc = 0
    for key, cfg in beej_mantras.CHANNELS.items():
        token = Path("data") / cfg["token_file"]
        if not token.exists():
            print(f"::warning::{key}: token file {token} missing, skipped")
            rc = 1
            continue
        try:
            yt = upload.service(token)
            name = yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
            if cfg["expected"].lower() not in name.lower():
                print(f"::error::{key}: token acts as '{name}', expected '{cfg['expected']}'. Skipped.")
                rc = 1
                continue
            by_kind: dict[str, list[tuple[str, str]]] = {"gayatri": [], "shloka": []}
            for vid, title, _ in bp.channel_beej_videos(yt):
                k = kind_of(title)
                if k:
                    by_kind[k].append((vid, title))
            print(f"::notice::{key} [{name}] gayatri={len(by_kind['gayatri'])} shloka={len(by_kind['shloka'])}")
            for k, vids in by_kind.items():
                for v, t in vids:
                    print(f"   {k}: {v} {t[:70]}")
            if not apply:
                continue
            main_pid = bp.ensure_playlist(yt, key)
            for k, vids in by_kind.items():
                if not vids:
                    continue
                spec = bp.KIND_SPECS[(key, k)]
                pid = upload.find_or_create_playlist(yt, spec["title"], spec["description"], spec["language"])
                try:
                    present = bp.playlist_video_ids(yt, pid)
                except Exception:  # noqa: BLE001  a just-created playlist can 404 for a few seconds
                    import time
                    time.sleep(20)
                    present = bp.playlist_video_ids(yt, pid)
                added = sum(1 for v, _ in vids if bp.add_once(yt, v, pid, present))
                ids = {v for v, _ in vids}
                removed = 0
                for it in bp._pages(lambda t: yt.playlistItems().list(part="contentDetails", playlistId=main_pid, maxResults=50, pageToken=t)):  # noqa: SLF001
                    if it["contentDetails"].get("videoId") in ids:
                        upload._retry(lambda: yt.playlistItems().delete(id=it["id"]).execute())  # noqa: SLF001
                        removed += 1
                print(f"::notice::{key} {k} playlist {pid}: added {added}, now {len(present)}; removed {removed} from the main beej playlist")
        except Exception as exc:  # noqa: BLE001
            print(f"::error::{key}: {type(exc).__name__}: {str(exc)[:600]}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
