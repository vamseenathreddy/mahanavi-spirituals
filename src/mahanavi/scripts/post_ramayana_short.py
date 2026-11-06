"""Mahanavi: the daily Ramayana story Short (content/ramayana_daily.py), 10 days from 2026-11-06.

    python -m mahanavi.scripts.post_ramayana_short --dry-run --story 1
    STATE_FILE=data/mahanavi_ramayana_state.json POST_SLOT=ramayana python -m mahanavi.scripts.post_ramayana_short --public
Each story is posted once (slug in state["used_ids"]); the video joins the Ramayana Stories playlist.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import sys
import time
from zoneinfo import ZoneInfo

from channels.engine import state as state_mod
from channels.engine import upload as eng_upload
from mahanavi.config import PROJECT_ROOT, get_settings
from mahanavi.content import ramayana_daily as rd
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.images.request_card_renderer import RequestCardRenderer
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader
from mahanavi.scripts.post_request_short import upload

IST = ZoneInfo("Asia/Kolkata")
FPS = 30


def _light_sweep(path) -> None:
    """A soft diagonal band of warm light (RGBA); the video slides it across the picture like a slow lens flare."""
    import numpy as np
    from PIL import Image

    w, h = 1500, 1920
    x = np.arange(w)[None, :] - np.arange(h)[:, None] * 0.35        # diagonal
    d = (x - w * 0.45) / (w * 0.16)
    a = np.exp(-(d ** 2)) * 70                                       # peak alpha 70/255
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2], rgba[..., 3] = 255, 214, 150, a.astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(path)


def cinematic(bg, text, music, secs: float, out) -> None:
    """Slow push-in with a gentle drift on the picture, a travelling light sweep, a breathing glow and a vignette;
    the words and frame stay still on top. Music is trimmed/looped to the length with a fade in and out."""
    import subprocess
    from pathlib import Path

    light = Path(out).with_name("light.png")
    _light_sweep(light)
    frames = int(secs * FPS)
    fc = (
        f"[0:v]scale=2160:3840,zoompan=z='1.0+0.0009*on':x='(iw-iw/zoom)/2+sin(on/48)*46':"
        f"y='(ih-ih/zoom)/2+cos(on/61)*60':d={frames}:s=1080x1920:fps={FPS},"
        f"eq=brightness='0.03*sin(2*PI*t/3.3)':saturation=1.12,vignette=PI/5[bg];"
        f"[2:v]format=rgba[lt];[bg][lt]overlay=x='-w+(W+w)*t/{secs}':y=0:shortest=1[lit];"
        f"[lit][1:v]overlay=0:0,fade=t=in:st=0:d=0.5,fade=t=out:st={secs - 0.5}:d=0.5,format=yuv420p[v];"
        f"[3:a]atrim=0:{secs},afade=t=in:st=0:d=0.8,afade=t=out:st={secs - 1.2}:d=1.2[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(bg), "-i", str(text),
           "-loop", "1", "-i", str(light), "-stream_loop", "-1", "-i", str(music),
           "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{secs}", "-r", str(FPS),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default="")
    ap.add_argument("--story", type=int, default=0, help="force story number 1-10 (testing)")
    args = ap.parse_args(argv)
    settings = get_settings()
    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(IST).date()
    try:
        st = state_mod.load()
        story = next((s for s in rd.STORIES if s.n == args.story), None) if args.story else rd.next_story(today, st["used_ids"])
        if story is None:
            print("no Ramayana story due: no post")
            return 0
        spec = rd.build(story)
        print(f"{today} -> {spec.slug}: {spec.title}")
        out_dir = settings.output_dir / "ramayana" / spec.slug
        bg_png, text_png = RequestCardRenderer(settings).render_parts(spec, 0, out_dir)
        own = PROJECT_ROOT / "assets" / "music" / "ramayana_bg.mp3"   # owner's song, looped/trimmed by assemble()
        music = own if own.exists() else settings.alert_short_music_path
        if music is None or not music.exists():
            raise MahanaviError(f"Music file missing: {music}")
        video = out_dir / f"{spec.slug}.mp4"
        cinematic(bg_png, text_png, music, spec.total_seconds, video)
        print(f"Assembled: {video} ({spec.total_seconds:.1f}s)")
        if args.dry_run:
            return 0
        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if spec.expected_channel.lower() not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected '{spec.expected_channel}'.")
        pid = eng_upload.find_or_create_playlist(youtube, rd.PLAYLIST_TITLE, rd.PLAYLIST_DESC, "te")
        spec = dataclasses.replace(spec, description_te=(
            f"▶ రామాయణ కథల ప్లేలిస్ట్: https://www.youtube.com/playlist?list={pid}\n\n{spec.description_te}"))
        privacy = "private" if args.private else "public"
        video_id = upload(youtube, spec, video, privacy)
        print(f"Channel: {got}\nUploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        print(f"::notice::ramayana short uploaded ({privacy}): https://www.youtube.com/watch?v={video_id}")
        state_mod.mark_posted(st, today.isoformat(), spec.slug, video_id, True, dt.datetime.now(IST).isoformat())
        if story.slug not in st["used_ids"]:
            st["used_ids"].append(story.slug)
        state_mod.save(st)
        for attempt in (1, 2):
            try:
                eng_upload.add_to_playlist(youtube, video_id, pid)
                print("Playlist: added to Ramayana Stories")
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    print(f"WARNING: could not add to playlist: {type(exc).__name__}: {exc}", file=sys.stderr)
                else:
                    time.sleep(20)
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"::error::ramayana short failed: {str(exc)[:400]}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"::error::ramayana short failed: {type(exc).__name__}: {str(exc)[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
