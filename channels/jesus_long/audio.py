"""Narration (Microsoft neural voice through edge-tts) and an original ambient pad generated here, so there is no
third-party music and no copyright claim. The pad is a slow chord loop (sine voices, slightly detuned, crossfaded)."""
from __future__ import annotations

import asyncio
import subprocess
import wave
from pathlib import Path

import numpy as np

VOICES = ("en-US-ChristopherNeural", "en-US-GuyNeural")
RATE = "-12%"
SR = 44100


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


async def _speak(text: str, voice: str, out: Path) -> None:
    import edge_tts

    await edge_tts.Communicate(text, voice, rate=RATE).save(str(out))


def speak(text: str, out: Path) -> Path:
    """One narration clip. Tries each voice twice before giving up (the service is occasionally busy)."""
    last = None
    for voice in VOICES:
        for _ in range(2):
            try:
                asyncio.run(_speak(text, voice, out))
                if out.exists() and out.stat().st_size > 1000:
                    return out
            except Exception as exc:  # noqa: BLE001
                last = exc
    raise RuntimeError(f"narration failed: {last}")


CHORDS = [  # A minor, F major, C major, G major, all spread over low octaves (Hz)
    [110.00, 164.81, 220.00, 261.63, 329.63],
    [87.31, 130.81, 174.61, 220.00, 261.63],
    [65.41, 130.81, 196.00, 261.63, 329.63],
    [98.00, 146.83, 196.00, 246.94, 293.66],
]
SEG = 24.0   # seconds per chord; the loop is len(CHORDS) * SEG = 96 s and wraps seamlessly


def pad_loop(path: Path) -> Path:
    n = int(SR * SEG * len(CHORDS))
    t = np.arange(n) / SR
    mix = np.zeros(n)
    for i, chord in enumerate(CHORDS):
        centre = (i + 0.5) * SEG
        d = np.abs(t - centre)
        d = np.minimum(d, SEG * len(CHORDS) - d)              # circular distance, so the last chord blends into the first
        w = np.where(d < SEG, np.cos(np.pi * d / (2 * SEG)) ** 2, 0.0)   # Hann crossfade: overlapping windows sum to 1
        voice = np.zeros(n)
        for j, f in enumerate(chord):
            for det in (-0.35, 0.0, 0.35):                      # a little detune gives the pad its slow shimmer
                voice += np.sin(2 * np.pi * (f + det) * t + j) / (1 + 0.25 * j)
        mix += w * voice
    mix *= 0.7 + 0.3 * np.sin(2 * np.pi * t / 12.0)             # slow breathing
    mix /= np.max(np.abs(mix)) * 1.6
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    return path


def silence(path: Path, seconds: float) -> Path:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", f"{seconds:.2f}",
                    "-c:a", "libmp3lame", str(path)], check=True)
    return path


MUSIC_DIR = Path(__file__).resolve().parent / "assets/music"


def music_tracks() -> list[Path]:
    return sorted(MUSIC_DIR.glob("*.mp3"))


def music_bed(path: Path, rotate: int = 0) -> Path | None:
    """The owner's own worship songs joined with 6 s crossfades into one bed (rotated so each video starts on a
    different song). The caller loops it. Returns None when no songs are present, so the generated pad is used."""
    tracks = music_tracks()
    if not tracks:
        return None
    k = rotate % len(tracks)
    tracks = tracks[k:] + tracks[:k]
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for t in tracks:
        cmd += ["-i", str(t)]
    if len(tracks) == 1:
        graph, last = "", "0:a"
    else:
        parts, last = [], "0:a"
        for i in range(1, len(tracks)):
            parts.append(f"[{last}][{i}:a]acrossfade=d=6:c1=tri:c2=tri[x{i}]")
            last = f"x{i}"
        graph, last = ";".join(parts), f"x{len(tracks) - 1}"
    cmd += ["-filter_complex", graph, "-map", f"[{last}]"] if graph else ["-map", "0:a"]
    cmd += ["-ar", "44100", "-ac", "2", str(path)]
    subprocess.run(cmd, check=True)
    return path
