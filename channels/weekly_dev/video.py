"""The Friday video: 1920x1080, a dated list of the week's AP government development actions scrolling upward
(credits style) over the Pulse Boosting yellow, a fixed header (title, date range, coins) and a fixed footer with the
subscribe reminder. Pillow draws the tall text strip once; ffmpeg moves it, so the scroll is smooth."""
from __future__ import annotations

import datetime as dt
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from channels.engine import render as eng
from channels.trending import config as cfg
from channels.trending import portraits
from channels.weekly_dev.collect import telugu_date

W, H = 1920, 1080
HEAD_H, FOOT_H = 230, 150
WIN_H = H - HEAD_H - FOOT_H
SPEED = 70            # pixels per second: about 4.5 s per two-line item, comfortable to read
INK, BROWN, RED, GOLD = (70, 0, 10), (95, 45, 0), (170, 10, 25), (255, 214, 0)
CARD_W, CARD_X = 1500, 210
TITLE_TE = "ఈ వారం ఆంధ్రప్రదేశ్ అభివృద్ధి"
SUBSCRIBE = cfg.CTA["te"][0]


def _fonts():
    latin, native = cfg._fonts("te")
    mk = lambda px, bold=False: eng._mixed_font(latin, px, native, bold)  # noqa: E731
    return mk


def _background() -> Image.Image:
    bg = Image.new("RGB", (W, H))
    px = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / (H - 1)
        px.line((0, y, W, y), fill=(int(255 - 12 * t), int(224 - 40 * t), int(20 - 10 * t)))
    return bg


def _coins_row(x_right: int, y: int, d: int = 96) -> Image.Image:
    coins = [portraits._coin(w, d) for w in ("ntr", "cbn", "pawan_smile", "modi")]
    gap = 26
    out = Image.new("RGBA", (sum(c.width for c in coins) + gap * (len(coins) - 1), coins[0].height), (0, 0, 0, 0))
    x = 0
    for c in coins:
        out.alpha_composite(c, (x, 0))
        x += c.width + gap
    return out


