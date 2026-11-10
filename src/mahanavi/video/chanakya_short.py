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
TOP_Y, BOTTOM_LIMIT, TEXT_W = 150, 965, 520
UI = {
    "te": dict(head="చాణక్య నీతి సూత్రాలు", sub="సూత్రం {d}/{n}",
               share="ఈ సూత్రాన్ని మీకు ఇష్టమైనవారికి WhatsApp లో పంపండి",
               subscribe="ప్రతిరోజూ ఒక చాణక్య సూత్రం కోసం సబ్‌స్క్రైబ్ చేయండి"),
    "hi": dict(head="चाणक्य नीति सूत्र", sub="सूत्र {d}/{n}",
               share="यह सूत्र अपनों को WhatsApp पर भेजिए",
               subscribe="रोज़ एक चाणक्य सूत्र के लिए सब्सक्राइब करें"),
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


def _wrapped_height(probe, text, font, maxw, lead=1.3):
    return sum(int((font.getbbox(ln)[3] - font.getbbox(ln)[1]) * lead) + 4 for ln in _wrap(probe, text, font, maxw))


def _layout(lang: str, day: int, k: float, numbered: bool = False) -> tuple[np.ndarray, int, int]:
    """Returns (RGBA layer, y where the teaching block ends, y where the share + subscribe block starts)."""
    ui = UI[lang]
    f_head, f_sub, f_sutra = _font(lang, int(56 * k)), _font(lang, int(28 * k)), _font(lang, int(48 * k))
    f_label, f_ex, f_subs, f_share = _font(lang, int(30 * k)), _font(lang, int(36 * k)), _font(lang, 40), _font(lang, int(36 * k))
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # the subscribe line is BIG and sits at the bottom of the safe area
    sub_h = _wrapped_height(probe, ui["subscribe"], f_subs, TEXT_W)
    sub_y = BOTTOM_LIMIT - sub_h
    share_h = _wrapped_height(probe, ui["share"], f_share, TEXT_W)
    share_y = sub_y - share_h - 18          # "send this to your loved ones on WhatsApp", just above the subscribe line
    y = TOP_Y

    def block(text, font, col, gap=0, ymax=None):
        nonlocal y
        for ln in _wrap(probe, text, font, TEXT_W):
            x = (W - probe.textlength(ln, font=font)) / 2
            d.text((x, y), ln, font=font, fill=col, stroke_width=4, stroke_fill=INK)
            bb = font.getbbox(ln)
            y += int((bb[3] - bb[1]) * 1.3) + 4
        y += gap

    if numbered:      # posts up to 10 Nov 2026 kept the "sutra N/total" line; later ones drop it
        block(ui["head"], f_head, GOLD, gap=2)
        block(ui["sub"].format(d=day + 1, n=cn.days()), f_sub, WHITE, gap=int(26 * k))
    else:
        block(ui["head"], f_head, GOLD, gap=int(26 * k))
    # the MAIN message is what Chanakya said (the sutra): bigger, on a dark gold-rimmed panel so it pops
    su_lines = _wrap(probe, cn.sutra(day, lang), f_sutra, TEXT_W - 20)
    su_h = sum(int((f_sutra.getbbox(ln)[3] - f_sutra.getbbox(ln)[1]) * 1.3) + 4 for ln in su_lines)
    pad = 22
    y += pad
    d.rounded_rectangle((W // 2 - TEXT_W // 2 - 14, y - pad, W // 2 + TEXT_W // 2 + 14, y + su_h + pad), radius=26,
                        fill=(18, 8, 4, 190), outline=(255, 200, 80, 255), width=4)
    for ln in su_lines:
        x = (W - probe.textlength(ln, font=f_sutra)) / 2
        d.text((x, y), ln, font=f_sutra, fill=(255, 226, 140), stroke_width=4, stroke_fill=INK)
        y += int((f_sutra.getbbox(ln)[3] - f_sutra.getbbox(ln)[1]) * 1.3) + 4
    y += pad + int(30 * k)
    block(cn.example(day, lang), f_ex, WHITE)
    end = y
    sy = share_y
    for ln in _wrap(probe, ui["share"], f_share, TEXT_W):
        x = (W - probe.textlength(ln, font=f_share)) / 2
        d.text((x, sy), ln, font=f_share, fill=(255, 236, 190), stroke_width=4, stroke_fill=INK)
        bb = f_share.getbbox(ln)
        sy += int((bb[3] - bb[1]) * 1.3) + 4
    sy = sub_y
    for ln in _wrap(probe, ui["subscribe"], f_subs, TEXT_W):
        x = (W - probe.textlength(ln, font=f_subs)) / 2
        d.text((x, sy), ln, font=f_subs, fill=GOLD, stroke_width=5, stroke_fill=INK)
        bb = f_subs.getbbox(ln)
        sy += int((bb[3] - bb[1]) * 1.3) + 4
    return np.asarray(img), end, share_y


def text_layer(lang: str, day: int, numbered: bool = False) -> np.ndarray:
    k = 1.5
    while True:
        lay, end, sub_y = _layout(lang, day, k, numbered)
        if end <= sub_y - 24 or k < 0.6:
            return lay
        k -= 0.03


def render(lang: str, day: int, out: Path, music: Path | None = None, numbered: bool = False) -> Path:
    files = image_files()
    pics = [Image.open(f) for f in files]
    seq = [cover(p) for p in pics] if pics else [gradient()]
    start = day % len(seq)
    seq = seq[start:] + seq[:start]          # a different picture first each day
    lay = text_layer(lang, day, numbered)
    la = lay[..., 3:4].astype(np.float32) / 255.0
    lrgb = lay[..., :3].astype(np.float32)
    vig = vignette()
    music = music or get_settings().alert_short_music_path
    total = int(SECONDS * FPS)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-stream_loop", "-1", "-i", str(music), "-filter_complex",
           f"[1:a]afade=t=in:st=0:d=1[a]", "-map", "0:v", "-map", "[a]", "-t", str(SECONDS),
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
