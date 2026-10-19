"""1920x1080 verse video: one slide per verse (photo background with a slow zoom, big verse text, gold reference),
narration read aloud, an original ambient pad under it, a short subscribe card at the end."""
from __future__ import annotations

import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from channels.jesus_long import audio

REPO = Path(__file__).resolve().parents[2]
BG_DIR = REPO / "channels/jesus/assets/backgrounds"
FONT_B = REPO / "ramana/assets/fonts/Poppins-Bold.ttf"
FONT_R = REPO / "ramana/assets/fonts/Poppins-Regular.ttf"
W, H = 1920, 1080
GOLD, WHITE = (255, 214, 140), (255, 255, 255)
PAUSE = 9.0          # seconds of quiet after each verse is read
MIN_TOTAL = 8 * 60 + 20   # long enough for mid-roll ads (8 minutes) with a little room
SUBSCRIBE_EN = "You may never see this channel again unless you subscribe right now"


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


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
    return sorted(BG_DIR.glob("*.webp")) + sorted(BG_DIR.glob("*.jpg")) + sorted(BG_DIR.glob("*.png"))


def _photo(path: Path, shade: float = 0.62) -> Image.Image:
    im = ImageOps.fit(Image.open(path).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    im = im.filter(ImageFilter.GaussianBlur(2))
    dark = Image.new("RGB", (W, H), (6, 10, 24))
    return Image.blend(im, dark, shade)


def verse_slide(bg: Path, text: str, ref: str, out: Path) -> Path:
    im = _photo(bg)
    d = ImageDraw.Draw(im)
    size = 86
    while True:
        f = _font(FONT_B, size)
        lines = _wrap(d, text, f, 1500)
        lh = int(size * 1.32)
        total = len(lines) * lh + 130
        if total <= 800 or size <= 44:
            break
        size -= 4
    y = (H - total) // 2
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0))
        y += lh
    fr = _font(FONT_B, 54)
    d.text(((W - d.textlength(ref, font=fr)) / 2, y + 36), ref, font=fr, fill=GOLD, stroke_width=1, stroke_fill=(0, 0, 0))
    fh = _font(FONT_R, 30)
    d.text((W - 330, H - 60), "@Jesusworshipwaves", font=fh, fill=(200, 210, 230))
    im.save(out)
    return out


def title_slide(bg: Path, heading: str, sub: str, out: Path) -> Path:
    im = _photo(bg, 0.55)
    d = ImageDraw.Draw(im)
    f1, f2 = _font(FONT_B, 96), _font(FONT_R, 52)
    lines = _wrap(d, heading, f1, 1600)
    y = H // 2 - len(lines) * 62 - 20
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f1)) / 2, y), ln, font=f1, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0))
        y += 124
    d.text(((W - d.textlength(sub, font=f2)) / 2, y + 20), sub, font=f2, fill=GOLD)
    im.save(out)
    return out


def subscribe_slide(bg: Path, out: Path) -> Path:
    im = _photo(bg, 0.6)
    d = ImageDraw.Draw(im)
    f1, f2 = _font(FONT_B, 76), _font(FONT_R, 44)
    lines = _wrap(d, SUBSCRIBE_EN, f1, 1500)
    y = H // 2 - len(lines) * 50 - 30
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f1)) / 2, y), ln, font=f1, fill=GOLD, stroke_width=2, stroke_fill=(0, 0, 0))
        y += 100
    tag = "Jesus Worship Waves  |  Bible verses with worship music"
    d.text(((W - d.textlength(tag, font=f2)) / 2, y + 40), tag, font=f2, fill=WHITE)
    im.save(out)
    return out


def clip(image: Path, seconds: float, out: Path, zoom: bool = True) -> Path:
    frames = int(seconds * 24)
    vf = (f"scale=2400:-1,zoompan=z='min(1+0.0004*on,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=24,"
          f"fade=t=in:st=0:d=1,fade=t=out:st={seconds - 1:.2f}:d=1,format=yuv420p") if zoom else \
        f"scale={W}:{H},fade=t=in:st=0:d=1,fade=t=out:st={seconds - 1:.2f}:d=1,format=yuv420p"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(image), "-vf", vf, "-t", f"{seconds:.2f}",
                    "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", str(out)], check=True)
    return out


