"""One 15 s verse Short: ONE static card (series name, verse number, the verse in a gold-rimmed panel, its meaning, a subscribe line)
over the channel's own background pictures that cross-fade slowly behind it. Same look and safe area as the Chanakya Shorts.

    python -m mahanavi.video.verse_short --series shiv_tandav_hi --day 0 --out out/v1.mp4
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from channels import verse_series as vs
from mahanavi.config import PROJECT_ROOT, get_settings
from mahanavi.images.fonts import FontManager
from mahanavi.video.lakshmi_name_short import FPS, GOLD, H, HIND, IMG_SECONDS, INK, SECONDS, W, XFADE, WHITE, _wrap, cover, vignette

TOP_Y, BOTTOM_LIMIT, TEXT_W = 140, 965, 540
CONTENT = {"shiv_tandav_hi": "mahanavi.content.shiv_tandav_hi", "shiv_tandav_trance": "mahanavi.content.shiv_tandav_hi"}
UI = {
    "hi": dict(sub="श्लोक {d}", subscribe="रोज़ एक श्लोक के लिए सब्सक्राइब करें"),
    "chant": dict(head="शिव ताण्डव ट्रांस", sub="जाप {d}", tail="हर हर महादेव", subscribe="रोज़ एक ट्रांस जाप के लिए सब्सक्राइब करें"),
    "te": dict(sub="శ్లోకం {d}", subscribe="రోజూ ఒక శ్లోకం కోసం సబ్‌స్క్రైబ్ చేయండి"),
}


def content(key: str):
    import importlib

    return importlib.import_module(CONTENT[key])


def image_files(s: vs.Series) -> list[Path]:
    folder = PROJECT_ROOT / "channels" / (s.bg_channel or s.channel) / "assets" / "backgrounds"
    files = sorted(p for p in folder.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) if folder.exists() else []
    hinted = [p for p in files if s.image_hint and s.image_hint in p.name.lower()]
    return hinted or files


def _font(lang: str, size: int):
    if lang == "hi":
        return ImageFont.truetype(str(HIND), size, layout_engine=ImageFont.Layout.RAQM)
    return FontManager(get_settings().telugu_font_path).get_font(size=size, weight="Bold")


def gradient() -> np.ndarray:
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top, bot = np.array([150, 50, 40], np.float32), np.array([25, 95, 110], np.float32)
    return np.broadcast_to(top * (1 - y) + bot * y, (H, W, 3)).astype(np.uint8).copy()


def _lines(probe, text: str, font, maxw: int) -> list[str]:
    out: list[str] = []
    for para in text.split("\n"):
        out += _wrap(probe, para, font, maxw)
    return out


def _lh(font) -> int:
    bb = font.getbbox("Ag")
    return int((bb[3] - bb[1]) * 1.34) + 4


def _layout(key: str, day: int, k: float) -> tuple[np.ndarray, int, int]:
    s, c = vs.SERIES[key], content(key)
    ui = UI["chant" if s.variant == "chant" else s.lang]
    verse, meaning = c.VERSES[day]
    head = ui.get("head", c.HEAD)
    if s.variant == "chant":
        verse, meaning = verse.split("\n")[0].replace("।", "").replace("॥", "").strip(), ui["tail"]
    f_head, f_sub, f_verse = _font(s.lang, int(52 * k)), _font(s.lang, int(30 * k)), _font(s.lang, int(36 * k))
    f_mean, f_subs = _font(s.lang, int(33 * k)), _font(s.lang, 38)
    f_en = ImageFont.truetype(str(HIND), int(28 * k))
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sub_lines = _lines(probe, ui["subscribe"], f_subs, TEXT_W)
    sub_y = BOTTOM_LIMIT - len(sub_lines) * _lh(f_subs)
    y = TOP_Y

    def block(text, font, col, gap=0):
        nonlocal y
        for ln in _lines(probe, text, font, TEXT_W):
            d.text(((W - probe.textlength(ln, font=font)) / 2, y), ln, font=font, fill=col, stroke_width=4, stroke_fill=INK)
            y += _lh(font)
        y += gap

    block(head, f_head, GOLD)
    block(ui["sub"].format(d=day + 1), f_sub, WHITE, gap=int(18 * k))
    verse = verse.replace(" ।", "\u00a0।").replace(" ॥", "\u00a0॥")   # keep the danda on the line it ends
    vl = _lines(probe, verse, f_verse, TEXT_W - 50)
    vl = [ln for ln in vl]
    for i in range(len(vl) - 1, 0, -1):          # a line holding only a danda goes back onto the line before it
        if vl[i].replace("\u00a0", "").strip() in ("।", "॥"):
            vl[i - 1] = vl[i - 1] + " " + vl[i].strip()
            del vl[i]
    too_wide = any(probe.textlength(ln, font=f_verse) > TEXT_W - 40 for ln in vl)
    pad = 20
    vh = len(vl) * _lh(f_verse)
    y += pad
    d.rounded_rectangle((W // 2 - TEXT_W // 2 - 14, y - pad, W // 2 + TEXT_W // 2 + 14, y + vh + pad), radius=26, fill=(18, 8, 4, 200), outline=(255, 200, 80, 255), width=4)
    for ln in vl:
        d.text(((W - probe.textlength(ln, font=f_verse)) / 2, y), ln, font=f_verse, fill=(255, 226, 140), stroke_width=3, stroke_fill=INK)
        y += _lh(f_verse)
    y += pad + int(22 * k)
    block(meaning, f_mean, WHITE, gap=int(14 * k))
    if s.variant == "meaning" and hasattr(c, "MEANING_EN"):
        block(c.MEANING_EN[day], f_en, (255, 236, 190))
    end = y
    sy = sub_y
    for ln in sub_lines:
        d.text(((W - probe.textlength(ln, font=f_subs)) / 2, sy), ln, font=f_subs, fill=GOLD, stroke_width=5, stroke_fill=INK)
        sy += _lh(f_subs)
    return np.asarray(img), (10**6 if too_wide else end), sub_y


def text_layer(key: str, day: int) -> np.ndarray:
    k = 1.4
    while True:
        lay, end, sub_y = _layout(key, day, k)
        if end <= sub_y - 20 or k < 0.5:
            return lay
        k -= 0.03


def render(key: str, day: int, out: Path, music: Path | None = None) -> Path:
    s = vs.SERIES[key]
    pics = [Image.open(f).convert("RGB") for f in image_files(s)]
    seq = [cover(p) for p in pics] if pics else [gradient()]
    start = day % len(seq)
    seq = seq[start:] + seq[:start]
    lay = text_layer(key, day)
    la = lay[..., 3:4].astype(np.float32) / 255.0
    lrgb = lay[..., :3].astype(np.float32)
    vig = vignette()
    music = music or get_settings().alert_short_music_path
    total = int(SECONDS * FPS)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-stream_loop", "-1", "-i", str(music), "-filter_complex", "[1:a]afade=t=in:st=0:d=1[a]", "-map", "0:v", "-map", "[a]", "-t", str(SECONDS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(total):
        t = f / FPS
        i = int(t // IMG_SECONDS)
        into = t - i * IMG_SECONDS
        a = seq[i % len(seq)]
        if into > IMG_SECONDS - XFADE and len(seq) > 1:
            w = (into - (IMG_SECONDS - XFADE)) / XFADE
            base = cv2.addWeighted(a, 1 - w, seq[(i + 1) % len(seq)], w, 0)
        else:
            base = a
        frame = base.astype(np.float32) * 0.5 * vig
        frame = frame * (1 - la) + lrgb * la
        p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", choices=sorted(vs.SERIES), required=True)
    ap.add_argument("--day", type=int, default=0)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    print(render(a.series, a.day, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
