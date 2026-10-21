"""1920x1080 Self-enquiry video: one slide per step (portrait photo on the left, bilingual text on the right), narration,
the channel's own Om music under it (ducked while the narrator speaks), silent practice pauses, a sources card at the end."""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from channels.ramana_long import audio, script

REPO = Path(__file__).resolve().parents[2]
BG_DIR = REPO / "ramana/assets/backgrounds"
FONT_B = REPO / "ramana/assets/fonts/Poppins-Bold.ttf"
FONT_R = REPO / "ramana/assets/fonts/Poppins-Regular.ttf"
FONT_TE = REPO / "ramana/assets/fonts/Ponnala-Regular.ttf"
W, H = 1920, 1080
GOLD, WHITE, SOFT = (244, 196, 100), (255, 255, 255), (222, 214, 200)
PHOTO_W = 780


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}".strip()
        if draw.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + ([cur] if cur else [])


def backgrounds() -> list[Path]:
    return sorted(BG_DIR.glob("*.jpg")) + sorted(BG_DIR.glob("*.webp")) + sorted(BG_DIR.glob("*.png"))


def _canvas(bg: Path) -> Image.Image:
    """Blurred, darkened cover of the photo fills the frame; the sharp portrait sits on the left."""
    src = Image.open(bg).convert("RGB")
    base = ImageOps.fit(src, (W, H), method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    base = Image.blend(base, Image.new("RGB", (W, H), (8, 6, 4)), 0.72)
    sharp = ImageOps.fit(src, (PHOTO_W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.3))
    base.paste(sharp, (0, 0))
    d = ImageDraw.Draw(base)
    d.rectangle((PHOTO_W, 0, PHOTO_W + 5, H), fill=GOLD)
    return base


def _centered(d, text, font, cx, y, fill, stroke=0):
    d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


PANEL_X0, PANEL_X1 = PHOTO_W + 70, W - 70
CX = (PANEL_X0 + PANEL_X1) // 2
CHAKRA_R = 430  # centre of the right panel; rotates behind the text
CHAKRA_BOX = 2 * CHAKRA_R + 40


def _layout(blocks, top, bottom, max_scale=1.6):
    """blocks: [(text, path, base_size, colour, gap_after)]. Picks the largest scale whose wrapped text fits the panel
    height and returns draw ops [(line, font, colour, y)] centred vertically, so short texts fill the space."""
    probe = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    mw = PANEL_X1 - PANEL_X0
    scale = max_scale
    while True:
        ops, y = [], 0
        for text, path, size, col, gap in blocks:
            f = _font(path, int(size * scale))
            for ln in _wrap(probe, text, f, mw):
                ops.append((ln, f, col, y))
                y += int(f.size * 1.36)
            y += int(gap * scale)
        total = y - int(blocks[-1][4] * scale)
        if total <= bottom - top or scale <= 0.7:
            break
        scale -= 0.05
    off = top + (bottom - top - total) // 2
    return [(ln, f, col, yy + off) for ln, f, col, yy in ops]


def _render(bg: Path, blocks, out: Path, top=80, bottom=H - 120, footer: str = "", small: str = ""):
    """Writes <out>_bg.png (opaque), <out>_chakra.png (transparent, centred on the bindu) and <out>_text.png (transparent)."""
    from mahanavi.images.sri_chakra import render_sri_chakra_png

    _canvas(bg).save(out.with_name(out.stem + "_bg.png"))
    render_sri_chakra_png(out.with_name(out.stem + "_chakra.png"), (CHAKRA_BOX, CHAKRA_BOX), CHAKRA_R,
                          accent=(244, 196, 100, 160), line_width=3)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for ln, f, col, y in _layout(blocks, top, bottom):
        _centered(d, ln, f, CX, y, col, stroke=2)
    if small:
        _centered(d, small, _font(FONT_R, 34), CX, H - 100, SOFT)
    _centered(d, footer or "Ramana Maharshi TV", _font(FONT_R, 30), CX, H - 52, (190, 180, 165))
    im.save(out.with_name(out.stem + "_text.png"))
    return out


def slide(bg: Path, head: str, en: str, te: str, out: Path, small: str = "") -> Path:
    return _render(bg, [(head, FONT_B, 76, GOLD, 50), (en, FONT_R, 54, WHITE, 40), (te, FONT_TE, 58, SOFT, 0)], out,
                   top=80, bottom=H - (150 if small else 90), small=small)


def title_slide(bg: Path, out: Path) -> Path:
    return _render(bg, [(script.TITLE_EN, FONT_B, 70, GOLD, 40), (script.TITLE_TE, FONT_TE, 60, WHITE, 40),
                        ("Guided practice with silent sitting", FONT_R, 40, SOFT, 0)], out)


def sources_slide(bg: Path, out: Path) -> Path:
    blocks = [("Sources", FONT_B, 72, GOLD, 40)]
    blocks += [(s_, FONT_R, 44, WHITE, 24) for s_ in script.SOURCES]
    blocks += [("Subscribe for daily teachings in Telugu and English", FONT_B, 46, GOLD, 0)]
    return _render(bg, blocks, out, top=80, bottom=H - 130,
                   footer="Explanation in our own words. Visuals are digitally created devotional artwork.")


def clip(stem: Path, seconds: float, out: Path, t0: float = 0.0) -> Path:
    """Photo backdrop, Sri Chakra turning slowly in place behind the text (one turn per 120 s, continuous across slides)."""
    bgp, ch, tx = (stem.with_name(stem.stem + n) for n in ("_bg.png", "_chakra.png", "_text.png"))
    ang = f"2*PI*(t+{t0:.2f})/120"
    x, y = CX - CHAKRA_BOX // 2, H // 2 - CHAKRA_BOX // 2
    fc = (f"[1:v]format=rgba,rotate=a='{ang}':c=none:ow=iw:oh=ih[c];"
          f"[0:v][c]overlay={x}:{y}:format=auto[b];[b][2:v]overlay=0:0:format=auto,"
          f"fade=t=in:st=0:d=1,fade=t=out:st={seconds - 1:.2f}:d=1,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "24", "-loop", "1", "-i", str(bgp),
                    "-framerate", "24", "-loop", "1", "-i", str(ch), "-framerate", "24", "-loop", "1", "-i", str(tx),
                    "-filter_complex", fc, "-map", "[v]", "-t", f"{seconds:.2f}", "-r", "24", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "22", str(out)], check=True)
    return out


