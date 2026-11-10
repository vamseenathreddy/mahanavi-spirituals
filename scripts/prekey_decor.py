"""prekey_decor.py: turn a green-screen character clip into a transparent pair that plain ffmpeg can overlay anywhere.

    python scripts/prekey_decor.py clip.mp4 ramana/assets/decor/peacock [--mode strict|floor]

writes <prefix>_rgb.mp4 and <prefix>_alpha.mp4 (grey = opacity). Overlay with ffmpeg alphamerge:
    -stream_loop -1 -i x_rgb.mp4 -stream_loop -1 -i x_alpha.mp4 ... [rgb][alpha]alphamerge[char];[bg][char]overlay
Keying is the same as mahanavi.video.decor_clips (mode strict keeps green feathers/parrots, floor also removes a lit green floor).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mahanavi.video.decor_clips import FPS, H, W, Clip  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("prefix")
    ap.add_argument("--mode", default="strict", choices=["strict", "floor"])
    ap.add_argument("--floor-cut", type=float, default=0.0, help="below this fraction of the height also remove leftover green floor/shadow (0 = off)")
    ap.add_argument("--feather", type=float, default=0.0, help="fade the left, right and top edges over this fraction of the width, hides clip borders")
    ap.add_argument("--fan-fade", type=float, default=0.0, help="from this second the clip's wide, frame-cropped shape is faded with a soft oval instead of a box edge (peacock fan)")
    args = ap.parse_args()
    clip = Clip(Path(args.clip), 720 / W, "full", args.mode)       # stored at the clip's own 720x1280, ffmpeg scales it on use
    h_, w_ = clip.frames[0].shape[:2]
    if args.floor_cut:
        y0 = int(h_ * args.floor_cut)
        for f in clip.frames:
            r, g, b = (f[y0:, :, i].astype(np.int16) for i in range(3))
            green = np.clip((g - np.maximum(r, b) - 25) / 30.0, 0, 1)
            f[y0:, :, 3] = (f[y0:, :, 3] * (1 - green)).astype(np.uint8)
    Path(args.prefix).parent.mkdir(parents=True, exist_ok=True)

    if args.feather:
        k = max(int(w_ * args.feather), 1)
        ramp = np.clip(np.arange(w_) / k, 0, 1)
        mask = np.minimum(ramp, ramp[::-1])[None, :] * np.clip(np.arange(h_) / max(int(h_ * 0.05), 1), 0, 1)[:, None]
        for f in clip.frames:
            f[..., 3] = (f[..., 3] * mask).astype(np.uint8)

    if args.fan_fade:
        yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
        cy = 0.64 * h_
        d = np.sqrt(((xx - w_ / 2) / (0.40 * w_)) ** 2 + ((yy - cy) / (0.62 * h_)) ** 2)
        oval = np.clip((1.0 - d) / 0.55, 0, 1)
        oval = oval * oval * (3 - 2 * oval)           # smoothstep: no visible rim
        for i, f in enumerate(clip.frames):
            w = float(np.clip((i / clip.fps - args.fan_fade) / 0.8, 0, 1))
            f[..., 3] = (f[..., 3] * (1 - w * (1 - oval))).astype(np.uint8)

    def sink(path: str, pix_in: str):   # noqa: E306
        return subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", pix_in, "-s", f"{w_}x{h_}", "-r", str(clip.fps),
                                 "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", path],
                                stdin=subprocess.PIPE)
    prgb, palpha = sink(f"{args.prefix}_rgb.mp4", "rgb24"), sink(f"{args.prefix}_alpha.mp4", "gray")
    for f in clip.frames:
        prgb.stdin.write(np.ascontiguousarray(f[..., :3]).tobytes())
        palpha.stdin.write(np.ascontiguousarray(f[..., 3]).tobytes())
    for p in (prgb, palpha):
        p.stdin.close()
        p.wait()
    print(f"wrote {args.prefix}_rgb.mp4 / _alpha.mp4 ({len(clip.frames)} frames @ {clip.fps:g} fps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
