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


@lru_cache(maxsize=16)
def squirrel_run(phase: int, tail_q: int) -> Image.Image:
    """Side view, facing right, running: phase 0..3 moves the legs, tail_q -3..3 sways the tail."""
    w, h = 340, 240
    img, d = _canvas(w, h)
    tail = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    td = ImageDraw.Draw(tail)
    for rx, ry, col, ox in ((52, 100, FUR, 0), (34, 76, FUR2, 6)):
        td.ellipse(((70 - rx + ox) * SS, (100 - ry) * SS, (70 + rx + ox) * SS, (100 + ry) * SS), fill=col,
                   outline=OUTLINE if col == FUR else None, width=4 * SS)
    tail = tail.rotate(tail_q * 3, resample=Image.BICUBIC, center=(90 * SS, 170 * SS))
    img.alpha_composite(tail)
    d = ImageDraw.Draw(img)
    legs = [(-26, 0), (8, -10), (26, 0), (-8, -10)]   # leg swing offsets by phase
    for i, base in enumerate((120, 190)):
        off = legs[(phase + 2 * i) % 4]
        _ell(d, base + off[0], 214 + off[1], 30, 13, FUR2)
        _ell(d, base + off[0] * 0.4, 198, 17, 24, FUR)
    _ell(d, 150, 160, 84, 52, FUR)
    _ell(d, 160, 182, 52, 26, BELLY, None, 0)
    hx, hy = 244, 130
    d.polygon([((hx - 24) * SS, (hy - 24) * SS), ((hx - 10) * SS, (hy - 66) * SS), ((hx + 10) * SS, (hy - 34) * SS)], fill=FUR, outline=OUTLINE, width=3 * SS)
    _ell(d, hx, hy, 46, 42, FUR)
    _ell(d, hx + 24, hy + 14, 26, 20, BELLY, None, 0)
    _ell(d, hx + 14, hy - 8, 9, 11, (30, 18, 10, 255), None, 0)
    _ell(d, hx + 17, hy - 12, 3, 3, (255, 255, 255, 255), None, 0)
    _ell(d, hx + 46, hy + 4, 8, 6, (60, 30, 20, 255), None, 0)
    _ell(d, hx + 6, hy + 14, 9, 6, (244, 150, 140, 190), None, 0)
    return _finish(img, w, h)


LILAC = (150, 132, 182, 255)
MANE_COLS = [(255, 120, 170), (200, 130, 255), (130, 160, 255), (120, 210, 230), (255, 170, 210)]


def _spline(pts, closed=True, n=14):
    """Catmull-Rom curve through the control points, returned as a dense list of points."""
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    return out


def _fill(img, pts, top, bot, outline=LILAC, ow=3, y0=None, y1=None):
    """Smooth closed shape with a vertical colour gradient and a soft outline (all coordinates in canvas units)."""
    sp = [(x * SS, y * SS) for x, y in pts]
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon(sp, fill=255)
    ys = [y for _, y in pts]
    lo, hi = (min(ys) if y0 is None else y0), (max(ys) if y1 is None else y1)
    col = np.zeros((img.size[1], img.size[0], 4), np.uint8)
    rows = np.clip((np.arange(img.size[1]) / SS - lo) / max(hi - lo, 1), 0, 1)[:, None]
    for c in range(3):
        col[..., c] = (top[c] * (1 - rows) + bot[c] * rows).astype(np.uint8)
    col[..., 3] = 255
    layer = Image.fromarray(col, "RGBA")
    layer.putalpha(mask)
    img.alpha_composite(layer)
    if outline:
        ImageDraw.Draw(img).line(sp + [sp[0]], fill=outline, width=ow * SS, joint="curve")


def _strand(d, pts, col, w0, w1):
    """A tapering flowing strand: overlapping dots along a smooth curve."""
    sp = _spline(pts, closed=False, n=30)
    for i, (x, y) in enumerate(sp):
        r = w0 + (w1 - w0) * i / max(len(sp) - 1, 1)
        d.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=col + (255,))


