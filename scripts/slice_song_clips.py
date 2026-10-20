#!/usr/bin/env python3
"""Slice a devotional song's audio into short vocal clips (<= 15 s) for Mahanavi song Shorts.

Usage: python scripts/slice_song_clips.py SOURCE.mp4 SLUG [--max-clips 8] [--out assets/songs]

How it works
  1. Decode to mono 22.05 kHz and measure loudness (50 ms frames, smoothed).
  2. Quiet dips in the sung line are candidate cut points, so a clip never ends mid-word.
  3. Clips are built greedily, 9-14.5 s long, each ending on the deepest dip in that range.
  4. Each clip is scored on loudness and on how much of its energy sits in the voice band
     (250-3400 Hz); instrumental-only stretches and the intro/outro score low and are dropped.
  5. The best clips are exported as MP3 (fade in/out, loudness-normalised) with a manifest.json
     recording start/end seconds in the source so any clip can be re-cut.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

MIN_LEN, MAX_LEN = 9.0, 14.5
SKIP_START, SKIP_END = 8.0, 10.0
FRAME = 0.05


def _db_frames(x, sr):
    hop = int(sr * FRAME)
    n = len(x) // hop
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1))
    return 20 * np.log10(rms + 1e-6)


def analyse(wav_path):
    sr, x = wavfile.read(wav_path)
    x = x.astype(np.float32) / 32768
    db = _db_frames(x, sr)
    k = int(0.3 / FRAME)
    smooth = np.convolve(db, np.ones(k) / k, mode="same")
    voice = sosfilt(butter(4, [250, 3400], btype="bandpass", fs=sr, output="sos"), x)
    voice_ratio = _db_frames(voice, sr) - db  # dB of voice band relative to full band (0 = all voice band)
    return smooth, voice_ratio, len(x) / sr


def candidate_cuts(smooth):
    thr = np.percentile(smooth, 35)
    cuts = []
    for i in range(2, len(smooth) - 2):
        if smooth[i] <= thr and smooth[i] == smooth[max(0, i - 6): i + 7].min():
            cuts.append(i)
    return cuts


def build_clips(smooth, voice_ratio, total):
    cuts = candidate_cuts(smooth)
    t = SKIP_START
    clips = []
    while t + MIN_LEN < total - SKIP_END:
        lo, hi = int((t + MIN_LEN) / FRAME), int(min(t + MAX_LEN, total - SKIP_END) / FRAME)
        window = [c for c in cuts if lo <= c <= hi]
        if window:
            end_i = min(window, key=lambda c: smooth[c])
        else:
            end_i = lo + int(np.argmin(smooth[lo:hi + 1]))
        s_i, e_i = int(t / FRAME), end_i
        clips.append({
            "start": round(s_i * FRAME, 2), "end": round(e_i * FRAME, 2),
            "db": float(smooth[s_i:e_i].mean()), "voice": float(voice_ratio[s_i:e_i].mean()),
        })
        t = e_i * FRAME
    return clips


def pick(clips, max_clips):
    if not clips:
        return []
    med_db = np.median([c["db"] for c in clips])
    good = [c for c in clips if c["db"] >= med_db - 1.5]
    good.sort(key=lambda c: (c["db"] - med_db) + 8 * c["voice"], reverse=True)
    chosen = sorted(good[:max_clips], key=lambda c: c["start"])
    return chosen


def export(src, clip, out_path):
    dur = clip["end"] - clip["start"]
    af = f"afade=t=in:d=0.15,afade=t=out:st={dur - 0.4:.2f}:d=0.4,loudnorm=I=-16:TP=-1.5:LRA=11"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", str(clip["start"]), "-t", f"{dur:.2f}", "-i", str(src),
         "-vn", "-af", af, "-ar", "44100", "-ac", "2", "-b:a", "128k", str(out_path)],
        check=True,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("slug")
    ap.add_argument("--max-clips", type=int, default=8)
    ap.add_argument("--out", default="assets/songs")
    a = ap.parse_args()
    out_dir = Path(a.out) / a.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.source, "-vn", "-ac", "1", "-ar", "22050", str(wav)], check=True)
        smooth, voice_ratio, total = analyse(wav)
    chosen = pick(build_clips(smooth, voice_ratio, total), a.max_clips)
    manifest = []
    for i, c in enumerate(chosen, 1):
        name = f"{a.slug}_{i:02d}.mp3"
        export(a.source, c, out_dir / name)
        manifest.append({"file": name, "start": c["start"], "end": c["end"], "seconds": round(c["end"] - c["start"], 1)})
    (out_dir / "manifest.json").write_text(json.dumps({"slug": a.slug, "clips": manifest}, indent=2), encoding="utf-8")
    print(f"{a.slug}: {len(manifest)} clips, {sum(m['seconds'] for m in manifest):.0f} s total")


if __name__ == "__main__":
    main()
