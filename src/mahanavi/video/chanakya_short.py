"""One 15 s Chanakya Neeti Short: ONE static card (header, five teachings, subscribe line) over Chanakya pictures that
cross-fade slowly behind it. The text never moves or changes, like the other single-card Shorts.

    python -m mahanavi.video.chanakya_short --lang te --day 0 --out out/chanakya_te_1.mp4

Pictures: every .jpg/.png in assets/images/chanakya/ (the owner's 10 images). With none, a dark maroon-to-teal gradient is used.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from mahanavi.config import PROJECT_ROOT, get_settings
from mahanavi.content import chanakya_neeti as cn
from mahanavi.images.fonts import FontManager
from mahanavi.video.lakshmi_name_short import FPS, GOLD, H, HIND, IMG_SECONDS, INK, SECONDS, W, XFADE, WHITE, _wrap, cover, vignette

OWN_IMAGES = PROJECT_ROOT / "assets" / "images" / "chanakya"
# Phone safe area on 720x1280 (same as the other Shorts): x 100..620, y about 150..925
TOP_Y, BOTTOM_LIMIT, TEXT_W = 150, 925, 520
UI = {
    "te": dict(head="చాణక్య నీతి", sub="నేటి 5 నీతి సూత్రాలు", day="రోజు {d}/{n}",
               subscribe="ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు"),
    "hi": dict(head="चाणक्य नीति", sub="आज के 5 नीति सूत्र", day="दिन {d}/{n}",
               subscribe="अभी सब्सक्राइब नहीं किया तो यह चैनल शायद दोबारा आपको न दिखे"),
}


def image_files() -> list[Path]:
    return sorted(p for p in OWN_IMAGES.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")) if OWN_IMAGES.exists() else []


def _font(lang: str, size: int):
    if lang == "hi":
        return ImageFont.truetype(str(HIND), size, layout_engine=ImageFont.Layout.RAQM)
    return FontManager(get_settings().telugu_font_path).get_font(size=size, weight="Bold")


def gradient() -> np.ndarray:
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top, bot = np.array([170, 60, 45], np.float32), np.array([25, 105, 115], np.float32)   # bright: the frame is dimmed to ~half later
    return np.broadcast_to(top * (1 - y) + bot * y, (H, W, 3)).astype(np.uint8).copy()


def _layout(lang: str, day: int, k: float) -> tuple[np.ndarray, int]:
    ui = UI[lang]
    f_head, f_sub, f_item, f_small = _font(lang, int(58 * k)), _font(lang, int(30 * k)), _font(lang, int(36 * k)), _font(lang, int(25 * k))
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = TOP_Y

    def block(text, font, col, x=None, gap=0, maxw=TEXT_W):
        nonlocal y
        for ln in _wrap(probe, text, font, maxw):
            xx = x if x is not None else (W - probe.textlength(ln, font=font)) / 2
            d.text((xx, y), ln, font=font, fill=col, stroke_width=4, stroke_fill=INK)
            bb = font.getbbox(ln)
            y += int((bb[3] - bb[1]) * 1.4) + 4
        y += gap

    block(ui["head"], f_head, GOLD, gap=2)
    block(f"{ui['sub']}  |  " + ui["day"].format(d=day + 1, n=cn.days()), f_sub, WHITE, gap=int(16 * k))
    for i, line in enumerate(cn.card(day, lang), 1):
        d.text((100, y), f"{i}.", font=f_item, fill=GOLD, stroke_width=4, stroke_fill=INK)
        num_w = int(probe.textlength("5. ", font=f_item))
        x0 = 100 + num_w
        for ln in _wrap(probe, line, f_item, 620 - x0):
            d.text((x0, y), ln, font=f_item, fill=(255, 248, 230), stroke_width=4, stroke_fill=INK)
            bb = f_item.getbbox(ln)
            y += int((bb[3] - bb[1]) * 1.3) + 4
        y += int(30 * k)
    y += int(6 * k)
    block(ui["subscribe"], f_small, WHITE)
    return np.asarray(img), y


def text_layer(lang: str, day: int) -> np.ndarray:
    k = 1.5
    while True:
        lay, end = _layout(lang, day, k)
        if end <= BOTTOM_LIMIT or k < 0.6:
            return lay
        k -= 0.03


def render(lang: str, day: int, out: Path, music: Path | None = None) -> Path:
    files = image_files()
    pics = [Image.open(f) for f in files]
    seq = [cover(p) for p in pics] if pics else [gradient()]
    start = day % len(seq)
    seq = seq[start:] + seq[:start]          # a different picture first each day
    lay = text_layer(lang, day)
    la = lay[..., 3:4].astype(np.float32) / 255.0
    lrgb = lay[..., :3].astype(np.float32)
    vig = vignette()
    music = music or get_settings().alert_short_music_path
    total = int(SECONDS * FPS)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-stream_loop", "-1", "-i", str(music), "-filter_complex",
           f"[1:a]afade=t=in:st=0:d=1,afade=t=out:st={SECONDS - 1.5}:d=1.5[a]", "-map", "0:v", "-map", "[a]", "-t", str(SECONDS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(total):
        t = f / FPS
        k = int(t // IMG_SECONDS)
        into = t - k * IMG_SECONDS
        a = seq[k % len(seq)]
        if into > IMG_SECONDS - XFADE and len(seq) > 1:
            w = (into - (IMG_SECONDS - XFADE)) / XFADE
            base = cv2.addWeighted(a, 1 - w, seq[(k + 1) % len(seq)], w, 0)
        else:
            base = a
        frame = base.astype(np.float32) * 0.52 * vig
        frame = frame * (1 - la) + lrgb * la          # the card is the same in every frame
        p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lang", choices=sorted(UI), required=True)
    ap.add_argument("--day", type=int, default=0, help="0 based day number")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    print(render(a.lang, a.day, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
