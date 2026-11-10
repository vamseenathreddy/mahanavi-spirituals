"""Lays ready-made green-screen character clips (assets/decor/*.mp4, 720x1280) over a list card, between the background
picture and the text layer, so the card's background picture stays and the words are always on top.

    python -m mahanavi.video.decor_clips bg.png text.png audio_source.mp4 out.mp4

Timeline (14 s card), tuned for the three Veo clips:
  top  : decor_top.mp4     (squirrel, parrot, butterflies, petals: edges of the screen) plays all the time, loops with a short cross-fade
  low  : decor_low_a.mp4   (unicorn, peacock, diya) 0 to 7.2 s, then
         decor_low_b.mp4   (baby elephant, cow and calf) 6.4 to 14 s, cross-faded over 0.8 s
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

W, H = 1080, 1920
FPS = 30
SECONDS = 14.0
PROJECT = Path(__file__).resolve().parents[3]
DECOR = PROJECT / "assets" / "decor"

# name, scale (of the full 1080x1920 frame), anchor "full" or "bottom", loop length used for cross-fading
LAYERS = {
    "top": dict(file="decor_top.mp4", scale=1.0, anchor="full", mode="strict"),      # has a green parrot: only the pure green screen is removed
    "low_a": dict(file="decor_low_a.mp4", scale=0.82, anchor="bottom", mode="floor"),
    "low_b": dict(file="decor_low_b.mp4", scale=0.82, anchor="bottom", mode="floor"),
}
XFADE = 0.8


class Clip:
    def __init__(self, path: Path, scale: float, anchor: str, mode: str = "strict"):
        self.mode = mode
        self.frames: list[np.ndarray] = []      # RGBA uint8, already resized, placed on a small canvas
        cap = cv2.VideoCapture(str(path))
        self.fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        w = int(round(W * scale))
        h = int(round(H * scale))
        self.x0 = (W - w) // 2
        self.y0 = 0 if anchor == "full" else H - h + 30
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            rgb = cv2.resize(rgb, (w, h), interpolation=cv2.INTER_AREA)
            self.frames.append(self._key(rgb, mode))
        cap.release()
        if anchor != "full":     # feather the clip rectangle so no box edge shows where a character touches the border
            ramp = lambda n, k: np.clip(np.arange(n) / k, 0, 1)
            fx = np.minimum(ramp(w, 60), ramp(w, 60)[::-1])
            fy = ramp(h, 80)
            mask = (fy[:, None] * fx[None, :]).astype(np.float32)
            for f in self.frames:
                f[..., 3] = (f[..., 3] * mask).astype(np.uint8)
        if not self.frames:
            raise RuntimeError(f"no frames in {path}")

    @staticmethod
    def _key(rgb: np.ndarray, mode: str = "strict") -> np.ndarray:
        """Green screen to alpha: the screen is pure green (R and B near 0). Parrot greens keep some red so they stay."""
        f = rgb.astype(np.float32)
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        mx = np.maximum(r, b)
        if mode == "floor":     # the lit green floor is brighter and yellower than the screen: key on green dominance
            bg = np.clip((g - mx - 55.0) / 35.0, 0, 1) * np.clip((g - 140.0) / 40.0, 0, 1) * np.clip((130.0 - b) / 40.0, 0, 1)
        else:
            bg = np.clip((70.0 - mx) / 45.0, 0, 1) * np.clip((g - 90.0) / 50.0, 0, 1)
        alpha = 1.0 - bg
        alpha = cv2.erode(alpha, np.ones((2, 2), np.uint8))
        # despill: on the soft edge pixels only, pull green down to the red/blue level
        edge = (alpha > 0.02) & (alpha < 0.98)
        edge = cv2.dilate(edge.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (g > mx + 25)
        g2 = np.where(edge, np.minimum(g, mx + 25), g)
        if mode == "floor":     # glows (diya flame, sparkle spray) blend gold with the green screen: pull that lime back to gold
            lime = (g2 - mx > 40) & (g2 > 165)
            g2 = np.where(lime, mx + 25.0, g2)
            alpha = np.where(lime, alpha * 0.6, alpha)
        out = np.dstack([r, g2, b, alpha * 255.0])
        return np.clip(out, 0, 255).astype(np.uint8)

    def frame_at(self, t: float) -> np.ndarray:
        i = int(t * self.fps)
        return self.frames[min(max(i, 0), len(self.frames) - 1)]

    @property
    def length(self) -> float:
        return len(self.frames) / self.fps


DIM = None   # set by compose(): per-pixel alpha multiplier (dim inside the text block)


def _over(base: np.ndarray, rgba: np.ndarray, x0: int, y0: int, gain: float = 1.0) -> None:
    h, w = rgba.shape[:2]
    y1, x1 = min(y0 + h, H), min(x0 + w, W)
    ys, xs = max(y0, 0), max(x0, 0)
    if y1 <= ys or x1 <= xs:
        return
    crop = rgba[ys - y0:y1 - y0, xs - x0:x1 - x0]
    a = (crop[..., 3:4].astype(np.float32) / 255.0) * gain
    if DIM is not None:
        a = a * DIM[ys:y1, xs:x1]
    dst = base[ys:y1, xs:x1].astype(np.float32)
    base[ys:y1, xs:x1] = (dst * (1 - a) + crop[..., :3].astype(np.float32) * a).astype(np.uint8)


def compose(bg_png: Path, text_png: Path, audio_src: Path, out: Path, decor_dir: Path = DECOR) -> Path:
    global DIM
    bg = np.asarray(Image.open(bg_png).convert("RGB").resize((W, H)))
    text = Image.open(text_png).convert("RGBA").resize((W, H))
    ta = np.asarray(text)[..., 3:4].astype(np.float32) / 255.0
    trgb = np.asarray(text)[..., :3].astype(np.float32)
    clips = {k: Clip(decor_dir / v["file"], v["scale"], v["anchor"], v["mode"]) for k, v in LAYERS.items()}
    # characters pass BEHIND the words: inside the text block they are dimmed so the list stays easy to read
    zone = np.zeros((H, W), np.float32)
    zone[240:1520, 170:910] = 1.0
    zone = cv2.GaussianBlur(zone, (0, 0), 28)

    DIM = (1.0 - 0.4 * zone)[..., None]
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(audio_src), "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "copy", "-t", f"{SECONDS:.2f}", "-movflags", "+faststart", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    top, lo_a, lo_b = clips["top"], clips["low_a"], clips["low_b"]
    loop = top.length - 0.5                       # the top clip restarts 0.5 s before its end, cross-faded
    for n in range(int(SECONDS * FPS)):
        t = n / FPS
        frame = bg.copy()
        # top layer, looping with a cross-fade
        if t < loop:
            _over(frame, top.frame_at(t), top.x0, top.y0)
        else:
            u = (t - loop) / 0.5
            if u < 1.0 and t < top.length:
                _over(frame, top.frame_at(t), top.x0, top.y0, 1 - u)
                _over(frame, top.frame_at(t - loop), top.x0, top.y0, u)
            else:
                _over(frame, top.frame_at(t - loop), top.x0, top.y0)
        # low layers: A first, B takes over with a cross-fade
        b_start = lo_a.length - 0.8 - XFADE + 0.8   # = a_end - XFADE
        a_end = min(lo_a.length, 7.2)
        b_start = a_end - XFADE
        if t < a_end:
            gain = 1.0 if t < b_start else 1 - (t - b_start) / XFADE
            _over(frame, lo_a.frame_at(t), lo_a.x0, lo_a.y0, gain)
        if t >= b_start:
            gain = min(1.0, (t - b_start) / XFADE)
            _over(frame, lo_b.frame_at(t - b_start), lo_b.x0, lo_b.y0, gain)
        frame = (frame.astype(np.float32) * (1 - ta) + trgb * ta).astype(np.uint8)    # the text and the gold frame stay on top
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    return out


if __name__ == "__main__":
    compose(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
