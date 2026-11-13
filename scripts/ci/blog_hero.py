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
HI_FONT = str(ROOT / "channels" / "engine" / "assets" / "fonts" / "Hind-Bold.ttf")

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
        base = Image.new("RGB", (1200, 630), (40, 20, 10))
        base = deity_bg.with_photo(base, deity_bg.pick(p["god"], dt.date(2026, 11, 15) + dt.timedelta(days=p["id"])), mix=0.4, dim=0)
        base = base.convert("RGBA")
        ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([0, 400, 1200, 630], fill=(20, 8, 0, 150))
        base = Image.alpha_composite(base, ov); dr = ImageDraw.Draw(base)
        ff = HI_FONT if cfg.get("lang") == "hi" else FONT; L = ImageFont.Layout.RAQM
        big = ImageFont.truetype(ff, 60, layout_engine=L); small = ImageFont.truetype(ff, 28, layout_engine=L)
        y = 425
        for line in wrap(dr, p["hero_title"], big, 1100)[:2]:
            dr.text((50, y), line, font=big, fill=(255, 226, 150)); y += 70
        dr.text((50, 575), cfg["name"] + "  |  " + cfg.get("hero_tag", "Brahma Purana series"), font=small, fill=(255, 255, 255))
        base.convert("RGB").save(out / p["hero"], quality=88)
        print("wrote", out / p["hero"])
main()
