"""One 15 s Hindi Purana Concept Short: ONE static card (type label, title in a gold panel, the teaching, share and subscribe
lines) over a deity photo. Same look as the Chanakya Short. Used by Divine Mantra Sangam and Devotional Trance Beats.

    python -m mahanavi.video.purana_concept_hindi_short --index 3 --out out/purana_hi_3.mp4
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from mahanavi.config import get_settings
from mahanavi.content import purana_concept_hindi as ph
from mahanavi.content.purana_concept_shorts import PURANA_CONCEPT_SHORTS
from mahanavi.images import deity_bg
from mahanavi.video.chanakya_short import BOTTOM_LIMIT, TEXT_W, TOP_Y, UI, _font, _wrapped_height, gradient
from mahanavi.video.lakshmi_name_short import FPS, GOLD, H, INK, SECONDS, W, WHITE, _wrap, cover, vignette


def _layout(index: int, k: float) -> tuple[np.ndarray, int, int]:
    c, h = PURANA_CONCEPT_SHORTS[index], ph.HINDI[index]
    ui = UI["hi"]
    f_inv, f_label, f_title, f_body = _font("hi", int(30 * k)), _font("hi", int(32 * k)), _font("hi", int(52 * k)), _font("hi", int(38 * k))
    f_subs, f_share = _font("hi", 40), _font("hi", int(36 * k))
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sub_h = _wrapped_height(probe, ui["subscribe"], f_subs, TEXT_W)
    sub_y = BOTTOM_LIMIT - sub_h
    share_y = sub_y - _wrapped_height(probe, ui["share"], f_share, TEXT_W) - 18
    y = TOP_Y

    def lines(text, font, maxw=TEXT_W):
        return _wrap(probe, text, font, maxw)

    def step(font, ln):
        bb = font.getbbox(ln)
        return int((bb[3] - bb[1]) * 1.3) + 4

    def block(text, font, col, gap=0, stroke=4):
        nonlocal y
        for ln in lines(text, font):
            d.text(((W - probe.textlength(ln, font=font)) / 2, y), ln, font=font, fill=col, stroke_width=stroke, stroke_fill=INK)
            y += step(font, ln)
        y += gap

    block(h.invocation, f_inv, WHITE, gap=int(8 * k))
    block(ph.LABEL[c.concept_type.value], f_label, GOLD, gap=int(18 * k))
    # the headline of the concept: bigger, on a dark gold-rimmed panel
    tl = lines(h.title, f_title, TEXT_W - 20)
    th, pad = sum(step(f_title, ln) for ln in tl), 20
    y += pad
    d.rounded_rectangle((W // 2 - TEXT_W // 2 - 14, y - pad, W // 2 + TEXT_W // 2 + 14, y + th + pad), radius=26,
                        fill=(18, 8, 4, 190), outline=(255, 200, 80, 255), width=4)
    for ln in tl:
        d.text(((W - probe.textlength(ln, font=f_title)) / 2, y), ln, font=f_title, fill=(255, 226, 140), stroke_width=4, stroke_fill=INK)
        y += step(f_title, ln)
    y += pad + int(26 * k)
    for para in h.body.split("\n"):
        if not para.strip():
            y += int(10 * k)
            continue
        block(para, f_body, WHITE)
    block(h.purana, f_inv, (255, 236, 190), gap=0)
    end = y
    sy = share_y
    for ln in lines(ui["share"], f_share):
        d.text(((W - probe.textlength(ln, font=f_share)) / 2, sy), ln, font=f_share, fill=(255, 236, 190), stroke_width=4, stroke_fill=INK)
        sy += step(f_share, ln)
    sy = sub_y
    for ln in lines(ui["subscribe"], f_subs):
        d.text(((W - probe.textlength(ln, font=f_subs)) / 2, sy), ln, font=f_subs, fill=GOLD, stroke_width=5, stroke_fill=INK)
        sy += step(f_subs, ln)
    return np.asarray(img), end, share_y


def text_layer(index: int) -> np.ndarray:
    k = 1.4
    while True:
        lay, end, share_y = _layout(index, k)
        if end <= share_y - 24 or k < 0.55:
            return lay
        k -= 0.03


def render(index: int, out: Path, music: Path | None = None, day: dt.date | None = None) -> Path:
    c = PURANA_CONCEPT_SHORTS[index]
    day = day or dt.date.today()
    photo = deity_bg.photo_for_story(day, title_en=c.title_en, *(c.title_te, c.invocation_te, c.body_te))
    base = cover(Image.open(photo)) if photo else gradient()
    lay = text_layer(index)
    la = lay[..., 3:4].astype(np.float32) / 255.0
    lrgb = lay[..., :3].astype(np.float32)
    frame = np.clip(base.astype(np.float32) * 0.52 * vignette(), 0, 255)
    frame = np.clip(frame * (1 - la) + lrgb * la, 0, 255).astype(np.uint8)
    music = music or get_settings().alert_short_music_path
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-stream_loop", "-1", "-i", str(music), "-filter_complex",
           f"[1:a]afade=t=in:st=0:d=1,afade=t=out:st={SECONDS - 1.5}:d=1.5[a]", "-map", "0:v", "-map", "[a]", "-t", str(SECONDS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    data = frame.tobytes()
    for _ in range(int(SECONDS * FPS)):
        p.stdin.write(data)
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--index", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    print(render(a.index, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