def _limb(d, joints, widths, col, hoof):
    """A leg as capsules between joints, tapering, ending in a hoof."""
    for (x0, y0), (x1, y1), w0, w1 in zip(joints, joints[1:], widths, widths[1:]):
        steps = 14
        for k in range(steps + 1):
            x, y, r = x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps, (w0 + (w1 - w0) * k / steps) / 2
            d.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=col, outline=None)
    hx, hy = joints[-1]
    d.ellipse(((hx - 10) * SS, (hy - 7) * SS, (hx + 12) * SS, (hy + 9) * SS), fill=hoof, outline=(120, 90, 40, 255), width=2 * SS)


@lru_cache(maxsize=32)
def unicorn(flap_q: int, leg_q: int) -> Image.Image:
    """Side view, facing right, flying in a gallop pose: flap_q -3..3 moves the wing, leg_q 0..1 alternates the leg pose."""
    w, h = 700, 470
    img, d = _canvas(w, h)
    ox, oy = 120, 90
    T = lambda pts: [(x + ox, y + oy) for x, y in pts]
    WHITE, SHADE = (255, 252, 255), (214, 206, 236)
    # tail: flowing strands from the dock
    dock = (88 + ox, 165 + oy)
    for i, col in enumerate(MANE_COLS * 2):
        dy = i * 7 - 18
        wav = 10 if i % 2 else -10
        _strand(d, [dock, (dock[0] - 40, dock[1] + 6 + dy * 0.4), (dock[0] - 85, dock[1] + 30 + dy + wav), (dock[0] - 130, dock[1] + 20 + dy * 1.4 - wav), (dock[0] - 165, dock[1] + 52 + dy * 1.2)],
                col, 8, 2)
    # far legs (a little darker), then the wing behind the body line, body, near legs
    far = ([(140, 205), (170, 262), (140, 300), (125, 322)], [(300, 205), (360, 245), (400, 262), (418, 270)]) if leg_q == 0 else \
          ([(140, 205), (118, 268), (84, 292), (66, 306)], [(300, 205), (340, 250), (372, 290), (380, 318)])
    for j in far:
        _limb(d, [(x + ox, y + oy) for x, y in j], [30, 17, 13, 12], (226, 218, 244, 255), (236, 205, 130, 255))
    # wing: fan of feathers around the shoulder, swung by the flap
    wing = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh = (240 + ox, 150 + oy)
    for k, (ang, ln) in enumerate(((110, 120), (126, 150), (142, 170), (158, 178), (174, 170), (190, 150), (205, 120), (218, 90))):
        a = math.radians(ang)
        tip = (sh[0] + ln * math.cos(a), sh[1] - ln * math.sin(a))
        side = (math.cos(a + math.pi / 2), -math.sin(a + math.pi / 2))
        mid = ((sh[0] + tip[0]) / 2, (sh[1] + tip[1]) / 2)
        pts = [sh, (mid[0] + side[0] * 15, mid[1] + side[1] * 15), tip, (mid[0] - side[0] * 12, mid[1] - side[1] * 12)]
        _fill(wing, _spline(pts, n=8), (255, 255, 255), (225, 214, 250), outline=(185, 170, 225, 255), ow=2)
    wing = wing.rotate(flap_q * 7, resample=Image.BICUBIC, center=(sh[0] * SS, sh[1] * SS))
    img.alpha_composite(wing)
    d = ImageDraw.Draw(img)
    body = T([(250, 150), (205, 146), (150, 146), (112, 152), (88, 168), (88, 205), (104, 242), (150, 240), (205, 240), (262, 236), (306, 222),
              (330, 192), (348, 150), (372, 112), (392, 100), (428, 108), (448, 100), (450, 86), (434, 66), (404, 50), (382, 28), (360, 20),
              (338, 40), (310, 80), (282, 118)])
    _fill(img, _spline(body, n=12), WHITE, SHADE, y0=20 + oy, y1=242 + oy)
    d = ImageDraw.Draw(img)
    # soft muscle shading on thigh and shoulder
    for cx, cy, rx, ry in ((130, 205, 36, 40), (305, 190, 30, 36), (210, 215, 70, 20)):
        sh_l = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh_l).ellipse(((cx + ox - rx) * SS, (cy + oy - ry) * SS, (cx + ox + rx) * SS, (cy + oy + ry) * SS), fill=(190, 178, 225, 70))
        img.alpha_composite(sh_l)
    d = ImageDraw.Draw(img)
    near = ([(150, 210), (130, 270), (90, 292), (64, 306)], [(310, 205), (352, 238), (398, 252), (424, 260)]) if leg_q == 0 else \
           ([(150, 210), (172, 268), (140, 304), (126, 326)], [(310, 205), (350, 252), (376, 292), (386, 322)])
    for j in near:
        _limb(d, [(x + ox, y + oy) for x, y in j], [34, 19, 14, 13], WHITE + (255,), (240, 210, 130, 255))
    # ear, mane
    d.polygon([((346 + ox) * SS, (34 + oy) * SS), ((352 + ox) * SS, (4 + oy) * SS), ((366 + ox) * SS, (30 + oy) * SS)], fill=WHITE + (255,), outline=LILAC, width=3 * SS)
    crest = [(352, 28), (338, 44), (322, 66), (306, 90), (292, 114), (280, 134)]
    for i, col in enumerate(MANE_COLS * 2):
        bx, by = crest[i % len(crest)]
        wav = 12 if i % 2 else -8
        _strand(d, [(bx + ox, by + oy), (bx - 22 + ox, by + 4 + oy), (bx - 52 + ox, by + 26 + wav + oy), (bx - 84 + ox, by + 30 + oy), (bx - 108 + ox, by + 52 - wav + oy)], col, 7, 2)
    # golden spiral horn
    base_a, base_b, tip = (386 + ox, 44 + oy), (404 + ox, 52 + oy), (462 + ox, -40 + oy)
    d.polygon([(base_a[0] * SS, base_a[1] * SS), (base_b[0] * SS, base_b[1] * SS), (tip[0] * SS, tip[1] * SS)], fill=(255, 214, 90, 255), outline=(190, 140, 30, 255), width=3 * SS)
    for t0 in (0.22, 0.4, 0.58, 0.76):
        cx, cy = base_a[0] + (tip[0] - base_a[0]) * t0, base_a[1] + (tip[1] - base_a[1]) * t0
        wdt = 9 * (1 - t0)
        d.line(((cx - wdt) * SS, (cy + 6) * SS, (cx + wdt + 4) * SS, (cy - 4) * SS), fill=(190, 140, 30, 255), width=3 * SS)
    # eye, nostril, mouth, cheek
    ex, ey = 396 + ox, 66 + oy
    d.ellipse(((ex - 12) * SS, (ey - 8) * SS, (ex + 12) * SS, (ey + 8) * SS), fill=(255, 255, 255, 255), outline=(70, 50, 100, 255), width=2 * SS)
    d.ellipse(((ex - 7) * SS, (ey - 8) * SS, (ex + 7) * SS, (ey + 8) * SS), fill=(110, 70, 170, 255))
    d.ellipse(((ex - 3) * SS, (ey - 4) * SS, (ex + 3) * SS, (ey + 2) * SS), fill=(20, 10, 40, 255))
    d.ellipse(((ex + 1) * SS, (ey - 7) * SS, (ex + 6) * SS, (ey - 2) * SS), fill=(255, 255, 255, 255))
    d.line(((ex - 12) * SS, (ey - 6) * SS, (ex - 20) * SS, (ey - 14) * SS), fill=(70, 50, 100, 255), width=3 * SS)
    d.ellipse(((437 + ox) * SS, (88 + oy) * SS, (445 + ox) * SS, (95 + oy) * SS), fill=(190, 150, 175, 255))
    d.arc(((410 + ox) * SS, (96 + oy) * SS, (444 + ox) * SS, (118 + oy) * SS), 20, 130, fill=(150, 110, 140, 255), width=3 * SS)
    cheek = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(cheek).ellipse(((388 + ox - 16) * SS, (92 + oy - 10) * SS, (388 + ox + 16) * SS, (92 + oy + 10) * SS), fill=(255, 170, 200, 120))
    img.alpha_composite(cheek)
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
    ((255, 150, 40), (120, 50, 10), 0.85, (540, 450, 1230, 260, 18.0, 8.0, 0.0)),
    ((255, 105, 180), (120, 30, 80), 0.7, (700, 330, 215, 60, 14.0, 5.0, 2.0)),
    ((90, 170, 255), (20, 60, 120), 0.75, (540, 450, 960, 560, 20.0, 10.0, 4.0)),   # hugs the side margins, crosses the middle quickly
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
        x = cx + sx * (math.tanh(2.6 * sx_raw) / math.tanh(2.6) if size in (0.75, 0.85) else sx_raw)
        y = cy + sy * math.sin(2 * math.pi * t / py + ph * 0.7)
        dx = sx * math.cos(2 * math.pi * t / px + ph)
        flap = 1 + int(9 * abs(math.sin(2 * math.pi * 1.7 * t + ph)))
        _paste(frame, butterfly(main, edge, flap), x, y, angle=-max(-25, min(25, dx / 30)), scale=size)
    _draw_squirrel(frame, t)
    _draw_unicorn(frame, t)


