"""Strip the 'subscribe or you may never see this channel again' line from every video description on upload
(owner 2026-11-05). One place for all channels: both YouTube client builders wrap their client with `wrap()`, so
videos().insert never sends the line, whichever script or language built the description. Comments and the
on-screen card text are not touched."""
from __future__ import annotations

import re

_S = r"[\s‌‍]*"
_END = r"[\s.!।🙏]*"
_PATTERNS = [
    # Telugu: "ఇప్పుడే సబ్స్క్రైబ్ చేయకపోతే / చేయండి, లేకపోతే ఈ ఛానల్ మీకు మళ్లీ కనిపించకపోవచ్చు"
    r"ఇప్పుడే" + _S + r"సబ్[‌‍]?స్క్రైబ్" + _S + r"చేయ(?:కపోతే|ండి,?" + _S + r"లేకపోతే)" + _S + r"ఈ" + _S + r"ఛానల్" + _S + r"మీకు" + _S + r"మళ్లీ" + _S + r"కనిపించకపోవచ్చు" + _END,
    # Hindi: "अभी सब्सक्राइब नहीं किया तो यह चैनल आपको दोबारा शायद न दिखे" and the "करें, वरना ..." variant
    r"अभी" + _S + r"सब्सक्राइब" + _S + r"(?:नहीं" + _S + r"किया" + _S + r"तो|करें,?" + _S + r"वरना)" + _S + r"यह" + _S + r"चैनल" + _S + r"(?:आपको" + _S + r"दोबारा|शायद" + _S + r"दोबारा" + _S + r"आपको)" + _S + r"(?:शायद" + _S + r")?न" + _S + r"दिखे" + _END,
    # English
    r"you" + _S + r"may" + _S + r"never" + _S + r"see" + _S + r"this" + _S + r"channel" + _S + r"again" + _S + r"unless" + _S + r"you" + _S + r"subscribe" + _S + r"right" + _S + r"now" + _END,
]
_RX = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]


def clean(text: str) -> str:
    if not text:
        return text
    out = text
    for rx in _RX:
        out = rx.sub("", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() if out != text else text


def clean_body(body: dict) -> dict:
    sn = body.get("snippet") or {}
    if "description" in sn:
        sn["description"] = clean(sn["description"])
    for loc in (body.get("localizations") or {}).values():
        if isinstance(loc, dict) and "description" in loc:
            loc["description"] = clean(loc["description"])
    return body


class _Videos:
    def __init__(self, inner):
        self._inner = inner

    def insert(self, *args, **kwargs):
        if isinstance(kwargs.get("body"), dict):
            clean_body(kwargs["body"])
        return self._inner.insert(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._inner, name)


def wrap(yt):
    """Return the same client with videos().insert cleaning the description."""
    real = yt.videos

    def videos():
        return _Videos(real())

    yt.videos = videos
    return yt
