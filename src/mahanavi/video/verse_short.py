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
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from channels import verse_series as vs
from mahanavi.config import PROJECT_ROOT, get_settings
from mahanavi.images.fonts import FontManager
from mahanavi.video.lakshmi_name_short import FPS, GOLD, H, HIND, IMG_SECONDS, INK, SECONDS, W, XFADE, WHITE, _wrap, cover, vignette

# Shorts buttons (owner 2026-11-28): the like/comment/share column covers the right ~16% and the title/channel bar the bottom ~22%, so text stays
# inside x 38..598 (block shifted left by SHIFT_X) and above y 1010.
TOP_Y, BOTTOM_LIMIT, TEXT_W = 100, 1010, 580
SHIFT_X = -22
CONTENT = {"shiv_tandav_hi": "mahanavi.content.shiv_tandav_hi", "shiv_tandav_trance": "mahanavi.content.shiv_tandav_hi",
           "vedas_te": "mahanavi.content.vedas_te", "vedas_hi": "mahanavi.content.vedas_hi",
           "vishnu_te": "mahanavi.content.vishnu_te", "vishnu_hi": "mahanavi.content.vishnu_hi"}
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
    skip = [t for t in s.image_skip.split(",") if t]
    files = [p for p in files if not any(t in p.name.lower() for t in skip)] or files
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
    # Telugu stacks tall vowel signs and conjuncts above and below the line: measure with a sample that has them, or lines overlap
    h = max(font.getbbox(t)[3] - font.getbbox(t)[1] for t in ("Ag", "శ్రృఞ్చ్ఛ్వ", "क्ष्वृ"))
    return int(h * 1.34) + 4


def _embossed(img: Image.Image, xy: tuple[float, float], text: str, font, fill: tuple[int, int, int], stroke: int) -> None:
    """Letters that look raised: soft drop shadow, dark outline, top-to-bottom shaded fill, bright upper-left rim and dark lower-right rim."""
    x, y = xy
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).text((x, y), text, font=font, fill=255)
    sm = Image.new("L", img.size, 0)
    ImageDraw.Draw(sm).text((x, y), text, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    black = Image.new("RGBA", img.size, (0, 0, 0, 255))
    sh = ImageChops.offset(sm, 5, 7).filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.75))
    img.paste(black, (0, 0), sh)
    img.paste(Image.new("RGBA", img.size, INK + (255,) if len(INK) == 3 else INK), (0, 0), sm)
    top = int(y)
    rows = np.clip((np.arange(img.size[1])[:, None] - top) / max(_lh(font), 1), 0, 1)
    light = np.array(fill, np.float32) * 0.55 + 255 * 0.45
    dark = np.array(fill, np.float32) * 0.72
    grad = (light[None, None, :] * (1 - rows[:, :, None]) + dark[None, None, :] * rows[:, :, None])
    gimg = Image.fromarray(np.broadcast_to(grad, (img.size[1], img.size[0], 3)).astype(np.uint8)).convert("RGBA")
    img.paste(gimg, (0, 0), m)
    rim_hi = ImageChops.subtract(m, ImageChops.offset(m, 2, 2)).point(lambda v: int(v * 1.0))
    rim_lo = ImageChops.subtract(m, ImageChops.offset(m, -2, -2)).point(lambda v: int(v * 0.85))
    img.paste(Image.new("RGBA", img.size, (255, 255, 255, 255)), (0, 0), rim_hi)
    img.paste(Image.new("RGBA", img.size, (60, 25, 0, 255)), (0, 0), rim_lo)


