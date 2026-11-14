"""1920x1080 Telugu reflection video: title, the Bible quote, a short story, the owner's opinion, a prayer, and a
handwritten signature. Telugu narration (edge-tts) over a quiet bed of the owner's worship songs."""
from __future__ import annotations

import asyncio
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from channels.jesus_long import audio as laudio
from channels.jesus_long import video as lv

REPO = Path(__file__).resolve().parents[2]
FONT_TE = REPO / "assets/fonts/NotoSansTelugu-Variable.ttf"
FONT_SIG = Path(__file__).resolve().parent / "assets" / "Signature.ttf"
W, H = lv.W, lv.H
GOLD, WHITE = lv.GOLD, lv.WHITE
VOICES = ("te-IN-MohanNeural", "te-IN-ShrutiNeural")
RATE = "-8%"
SUBSCRIBE_TE = "తర్వాతి సందేశం కోసం సబ్‌స్క్రైబ్ చేసి, బెల్ ఐకాన్ నొక్కి ఆల్ నోటిఫికేషన్స్ ఎంచుకోండి"
HEAD_STORY, HEAD_OPINION, HEAD_PRAYER = "ఒక చిన్న కథ", "నా అభిప్రాయం", "ప్రార్థన"


def _te(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT_TE), size, layout_engine=ImageFont.Layout.RAQM)
    try:
        f.set_variation_by_axes([700 if bold else 500])
    except Exception:  # noqa: BLE001
        pass
    return f


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + ([cur] if cur else [])


def text_slide(bg: Path, body: str, out: Path, head: str = "", ref: str = "", shade: float = 0.66) -> Path:
    im = lv._photo(bg, shade)  # noqa: SLF001
    d = ImageDraw.Draw(im)
    size = 74
    while True:
        f = _te(size, bold=True)
        lines = _wrap(d, body, f, 1560)
        lh = int(size * 1.55)
        total = len(lines) * lh + (110 if ref else 0) + (90 if head else 0)
        if total <= 900 or size <= 40:
            break
        size -= 4
    y = (H - total) // 2
    if head:
        fh = _te(54, bold=True)
        d.text(((W - d.textlength(head, font=fh)) / 2, y), head, font=fh, fill=GOLD, stroke_width=1, stroke_fill=(0, 0, 0))
        y += 90
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0))
        y += lh
    if ref:
        fr = _te(58, bold=True)
        d.text(((W - d.textlength(ref, font=fr)) / 2, y + 24), ref, font=fr, fill=GOLD, stroke_width=1, stroke_fill=(0, 0, 0))
    im.save(out)
    return out


def title_slide(bg: Path, title: str, sub: str, out: Path) -> Path:
    im = lv._photo(bg, 0.55)  # noqa: SLF001
    d = ImageDraw.Draw(im)
    f1, f2 = _te(100, True), _te(52)
    lines = _wrap(d, title, f1, 1600)
    y = H // 2 - len(lines) * 80 - 20
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f1)) / 2, y), ln, font=f1, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0))
        y += 160
    d.text(((W - d.textlength(sub, font=f2)) / 2, y + 10), sub, font=f2, fill=GOLD)
    im.save(out)
    return out


