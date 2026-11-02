"""One 15 s Short per Lakshmi name: Lakshmi images cross-fading behind, a steadily turning chakra in the middle, the name and
its meaning fading in over it. Frames are drawn with numpy/cv2 and piped to ffmpeg (no per-image overlays to manage).

    python -m mahanavi.video.lakshmi_name_short --n 94 --out out/lakshmi_94.mp4

Images: every .jpg/.png in assets/images/lakshmi108/ (put the owner's Lakshmi pictures there, 8 to 12 is ideal); if that folder is
empty the two small stock Lakshmi photos are used (blurred wide so they still fill the screen).
"""
from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from mahanavi.config import PROJECT_ROOT, get_settings
from mahanavi.content.lakshmi108 import NAMES, SOURCES, STOTRA_SOURCE
from mahanavi.images.fonts import FontManager

W, H, FPS, SECONDS = 720, 1280, 24, 15.0
IMG_SECONDS, XFADE = 4.2, 1.2          # each picture stays this long, then cross-fades into the next
GOLD, WHITE, INK = (255, 214, 120), (255, 255, 255), (18, 8, 0)
HIND = PROJECT_ROOT / "channels" / "engine" / "assets" / "fonts" / "Hind-Bold.ttf"
HIND_R = PROJECT_ROOT / "channels" / "engine" / "assets" / "fonts" / "Hind-Medium.ttf"
OWN_IMAGES = PROJECT_ROOT / "assets" / "images" / "lakshmi108"
STOCK = [PROJECT_ROOT / "assets" / "images" / "deities" / f for f in ("lakshmi_g1.jpg", "lakshmi_g2.jpg")]


def image_files() -> list[Path]:
    own = sorted(p for p in OWN_IMAGES.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")) if OWN_IMAGES.exists() else []
    return own or [p for p in STOCK if p.exists()]


def cover(img: Image.Image, scale: float = 1.0) -> np.ndarray:
    """Fill the 720x1280 frame: sharp crop when the picture is big enough, else a blurred copy behind a centred one."""
    iw, ih = img.size
    s = max(W / iw, H / ih) * scale
    if iw * ih >= 700 * 1200:
        r = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
        x, y = (r.width - W) // 2, (r.height - H) // 2
        return np.asarray(r.crop((x, y, x + W, y + H)).convert("RGB"))
    big = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)   # low-res picture: blurred backdrop + sharp centred copy
    x, y = (big.width - W) // 2, (big.height - H) // 2
    back = np.asarray(big.crop((x, y, x + W, y + H)).convert("RGB"))
    back = cv2.GaussianBlur(back, (0, 0), 14)
    fit = min(W * 0.96 / iw, H * 0.62 / ih) * scale
    fg = img.resize((int(iw * fit), int(ih * fit)), Image.LANCZOS).convert("RGB")
    out = back.copy()
    ox, oy = (W - fg.width) // 2, int(H * 0.30) - fg.height // 2 + int(H * 0.20)
    oy = max(0, min(H - fg.height, oy))
    out[oy:oy + fg.height, ox:ox + fg.width] = np.asarray(fg)
    return out


def chakra(size: int = 608) -> np.ndarray:
    """RGBA lotus mandala: rings, 16 outer and 8 inner petals, two interlocking triangles and a bindu (drawn once, then rotated)."""
    S = size * 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S // 2
    g = GOLD + (255,)
    soft = GOLD + (150,)
    for r, wd in ((0.98, 6), (0.93, 3), (0.62, 4), (0.36, 3)):
        d.ellipse((c - c * r, c - c * r, c + c * r, c + c * r), outline=g, width=wd * 2)
    for ring, n, r0, r1, half in ((0, 16, 0.64, 0.92, 0.075), (1, 8, 0.37, 0.61, 0.13)):
        for k in range(n):
            a = 2 * math.pi * k / n + (math.pi / n if ring else 0)
            tip = (c + c * r1 * math.cos(a), c + c * r1 * math.sin(a))
            l = (c + c * r0 * math.cos(a - half * 2.4), c + c * r0 * math.sin(a - half * 2.4))
            r = (c + c * r0 * math.cos(a + half * 2.4), c + c * r0 * math.sin(a + half * 2.4))
            mid = (c + c * (r0 + (r1 - r0) * 0.55) * math.cos(a), c + c * (r0 + (r1 - r0) * 0.55) * math.sin(a))
            d.line([l, mid, tip, mid, r, l], fill=g, width=5)
            d.polygon([l, tip, r], fill=soft[:3] + (40,))
    for up in (1, -1):
        pts = [(c + c * 0.34 * math.sin(math.radians(a)), c - up * c * 0.34 * math.cos(math.radians(a))) for a in (0, 120, 240)]
        d.line(pts + [pts[0]], fill=g, width=6)
    d.ellipse((c - 18, c - 18, c + 18, c + 18), fill=g)
    return np.asarray(im.resize((size, size), Image.LANCZOS))


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + ([cur] if cur else [])


SUBSCRIBE = "ఇప్పుడే సబ్‌స్క్రైబ్ చేయకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు"
TAGLINE = "ప్రతిరోజు ఒక నామం యొక్క అర్థాన్ని తెలుసుకోండి"
BOTTOM_LIMIT = 1030     # lowest y the text may reach (the Shorts bottom bar sits below this)


