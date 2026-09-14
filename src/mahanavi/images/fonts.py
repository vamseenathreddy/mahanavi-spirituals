"""
FontManager: loads a single variable Telugu font file and hands out
cached ImageFont instances at whichever (weight, size) is requested.

Why RAQM matters: Telugu (like other Indic scripts) uses vowel signs and
conjunct consonants that must be *shaped* — reordered and combined by a
text-shaping engine — to render correctly. Pillow's default layout engine
draws each codepoint's glyph independently, which garbles Telugu. Passing
`layout_engine=ImageFont.Layout.RAQM` (backed by HarfBuzz) fixes this, and
is why the project depends on Pillow being built with libraqm support
(true for the standard `Pillow` wheels from PyPI on Linux/macOS/Windows).
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import ImageFont

from mahanavi.exceptions import ImageRenderError

logger = logging.getLogger(__name__)

_VALID_WEIGHTS = {
    "Thin", "ExtraLight", "Light", "Regular", "Medium",
    "SemiBold", "Bold", "ExtraBold", "Black",
}


class FontManager:
    """Loads and caches Telugu font instances at requested weight/size."""

    def __init__(self, font_path: Path) -> None:
        if not font_path.exists():
            raise ImageRenderError(
                f"Telugu font not found at {font_path}. "
                "Download a Telugu-supporting font (e.g. Noto Sans Telugu) "
                "and set MAHANAVI_TELUGU_FONT_PATH, or place it at the default path."
            )
        self._font_path = font_path
        self._cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
        self._raqm_available = self._check_raqm()

    def get_font(self, size: int, weight: str = "Regular") -> ImageFont.FreeTypeFont:
        if weight not in _VALID_WEIGHTS:
            raise ImageRenderError(
                f"Unknown font weight '{weight}'. Expected one of: {sorted(_VALID_WEIGHTS)}"
            )
        cache_key = (weight, size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        layout_engine = ImageFont.Layout.RAQM if self._raqm_available else ImageFont.Layout.BASIC
        font = ImageFont.truetype(str(self._font_path), size, layout_engine=layout_engine)

        try:
            font.set_variation_by_name(weight)
        except OSError:
            # Not a variable font, or this weight isn't a named instance —
            # fall back to whatever the file's default weight is.
            logger.warning(
                "Font %s has no named instance '%s'; using default weight.",
                self._font_path.name, weight,
            )

        self._cache[cache_key] = font
        return font

    @staticmethod
    def _check_raqm() -> bool:
        try:
            from PIL import features
            available = bool(features.check("raqm"))
        except Exception:  # pragma: no cover - defensive, feature check itself failing
            available = False

        if not available:
            logger.warning(
                "Pillow was built without libraqm support — Telugu text will "
                "NOT shape correctly (conjuncts/vowel signs may render broken). "
                "Install a Pillow build with raqm support to fix this."
            )
        return available
