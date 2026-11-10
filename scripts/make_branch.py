"""make_branch.py: draws the little branch (1080x1920, transparent) the small Ramana peacock hops onto, top right beside the head.
    python scripts/make_branch.py ramana/assets/decor/branch.png
"""
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
rng = random.Random(7)
pts = [(W + 40, 452), (950, 432), (880, 414), (815, 400), (790, 394)]       # right edge to the tip (kept right of the icon row), the peacock's feet touch y~395 before the final shift up
for i in range(len(pts) - 1):
    (x0, y0), (x1, y1) = pts[i], pts[i + 1]
    wd = int(22 - 4 * i)
    d.line([(x0, y0), (x1, y1)], fill=(88, 58, 34, 255), width=wd)
    d.line([(x0, y0 - wd // 3), (x1, y1 - wd // 3)], fill=(128, 90, 52, 255), width=max(wd // 4, 2))
for x, y, dx, dy in [(880, 414, 20, 40), (800, 400, -10, 44), (760, 392, -34, -26)]:       # twigs
    d.line([(x, y), (x + dx, y + dy)], fill=(88, 58, 34, 255), width=6)


def leaf(cx, cy, ang, ln=58, wd=22, col=(70, 130, 58, 235)):
    pts = []
    for t in range(0, 21):
        a = math.pi * t / 20
        pts.append((ln / 2 * math.cos(a), wd / 2 * math.sin(a)))
    for t in range(20, -1, -1):
        a = math.pi * t / 20
        pts.append((ln / 2 * math.cos(a), -wd / 2 * math.sin(a)))
    ca, sa = math.cos(ang), math.sin(ang)
    d.polygon([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts], fill=col)


for cx, cy, ang in [(902, 460, 0.9), (870, 452, 2.2), (822, 448, 1.1), (792, 436, 2.4), (818, 372, -0.7), (808, 426, 1.6), (905, 392, -1.0), (846, 372, -0.9)]:
    leaf(cx, cy, ang, col=(60 + rng.randint(0, 30), 120 + rng.randint(0, 30), 50 + rng.randint(0, 20), 235))
img = img.filter(ImageFilter.GaussianBlur(0.8))
shifted = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shifted.paste(img, (0, -90))          # up, clear of the Telugu quote line: feet line is y~305
shifted.save(sys.argv[1])
