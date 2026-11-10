"""Lakshmi decor layers: gold coins (float, then one shower) and baby elephants pouring golden water, laid BEHIND the text.

Prekeyed pairs (RGB mp4 + alpha mp4, made with scripts/prekey_decor.py --gold-despill) live in assets/decor_lakshmi/:
    python scripts/prekey_decor.py coins.mp4 assets/decor_lakshmi/coins --mode strict --gold-despill
    python scripts/prekey_decor.py eleph.mp4 assets/decor_lakshmi/eleph --mode floor --gold-despill
The clips are streamed frame by frame (no big frame cache) and played once at the start of the 15 s Short.
Any missing file just means that layer is skipped.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from mahanavi.config import PROJECT_ROOT

DECOR = PROJECT_ROOT / "assets" / "decor_lakshmi"
# name -> (cycle seconds, gain, fade-in s, fade-out s, scale, anchor)
LAYERS = {
    "coins": dict(cycle=7.6, gain=0.28, fin=0.25, fout=0.9, scale=1.0, anchor="full", center_dim=0.12),
    "eleph": dict(cycle=7.6, gain=0.32, fin=0.5, fout=0.7, scale=0.75, anchor="bottom", feather_top=0.07, corners=0.56, inner_feather=0.30),
}


class _Stream:
    def __init__(self, name: str, cfg: dict, w: int, h: int):
        self.cfg, self.w, self.h = cfg, w, h
        self.rgb = cv2.VideoCapture(str(DECOR / f"{name}_rgb.mp4"))
        self.alpha = cv2.VideoCapture(str(DECOR / f"{name}_alpha.mp4"))
        self.pos = 0
        self.fps = self.rgb.get(cv2.CAP_PROP_FPS) or 24.0
        self.n = int(self.rgb.get(cv2.CAP_PROP_FRAME_COUNT))

    def at(self, t: float):
        """(rgb float HxWx3, alpha float HxWx1 already faded) for second t of the Short, or None."""
        c = self.cfg
        if t >= c["cycle"]:        # plays once only, then the picture and the text have the screen to themselves
            return None
        local = t
        idx = min(int(local * self.fps), self.n - 1)
        if idx != self.pos:
            self.rgb.set(cv2.CAP_PROP_POS_FRAMES, idx)
            self.alpha.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok1, f = self.rgb.read()
        ok2, a = self.alpha.read()
        self.pos = idx + 1
        if not (ok1 and ok2):
            return None
        fade = min(1.0, local / c["fin"], (c["cycle"] - local) / c["fout"]) if c["fout"] else 1.0
        fade = max(0.0, min(1.0, fade))
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        al = a[..., 0] if a.ndim == 3 else a
        if c["scale"] != 1.0:
            s = c["scale"]
            rgb = cv2.resize(rgb, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
            al = cv2.resize(al, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        al = al.astype(np.float32)[..., None] / 255.0 * (c["gain"] * fade)
        if c.get("feather_x"):       # soft sides and top so the clip never shows as a box
            hh, ww = al.shape[:2]
            k = max(int(ww * c["feather_x"]), 1)
            ramp = np.clip(np.arange(ww, dtype=np.float32) / k, 0, 1)
            ramp = np.minimum(ramp, ramp[::-1])
            ramp = ramp * ramp * (3 - 2 * ramp)
            top = np.clip(np.arange(hh, dtype=np.float32) / max(int(hh * c.get("feather_top", 0.05)), 1), 0, 1)
            al = al * ramp[None, :, None] * top[:, None, None]
        if c.get("center_dim") is not None:       # keep the middle (goddess and name) clear: the layer lives along the sides
            xs = np.abs(np.linspace(-1, 1, al.shape[1], dtype=np.float32))
            m = c["center_dim"] + (1 - c["center_dim"]) * np.clip((xs - 0.30) / 0.35, 0, 1)
            al = al * m[None, :, None]
        return rgb.astype(np.float32), al


class LakshmiDecor:
    def __init__(self, w: int, h: int, names=("eleph", "coins")):
        self.w, self.h = w, h
        self.streams = [_Stream(n, LAYERS[n], w, h) for n in names
                        if (DECOR / f"{n}_rgb.mp4").exists() and (DECOR / f"{n}_alpha.mp4").exists()]

    def apply(self, frame: np.ndarray, t: float, avoid: np.ndarray | None = None) -> np.ndarray:
        """avoid: HxWx1 0..1 soft mask of where the text is; the decor fades out there so the words stay easy to read."""
        for s in self.streams:
            got = s.at(t)
            if got is None:
                continue
            rgb, al = got
            if s.cfg.get("corners"):
                self._corners(frame, s.cfg, rgb, al, avoid)
                continue
            hh, ww = rgb.shape[:2]
            x0 = (self.w - ww) // 2
            y0 = 0 if s.cfg["anchor"] == "full" else self.h - hh
            x0c, y0c = max(x0, 0), max(y0, 0)
            sub = (slice(y0c, min(y0 + hh, self.h)), slice(x0c, min(x0 + ww, self.w)))
            r = rgb[sub[0].start - y0:sub[0].stop - y0, sub[1].start - x0:sub[1].stop - x0]
            a = al[sub[0].start - y0:sub[0].stop - y0, sub[1].start - x0:sub[1].stop - x0]
            if avoid is not None:
                a = a * (1 - avoid[sub])
            frame[sub] = frame[sub] * (1 - a) + r * a
        return frame

    def _corners(self, frame: np.ndarray, cfg: dict, rgb: np.ndarray, al: np.ndarray, avoid=None) -> None:
        """One elephant in each bottom corner: the clip's left part to the left corner, its right part to the right corner."""
        hh, ww = rgb.shape[:2]
        pw = int(ww * cfg["corners"])
        top = np.clip(np.arange(hh, dtype=np.float32) / max(int(hh * cfg.get("feather_top", 0.05)), 1), 0, 1)
        k = max(int(pw * cfg["inner_feather"]), 1)
        ramp = np.clip(np.arange(pw, dtype=np.float32)[::-1] / k, 0, 1)      # 1 at the screen edge, fading toward the middle
        ramp = ramp * ramp * (3 - 2 * ramp)
        y0 = self.h - hh
        for side in ("L", "R"):
            r = rgb[:, :pw] if side == "L" else rgb[:, ww - pw:]
            a = al[:, :pw] if side == "L" else al[:, ww - pw:]
            m = ramp if side == "L" else ramp[::-1]
            a = a * m[None, :, None] * top[:, None, None]
            x0 = 0 if side == "L" else self.w - pw
            if avoid is not None:
                a = a * (1 - avoid[y0:, x0:x0 + pw])
            frame[y0:, x0:x0 + pw] = frame[y0:, x0:x0 + pw] * (1 - a) + r * a