def build(theme_key: str, theme: dict, workdir: Path, out_mp4: Path, seed: int = 0) -> dict:
    """Returns {'duration', 'chapters': [(seconds, label)], 'verses': n}."""
    workdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    bgs = backgrounds()
    rng.shuffle(bgs)
    verses = theme["verses"]
    heading = f"{len(verses)} Bible Verses for {theme['title']}"
    segments = []   # (image, voice_path_or_None, seconds, chapter_label)
    intro_text = (f"Welcome to Jesus Worship Waves. Take a slow, deep breath. These are {len(verses)} Bible verses for {theme['phrase']}. "
                  "Let the word of God settle your heart.")
    iv = audio.speak(intro_text, workdir / "intro.mp3")
    segments.append((title_slide(bgs[0], heading, "Scripture reading with soft worship music", workdir / "s_intro.png"), iv,
                     audio.duration(iv) + 3.0, "Introduction"))
    for i, v in enumerate(verses):
        vp = audio.speak(f"{v['text']} {v['ref']}.", workdir / f"v{i:02d}.mp3")
        img = verse_slide(bgs[(i + 1) % len(bgs)], v["text"], v["ref"], workdir / f"s{i:02d}.png")
        segments.append((img, vp, audio.duration(vp) + PAUSE, v["ref"]))
    outro_text = "May the Lord bless you and keep you. If this brought you peace, subscribe, and share it with someone who needs it. Amen."
    ov = audio.speak(outro_text, workdir / "outro.mp3")
    segments.append((subscribe_slide(bgs[1 % len(bgs)], workdir / "s_outro.png"), ov, audio.duration(ov) + 6.0, "Amen"))

    total = sum(s[2] for s in segments)
    if total < MIN_TOTAL:                               # lengthen the quiet after each verse so the video reaches 8+ minutes
        extra = (MIN_TOTAL - total) / len(verses)
        segments = [(a, b, c + (extra if 0 < k <= len(verses) else 0), d) for k, (a, b, c, d) in enumerate(segments)]
        total = sum(s[2] for s in segments)

    clips, voice_parts, chapters, t = [], [], [], 0.0
    sil = workdir / "sil"
    sil.mkdir(exist_ok=True)
    for k, (img, vp, secs, label) in enumerate(segments):
        clips.append(clip(img, secs, workdir / f"c{k:02d}.mp4"))
        voice_parts.append(vp)
        gap = audio.silence(sil / f"g{k:02d}.mp3", max(0.2, secs - audio.duration(vp)))
        voice_parts.append(gap)
        chapters.append((int(t), label))
        t += secs
    listing = workdir / "clips.txt"
    listing.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
    vlist = workdir / "voice.txt"
    vlist.write_text("".join(f"file '{p.resolve()}'\n" for p in voice_parts), encoding="utf-8")
    bed = audio.music_bed(workdir / "bed.wav", rotate=seed)
    if bed is not None:
        # the owner's songs: low, softened (highs rolled off so vocals do not fight the reading), and pushed down
        # further whenever the narrator speaks; the voice stays clearly on top
        mixgraph = ("[1:a]aresample=44100,volume=2.0,asplit=2[v][vsc];"
                    "[2:a]aresample=44100,lowpass=f=4200,highpass=f=60,volume=0.22[m0];"
                    "[m0][vsc]sidechaincompress=threshold=0.015:ratio=10:attack=30:release=900:makeup=1[m];"
                    f"[v][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,afade=t=out:st={total - 5:.2f}:d=5[a]")
        music_in = bed
    else:
        music_in = audio.pad_loop(workdir / "pad.wav")
        mixgraph = (f"[1:a]aresample=44100,volume=1.9[v];[2:a]aresample=44100,volume=0.30,aecho=0.8:0.6:900:0.25[m];"
                    f"[v][m]amix=inputs=2:duration=first:dropout_transition=0,afade=t=out:st={total - 4:.2f}:d=4[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-f", "concat", "-safe", "0",
                    "-i", str(vlist), "-stream_loop", "-1", "-i", str(music_in),
                    "-filter_complex", mixgraph,
                    "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-movflags", "+faststart", str(out_mp4)], check=True)
    return {"duration": round(total, 1), "chapters": chapters, "verses": len(verses)}


def thumbnail(theme: dict, out: Path, seed: int = 0) -> Path:
    bgs = backgrounds()
    bg = bgs[seed % len(bgs)]
    im = ImageOps.fit(Image.open(bg).convert("RGB"), (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.3))
    im = Image.blend(im, Image.new("RGB", (1280, 720), (6, 10, 24)), 0.50)
    d = ImageDraw.Draw(im)
    n = len(theme["verses"])
    f1, f2, f3 = _font(FONT_B, 150), _font(FONT_B, 96), _font(FONT_R, 44)
    a = f"{n} BIBLE VERSES"
    d.text(((1280 - d.textlength(a, font=f1)) / 2, 110), a, font=f1, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
    lines = _wrap(d, f"FOR {theme['title'].upper()}", f2, 1150)
    y = 300
    for ln in lines:
        d.text(((1280 - d.textlength(ln, font=f2)) / 2, y), ln, font=f2, fill=GOLD, stroke_width=2, stroke_fill=(0, 0, 0))
        y += 112
    sub = "Scripture reading with soft worship music"
    d.text(((1280 - d.textlength(sub, font=f3)) / 2, 620), sub, font=f3, fill=WHITE)
    im.save(out, quality=92)
    return out
