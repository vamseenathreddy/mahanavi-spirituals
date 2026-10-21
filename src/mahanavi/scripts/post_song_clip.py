"""post_song_clip.py: one sung-line Short per run, cut from the owner's own songs (assets/songs).

Usage:
    python -m mahanavi.scripts.post_song_clip --dry-run            # render + assemble only, no upload
    python -m mahanavi.scripts.post_song_clip                      # upload UNLISTED (review in Studio)
    python -m mahanavi.scripts.post_song_clip --public             # upload public
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from mahanavi.config import get_settings
from mahanavi.content import song_clips
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.images.request_card_renderer import RequestCardRenderer
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader
from mahanavi.scripts.post_request_short import upload

IST = ZoneInfo("Asia/Kolkata")
FPS = 30


def assemble_clip(image: Path, clip: Path, seconds: float, out: Path) -> Path:
    """The card for the clip's length, with the clip's own audio (already faded and level-matched), no extra fades."""
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-t", f"{seconds:.2f}", "-i", str(image),
           "-i", str(clip), "-vf", "scale=1080:1920,setsar=1,format=yuv420p", "-t", f"{seconds:.2f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="", help="ISO date override (testing).")
    ap.add_argument("--offset", type=int, default=0, help="shift the rotation (e.g. a second Short on the same day).")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    try:
        spec, clip = song_clips.build(today, args.offset)
        print(f"{today} -> {spec.slug} ({spec.total_seconds:.1f}s) {clip.name}")
        out_dir = settings.output_dir / "song_clips" / spec.slug
        slides = RequestCardRenderer(settings).render_all(spec, out_dir)
        video = assemble_clip(slides[0].path, clip, spec.total_seconds, out_dir / f"{spec.slug}.mp4")
        print(f"Assembled: {video}")
        if args.dry_run:
            return 0
        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if spec.expected_channel.lower() not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected '{spec.expected_channel}'.")
        try:  # link the full song at the top of the description; never blocks the upload
            import dataclasses

            song = song_clips.pick(today, args.offset)[0]
            link = song_clips.full_video_link(youtube, song)
            if link:
                spec = dataclasses.replace(spec, description_te=f"▶ పూర్తి పాట / Full song: {link}\n\n{spec.description_te}")
                print(f"Full song: {link}")
            else:
                print("Note: full song not found on the channel; no link added.")
        except Exception as exc:  # noqa: BLE001
            print(f"Note: full-song link skipped ({type(exc).__name__}).")
        video_id = upload(youtube, spec, video, "public" if args.public else "unlisted")
        print(f"Channel: {got}\nUploaded: https://www.youtube.com/watch?v={video_id}")
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # googleapiclient HttpError etc.
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