def build(workdir: Path, out_mp4: Path, fake_voice: bool = False) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    speak = audio.fake_speak if fake_voice else audio.speak
    bgs = backgrounds()
    segments = []  # (image, voice, seconds, chapter label)
    for i, s in enumerate(script.SLIDES):
        vp = speak(s["say"], workdir / f"v{i:02d}.mp3")
        bg = bgs[i % len(bgs)]
        img = (title_slide(bg, workdir / f"s{i:02d}.png") if i == 0 else
               slide(bg, s["head"], s["en"], s["te"], workdir / f"s{i:02d}.png",
                     small="Sit quietly. Eyes closed or softly open." if s["pause"] >= 100 else ""))
        segments.append((img, vp, audio.duration(vp) + s["pause"], s["label"]))
    last = bgs[len(script.SLIDES) % len(bgs)]
    segments.append((sources_slide(last, workdir / "s_end.png"), speak("Om Shanti.", workdir / "v_end.mp3"), 9.0, "Sources"))
    total = sum(sg[2] for sg in segments)

    clips, voice_parts, chapters, t = [], [], [], 0.0
    sil = workdir / "sil"
    sil.mkdir(exist_ok=True)
    for k, (img, vp, secs, label) in enumerate(segments):
        clips.append(clip(img, secs, workdir / f"c{k:02d}.mp4", t0=t))
        voice_parts += [vp, audio.silence(sil / f"g{k:02d}.mp3", max(0.2, secs - audio.duration(vp)))]
        chapters.append((int(t), label))
        t += secs
    (workdir / "clips.txt").write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
    (workdir / "voice.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in voice_parts), encoding="utf-8")
    bed = audio.om_bed(workdir / "bed.wav")
    mix = ("[1:a]aresample=44100,volume=2.0,asplit=2[v][vsc];"
           "[2:a]aresample=44100,lowpass=f=5000,volume=0.40[m0];"
           "[m0][vsc]sidechaincompress=threshold=0.015:ratio=8:attack=30:release=900:makeup=1[m];"
           f"[v][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,afade=t=out:st={total - 5:.2f}:d=5[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(workdir / "clips.txt"),
                    "-f", "concat", "-safe", "0", "-i", str(workdir / "voice.txt"), "-stream_loop", "-1", "-i", str(bed),
                    "-filter_complex", mix, "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", str(out_mp4)], check=True)
    return {"duration": round(total, 1), "chapters": chapters}


def thumbnail(out: Path) -> Path:
    bg = backgrounds()[0]
    src = Image.open(bg).convert("RGB")
    im = ImageOps.fit(src, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.25))
    im = Image.blend(im, Image.new("RGB", (1280, 720), (8, 6, 4)), 0.52)
    d = ImageDraw.Draw(im)
    f1, f2, f3, ft = _font(FONT_B, 92), _font(FONT_B, 78), _font(FONT_R, 44), _font(FONT_TE, 64)
    _centered(d, "MEDITATION TECHNIQUE", f1, 640, 110, WHITE, 3)
    _centered(d, "OF RAMANA MAHARSHI", f2, 640, 240, GOLD, 2)
    _centered(d, "నేను ఎవరిని? ఆత్మవిచారణ", ft, 640, 380, WHITE, 2)
    _centered(d, "Self-Enquiry step by step | Guided practice", f3, 640, 540, WHITE)
    im.save(out, quality=92)
    return out
