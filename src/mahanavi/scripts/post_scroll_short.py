"""post_scroll_short.py: builds and uploads a scrolling-lyrics Short (content/scroll_shorts.py).

    python -m mahanavi.scripts.post_scroll_short --spec hanuman_chalisa_scroll --dry-run
    python -m mahanavi.scripts.post_scroll_short --spec hanuman_chalisa_scroll --privacy public
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps

from mahanavi.config import get_settings
from mahanavi.content.scroll_shorts import SCROLL, ScrollShort
from mahanavi.exceptions import MahanaviError, YouTubeUploadError
from mahanavi.images.fonts import FontManager
from mahanavi.publishers.youtube_shorts_uploader import YouTubeShortsUploader

W, H = 720, 1280   # 720p keeps the 3-minute encode fast
FPS = 24
WHITE, GOLD, INK = (255, 255, 255), (255, 214, 120), (12, 6, 0)
FONT_SIZE, LINE_H, GAP_H, STROKE = 44, 75, 47, 4
START_Y, END_Y = 667, 427   # where the text block starts on screen, and how far up the last line travels


def news_background(person: str, out: Path) -> Path:
    """Dark TDP-yellow gradient with the leader's cut-out, large and dimmed, behind the scrolling text."""
    root = Path(__file__).resolve().parents[3] / "channels/trending/assets/people"
    top, bot = (70, 52, 0), (8, 6, 0)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    p = Image.open(root / f"{person}.png").convert("RGBA")
    p = p.resize((int(p.width * 1000 / p.height), 1000), Image.LANCZOS)
    fade = Image.new("L", p.size, 255)   # the cut-out ends at the shoulders: fade the bottom so there is no hard edge
    fd = ImageDraw.Draw(fade)
    for i in range(380):
        fd.line((0, p.height - 1 - i, p.width, p.height - 1 - i), fill=int(255 * i / 380))
    a = ImageChops.multiply(p.getchannel("A"), fade).point(lambda v: int(v * 0.35))
    p.putalpha(a)
    img.paste(p, ((W - p.width) // 2, 40), p)
    img.save(out, quality=95)
    return out


def background(spec: ScrollShort, out: Path) -> Path:
    from mahanavi.images.deity_bg import DEITIES

    if spec.bg.startswith("news:"):
        return news_background(spec.bg.split(":", 1)[1], out)
    img = Image.open(DEITIES / spec.photo).convert("RGB")
    img = ImageOps.fit(img, (W, H), method=Image.LANCZOS, centering=(0.5, 0.4))
    img = ImageEnhance.Brightness(img).enhance(1 - spec.dim)
    img.save(out, quality=95)
    return out


def text_layer(spec: ScrollShort, settings, out: Path) -> tuple[Path, int]:
    if spec.lang == "hi":   # Devanagari: Hind (the Telugu font has no Devanagari glyphs)
        from mahanavi.images.request_card_renderer import ENGINE_FONTS

        font = ImageFont.truetype(str(ENGINE_FONTS / "Hind-Bold.ttf"), FONT_SIZE, layout_engine=ImageFont.Layout.RAQM)
    else:
        font = FontManager(settings.telugu_font_path).get_font(size=FONT_SIZE, weight="Bold")
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    max_w = W - 90

    def fit(ln: str) -> list[str]:
        """A line wider than the screen is split at the space that balances the two halves."""
        if not ln or probe.textlength(ln, font=font) <= max_w:
            return [ln]
        words = ln.split(" ")
        best = min(range(1, len(words)), key=lambda i: abs(probe.textlength(" ".join(words[:i]), font=font)
                                                           - probe.textlength(" ".join(words[i:]), font=font)))
        return fit(" ".join(words[:best])) + fit(" ".join(words[best:]))

    heads: list[bool] = []   # a source line starting with "§" is a gold heading (all its wrapped pieces are gold)
    lines: list[str] = []
    for src in spec.lines:
        head = src.startswith("§")
        for piece in fit(src[1:] if head else src):
            lines.append(piece)
            heads.append(head)
    widest = max(probe.textlength(ln, font=font) for ln in lines)
    assert widest <= W - 40, f"a line is still wider than the screen ({widest:.0f}px)"
    heights, y = [], 0
    for ln in lines:
        heights.append(LINE_H if ln else GAP_H)
    total = sum(heights) + 80
    layer = Image.new("RGBA", (W, total), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    blocks_seen, in_block = 0, False
    y = 40
    for ln, h, head in zip(lines, heights, heads):
        if not ln:
            in_block = False
            y += h
            continue
        if not in_block:
            blocks_seen += 1
            in_block = True
        colour = GOLD if (head or blocks_seen <= spec.gold_lines) else WHITE
        x = (W - probe.textlength(ln, font=font)) / 2
        d.text((x, y), ln, font=font, fill=colour, stroke_width=STROKE, stroke_fill=INK)
        y += h
    layer.save(out)
    return out, total


def build(spec: ScrollShort, settings, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    bg = background(spec, out_dir / "bg.png")
    txt, th = text_layer(spec, settings, out_dir / "text.png")
    music = (Path(__file__).resolve().parents[3] / spec.music) if spec.music else settings.alert_short_music_path
    if music is None or not music.exists():
        raise MahanaviError(f"Music file missing: {music}")
    if spec.seconds <= 0:   # news payloads: reading time from the amount of text (about 50 px/s, 25-150 s)
        import dataclasses

        spec = dataclasses.replace(spec, seconds=min(150.0, max(25.0, (START_Y - END_Y + th) / 50.0)))
    speed = (START_Y - END_Y + th) / spec.seconds
    video = out_dir / f"{spec.slug}.mp4"
    fc = (f"[0:v]scale={W}:{H},setsar=1,fps={FPS}[b];"
          f"[1:v]format=rgba[t];"
          f"[b][t]overlay=x=0:y='{START_Y}-{speed:.4f}*t':shortest=1,format=yuv420p[v];"
          f"[2:a]afade=t=in:st=0:d=1.5,afade=t=out:st={spec.seconds - 2:.1f}:d=2[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-t", f"{spec.seconds:.1f}", "-i", str(bg),
           "-loop", "1", "-framerate", str(FPS), "-t", f"{spec.seconds:.1f}", "-i", str(txt),
           "-stream_loop", "-1", "-i", str(music), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-t", f"{spec.seconds:.1f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(video)]
    subprocess.run(cmd, check=True)
    return video


def upload(youtube, spec: ScrollShort, video: Path, privacy: str) -> str:
    from googleapiclient.http import MediaFileUpload

    from mahanavi.content.alert_seo import _CHANNEL_FOOTER_EN, _CHANNEL_FOOTER_TE
    from mahanavi.content.branding import brand_tags, brand_title
    from mahanavi.publishers.youtube_shorts_uploader import DEFAULT_CATEGORY_ID

    mahanavi = "mahanavi" in spec.expected_channel.lower()
    if mahanavi:
        desc = (f"{spec.description}\n\n{_CHANNEL_FOOTER_TE}\n\n---\n\n{spec.description_en}\n\n{_CHANNEL_FOOTER_EN}\n\n"
                f"{' '.join(spec.hashtags)}")
    else:
        desc = f"{spec.description}\n\n{' '.join(spec.hashtags)}"
    body = {
        "snippet": {"title": brand_title(spec.title) if mahanavi else spec.title, "description": desc,
                    "tags": brand_tags(spec.tags) if mahanavi else spec.tags, "categoryId": DEFAULT_CATEGORY_ID,
                    "defaultLanguage": spec.lang, "defaultAudioLanguage": spec.lang},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        "localizations": {"en": {"title": spec.title_en, "description": spec.description_en}},
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
    return str(youtube.videos().insert(part="snippet,status,localizations", body=body, media_body=media).execute()["id"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", default="hanuman_chalisa_scroll", choices=sorted(SCROLL) + ["news_custom"])
    ap.add_argument("--payload", help="JSON file for --spec news_custom (title, title_en, lines, person, sources)")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.spec == "news_custom":
        import json

        from mahanavi.content.scroll_shorts import news_spec

        spec = news_spec(json.loads(Path(args.payload).read_text(encoding="utf-8")))
    else:
        spec = SCROLL[args.spec]
    settings = get_settings()
    try:
        video = build(spec, settings, settings.output_dir / "scroll_shorts" / spec.slug)
        print(f"Assembled: {video} ({spec.seconds:.0f}s)")
        if args.dry_run:
            return 0
        youtube = YouTubeShortsUploader(settings)._build_service()  # noqa: SLF001
        got = youtube.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]
        if spec.expected_channel.lower() not in got.lower():
            raise MahanaviError(f"NOT posting: the token acts as channel '{got}', expected '{spec.expected_channel}'.")
        vid = upload(youtube, spec, video, args.privacy)
        print(f"Channel: {got}\nUploaded ({args.privacy}): https://www.youtube.com/watch?v={vid}")
        print(f"::notice::scroll short uploaded ({args.privacy}): https://www.youtube.com/watch?v={vid}")
        return 0
    except (MahanaviError, YouTubeUploadError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        print(f"::error::scroll short failed: {str(exc)[:400]}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"::error::scroll short failed: {type(exc).__name__}: {str(exc)[:400]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
