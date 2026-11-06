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
    """Rainbow-coloured butterflies that flutter very slowly across the picture (RGBA PNG sequence; ffmpeg overlays it)."""
    import math
    import random

    from PIL import Image, ImageDraw, ImageFilter

    folder.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(11)
    w, h = 1080, 1920
    rainbow = [(255, 70, 70), (255, 150, 40), (255, 220, 60), (90, 220, 110), (60, 200, 240), (90, 120, 255), (190, 100, 255), (255, 110, 200)]
    flies = []
    for i in range(9):
        flies.append(dict(x=rnd.uniform(80, w - 80), y=rnd.uniform(200, h - 200), s=rnd.choice([44, 52, 60, 70]), c=rainbow[i % 8],
                          vx=rnd.uniform(-60, 60), vy=rnd.uniform(-120, -55), sway=rnd.uniform(50, 100), ph=rnd.uniform(0, 6.28),
                          fr=rnd.uniform(1.6, 2.3)))

    UP = [(0.05, -0.05), (0.22, -0.55), (0.62, -0.95), (0.98, -0.78), (1.0, -0.4), (0.78, -0.08), (0.3, 0.04)]
    LO = [(0.05, 0.0), (0.7, 0.0), (0.88, 0.32), (0.7, 0.72), (0.38, 0.82), (0.12, 0.45)]

    for f in range(int(secs * FPS)):
        t = f / FPS
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for b in flies:
            x = (b["x"] + b["vx"] * t + math.sin(t * 1.1 + b["ph"]) * b["sway"]) % w
            y = (b["y"] + b["vy"] * t + math.cos(t * 0.8 + b["ph"]) * b["sway"] * 0.6) % h
            s = b["s"] * 2                                   # drawn at 2x, then shrunk for smooth edges
            flap = 0.22 + 0.78 * abs(math.cos(2 * math.pi * b["fr"] * t + b["ph"]))
            rot = math.sin(t * 1.1 + b["ph"]) * 0.4
            size = int(s * 2.4)
            lay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ox = oy = size / 2
            col = b["c"]
            light = tuple(min(255, c + 80) for c in col)
            dark = tuple(int(c * 0.55) for c in col)
            for side in (-1, 1):
                for shape, tone in ((LO, dark), (UP, col)):
                    pts = [(ox + side * px * s * flap, oy + py * s) for px, py in shape]
                    ld.polygon(pts, fill=tone + (235,), outline=(30, 15, 10, 230))
                    cxp = sum(px for px, _ in shape) / len(shape)
                    cyp = sum(py for _, py in shape) / len(shape)
                    inner = [(ox + side * (cxp + (px - cxp) * 0.55) * s * flap, oy + (cyp + (py - cyp) * 0.55) * s) for px, py in shape]
                    ld.polygon(inner, fill=light + (170,))
            ld.ellipse((ox - s * 0.05, oy - s * 0.35, ox + s * 0.05, oy + s * 0.55), fill=(30, 15, 10, 255))
            ld.line((ox, oy - s * 0.32, ox - s * 0.18, oy - s * 0.6), fill=(30, 15, 10, 255), width=max(2, int(s * 0.03)))
            ld.line((ox, oy - s * 0.32, ox + s * 0.18, oy - s * 0.6), fill=(30, 15, 10, 255), width=max(2, int(s * 0.03)))
            lay = lay.rotate(-math.degrees(rot), resample=Image.Resampling.BICUBIC).resize((size // 2, size // 2), Image.Resampling.LANCZOS)
            im.alpha_composite(lay, (int(x - size / 4), int(y - size / 4)))
        im.filter(ImageFilter.GaussianBlur(0.7)).save(folder / f"d{f:04d}.png")


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
        f"[2:v]format=rgba[dt];[bg][dt]overlay=0:0:shortest=1[lit];"
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
