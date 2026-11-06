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


def _dust(folder, secs: float) -> None:
    """Golden dust motes that drift slowly upward and twinkle (RGBA PNG sequence at half size; ffmpeg scales it up)."""
    import random

    from PIL import Image, ImageDraw, ImageFilter

    folder.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(7)
    w, h, n = 540, 960, 70
    motes = [dict(x=rnd.uniform(0, w), y=rnd.uniform(0, h), r=rnd.choice([2, 2, 3, 3, 4, 6]), v=rnd.uniform(14, 40),
                  sway=rnd.uniform(6, 18), ph=rnd.uniform(0, 6.28), tw=rnd.uniform(0.6, 1.6)) for _ in range(n)]
    import math

    for f in range(int(secs * FPS)):
        t = f / FPS
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for m in motes:
            y = (m["y"] - m["v"] * t) % h
            x = m["x"] + math.sin(t * 0.7 + m["ph"]) * m["sway"]
            a = int(120 + 110 * math.sin(t * m["tw"] * 3 + m["ph"]))
            r = m["r"]
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 220, 140, max(0, min(255, a))))
        im.filter(ImageFilter.GaussianBlur(1.6)).save(folder / f"d{f:04d}.png")


def cinematic(bg, text, music, secs: float, out) -> None:
    """One steady, slow push-in on the picture, drifting golden dust over it and a soft vignette; the words and frame stay
    still on top. Music is trimmed/looped to the length with a fade in and out."""
    import shutil
    import subprocess
    from pathlib import Path

    dust = Path(out).with_name("dust")
    _dust(dust, secs)
    frames = int(secs * FPS)
    fc = (
        f"[0:v]scale=2160:3840,zoompan=z='1.0+0.00055*on':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={frames}:s=1080x1920:fps={FPS},"
        f"vignette=PI/5[bg];"
        f"[2:v]scale=1080:1920,format=rgba[dt];[bg][dt]overlay=0:0:shortest=1[lit];"
        f"[lit][1:v]overlay=0:0,fade=t=in:st=0:d=0.5,fade=t=out:st={secs - 0.5}:d=0.5,format=yuv420p[v];"
        f"[3:a]atrim=0:{secs},afade=t=in:st=0:d=0.8,afade=t=out:st={secs - 1.2}:d=1.2[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(bg), "-i", str(text),
           "-framerate", str(FPS), "-i", str(dust / "d%04d.png"), "-stream_loop", "-1", "-i", str(music),
           "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{secs}", "-r", str(FPS),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", str(out)]
    try:
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(dust, ignore_errors=True)


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