def _layout(key: str, day: int, k: float) -> tuple[np.ndarray, int, int]:
    s, c = vs.SERIES[key], content(key)
    ui = UI["chant" if s.variant == "chant" else s.lang]
    verse, meaning = c.VERSES[day]
    head = c.HEADS[day] if hasattr(c, "HEADS") else ui.get("head", c.HEAD)
    sub = c.SUBS[day] if hasattr(c, "SUBS") else ui["sub"].format(d=day + 1)
    no_subscribe = hasattr(c, "SUBS")   # the Vedas cards carry no subscribe line and no numbering (owner rules 2026-11-06 / 2026-11-14)
    if s.variant == "chant":
        verse, meaning = verse.split("\n")[0].replace("।", "").replace("॥", "").strip(), ui["tail"]
    f_head, f_sub, f_verse = _font(s.lang, int(56 * k)), _font(s.lang, int(32 * k)), _font(s.lang, int(40 * k))
    f_mean, f_subs = _font(s.lang, int(36 * k)), _font(s.lang, 38)
    f_en = ImageFont.truetype(str(HIND), int(31 * k))
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sub_lines = [] if no_subscribe else _lines(probe, ui["subscribe"], f_subs, TEXT_W)
    sub_y = BOTTOM_LIMIT - len(sub_lines) * _lh(f_subs)
    y = TOP_Y

    def block(text, font, col, gap=0):
        nonlocal y
        for ln in _lines(probe, text, font, TEXT_W):
            _embossed(img, ((W - probe.textlength(ln, font=font)) / 2, y), ln, font, col, 4)
            y += _lh(font)
        y += gap

    block(head, f_head, GOLD)
    block(sub, f_sub, WHITE, gap=int(18 * k))
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
        _embossed(img, ((W - probe.textlength(ln, font=f_verse)) / 2, y), ln, f_verse, (255, 226, 140), 3)
        y += _lh(f_verse)
    y += pad + int(22 * k)
    block(meaning, f_mean, WHITE, gap=int(14 * k))
    if s.variant == "meaning" and hasattr(c, "MEANING_EN"):
        block(c.MEANING_EN[day], f_en, (255, 236, 190))
    end = y
    sy = sub_y
    for ln in sub_lines:
        _embossed(img, ((W - probe.textlength(ln, font=f_subs)) / 2, sy), ln, f_subs, GOLD, 5)
        sy += _lh(f_subs)
    return np.roll(np.asarray(img), SHIFT_X, axis=1), (10**6 if too_wide else end), sub_y


def text_layer(key: str, day: int) -> np.ndarray:
    k = 1.4
    while True:
        lay, end, sub_y = _layout(key, day, k)
        if end <= sub_y - 20 or k < 0.5:
            return lay
        k -= 0.03


SEG, XF = 5.8, 0.8        # seconds taken from each clip, and the cross-fade between clips


class _ClipBg:
    """Faded background built from several clips: each day starts on a different clip and at a different second, so the days never look
    the same and nothing visibly loops (15 s = 3 clips x 5.8 s with 0.8 s cross-fades). Dimmed and softened so the text reads neatly."""

    def __init__(self, paths: list[Path], day: int, shift: int):
        n = len(paths)
        order = [(day + shift + i) % n for i in range(n)]
        self.segs = []
        for i, ci in enumerate(order):
            off = round(((day * 1.3 + i * 0.9 + shift * 0.5) % 2.0), 2)       # 0..2 s into the 8 s clip, so 5.8 s always fits
            self.segs.append((paths[ci], off))
        self.caps = [cv2.VideoCapture(str(p)) for p, _ in self.segs]
        for cap, (_, off) in zip(self.caps, self.segs):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(off * 24))
        self.n = 0

    def _read(self, i: int) -> np.ndarray:
        ok, fr = self.caps[i].read()
        if not ok:
            self.caps[i].set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, fr = self.caps[i].read()
        return cover(Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))

    def frame(self, t: float) -> np.ndarray:
        step = SEG - XF                                   # a new clip starts every 5.0 s and fades in over 0.8 s
        i = min(int(t // step), len(self.segs) - 1)
        into = t - i * step
        cur = self._read(i)
        if i > 0 and into < XF:                           # the previous clip keeps playing while it fades out
            w = into / XF
            cur = cv2.addWeighted(self._read(i - 1), 1 - w, cur, w, 0)
        return cv2.GaussianBlur(cur, (0, 0), 2.2)


def _open_bg_video(s: vs.Series, day: int):
    """_ClipBg when every clip in s.bg_video exists in the repo, else None (pictures are used)."""
    paths = [PROJECT_ROOT / x for x in s.bg_video.split(",") if x]
    if not paths or not all(p.exists() for p in paths):
        return None
    return _ClipBg(paths, day, s.bg_shift)


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
    vid = _open_bg_video(s, day)
    for f in range(total):
        t = f / FPS
        if vid is not None:
            base = vid.frame(t)
            frame = base.astype(np.float32) * 0.78 * (0.5 + 0.5 * vig)     # faded, but the deity stays clearly visible
            frame = frame * (1 - la) + lrgb * la
            p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
            continue
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