SQ_LEFT, SQ_RIGHT, SQ_Y = 140, 940, 250
# (start s, end s, what): sit left, run right, sit right, run left, sit left
SQ_PLAN = [(0.0, 2.5, "sit_l"), (2.5, 5.0, "run_r"), (5.0, 8.0, "sit_r"), (8.0, 10.5, "run_l"), (10.5, 1e9, "sit_l")]


def _draw_squirrel(frame: np.ndarray, t: float) -> None:
    for a, b, what in SQ_PLAN:
        if a <= t < b:
            u = (t - a) / (b - a) if b < 1e8 else 0.0
            break
    if what.startswith("sit"):
        tail_q = int(round(6 * math.sin(2 * math.pi * t / 1.6)))
        blink = (t % 3.4) < 0.14
        nibble = int(round(1 + math.sin(2 * math.pi * t / 0.9)))
        spr = squirrel(tail_q, blink, nibble)
        if what == "sit_r":
            spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
        x = SQ_LEFT if what == "sit_l" else SQ_RIGHT
        _paste(frame, spr, x, SQ_Y + 4 * math.sin(2 * math.pi * t / 1.6), scale=0.62)
    else:
        e = u * u * (3 - 2 * u)                      # ease in and out
        x = SQ_LEFT + (SQ_RIGHT - SQ_LEFT) * (e if what == "run_r" else 1 - e)
        phase = int(t * 9) % 4
        spr = squirrel_run(phase, int(round(3 * math.sin(2 * math.pi * t * 3))))
        if what == "run_l":
            spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
        _paste(frame, spr, x, SQ_Y - 16 - 10 * abs(math.sin(2 * math.pi * t * 4.5)), scale=0.62)


UNI_Y = 1625
# (start s, end s, direction): fly right, then back left, then rest off screen
UNI_PLAN = [(0.8, 6.8, 1), (7.2, 13.2, -1)]


def _draw_unicorn(frame: np.ndarray, t: float) -> None:
    for a, b, direction in UNI_PLAN:
        if a <= t < b:
            u = (t - a) / (b - a)
            x = -150 + 1380 * u if direction == 1 else 1230 - 1380 * u
            y = UNI_Y + 28 * math.sin(2 * math.pi * t / 2.4)
            spr = unicorn(int(round(3 * math.sin(2 * math.pi * t * 1.3))), int(t * 2.2) % 2)
            if direction == -1:
                spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
            for k in range(1, 5):                           # a little trail of sparkles behind
                tx = x - direction * (150 + 55 * k)
                _paste(frame, sparkle(40), tx, y + 10 * math.sin(t * 5 + k), alpha=max(0.0, 0.8 - 0.17 * k), scale=0.7)
            _paste(frame, spr, x, y, scale=0.62)
            return


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
