"""Scrolling lifestyle video: 1920x1080, a tall text strip scrolling up over a dimmed background, with a narrator.
Each point is read aloud once and the scroll is timed to the voice: the point being read sits in the middle of the screen
(keyframes at the middle of each clip), so the scroll speeds up and slows down with the narration. The text is large and
the whole video is at least MIN_SECONDS (5 minutes). Text fades under soft top and bottom bands, so nothing is cut hard."""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from channels.engine.render import _font, _mixed_font
from channels.lifestyle import topics

W, H = 1920, 1080
MIN_SECONDS = 300
COL_L, COL_R = 120, 1800
GOLD, WHITE, SOFT = (255, 214, 120), (255, 255, 255), (236, 226, 204)
REPO = Path(__file__).resolve().parents[2]
FONTS = REPO / "channels/engine/assets/fonts"
TELUGU_PLAIN = REPO / "assets/fonts/Ponnala-Regular.ttf"
TELUGU_LATIN = REPO / "assets/fonts/NotoSansTelugu-Variable.ttf"


def _fonts(lang: str, size: int, bold: bool = False):
    if lang == "te":
        # Noto Telugu for everything: the decorative Ponnala draws the vowel sign ృ (as in స్మృతి) and some conjuncts badly
        font = _font(TELUGU_LATIN, size)
        if bold:
            try:
                font.set_variation_by_name("Bold")
            except OSError:
                pass
        return font
    return _font(FONTS / ("Hind-Bold.ttf" if bold else "Hind-Medium.ttf"), size)


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    return lines + ([cur] if cur else [])


def narration_texts(lang: str, theme: dict) -> list[str]:
    """What the narrator reads: the video title, then each point as 'title. body' (the source line is on screen only),
    then the subscribe line."""
    data = theme[lang]
    return [data["title"]] + [f"{t}. {b}" for t, b, _s in data["points"]] + [topics.CTA[lang]]


def build_strip(lang: str, theme: dict, tops: list | None = None, spans: list | None = None) -> Image.Image:
    """The whole scrolling text as one tall transparent image. `tops`, if given, is filled with each point's top y;
    `spans` with (top, bottom) of every narrated block: the heading, each point, the closing subscribe block."""
    data = theme[lang]
    probe = ImageDraw.Draw(Image.new("L", (W, 10)))
    f_head, f_title = _fonts(lang, 112, True), _fonts(lang, 92, True)
    f_body, f_src, f_num = _fonts(lang, 70), _fonts(lang, 44), _fonts(lang, 76, True)
    f_cta = _fonts(lang, 76, True)
    text_l = COL_L + 190
    body_w = COL_R - text_l

    blocks = []  # (kind, lines, font, color, y_extra_after)
    blocks.append(("head", _wrap(probe, data["title"], f_head, COL_R - COL_L), f_head, GOLD, 170))
    for i, (title, body, src) in enumerate(data["points"], start=1):
        blocks.append(("num", [str(i)], f_num, (30, 20, 8), 0))
        blocks.append(("title", _wrap(probe, title, f_title, body_w), f_title, GOLD, 14))
        blocks.append(("body", _wrap(probe, body, f_body, body_w), f_body, WHITE, 12))
        blocks.append(("src", _wrap(probe, f"({src})", f_src, body_w), f_src, SOFT, 130))
    blocks.append(("cta", _wrap(probe, topics.CTA[lang], f_cta, COL_R - COL_L), f_cta, GOLD, 40))
    blocks.append(("cta", _wrap(probe, topics.DISCLAIMER[lang], f_src, COL_R - COL_L), f_src, SOFT, 0))

    LH = 1.42
    total = 60
    for kind, lines, font, _c, after in blocks:
        if kind == "num":
            continue
        total += int(len(lines) * font.size * LH) + after
    strip = Image.new("RGBA", (W, total + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(strip)
    y, point_top = 30, 0
    span_top = 30
    for n, (kind, lines, font, color, after) in enumerate(blocks):
        if kind == "num":
            point_top = y
            span_top = y
            if tops is not None:
                tops.append(y)
            r = 58
            cx, cy = COL_L + 70, point_top + 66
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD)
            w = d.textlength(lines[0], font=font)
            d.text((cx - w / 2, cy - font.size * 0.62), lines[0], font=font, fill=color)
            continue
        if kind == "cta" and n == len(blocks) - 2 and spans is not None:
            span_top = y
        lh = int(font.size * LH)
        for ln in lines:
            if kind in ("head", "cta"):
                x = (W - d.textlength(ln, font=font)) / 2
            else:
                x = text_l
            d.text((x, y), ln, font=font, fill=color)
            y += lh
        if spans is not None and (kind == "head" or kind == "src" or (kind == "cta" and n == len(blocks) - 1)):
            if kind == "src":
                spans.append((span_top, y))
            elif kind == "head":
                spans.append((30, y))
            else:
                spans.append((span_top, y))
        y += after
    return strip.crop((0, 0, W, min(strip.height, y + 40)))


def background(path: Path) -> Image.Image:
    img = Image.open(path).convert("RGB")
    scale = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
    left, top = (img.width - W) // 2, (img.height - H) // 2
    img = img.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(6))
    return Image.blend(img, Image.new("RGB", (W, H), (8, 6, 4)), 0.74)


