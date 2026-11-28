"""Render one tech card as a silent-style 1080x1920 Short (text over a dark grid, soft music): hook, code panel, points, takeaway,
revealed one after another. Safe area: x 70..940, y 190..1250 (clear of the Shorts buttons and title bar)."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from mahanavi.config import get_settings
from mahanavi.content import tech_bank

W, H, FPS, SECONDS = 1080, 1920, 30, 14
X0, X1, Y0, Y1 = 70, 940, 190, 1290
ROOT = Path(__file__).resolve().parents[3]
BOLD = str(ROOT / "ramana/assets/fonts/Poppins-Bold.ttf")
MED = str(ROOT / "ramana/assets/fonts/Poppins-Medium.ttf")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
ACCENT = {"Kubernetes": (80, 140, 255), "Docker": (60, 190, 255), "Terraform": (170, 120, 255), "Git": (255, 130, 80), "CI/CD": (90, 220, 150),
          "DevSecOps": (255, 90, 110), "Linux": (255, 210, 70), "Azure": (60, 160, 255), "AWS": (255, 170, 40), "GCP": (90, 200, 120),
          "LLM": (255, 110, 200), "Vertex AI": (110, 190, 255), "MLOps": (200, 140, 255), "Observability": (80, 230, 210), "DevOps": (120, 220, 120)}
CODE_BG, CODE_FG, WHITE, SOFT = (13, 17, 23), (170, 255, 190), (255, 255, 255), (196, 206, 224)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, int(size))


def wrap(d: ImageDraw.ImageDraw, text: str, f, width: int) -> list[str]:
    out, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            out.append(cur)
            cur = w
    return out + [cur]


def background(accent: tuple[int, int, int]) -> np.ndarray:
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top, bot = np.array([10, 16, 34], np.float32), np.array([4, 6, 14], np.float32)
    bg = np.broadcast_to(top * (1 - y) + bot * y, (H, W, 3)).copy()
    for g in range(0, W, 90):
        bg[:, g:g + 1] += 7
    for g in range(0, H, 90):
        bg[g:g + 1, :] += 7
    glow = np.exp(-(((np.arange(W)[None, :] - 900) / 520.0) ** 2 + ((np.arange(H)[:, None] - 250) / 420.0) ** 2))[..., None]
    bg += glow * np.array(accent, np.float32) * 0.22
    return np.clip(bg, 0, 255)


class Layer:
    def __init__(self, img: Image.Image, t_on: float, y: int):
        self.img, self.t_on, self.y = img, t_on, y   # RGBA strip full width; y = top in frame


def build(day: int) -> tuple[list[Layer], tuple[int, int, int]]:
    cat, hook, code, points, take = tech_bank.CARDS[day]
    acc = ACCENT.get(cat, (120, 200, 255))
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for k in [1.4 - 0.05 * i for i in range(0, 19)]:
        els = _elements(probe, cat, hook, code, points, take, acc, k)
        total = sum(e[0].height for e in els) + 36 * (len(els) - 1)
        if total <= Y1 - Y0:
            break
    gap = min(80, 36 + (Y1 - Y0 - total) // max(1, len(els) - 1))
    layers, y, t = [], Y0, 0.0
    for img, dt_ in els:
        layers.append(Layer(img, t, y))
        y += img.height + gap
        t += dt_
    return layers, acc


def _strip(h: int) -> Image.Image:
    return Image.new("RGBA", (W, h), (0, 0, 0, 0))


def _elements(d, cat, hook, code, points, take, acc, k):
    els = []
    # category chip + channel label
    f = font(BOLD, 40 * k)
    chip = _strip(int(70 * k))
    cd = ImageDraw.Draw(chip)
    tw = cd.textlength(cat.upper(), font=f)
    cd.rounded_rectangle([X0, 0, X0 + tw + 50, int(64 * k)], radius=int(32 * k), fill=acc + (255,))
    cd.text((X0 + 25, int(8 * k)), cat.upper(), font=f, fill=(10, 14, 28, 255))
    fl = font(MED, 36 * k)
    cd.text((X1 - cd.textlength("Reddy Linux", font=fl), int(12 * k)), "Reddy Linux", font=fl, fill=SOFT + (255,))
    els.append((chip, 0.0))
    # hook
    fh = font(BOLD, 86 * k)
    lines = wrap(d, hook, fh, X1 - X0)
    lh = int(fh.size * 1.22)
    hk = _strip(lh * len(lines))
    hd = ImageDraw.Draw(hk)
    for i, ln in enumerate(lines):
        hd.text((X0, i * lh), ln, font=fh, fill=WHITE + (255,))
    els.append((hk, 0.6))
    # code panel
    if code:
        size = 40 * k
        fc = font(MONO, size)
        while max(d.textlength(c, font=fc) for c in code) > X1 - X0 - 70 and size > 18:
            size -= 1
            fc = font(MONO, size)
        lhc = int(size * 1.5)
        ph = lhc * len(code) + 110
        pan = _strip(ph)
        pd = ImageDraw.Draw(pan)
        pd.rounded_rectangle([X0, 0, X1, ph - 20], radius=26, fill=CODE_BG + (255,), outline=acc + (255,), width=3)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            pd.ellipse([X0 + 28 + i * 38, 24, X0 + 52 + i * 38, 48], fill=c + (255,))
        for i, c in enumerate(code):
            pd.text((X0 + 36, 76 + i * lhc), c, font=fc, fill=CODE_FG + (255,))
        els.append((pan, 1.2))
    # points
    fp = font(MED, 50 * k)
    for n, p in enumerate(points):
        ls = wrap(d, p, fp, X1 - X0 - 130)
        lhp = int(fp.size * 1.3)
        h = max(lhp * len(ls) + 30, 100)
        row = _strip(h)
        rd = ImageDraw.Draw(row)
        rd.ellipse([X0, 10, X0 + 78, 88], fill=acc + (255,))
        fn = font(BOLD, 46 * k)
        rd.text((X0 + 39 - rd.textlength(str(n + 1), font=fn) / 2, 18), str(n + 1), font=fn, fill=(10, 14, 28, 255))
        for i, ln in enumerate(ls):
            rd.text((X0 + 110, 8 + i * lhp), ln, font=fp, fill=WHITE + (255,))
        els.append((row, 2.2 if n == 0 else 1.8))
    # takeaway
    ft = font(BOLD, 52 * k)
    ls = wrap(d, take, ft, X1 - X0 - 70)
    lht = int(ft.size * 1.28)
    th = lht * len(ls) + 60
    tk = _strip(th)
    td = ImageDraw.Draw(tk)
    td.rounded_rectangle([X0, 0, X1, th - 10], radius=24, fill=acc + (60,), outline=acc + (255,), width=4)
    for i, ln in enumerate(ls):
        td.text((X0 + 35, 24 + i * lht), ln, font=ft, fill=(255, 235, 150, 255))
    els.append((tk, 1.8))
    return els


def render(day: int, out: Path, music: Path | None = None) -> Path:
    layers, acc = build(day)
    bg = background(acc)
    arrs = [(np.asarray(L.img, dtype=np.float32), L.t_on, L.y) for L in layers]
    music = music or get_settings().alert_short_music_path
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-stream_loop", "-1", "-i", str(music), "-filter_complex", "[1:a]volume=0.5,afade=t=in:st=0:d=1[a]", "-map", "0:v", "-map", "[a]",
           "-t", str(SECONDS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
           "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(SECONDS * FPS):
        t = f / FPS
        frame = bg.copy()
        for a, t_on, y in arrs:
            al = min(1.0, max(0.0, (t - t_on) / 0.45))
            if al <= 0:
                continue
            h = a.shape[0]
            reg = frame[y:y + h]
            m = a[..., 3:4] / 255.0 * al
            reg[:] = reg * (1 - m) + a[..., :3] * m
        p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int, default=0)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    print(render(a.day, a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