# ---- the same theme as an ffmpeg post-process, for Shorts whose text is already baked into the video -------------------------
LAKSHMI_WORDS = ("lakshmi", "laxmi", "లక్ష్మి", "లక్ష్మీ", "लक्ष्मी", "लक्ष्मि")


def is_lakshmi(*texts: str) -> bool:
    blob = " ".join(t for t in texts if t).lower()
    return any(w in blob for w in LAKSHMI_WORDS)


def themed(src: Path, dst: Path | None = None) -> Path:
    """Overlay the Lakshmi theme (coins along the sides, a baby elephant in each bottom corner, both see-through, once at the start)
    on a finished Short. Returns dst (default: replaces src). Never raises: on any problem the original video is kept."""
    import shutil
    import subprocess

    dst = dst or src.with_name(src.stem + "_lk.mp4")
    files = [DECOR / f"{n}_{k}.mp4" for n in ("coins", "eleph") for k in ("rgb", "alpha")]
    try:
        if not all(f.exists() for f in files):
            return src
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(src)],
                            capture_output=True, text=True, check=True)
        w, h = (int(x) for x in pr.stdout.strip().split(",")[:2])
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)],
                                   capture_output=True, text=True, check=True).stdout.strip())
        sc = w / 720.0
        ec, cc = LAYERS["eleph"], LAYERS["coins"]
        pw = int(540 * sc * ec["corners"])
        eh = int(960 * sc)
        ss = "(t*t*(3-2*t))"
        coins_a = (f"alpha(X,Y)*{cc['gain']}*({cc['center_dim']}+{1 - cc['center_dim']}*clip((abs(2*X/W-1)-0.30)/0.35,0,1))")

        def piece(side: str) -> str:
            t = (f"clip((W-1-X)/({ec['inner_feather']}*W),0,1)" if side == "L" else f"clip(X/({ec['inner_feather']}*W),0,1)")
            t_ = ss.replace("t", f"({t})")
            return f"alpha(X,Y)*{ec['gain']}*{t_}*clip(Y/({ec['feather_top']}*H),0,1)"

        fo = lambda c: f"fade=t=in:st=0:d={c['fin']}:alpha=1,fade=t=out:st={max(min(c['cycle'], dur) - c['fout'], 0.5):.2f}:d={c['fout']}:alpha=1"   # noqa: E731
        geq = lambda a: f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{a}'"                                          # noqa: E731
        fg = (f"[1:v][2:v]alphamerge,format=yuva420p,scale={w}:{h},{geq(coins_a)},{fo(cc)}[co];"
              f"[3:v][4:v]alphamerge,format=yuva420p,scale=iw*{ec['scale'] * sc:.4f}:ih*{ec['scale'] * sc:.4f},split[e1][e2];"
              f"[e1]crop={pw}:{eh}:0:0,{geq(piece('L'))},{fo(ec)}[el];"
              f"[e2]crop={pw}:{eh}:iw-{pw}:0,{geq(piece('R'))},{fo(ec)}[er];"
              f"[0:v][co]overlay=0:0:eof_action=pass[v1];[v1][el]overlay=0:H-h:eof_action=pass[v2];[v2][er]overlay=W-w:H-h:eof_action=pass,format=yuv420p[v]")
        tmp = dst.with_name(dst.stem + "_tmp.mp4")
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src)]
        for f in files:
            cmd += ["-i", str(f)]
        cmd += ["-filter_complex", fg, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "copy",
                "-movflags", "+faststart", str(tmp)]
        subprocess.run(cmd, check=True, capture_output=True)
        shutil.move(str(tmp), str(dst))
        return dst
    except Exception as exc:    # noqa: BLE001  the theme is decoration: keep the plain video rather than lose the post
        print(f"WARNING: Lakshmi theme not added: {type(exc).__name__}: {exc}")
        return src