def signature_slide(bg: Path, out: Path) -> Path:
    im = lv._photo(bg, 0.6)  # noqa: SLF001
    d = ImageDraw.Draw(im)
    fsig = ImageFont.truetype(str(FONT_SIG), 190, layout_engine=ImageFont.Layout.RAQM)
    try:
        fsig.set_variation_by_axes([600])
    except Exception:  # noqa: BLE001
        pass
    d.text(((W - d.textlength("Vamsee", font=fsig)) / 2, 230), "Vamsee", font=fsig, fill=(255, 236, 190), stroke_width=1, stroke_fill=(40, 20, 0))
    d.line([(W // 2 - 330, 470), (W // 2 + 330, 470)], fill=GOLD, width=3)
    f1, f2 = _te(56, True), _te(46)
    for i, ln in enumerate(_wrap(d, SUBSCRIBE_TE, f1, 1500)):
        d.text(((W - d.textlength(ln, font=f1)) / 2, 540 + i * 90), ln, font=f1, fill=GOLD, stroke_width=2, stroke_fill=(0, 0, 0))
    tag = "Jesus Worship Waves"
    d.text(((W - d.textlength(tag, font=f2)) / 2, 780), tag, font=f2, fill=WHITE)
    im.save(out)
    return out


async def _speak(text: str, voice: str, out: Path) -> None:
    import edge_tts

    await edge_tts.Communicate(text, voice, rate=RATE).save(str(out))


def speak(text: str, out: Path) -> Path:
    last = None
    for voice in VOICES:
        for _ in range(2):
            try:
                asyncio.run(_speak(text, voice, out))
                if out.exists() and out.stat().st_size > 1000:
                    return out
            except Exception as exc:  # noqa: BLE001
                last = exc
    raise RuntimeError(f"Telugu narration failed: {last}")


def build(item: dict, workdir: Path, out_mp4: Path, seed: int = 0, voice: bool = True) -> dict:
    """Returns {'duration', 'chapters': [(seconds, label)]}. voice=False makes silent timing from text length (layout test)."""
    workdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    bgs = lv.backgrounds()
    rng.shuffle(bgs)
    segs = []   # (image, text_to_read, pause_after, chapter)
    ref = item["ref_te"]
    segs.append((title_slide(bgs[0], item["title_te"], f"{ref}  |  {item['ref_en']}", workdir / "s_title.png"),
                 f"నమస్కారం. ఈరోజు వచనం, {ref}.", 2.0, item["title_te"]))
    segs.append((text_slide(bgs[1 % len(bgs)], item["verse"], workdir / "s_verse.png", ref=ref), f"{item['verse']} {ref}.", 7.0, f"వచనం: {ref}"))
    k = 2
    for i, p in enumerate(item["story"]):
        segs.append((text_slide(bgs[k % len(bgs)], p, workdir / f"s_story{i}.png", head=HEAD_STORY), p, 2.0, HEAD_STORY if i == 0 else ""))
        k += 1
    for i, p in enumerate(item["opinion"]):
        segs.append((text_slide(bgs[k % len(bgs)], p, workdir / f"s_op{i}.png", head=HEAD_OPINION), p, 2.5, HEAD_OPINION if i == 0 else ""))
        k += 1
    segs.append((text_slide(bgs[k % len(bgs)], item["prayer"], workdir / "s_prayer.png", head=HEAD_PRAYER), item["prayer"], 4.0, HEAD_PRAYER))
    segs.append((signature_slide(bgs[(k + 1) % len(bgs)], workdir / "s_sig.png"), "మీ వంశీ. సబ్‌స్క్రైబ్ చేసి, బెల్ ఐకాన్ నొక్కండి.", 5.0, "Vamsee"))

    clips, voice_parts, chapters, t = [], [], [], 0.0
    sil = workdir / "sil"
    sil.mkdir(exist_ok=True)
    for n, (img, text, pause, label) in enumerate(segs):
        if voice:
            vp = speak(text, workdir / f"v{n:02d}.mp3")
            dur = laudio.duration(vp)
        else:
            vp, dur = None, max(3.0, len(text) / 11.0)
        secs = dur + pause + 1.0
        clips.append(lv.clip(img, secs, workdir / f"c{n:02d}.mp4"))
        if vp is not None:
            voice_parts += [vp, laudio.silence(sil / f"g{n:02d}.mp3", max(0.2, secs - dur))]
        if label:
            chapters.append((int(t), label))
        t += secs
    total = t
    if not voice:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(_listing(workdir, clips)), "-c", "copy", str(out_mp4)], check=True)
        return {"duration": round(total, 1), "chapters": chapters}
    vlist = workdir / "voice.txt"
    vlist.write_text("".join(f"file '{p.resolve()}'\n" for p in voice_parts), encoding="utf-8")
    bed = laudio.music_bed(workdir / "bed.wav", rotate=seed)
    if bed is not None:
        mixgraph = ("[1:a]aresample=44100,volume=2.0,asplit=2[v][vsc];"
                    "[2:a]aresample=44100,lowpass=f=4200,highpass=f=60,volume=0.20[m0];"
                    "[m0][vsc]sidechaincompress=threshold=0.015:ratio=10:attack=30:release=900:makeup=1[m];"
                    f"[v][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,afade=t=out:st={total - 5:.2f}:d=5[a]")
        music_in = bed
    else:
        music_in = laudio.pad_loop(workdir / "pad.wav")
        mixgraph = (f"[1:a]aresample=44100,volume=1.9[v];[2:a]aresample=44100,volume=0.30,aecho=0.8:0.6:900:0.25[m];"
                    f"[v][m]amix=inputs=2:duration=first:dropout_transition=0,afade=t=out:st={total - 4:.2f}:d=4[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(_listing(workdir, clips)), "-f", "concat", "-safe", "0",
                    "-i", str(vlist), "-stream_loop", "-1", "-i", str(music_in), "-filter_complex", mixgraph,
                    "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-movflags", "+faststart", str(out_mp4)], check=True)
    return {"duration": round(total, 1), "chapters": chapters}


def _listing(workdir: Path, clips: list[Path]) -> Path:
    p = workdir / "clips.txt"
    p.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
    return p


def thumbnail(item: dict, out: Path, seed: int = 0) -> Path:
    from PIL import ImageOps

    bgs = lv.backgrounds()
    im = ImageOps.fit(Image.open(bgs[seed % len(bgs)]).convert("RGB"), (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.3))
    im = Image.blend(im, Image.new("RGB", (1280, 720), (6, 10, 24)), 0.5)
    d = ImageDraw.Draw(im)
    f1, f2 = _te(104, True), _te(54, True)
    y = 150
    for ln in _wrap(d, item["title_te"], f1, 1160):
        d.text(((1280 - d.textlength(ln, font=f1)) / 2, y), ln, font=f1, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
        y += 150
    d.text(((1280 - d.textlength(item["ref_te"], font=f2)) / 2, y + 20), item["ref_te"], font=f2, fill=GOLD, stroke_width=2, stroke_fill=(0, 0, 0))
    fsig = ImageFont.truetype(str(FONT_SIG), 80, layout_engine=ImageFont.Layout.RAQM)
    d.text((1280 - 330, 600), "Vamsee", font=fsig, fill=(255, 236, 190), stroke_width=1, stroke_fill=(40, 20, 0))
    im.save(out, quality=92)
    return out