def fade_bands() -> Image.Image:
    """Opaque dark bands at the top and bottom that fade into the picture, hiding the text's hard entry and exit."""
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = band.load()
    for y in range(H):
        a = 0
        if y < 130:
            a = int(235 * (1 - y / 130))
        elif y > H - 130:
            a = int(235 * ((y - (H - 130)) / 130))
        if a:
            for x in range(W):
                px[x, y] = (8, 6, 4, a)
    return band


def scroll_expr(spans: list, starts: list, durs: list) -> str:
    """ffmpeg crop-y expression: block k is centred on screen at the middle of its narration, linear in between."""
    ys = [H + (a + b) / 2 - H / 2 for a, b in spans]
    ks = [s + d / 2 for s, d in zip(starts, durs)]
    parts = [f"{ys[0]:.1f}"]
    for i in range(len(ys) - 1):
        parts.append(f"+({ys[i + 1] - ys[i]:.2f})*clip((t-{ks[i]:.3f})/{ks[i + 1] - ks[i]:.3f},0,1)")
    return "".join(parts)


def chapter_seconds(starts: list) -> list[int]:
    """YouTube chapter times: the start of each point's narration (index 0 is the heading, the last the subscribe line)."""
    out, prev = [], -10
    for s in starts[1:-1]:
        prev = max(int(s), prev + 10)   # YouTube wants chapters at least 10 s apart
        out.append(prev)
    return out


def render(lang: str, theme: dict, bg_path: Path, music_path: Path, voice_path: Path, out: Path, workdir: Path,
           spans: list, starts: list, durs: list, total: float, fps: int = 15, preview_seconds: int | None = None) -> float:
    workdir.mkdir(parents=True, exist_ok=True)
    strip = build_strip(lang, theme)
    padded = Image.new("RGBA", (W, strip.height + 2 * H), (0, 0, 0, 0))  # room above and below so a plain crop can scroll
    padded.paste(strip, (0, H))
    padded.save(workdir / "strip.png")
    background(bg_path).save(workdir / "bg.png")
    fade_bands().save(workdir / "fade.png")
    run = float(preview_seconds) if preview_seconds else float(total)
    # `loop` keeps each still in memory (an image input with -loop 1 re-decodes the PNG every frame, ~5x slower), and
    # cropping a window out of the tall strip first keeps every frame cheap.
    fc = (f"[0:v]loop=loop=-1:size=1[b];[1:v]loop=loop=-1:size=1,crop={W}:{H}:0:'{scroll_expr(spans, starts, durs)}'[s];"
          f"[2:v]loop=loop=-1:size=1[f];[b][s]overlay=0:0[a];[a][f]overlay=0:0,format=yuv420p[v];"
          f"[3:a]volume=0.12,afade=t=in:d=2[m];[4:a]apad[vo];"
          f"[m][vo]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={max(run - 3, 0):.2f}:d=3[a2]")
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-framerate", str(fps), "-i", str(workdir / "bg.png"),
           "-framerate", str(fps), "-i", str(workdir / "strip.png"),
           "-framerate", str(fps), "-i", str(workdir / "fade.png"),
           "-stream_loop", "-1", "-i", str(music_path),
           "-i", str(voice_path),
           "-filter_complex", fc, "-map", "[v]", "-map", "[a2]",
           "-t", f"{run}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-r", str(fps),
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    return run
