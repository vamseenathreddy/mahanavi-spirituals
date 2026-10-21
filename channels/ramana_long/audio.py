"""Narration through edge-tts (Indian English voices first), the channel's own Om music bed, and silences."""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from channels.jesus_long.audio import duration, silence  # noqa: F401 (re-exported)

VOICES = ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural", "en-US-ChristopherNeural")
RATE = "-10%"
REPO = Path(__file__).resolve().parents[2]
OM_DIR = REPO / "ramana/assets"


async def _speak(text: str, voice: str, out: Path) -> None:
    import edge_tts

    await edge_tts.Communicate(text, voice, rate=RATE).save(str(out))


def speak(text: str, out: Path) -> Path:
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


def fake_speak(text: str, out: Path) -> Path:
    """Offline stand-in used only for local layout tests: silence as long as the words would take."""
    secs = max(2.0, len(text.split()) / 2.3)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", f"{secs:.2f}",
                    "-c:a", "libmp3lame", str(out)], check=True)
    return out


def om_bed(path: Path) -> Path:
    """The six Om chant clips plus the master, joined with crossfades into one loopable bed."""
    tracks = sorted(OM_DIR.glob("om_*.mp3"))
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for t in tracks:
        cmd += ["-i", str(t)]
    parts, last = [], "0:a"
    for i in range(1, len(tracks)):
        parts.append(f"[{last}][{i}:a]acrossfade=d=4:c1=tri:c2=tri[x{i}]")
        last = f"x{i}"
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{last}]", "-ar", "44100", "-ac", "2", str(path)]
    subprocess.run(cmd, check=True)
    return path
