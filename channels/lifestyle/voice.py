"""Narration for the lifestyle videos: one short clip per point, read when that point is in the middle of the screen.

Voice providers, first one available wins:
  1. Sarvam AI (bulbul:v3, the natural Indian-language voice the Puranam videos already use) when MAHANAVI_SARVAM_API_KEY is set.
  2. Microsoft neural voices through edge-tts (te-IN-ShrutiNeural, hi-IN-SwaraNeural, hi-IN-MadhurNeural): no key needed.
LIFESTYLE_FAKE_TTS=1 makes silent stand-in clips of about the right length (tests and layout previews only).
A clip is one point read once, at a calm pace, so the voice breathes between points instead of running on like a machine."""
from __future__ import annotations

import asyncio
import base64
import os
import subprocess
import wave
from pathlib import Path

RATE = 24000
VOICES = {"te": "te-IN-ShrutiNeural", "hi": "hi-IN-SwaraNeural", "tb": "hi-IN-MadhurNeural"}
SARVAM_LANG = {"te": "te-IN", "hi": "hi-IN", "tb": "hi-IN"}
SARVAM_SPEAKER = {"te": "priya", "hi": "priya", "tb": "rahul"}


def _to_wav(src: Path, dst: Path) -> None:
    """24 kHz mono 16-bit wav, leading silence trimmed, loudness levelled so every clip sounds equally loud.
    Two ffmpeg passes: silenceremove and loudnorm chained in one filter graph hang on some ffmpeg builds."""
    mid = dst.with_suffix(".trim.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05",
                    "-ar", str(RATE), "-ac", "1", str(mid)], check=True, timeout=120)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mid), "-af", "loudnorm=I=-17:TP=-1.5:LRA=9",
                    "-ar", str(RATE), "-ac", "1", "-sample_fmt", "s16", str(dst)], check=True, timeout=120)
    mid.unlink(missing_ok=True)


def _fake(text: str, dst: Path) -> None:
    seconds = max(3.0, len(text.split()) * 0.42)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate={RATE}",
                    "-t", f"{seconds:.2f}", "-af", "volume=0.2", str(dst)], check=True)


def _edge(text: str, voice_key: str, dst: Path) -> None:
    import edge_tts

    async def go():
        # a little slower than the default and slightly lower: warmer and less hurried than the stock setting
        await edge_tts.Communicate(text, VOICES[voice_key], rate="-8%", pitch="-2Hz").save(str(dst))
    asyncio.run(go())


def _sarvam(text: str, voice_key: str, dst: Path) -> None:
    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=os.environ["MAHANAVI_SARVAM_API_KEY"])
    r = client.text_to_speech.convert(text=text, language_code=SARVAM_LANG[voice_key], model="bulbul:v3",
                                      speaker=SARVAM_SPEAKER[voice_key], pace=0.95, output_audio_codec="wav")
    dst.write_bytes(base64.b64decode(r.audios[0]))


def provider() -> str:
    if os.environ.get("LIFESTYLE_FAKE_TTS") == "1":
        return "fake"
    return "sarvam" if os.environ.get("MAHANAVI_SARVAM_API_KEY") else "edge"


def synth_clips(texts: list[str], voice_key: str, workdir: Path) -> list[Path]:
    """One wav per text. Retries a failing clip twice; raises if a clip still fails (never ships a silent video)."""
    workdir.mkdir(parents=True, exist_ok=True)
    prov = provider()
    out = []
    for i, text in enumerate(texts):
        raw, wav = workdir / f"raw_{i:02d}.mp3", workdir / f"clip_{i:02d}.wav"
        last = None
        for _try in range(3):
            try:
                {"fake": lambda: _fake(text, raw), "sarvam": lambda: _sarvam(text, voice_key, raw),
                 "edge": lambda: _edge(text, voice_key, raw)}[prov]()
                _to_wav(raw, wav)
                last = None
                break
            except Exception as exc:  # noqa: BLE001
                last = exc
        if last is not None:
            raise RuntimeError(f"TTS ({prov}) failed on clip {i}: {last}") from last
        out.append(wav)
    return out


def durations(clips: list[Path]) -> list[float]:
    out = []
    for c in clips:
        with wave.open(str(c)) as w:
            out.append(w.getnframes() / w.getframerate())
    return out


def timeline(durs: list[float], min_total: float, gap: float = 0.9, max_gap: float = 3.0, tail: float = 3.0):
    """(start seconds per clip, total seconds). Gaps grow (up to max_gap) so the video is at least min_total long."""
    n = len(durs)
    need = min_total - tail - sum(durs)
    g = min(max_gap, max(gap, need / max(n - 1, 1)))
    starts, t = [], 1.0
    for d in durs:
        starts.append(t)
        t += d + g
    return starts, max(min_total, t - g + tail)


def assemble(clips: list[Path], starts: list[float], total: float, dst: Path) -> None:
    """One wav with every clip placed at its start time (silence between)."""
    buf = bytearray(int(total * RATE) * 2)
    for c, s in zip(clips, starts):
        with wave.open(str(c)) as w:
            data = w.readframes(w.getnframes())
        off = int(s * RATE) * 2
        buf[off:off + len(data)] = data[: max(0, len(buf) - off)]
    with wave.open(str(dst), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(buf))
