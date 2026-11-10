"""Friendly animated decoration for the list cards (festival and vrata calendars): a squirrel that swishes its tail, blinks
and nibbles an acorn in the top left corner, three butterflies that flutter across the card, and twinkling sparkles.
All art is original and drawn in code. It is composited over an already assembled video, the audio is copied untouched.

    python -m mahanavi.video.decor_animation in.mp4 out.mp4
"""
from __future__ import annotations

import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
SS = 3   # supersampling for smooth edges
OUTLINE = (70, 38, 18, 255)


def _canvas(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _ell(d: ImageDraw.ImageDraw, cx, cy, rx, ry, fill, outline=OUTLINE, width=3):
    d.ellipse(((cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS), fill=fill, outline=outline, width=max(width, 0) * SS)


def _finish(img: Image.Image, w: int, h: int) -> Image.Image:
    return img.resize((w, h), Image.LANCZOS)


@lru_cache(maxsize=256)
def butterfly(main: tuple, edge: tuple, open_q: int) -> Image.Image:
    """open_q 1..10: how far the wings are spread (flapping)."""
    o = max(open_q, 1) / 10.0
    w = h = 200
    img, d = _canvas(w, h)
    cx, cy = 100, 100
    for side in (-1, 1):
        _ell(d, cx + side * 52 * o, cy - 26, 56 * o + 2, 52, main + (255,), edge + (255,), 4)
        _ell(d, cx + side * 40 * o, cy + 38, 38 * o + 2, 34, tuple(min(255, int(c * 0.9)) for c in main) + (255,), edge + (255,), 4)
        if o > 0.35:
            _ell(d, cx + side * 56 * o, cy - 30, 14 * o + 1, 14, (255, 255, 255, 235), None, 0)
            _ell(d, cx + side * 40 * o, cy + 38, 8 * o + 1, 8, (255, 255, 255, 235), None, 0)
    _ell(d, cx, cy + 4, 7, 40, (60, 34, 20, 255), (30, 18, 10, 255), 2)
    _ell(d, cx, cy - 40, 9, 9, (60, 34, 20, 255), (30, 18, 10, 255), 2)
    d.line(((cx - 3) * SS, (cy - 46) * SS, (cx - 22) * SS, (cy - 80) * SS), fill=(40, 24, 14, 255), width=3 * SS)
    d.line(((cx + 3) * SS, (cy - 46) * SS, (cx + 22) * SS, (cy - 80) * SS), fill=(40, 24, 14, 255), width=3 * SS)
    return _finish(img, w, h)


FUR, FUR2, BELLY = (181, 102, 40, 255), (214, 140, 70, 255), (246, 214, 168, 255)


@lru_cache(maxsize=128)
def squirrel(tail_q: int, blink: bool, nibble_q: int) -> Image.Image:
    """tail_q -6..6: tail swing, nibble_q 0..2: head dip while nibbling the acorn."""
    w, h = 300, 340
    img, d = _canvas(w, h)
    tail = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    td = ImageDraw.Draw(tail)
    for rx, ry, col, ox in ((70, 130, FUR, 0), (46, 100, FUR2, 6)):
        td.ellipse(((205 - rx + ox) * SS, (150 - ry) * SS, (205 + rx + ox) * SS, (150 + ry) * SS), fill=col,
                   outline=OUTLINE if col == FUR else None, width=4 * SS)
    tail = tail.rotate(-tail_q * 2.2, resample=Image.BICUBIC, center=(190 * SS, 270 * SS))
    img.alpha_composite(tail)
    d = ImageDraw.Draw(img)
    dip = nibble_q * 4
    _ell(d, 120, 240, 66, 78, FUR)
    _ell(d, 124, 252, 40, 56, BELLY, None, 0)
    _ell(d, 82, 312, 26, 14, FUR2)
    _ell(d, 150, 312, 26, 14, FUR2)
    hx, hy = 112, 130 + dip
    d.polygon([((hx - 48) * SS, (hy - 30) * SS), ((hx - 30) * SS, (hy - 84) * SS), ((hx - 8) * SS, (hy - 44) * SS)], fill=FUR, outline=OUTLINE, width=3 * SS)
    d.polygon([((hx + 48) * SS, (hy - 30) * SS), ((hx + 30) * SS, (hy - 84) * SS), ((hx + 8) * SS, (hy - 44) * SS)], fill=FUR, outline=OUTLINE, width=3 * SS)
    _ell(d, hx - 30, hy - 56, 8, 12, (240, 160, 150, 255), None, 0)
    _ell(d, hx + 30, hy - 56, 8, 12, (240, 160, 150, 255), None, 0)
    _ell(d, hx, hy, 58, 52, FUR)
    _ell(d, hx, hy + 22, 34, 24, BELLY, None, 0)
    for ex in (-24, 24):
        if blink:
            d.line(((hx + ex - 10) * SS, (hy - 6) * SS, (hx + ex + 10) * SS, (hy - 6) * SS), fill=(30, 18, 10, 255), width=4 * SS)
        else:
            _ell(d, hx + ex, hy - 6, 11, 13, (30, 18, 10, 255), None, 0)
            _ell(d, hx + ex + 3, hy - 10, 4, 4, (255, 255, 255, 255), None, 0)
    _ell(d, hx - 38, hy + 14, 10, 7, (244, 150, 140, 190), None, 0)
    _ell(d, hx + 38, hy + 14, 10, 7, (244, 150, 140, 190), None, 0)
    _ell(d, hx, hy + 12, 8, 6, (60, 30, 20, 255), None, 0)
    d.arc(((hx - 14) * SS, (hy + 12) * SS, hx * SS, (hy + 30) * SS), 20, 160, fill=(60, 30, 20, 255), width=3 * SS)
    d.arc((hx * SS, (hy + 12) * SS, (hx + 14) * SS, (hy + 30) * SS), 20, 160, fill=(60, 30, 20, 255), width=3 * SS)
    ay = 218 + dip // 2
    _ell(d, 118, ay + 12, 20, 24, (205, 150, 80, 255), (110, 70, 30, 255), 3)
    d.pieslice((98 * SS, (ay - 14) * SS, 138 * SS, (ay + 22) * SS), 180, 360, fill=(120, 76, 36, 255), outline=(80, 48, 20, 255), width=3 * SS)
    _ell(d, 96, ay + 6, 14, 12, FUR2)
    _ell(d, 140, ay + 6, 14, 12, FUR2)
    return _finish(img, w, h)


@lru_cache(maxsize=8)
def sparkle(size: int) -> Image.Image:
    img, d = _canvas(size, size)
    c = size / 2
    pts = []
    for i in range(8):
        r = c if i % 2 == 0 else c * 0.22
        a = math.pi / 4 * i - math.pi / 2
        pts.append(((c + r * math.cos(a)) * SS, (c + r * math.sin(a)) * SS))
    d.polygon(pts, fill=(255, 236, 160, 255))
    return _finish(img, size, size)


def _paste(frame: np.ndarray, spr: Image.Image, cx: float, cy: float, alpha: float = 1.0, angle: float = 0.0, scale: float = 1.0) -> None:
    if angle:
        spr = spr.rotate(angle, resample=Image.BICUBIC, expand=True)
    if scale != 1.0:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    a = np.asarray(spr)
    x0, y0 = int(cx - a.shape[1] / 2), int(cy - a.shape[0] / 2)
    fx0, fy0, fx1, fy1 = max(x0, 0), max(y0, 0), min(x0 + a.shape[1], W), min(y0 + a.shape[0], H)
    if fx0 >= fx1 or fy0 >= fy1:
        return
    crop = a[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    al = crop[..., 3:4].astype(np.float32) / 255.0 * alpha
    dst = frame[fy0:fy1, fx0:fx1].astype(np.float32)
    frame[fy0:fy1, fx0:fx1] = (dst * (1 - al) + crop[..., :3].astype(np.float32) * al).astype(np.uint8)


# main colour, edge colour, size, path (x centre, x swing, y centre, y swing, x period s, y period s, phase); the blue one uses a sharpened x
BUTTERFLIES = [
    ((255, 150, 40), (120, 50, 10), 0.85, (540, 440, 1640, 120, 11.0, 4.2, 0.0)),
    ((255, 105, 180), (120, 30, 80), 0.7, (700, 330, 215, 60, 9.0, 3.1, 2.0)),
    ((90, 170, 255), (20, 60, 120), 0.75, (540, 450, 960, 560, 13.0, 6.5, 4.0)),   # hugs the side margins, crosses the middle quickly
]
SPARKLES = [(120, 560, 52, 0.0), (960, 700, 44, 1.1), (90, 1180, 40, 2.3), (985, 1320, 54, 0.6), (880, 300, 36, 1.9), (200, 1700, 48, 2.9)]


def draw_frame(frame: np.ndarray, t: float) -> None:
    """Draws every decoration for time t (seconds) onto an RGB frame, in place."""
    for x, y, size, ph in SPARKLES:
        a = 0.5 + 0.5 * math.sin(t * 3.2 + ph * 2)
        if a > 0.25:
            _paste(frame, sparkle(size), x, y, alpha=a, scale=0.6 + 0.5 * a)
    for main, edge, size, (cx, sx, cy, sy, px, py, ph) in BUTTERFLIES:
        sx_raw = math.sin(2 * math.pi * t / px + ph)
        x = cx + sx * (math.tanh(2.6 * sx_raw) / math.tanh(2.6) if size == 0.75 else sx_raw)
        y = cy + sy * math.sin(2 * math.pi * t / py + ph * 0.7)
        dx = sx * math.cos(2 * math.pi * t / px + ph)
        flap = 1 + int(9 * abs(math.sin(2 * math.pi * 3.2 * t + ph)))
        _paste(frame, butterfly(main, edge, flap), x, y, angle=-max(-25, min(25, dx / 30)), scale=size)
    tail_q = int(round(6 * math.sin(2 * math.pi * t / 1.6)))
    blink = (t % 3.4) < 0.14
    nibble = int(round(1 + math.sin(2 * math.pi * t / 0.9)))
    bob = 4 * math.sin(2 * math.pi * t / 1.6)
    _paste(frame, squirrel(tail_q, blink, nibble), 140, 250 + bob, scale=0.62)


def decorate(src: Path, dst: Path) -> Path:
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    ok, frame_bgr = cap.read()
    if not ok:
        raise RuntimeError(f"cannot read {src}")
    h, w = frame_bgr.shape[:2]
    if (w, h) != (W, H):
        raise RuntimeError(f"expected {W}x{H}, got {w}x{h}")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-",
           "-i", str(src), "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(dst)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = 0
    while ok:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        draw_frame(rgb, n / fps)
        p.stdin.write(rgb.tobytes())
        n += 1
        ok, frame_bgr = cap.read()
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    return dst


if __name__ == "__main__":
    decorate(Path(sys.argv[1]), Path(sys.argv[2]))
