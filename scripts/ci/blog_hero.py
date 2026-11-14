#!/usr/bin/env python3
"""Make 1200x630 hero images for a site's posts: deity photo behind, English title band on top.
  python scripts/ci/blog_hero.py --site purana"""
from __future__ import annotations
import argparse, datetime as dt, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from mahanavi.images import deity_bg  # noqa: E402
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
TE_FONT = str(ROOT / "assets" / "fonts" / "NotoSansTelugu-Variable.ttf")
HI_FONT = str(ROOT / "channels" / "engine" / "assets" / "fonts" / "Hind-Bold.ttf")

def nature(seed: int) -> Image.Image:
    """Generated sunrise / hills / lotus-pond style backdrop, used when no deity photo matches the topic."""
    import random, math
    r = random.Random(seed)
    pal = [((255, 190, 90), (120, 40, 60), (30, 18, 40)), ((255, 220, 140), (70, 120, 150), (14, 40, 50)),
           ((250, 150, 90), (90, 50, 110), (25, 15, 45)), ((255, 235, 170), (60, 140, 110), (12, 50, 40))]
    top, mid, dark = pal[seed % len(pal)]
    im = Image.new("RGB", (1200, 630)); px = im.load()
    for y in range(630):
        t = y / 630
        for x in range(1200):
            a = min(1, math.hypot((x - 600 - r.randint(0, 0)) / 700, (y - 330) / 330))
            c = tuple(int(top[i] * (1 - a) + mid[i] * a) for i in range(3))
            px[x, y] = tuple(int(c[i] * (1 - t * 0.35) + dark[i] * t * 0.35) for i in range(3))
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse([520, 190, 680, 350], fill=(255, 245, 210, 235))
    for k in range(3):
        base = 360 + k * 70; col = tuple(int(dark[i] + (mid[i] - dark[i]) * (0.5 - k * 0.25)) for i in range(3))
        ph = r.random() * 6; pts = [(0, 630)] + [(x, base - 40 * math.sin(x / (170 + k * 60) + ph) - 25 * math.sin(x / 70 + ph * 2)) for x in range(0, 1220, 20)] + [(1200, 630)]
        d.polygon(pts, fill=col + (255,))
    return im


def wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--site", required=True); a = ap.parse_args()
    d = ROOT / "content" / "sites" / a.site
    cfg = json.loads((d / "site.json").read_text())
    out = ROOT / "assets" / "blog" / cfg["hero_dir"]; out.mkdir(parents=True, exist_ok=True)
    for f in sorted((d / "posts").glob("*.json")):
        p = json.loads(f.read_text())
        photo = deity_bg.pick(p["god"], dt.date(2026, 11, 15) + dt.timedelta(days=p["id"])) if p["god"] != "nature" else None
        if photo is None:
            base = nature(p["id"])
        else:
            base = Image.new("RGB", (1200, 630), (40, 20, 10))
            base = deity_bg.with_photo(base, photo, mix=0.4, dim=0)
        base = base.convert("RGBA")
        ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([0, 400, 1200, 630], fill=(20, 8, 0, 150))
        base = Image.alpha_composite(base, ov); dr = ImageDraw.Draw(base)
        ff = {"hi": HI_FONT, "te": TE_FONT}.get(cfg.get("lang"), FONT); L = ImageFont.Layout.RAQM
        big = ImageFont.truetype(ff, 60, layout_engine=L); small = ImageFont.truetype(ff, 28, layout_engine=L)
        if cfg.get("lang") == "te":
            for f_ in (big, small):
                f_.set_variation_by_name("Bold")
        y = 425
        for line in wrap(dr, p["hero_title"], big, 1100)[:2]:
            dr.text((50, y), line, font=big, fill=(255, 226, 150)); y += 70
        dr.text((50, 575), (cfg["name"] + "  |  " + cfg.get("hero_tag", "Brahma Purana series")) if cfg.get("hero_tag") != cfg["name"] else cfg["name"], font=small, fill=(255, 255, 255))
        base.convert("RGB").save(out / p["hero"], quality=88)
        print("wrote", out / p["hero"])
main()