def text_layers(n: int) -> list[tuple[float, np.ndarray]]:
    """[(fade-in start second, RGBA layer)]: header, name, meaning, story lines, source, subscribe reminder.
    The blocks are stacked from the top; if the stack would pass BOTTOM_LIMIT every font is shrunk a little and it is laid out again."""
    scale = 1.28     # start big; shrink in steps until the whole stack fits above BOTTOM_LIMIT
    while True:
        layers, end = _layout(n, scale)
        if end <= BOTTOM_LIMIT or scale < 0.8:
            return layers
        scale -= 0.03


def _layout(n: int, k: float) -> tuple[list[tuple[float, np.ndarray]], int]:
    te, tr, mean, l1, l_en, l2, src = NAMES[n - 1]
    s = get_settings()
    tel = FontManager(s.telugu_font_path)
    f_head = tel.get_font(size=int(34 * k), weight="Bold")
    f_tag = tel.get_font(size=int(29 * k), weight="Bold")
    f_name = tel.get_font(size=int(58 * k), weight="Bold")
    f_te = tel.get_font(size=int(34 * k), weight="Bold")
    f_en = ImageFont.truetype(str(HIND_R), int(30 * k), layout_engine=ImageFont.Layout.RAQM)
    f_cnt = ImageFont.truetype(str(HIND), int(30 * k), layout_engine=ImageFont.Layout.RAQM)
    f_tr = ImageFont.truetype(str(HIND), int(38 * k), layout_engine=ImageFont.Layout.RAQM)
    f_small = tel.get_font(size=int(26 * k), weight="Bold")
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    maxw = W - 90

    def layer(items: list[tuple[str, object, tuple, int]], y: int) -> tuple[np.ndarray, int]:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for text, font, col, gap in items:
            for ln in _wrap(probe, text, font, maxw):
                x = (W - probe.textlength(ln, font=font)) / 2
                d.text((x, y), ln, font=font, fill=col, stroke_width=4, stroke_fill=INK)
                bb = font.getbbox(ln)
                y += int((bb[3] - bb[1]) * 1.42) + 4
            y += gap
        return np.asarray(img), y

    out: list[tuple[float, np.ndarray]] = []
    a, y = layer([("శ్రీ లక్ష్మీ దేవి 108 నామాలు", f_head, GOLD, 2), (TAGLINE, f_tag, WHITE, 2), (f"{n} / 108", f_cnt, GOLD, 0)], 70)
    out.append((0.2, a))
    a, y = layer([(f"ఓం {te} నమః", f_name, GOLD, 2), (tr, f_tr, WHITE, 0)], max(y + 36, 270))
    out.append((0.7, a))
    a, y = layer([(mean, f_en, (255, 236, 190), 0)], y + 4)
    out.append((2.0, a))
    a, y = layer([(l1, f_te, WHITE, 4), (l_en, f_en, (255, 248, 230), 4), (l2, f_te, WHITE, 0)], y + 22)
    out.append((3.2, a))
    foot = [(f"{SOURCES[src]}", f_small, GOLD, 2)] if SOURCES[src] else []
    foot.append((STOTRA_SOURCE, f_small, (230, 200, 130), 0))
    a, y = layer(foot, y + 18)
    out.append((6.0, a))
    a, y = layer([(SUBSCRIBE, f_small, WHITE, 0)], y + 16)
    out.append((8.0, a))
    return out, y


def vignette() -> np.ndarray:
    """Edge vignette plus a darker band behind the text (from 22% of the height down) so the words stay easy to read."""
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip(1.05 - 0.55 * d ** 2, 0.25, 1.0)
    band = np.clip(1.0 - 0.45 * np.clip((yy - 0.20 * H) / (0.10 * H), 0, 1), 0.55, 1.0)
    return (v * band).astype(np.float32)[..., None]


def render(n: int, out: Path, music: Path | None = None) -> Path:
    assert 1 <= n <= 108
    files = image_files()
    if not files:
        raise SystemExit("no Lakshmi images found")
    pics = [Image.open(f) for f in files]
    start = (n - 1) % len(pics)     # a different picture first on different days
    seq = [cover(pics[(start + i) % len(pics)]) for i in range(len(pics))]
    chk = chakra()
    layers = text_layers(n)
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
    cs = chk.shape[0]
    for f in range(total):
        t = f / FPS
        slot = IMG_SECONDS
        k = int(t // slot)
        into = t - k * slot
        a = seq[k % len(seq)]
        if into > slot - XFADE:
            b = seq[(k + 1) % len(seq)]
            w = (into - (slot - XFADE)) / XFADE
            base = cv2.addWeighted(a, 1 - w, b, w, 0)
        else:
            base = a
        frame = (base.astype(np.float32) * 0.52 * vig)
        # chakra, turning at a constant size in the middle behind the text
        # the wheel turns steadily at one size (owner: it must rotate, but never pulse in and out like breathing)
        R = cv2.getRotationMatrix2D((cs / 2, cs / 2), -t * 12.0, 1.0)
        rot = cv2.warpAffine(chk, R, (cs, cs), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        ox, oy = (W - cs) // 2, int(H * 0.47) - cs // 2
        x0, y0, x1, y1 = max(ox, 0), max(oy, 0), min(ox + cs, W), min(oy + cs, H)
        sub = rot[y0 - oy:y1 - oy, x0 - ox:x1 - ox].astype(np.float32)
        al = sub[..., 3:4] / 255.0 * (0.50 * min(1.0, t / 1.5))
        frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - al) + sub[..., :3] * al
        for start_s, lay in layers:
            fade = 1.0     # all text is on screen from the first frame, like the other Shorts (no line-by-line reveal)
            la = lay[..., 3:4].astype(np.float32) / 255.0 * fade
            frame = frame * (1 - la) + lay[..., :3].astype(np.float32) * la
        p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    print(render(a.n, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
