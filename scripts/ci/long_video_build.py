"""Build a long explainer video from content/long/<slug>.md: Telugu narration (edge-tts), big readable text frames over deity/nature photos, soft pad music.
Usage: python scripts/ci/long_video_build.py <slug> [--art path.jpg]   Output: build/long/<slug>/video.mp4, thumb.jpg"""
import asyncio
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from channels.jesus_long import audio as A  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FONT = str(ROOT / "assets/fonts/NotoSansTelugu-Variable.ttf")
W, H = 1280, 720
VOICES = ("te-IN-MohanNeural", "te-IN-ShrutiNeural")
PHOTOS = ["shiva_g1", "shiva_g2", "shiva_n1", "shiva_n2", "shiva_n3", "shiva_n4", "shiva_n5", "shiva_n6", "shiva_n7", "shiva_n8", "shiva_n9", "shiva_n10", "shivafamily_n1", "shivafamily_n2"]


def font(size, w="Bold"):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name(w)
    except Exception:
        pass
    return f


async def _tts(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="-4%").save(str(out))


def tts(text, out):
    for voice in VOICES:
        for _ in range(3):
            try:
                asyncio.run(_tts(text, voice, out))
                if out.exists() and out.stat().st_size > 800:
                    return
            except Exception as e:  # noqa: BLE001
                print("tts retry:", e)
    raise RuntimeError("tts failed: " + text[:40])


def parse(md):
    """-> list of (section_title, [chunks])"""
    secs, cur = [], None
    for line in md.splitlines():
        if line.startswith("## "):
            t = re.sub(r"\s*\(\d+:\d+\)\s*$", "", line[3:]).strip()
            t = re.sub(r"^\d+\.\s*", "", t)
            cur = (t, [])
            secs.append(cur)
        elif cur and line.strip() and not line.startswith(("#", "(")):
            txt = re.sub(r"^\d+\.\s*", "", line.strip())
            parts = re.split(r"(?<=[.।?!:])\s+", txt)
            buf = ""
            for p in parts:
                if buf and len(buf) + len(p) > 150:
                    cur[1].append(buf)
                    buf = p
                else:
                    buf = (buf + " " + p).strip()
                if len(buf) >= 70:
                    cur[1].append(buf)
                    buf = ""
            if buf:
                cur[1].append(buf)
    return [s for s in secs if s[1]]


def bg_for(key):
    p = next((ROOT / "assets/images/deities").glob(key + ".*"))
    im = Image.open(p).convert("RGB")
    bg = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35)).filter(ImageFilter.GaussianBlur(10))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 5, 3)), 0.5)
    fg = ImageOps.contain(im, (380, 560), method=Image.Resampling.LANCZOS)
    bg.paste(fg, (W - fg.width - 40, 70))
    return bg


def wrap(d, text, f, maxw):
    lines, line = [], ""
    for w in text.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            line = t
        else:
            lines.append(line)
            line = w
    lines.append(line)
    return lines


def frame(base, title, text, out):
    im = base.copy()
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 0, W, 78), fill=(0, 0, 0, 190))
    d.text((40, 39), title, font=font(40), fill=(255, 214, 120), anchor="lm")
    size = 54
    while True:
        f = font(size)
        lines = wrap(d, text, f, 800)
        if len(lines) * size * 1.5 <= 440 or size <= 38:
            break
        size -= 4
    box_h = int(len(lines) * size * 1.5 + 50)
    top = 110 + (480 - box_h) // 2 if box_h < 480 else 110
    d.rounded_rectangle((24, top, 880, top + box_h), 24, fill=(8, 4, 2, 205), outline=(255, 190, 80, 200), width=3)
    y = top + 28
    for ln in lines:
        d.text((55, y), ln, font=f, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))
        y += int(size * 1.5)
    im.save(out, quality=88)


def main(slug):
    secs = parse((ROOT / "content/long" / f"{slug}.md").read_text(encoding="utf-8"))
    work = ROOT / "build/long" / slug
    work.mkdir(parents=True, exist_ok=True)
    bases = {}
    frames, aud, n = [], [], 0
    for si, (title, chunks) in enumerate(secs):
        key = PHOTOS[si % len(PHOTOS)]
        bases.setdefault(key, bg_for(key))
        for c in chunks:
            n += 1
            mp3 = work / f"n{n:03d}.mp3"
            tts(c, mp3)
            seg = A.duration(mp3) + 0.8
            wav = work / f"p{n:03d}.wav"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-af", f"apad=whole_dur={seg:.2f}", "-ar", "44100", "-ac", "1", str(wav)], check=True)
            jpg = work / f"f{n:03d}.jpg"
            frame(bases[key], title, c, jpg)
            aud.append(wav)
            frames.append(f"file '{jpg.name}'\nduration {seg:.2f}")
    frames.append(f"file 'f{n:03d}.jpg'")
    (work / "frames.txt").write_text("\n".join(frames))
    (work / "voice.txt").write_text("\n".join(f"file '{p.name}'" for p in aud))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(work / "voice.txt"), "-c:a", "pcm_s16le", str(work / "voice.wav")], check=True)
    total = A.duration(work / "voice.wav")
    pad = A.pad_loop(work / "pad.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(work / "voice.wav"), "-stream_loop", "-1", "-i", str(pad),
                    "-filter_complex", "[1:a]volume=0.16[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "[a]", "-t", f"{total:.2f}", "-c:a", "aac", "-b:a", "160k", str(work / "mix.m4a")], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(work / "frames.txt"), "-i", str(work / "mix.m4a"),
                    "-vf", "fps=10,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "24",
                    "-c:a", "copy", "-t", f"{total:.2f}", "-movflags", "+faststart", str(work / "video.mp4")], check=True)
    print(slug, f"{total/60:.1f} min", f"{(work / 'video.mp4').stat().st_size/1e6:.1f} MB", n, "frames")


if __name__ == "__main__":
    main(sys.argv[1])
