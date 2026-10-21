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


def slide(bg: Path, head: str, en: str, te: str, out: Path, small: str = "") -> Path:
    im = _canvas(bg)
    d = ImageDraw.Draw(im)
    x0, x1 = PHOTO_W + 70, W - 70
    cx, mw = (x0 + x1) // 2, x1 - x0
    y = 170
    fh = _font(FONT_B, 76)
    for ln in _wrap(d, head, fh, mw):
        _centered(d, ln, fh, cx, y, GOLD)
        y += 98
    y += 50
    fe = _font(FONT_R, 54)
    for ln in _wrap(d, en, fe, mw):
        _centered(d, ln, fe, cx, y, WHITE)
        y += 74
    y += 40
    ft = _font(FONT_TE, 58)
    for ln in _wrap(d, te, ft, mw):
        _centered(d, ln, ft, cx, y, SOFT)
        y += 84
    if small:
        _centered(d, small, _font(FONT_R, 34), cx, H - 90, SOFT)
    _centered(d, "Ramana Maharshi TV", _font(FONT_R, 30), cx, H - 50, (190, 180, 165))
    im.save(out)
    return out


def title_slide(bg: Path, out: Path) -> Path:
    im = _canvas(bg)
    d = ImageDraw.Draw(im)
    x0, x1 = PHOTO_W + 70, W - 70
    cx, mw = (x0 + x1) // 2, x1 - x0
    y = 200
    f1 = _font(FONT_B, 70)
    for ln in _wrap(d, script.TITLE_EN, f1, mw):
        _centered(d, ln, f1, cx, y, GOLD)
        y += 92
    y += 40
    f2 = _font(FONT_TE, 60)
    for ln in _wrap(d, script.TITLE_TE, f2, mw):
        _centered(d, ln, f2, cx, y, WHITE)
        y += 86
    _centered(d, "Guided practice with silent sitting", _font(FONT_R, 40), cx, y + 50, SOFT)
    im.save(out)
    return out


def sources_slide(bg: Path, out: Path) -> Path:
    im = _canvas(bg)
    d = ImageDraw.Draw(im)
    x0, x1 = PHOTO_W + 70, W - 70
    cx, mw = (x0 + x1) // 2, x1 - x0
    _centered(d, "Sources", _font(FONT_B, 72), cx, 190, GOLD)
    y = 320
    f = _font(FONT_R, 44)
    for s in script.SOURCES:
        for ln in _wrap(d, s, f, mw):
            _centered(d, ln, f, cx, y, WHITE)
            y += 62
        y += 24
    _centered(d, "Subscribe for daily teachings in Telugu and English", _font(FONT_B, 46), cx, y + 50, GOLD)
    fs = _font(FONT_R, 30)
    _centered(d, "Explanation in our own words. Visuals are digitally created devotional artwork.", fs, cx, H - 100, SOFT)
    im.save(out)
    return out


def clip(image: Path, seconds: float, out: Path, zoom: bool = True) -> Path:
    fade = f"fade=t=in:st=0:d=1,fade=t=out:st={seconds - 1:.2f}:d=1,format=yuv420p"
    if zoom and seconds <= 40:
        frames = int(seconds * 24)
        vf = f"scale=2400:-1,zoompan=z='min(1+0.0003*on,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=24,{fade}"
    else:
        vf = f"scale={W}:{H},{fade}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(image), "-vf", vf, "-t", f"{seconds:.2f}",
                    "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(out)], check=True)
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
        clips.append(clip(img, secs, workdir / f"c{k:02d}.mp4"))
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
