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
    args = ap.parse_args()
    clip = Clip(Path(args.clip), 1.0, "full", args.mode)
    Path(args.prefix).parent.mkdir(parents=True, exist_ok=True)

    def sink(path: str, pix_in: str):
        return subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", pix_in, "-s", f"{W}x{H}", "-r", str(clip.fps),
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