def build_header(items: list[dict], mk) -> Image.Image:
    im = Image.new("RGBA", (W, HEAD_H), (255, 214, 0, 255))
    g = ImageDraw.Draw(im)
    for y in range(HEAD_H):
        g.line((0, y, W, y), fill=(255, 214 + int(10 * y / HEAD_H), 10, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, HEAD_H - 8, W, HEAD_H), fill=RED)
    logo = Image.open(cfg.CHANNEL_DIR / "assets/logo.png").convert("RGBA")
    k = 230 / logo.width
    logo = logo.resize((230, int(logo.height * k)), Image.LANCZOS)
    im.alpha_composite(logo, (50, (HEAD_H - logo.height) // 2 - 4))
    f1, f2 = mk(78, True), mk(44)
    d.text((330, 26), TITLE_TE, font=f1, fill=INK, stroke_width=1, stroke_fill=INK)
    first, last = dt.date.fromisoformat(items[0]["date"]), dt.date.fromisoformat(items[-1]["date"])
    d.text((330, 130), f"{telugu_date(first)}  నుంచి  {telugu_date(last)}  వరకు", font=f2, fill=BROWN)
    coins = _coins_row(0, 0)
    im.alpha_composite(coins, (W - coins.width - 50, (HEAD_H - coins.height) // 2 - 4))
    return im


def build_footer(mk) -> Image.Image:
    im = Image.new("RGBA", (W, FOOT_H), (150, 10, 25, 255))
    d = ImageDraw.Draw(im)
    f = mk(52, True)
    lines = eng._wrap(d, SUBSCRIBE, f, 0, 1500)
    lh = 64
    y = (FOOT_H - lh * len(lines)) // 2 - 4
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=(255, 244, 200, 255))
        y += lh
    d.text((W - 330, FOOT_H - 42), cfg.HANDLE, font=mk(30), fill=(255, 214, 120, 255))
    return im


def build_strip(items: list[dict], mk) -> Image.Image:
    """Tall RGBA strip: one card per item (date chip, headline, publisher), then a closing line. The first card starts
    a window's height down so the list rises into view from the bottom."""
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    fd, fh, fs = mk(46, True), mk(56, True), mk(34)
    START = WIN_H - 330   # the first card is already rising into view at t=0
    cards, total = [], START
    for it in items:
        lines = eng._wrap(probe, it["headline"], fh, 1, CARD_W - 120)
        h = 24 + 66 + len(lines) * 80 + 14 + 54 + 26
        cards.append((it, lines, h))
        total += h + 36
    close_h = 330
    total += close_h + WIN_H
    strip = Image.new("RGBA", (W, total), (0, 0, 0, 0))
    d = ImageDraw.Draw(strip)
    y = START
    for it, lines, h in cards:
        d.rounded_rectangle((CARD_X, y, CARD_X + CARD_W, y + h), 26, fill=(255, 250, 225, 235), outline=(190, 20, 30, 255), width=4)
        day = dt.date.fromisoformat(it["date"])
        chip = telugu_date(day, weekday=True)
        cw = int(d.textlength(chip, font=fd)) + 56
        d.rounded_rectangle((CARD_X + 40, y + 24, CARD_X + 40 + cw, y + 24 + 66), 33, fill=(170, 10, 25, 255))
        d.text((CARD_X + 68, y + 24 + 6), chip, font=fd, fill=(255, 255, 255, 255))
        ty = y + 24 + 66 + 12
        for ln in lines:
            d.text((CARD_X + 60, ty), ln, font=fh, fill=INK, stroke_width=1, stroke_fill=INK)
            ty += 80
        d.text((CARD_X + 60, ty + 6), f"మూలం: {it['publisher']}", font=fs, fill=BROWN)
        y += h + 36
    fb = mk(70, True)
    d.rounded_rectangle((CARD_X, y, CARD_X + CARD_W, y + close_h), 26, fill=(170, 10, 25, 240))
    for i, ln in enumerate(("జై తెలుగుదేశం! జై ఆంధ్రప్రదేశ్!", "ప్రతి శుక్రవారం, ఈ వారం అభివృద్ధి వార్తలు")):
        d.text(((W - d.textlength(ln, font=fb)) / 2, y + 70 + i * 100), ln, font=fb, fill=(255, 244, 200, 255))
    strip._scroll_distance = y + close_h // 2 - WIN_H // 2   # noqa: SLF001  (until the closing card is mid-window)
    return strip


def duration_for(distance: int) -> float:
    return distance / SPEED + 5.0     # scroll, then 5 s holding on the closing card


def render(items: list[dict], out_mp4: Path, workdir: Path, music_seed: int = 0) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    mk = _fonts()
    strip = build_strip(items, mk)
    distance = strip._scroll_distance  # noqa: SLF001
    dur = duration_for(distance)
    paths = {k: workdir / f"{k}.png" for k in ("bg", "strip", "head", "foot")}
    _background().save(paths["bg"])
    strip.save(paths["strip"])
    build_header(items, mk).save(paths["head"])
    build_footer(mk).save(paths["foot"])
    tracks = sorted((cfg.CHANNEL_DIR / "assets/music/approved").glob("*.mp3"))
    music = str(random.Random(music_seed).choice(tracks)) if tracks else None
    top, v = HEAD_H, SPEED
    fc = (f"[0:v][1:v]overlay=x=0:y='{top + 0}-min(t*{v},{distance})+0':format=auto[a];"
          f"[a][2:v]overlay=0:0[b];[b][3:v]overlay=0:{H - FOOT_H},format=yuv420p[v]")
    cmd = ["ffmpeg", "-y", "-v", "error",
           *sum((["-loop", "1", "-framerate", "30", "-t", f"{dur:.2f}", "-i", str(paths[k])] for k in ("bg", "strip", "head", "foot")), [])]
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]
    cmd += ["-filter_complex", fc + (";[4:a]volume=0.55,afade=t=out:st=%.2f:d=3[aud]" % (dur - 3) if music else ""),
            "-map", "[v]", *(["-map", "[aud]"] if music else []),
            "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30", "-pix_fmt", "yuv420p",
            *(["-c:a", "aac", "-b:a", "192k", "-ar", "48000"] if music else []), "-movflags", "+faststart", str(out_mp4)]
    subprocess.run(cmd, check=True)
    return {"duration": round(dur, 1), "music": Path(music).name if music else "", "items": len(items)}


def thumbnail(items: list[dict], out_png: Path) -> None:
    """1280x720 thumbnail: big title, date range, the four coins."""
    mk = _fonts()
    im = _background().resize((1280, 720))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1280, 22), fill=RED)
    d.rectangle((0, 698, 1280, 720), fill=RED)
    big, mid = mk(118, True), mk(60, True)
    for i, ln in enumerate(("ఈ వారం", "ఆంధ్రప్రదేశ్ అభివృద్ధి")):
        d.text(((1280 - d.textlength(ln, font=big)) / 2, 70 + i * 160), ln, font=big, fill=INK, stroke_width=2, stroke_fill=INK)
    first, last = dt.date.fromisoformat(items[0]["date"]), dt.date.fromisoformat(items[-1]["date"])
    rng = f"{first.day} {telugu_date(first).split()[1]} నుంచి {last.day} {telugu_date(last).split()[1]} వరకు"
    pw = int(d.textlength(rng, font=mid)) + 90
    d.rounded_rectangle(((1280 - pw) // 2, 420, (1280 + pw) // 2, 510), 45, fill=RED)
    d.text(((1280 - d.textlength(rng, font=mid)) / 2, 428), rng, font=mid, fill=(255, 255, 255))
    coins = _coins_row(0, 0, 120)
    im.paste(coins, ((1280 - coins.width) // 2, 545), coins)
    im.convert("RGB").save(out_png, quality=92)
