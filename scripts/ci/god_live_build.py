"""Build the looping chant video for one god: photos + Telugu voice reading the 108 names + generated ambient pad.
Output: build/live/<god>/loop.mp4 (about 12-15 minutes; the live stream repeats it)."""
import asyncio
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from channels.jesus_long import audio as A  # noqa: E402
from channels.live_gods import gods as G  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FONT = str(ROOT / "assets/fonts/NotoSansTelugu-Variable.ttf")
W, H = 1280, 720
VOICES = ("te-IN-MohanNeural", "te-IN-ShrutiNeural")


def font(size):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    return f


async def _tts(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="-10%").save(str(out))


def tts(text, out):
    for voice in VOICES:
        for _ in range(3):
            try:
                asyncio.run(_tts(text, voice, out))
                if out.exists() and out.stat().st_size > 800:
                    return
            except Exception as e:  # noqa: BLE001
                print("tts retry:", e)
    raise RuntimeError("tts failed: " + text)


def photo(key, shade=0.38):
    p = next((ROOT / "assets/images/deities").glob(key + ".*"))
    im = Image.open(p).convert("RGB")
    bg = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(24))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (8, 6, 4)), 0.55)
    fg = ImageOps.contain(im, (W, H - 150), method=Image.Resampling.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, 10))
    return bg


def frame(base, idx, text_te, god, out):
    im = base.copy()
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, H - 150, W, H), fill=(10, 6, 2, 215))
    f1, f2 = font(54), font(30)
    t = f"ఓం {text_te} నమః"
    d.text((W / 2, H - 100), t, font=f1, fill=(255, 214, 120), anchor="mm")
    d.text((W / 2, H - 38), f"{idx}/108  |  {G.GODS[god]['names_te']}", font=f2, fill=(235, 225, 205), anchor="mm")
    im.save(out, quality=88)


def main(god):
    names = G.names(god)
    g = G.GODS[god]
    work = ROOT / "build/live" / god
    work.mkdir(parents=True, exist_ok=True)
    keys = g["photos"]
    bases = [photo(k) for k in keys]
    per = max(1, 108 // len(keys) + (1 if 108 % len(keys) else 0))
    lines, aud = [], []
    for i, n in enumerate(names, 1):
        mp3 = work / f"n{i:03d}.mp3"
        tts(f"ఓం {n} నమః", mp3)
        seg = max(A.duration(mp3) + 3.2, 7.0)
        padded = work / f"p{i:03d}.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-af", f"apad=whole_dur={seg:.2f}", "-ar", "44100", "-ac", "1", str(padded)], check=True)
        aud.append(padded)
        jpg = work / f"f{i:03d}.jpg"
        frame(bases[min((i - 1) // per, len(bases) - 1)], i, n, god, jpg)
        lines.append(f"file '{jpg.name}'\nduration {seg:.2f}")
    lines.append(f"file '{(work / 'f108.jpg').name}'")
    (work / "frames.txt").write_text("\n".join(lines))
    (work / "voice.txt").write_text("\n".join(f"file '{p.name}'" for p in aud))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(work / "voice.txt"), "-c:a", "pcm_s16le", str(work / "voice.wav")], check=True)
    total = A.duration(work / "voice.wav")
    pad = A.pad_loop(work / "pad.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(work / "voice.wav"), "-stream_loop", "-1", "-i", str(pad),
                    "-filter_complex", "[1:a]volume=0.32[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "[a]", "-t", f"{total:.2f}", "-c:a", "aac", "-b:a", "128k", str(work / "mix.m4a")], check=True)
    out = work / "loop.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(work / "frames.txt"), "-i", str(work / "mix.m4a"),
                    "-vf", "fps=10,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "24",
                    "-c:a", "copy", "-t", f"{total:.2f}", "-movflags", "+faststart", str(out)], check=True)
    print(god, "loop", f"{total/60:.1f} min", f"{out.stat().st_size/1e6:.1f} MB")
    th = work / "thumb.jpg"
    Image.open(work / "f001.jpg").save(th, quality=90)


if __name__ == "__main__":
    main(sys.argv[1])
