"""Long-video thumbnail maker (1280x720): deity photo or your own art on the right, big Telugu hook text on the left.
Usage: python scripts/ci/thumb_make.py OUT.jpg --photo shiva_g1 [--art path.jpg] --line1 "..." --line2 "..." [--line3 "..."] [--badge "10 నిమిషాలు"] [--theme gold|red|green]"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
FONT = str(ROOT / "assets/fonts/NotoSansTelugu-Variable.ttf")
W, H = 1280, 720
THEMES = {
    "gold": dict(bg=((120, 20, 10), (40, 6, 20)), l1=(255, 224, 90), l2=(255, 255, 255), l3=(255, 160, 40), badge=(220, 30, 30)),
    "red": dict(bg=((150, 10, 20), (45, 4, 12)), l1=(255, 235, 120), l2=(255, 255, 255), l3=(255, 190, 60), badge=(255, 200, 30)),
    "green": dict(bg=((10, 80, 50), (4, 25, 20)), l1=(255, 235, 120), l2=(255, 255, 255), l3=(255, 170, 50), badge=(220, 30, 30)),
}


def font(size):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_name("Black")
    except Exception:
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    return f


def fit(draw, text, max_w, size, min_size=40):
    while size > min_size:
        if draw.textlength(text, font=font(size)) <= max_w:
            break
        size -= 4
    return font(size)


def make(out, photo=None, art=None, l1="", l2="", l3="", badge="", theme="gold"):
    t = THEMES[theme]
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        k = y / H
        c = tuple(int(t["bg"][0][i] * (1 - k) + t["bg"][1][i] * k) for i in range(3))
        for x in range(W):
            px[x, y] = c
    src = Path(art) if art else next((ROOT / "assets/images/deities").glob(photo + ".*"))
    ph = Image.open(src).convert("RGB")
    glow = ImageOps.fit(ph, (W, H), method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    im = Image.blend(im, glow, 0.35)
    fg = ImageOps.fit(ph, (620, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    mask = Image.linear_gradient("L").rotate(90).resize((620, H))
    mask = ImageOps.invert(mask).point(lambda v: 255 if v > 230 else min(255, int(v * 1.2)))
    mask = Image.linear_gradient("L").rotate(90).resize((620, H)).point(lambda v: min(255, v * 3))
    im.paste(fg, (W - 620, 0), ImageOps.mirror(mask) if False else mask.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_LEFT_RIGHT))
    d = ImageDraw.Draw(im)
    maxw = 700
    y = 90
    for text, col, size in ((l1, t["l1"], 120), (l2, t["l2"], 104), (l3, t["l3"], 92)):
        if not text:
            continue
        f = fit(d, text, maxw, size)
        d.text((50, y), text, font=f, fill=col, stroke_width=7, stroke_fill=(20, 0, 0))
        y += int(f.size * 1.45)
    if badge:
        bf = font(46)
        bw = int(d.textlength(badge, font=bf)) + 50
        d.rounded_rectangle((40, H - 110, 40 + bw, H - 40), 14, fill=t["badge"])
        d.text((65, H - 100), badge, font=bf, fill=(255, 255, 255) if theme != "red" else (60, 0, 0))
    im.save(out, quality=92)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("out")
    a.add_argument("--photo", default="shiva_g1")
    a.add_argument("--art")
    a.add_argument("--line1", default="")
    a.add_argument("--line2", default="")
    a.add_argument("--line3", default="")
    a.add_argument("--badge", default="")
    a.add_argument("--theme", default="gold")
    x = a.parse_args()
    make(x.out, x.photo, x.art, x.line1, x.line2, x.line3, x.badge, x.theme)
