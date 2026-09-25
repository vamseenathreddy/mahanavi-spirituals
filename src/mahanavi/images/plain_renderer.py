"""
PlainImageRenderer: uses the selected deity image exactly as-is — no
gradient background, no border, no Telugu text/date/Panchang panel baked
into the pixels. All of that content instead lives in the caption text
(see content/generator.py, which already writes out the full Panchang
breakdown as text — nothing needed changing there).

This exists alongside PillowImageRenderer (the branded-card version) as a
second implementation of the same ImageRenderer interface — swap between
them in bootstrap.py, nothing else in the codebase needs to change either
way. Chosen over PillowImageRenderer per explicit request: a plain photo
+ a separate rich caption, matching how the channel's existing manual
posts look, rather than a designed info-card.

Deliberately does NOT use Pillow to resize/crop/re-encode the image —
just copies the original file byte-for-byte. Cropping to fixed canvas
dimensions (as PillowImageRenderer does) risks cutting off part of a
differently-proportioned source photo; copying the original avoids that
entirely and keeps full source quality.
"""

from __future__ import annotations

import logging
import shutil
from datetime import date
from pathlib import Path

from mahanavi.config import Settings
from mahanavi.core.interfaces import ImageRenderer
from mahanavi.core.models import PanchangData, SelectedImage
from mahanavi.exceptions import ImageRenderError

logger = logging.getLogger(__name__)


class PlainImageRenderer(ImageRenderer):
    """Copies the selected deity image through untouched — no overlay."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def render(
        self,
        selected_image: SelectedImage,
        panchang: PanchangData,  # noqa: ARG002 - unused; Panchang lives in the caption text, not the image
        for_date: date,
    ) -> Path:
        self._settings.output_dir.mkdir(parents=True, exist_ok=True)
        ext = selected_image.path.suffix.lower().lstrip(".") or "jpg"
        filename = f"{for_date.isoformat()}_{selected_image.folder_name}.{ext}"
        output_path = self._settings.output_dir / filename

        try:
            shutil.copy2(selected_image.path, output_path)
        except OSError as exc:
            raise ImageRenderError(
                f"Could not copy deity image {selected_image.path} to {output_path}: {exc}"
            ) from exc

        logger.info("Using plain deity image (no overlay) at %s", output_path)
        return output_path
