"""
PillowImageRenderer: composes the final branded devotional image from:
  - the selected deity image
  - today's Panchang data
  - today's date (rendered in Telugu)
  - channel logo + watermark

Layout (top to bottom), all fractions of canvas height so this scales if
canvas_width/canvas_height are changed in config:
    1. Header band  — logo (left) + Telugu date/weekday (right)
    2. Deity banner — Telugu deity name, centered
    3. Deity image  — cover-cropped into a rounded, gold-bordered frame with
                       a soft drop shadow
    4. Panchang panel — semi-transparent cream card, label:value rows
                         in two columns
    5. Footer       — centered watermark text
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, UnidentifiedImageError

from mahanavi.config import Settings
from mahanavi.core.interfaces import ImageRenderer
from mahanavi.core.models import PanchangData, SelectedImage
from mahanavi.exceptions import ImageRenderError
from mahanavi.images.fonts import FontManager
from mahanavi.images.layout import (
    COLOR_GOLD,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_TEXT_DARK,
    COLOR_TEXT_LIGHT,
    FOOTER_HEIGHT_FRAC,
    HEADER_HEIGHT_FRAC,
    IMAGE_AREA_HEIGHT_FRAC,
    MARGIN_X_FRAC,
    cover_fit,
    draw_drop_shadow,
    paste_with_rounded_corners,
    vertical_gradient,
)
from mahanavi.images.telugu_text import (
    PANCHANG_LABELS,
    format_telugu_date,
    translate_nakshatram,
    translate_tithi,
)

logger = logging.getLogger(__name__)


class PillowImageRenderer(ImageRenderer):
    """Composes the branded daily devotional image using Pillow."""

    def __init__(
        self,
        settings: Settings,
        font_manager: FontManager | None = None,
        decorative_font_manager: FontManager | None = None,
    ) -> None:
        self._settings = settings
        self._fonts = font_manager or FontManager(settings.telugu_font_path)
        # Only used where content is guaranteed pure Telugu with no Latin
        # or emoji characters — Ponnala has neither (confirmed via a real
        # render test that showed tofu boxes for both). That currently
        # means just the header date line; the deity banner has an emoji
        # and the panel/footer mix in Latin content, so they stay on the
        # main font.
        self._decorative_fonts = decorative_font_manager or FontManager(settings.decorative_font_path)

    def render(
        self,
        selected_image: SelectedImage,
        panchang: PanchangData,
        for_date: date,
    ) -> Path:
        width = self._settings.canvas_width
        height = self._settings.canvas_height
        margin_x = int(width * MARGIN_X_FRAC)

        try:
            canvas = vertical_gradient(width, height, (74, 14, 20), (191, 87, 0)).convert("RGBA")
            draw = ImageDraw.Draw(canvas)

            cursor_y = self._draw_header(canvas, draw, for_date, width, height, margin_x)
            cursor_y = self._draw_deity_banner(draw, selected_image, width, cursor_y)
            cursor_y = self._draw_deity_image(canvas, selected_image, width, height, margin_x, cursor_y)
            self._draw_panchang_panel(canvas, draw, panchang, width, height, margin_x, cursor_y)
            self._draw_footer(draw, width, height)

            output_path = self._build_output_path(selected_image, for_date)
            final = canvas.convert("RGB")
            final.save(
                output_path,
                format=self._settings.image_output_format,
                quality=self._settings.image_output_quality,
                optimize=True,
            )
            logger.info("Rendered devotional image to %s", output_path)
            return output_path

        except UnidentifiedImageError as exc:
            raise ImageRenderError(f"Could not open deity image: {selected_image.path}") from exc
        except OSError as exc:
            raise ImageRenderError(f"Image rendering/save failed: {exc}") from exc

    # --- Section renderers -------------------------------------------------

    def _draw_header(
        self, canvas: Image.Image, draw: ImageDraw.ImageDraw, for_date: date,
        width: int, height: int, margin_x: int,
    ) -> int:
        header_height = int(height * HEADER_HEIGHT_FRAC)

        logo_path = self._settings.logo_path
        if logo_path and logo_path.exists():
            try:
                logo = Image.open(logo_path).convert("RGBA")
                logo_size = int(header_height * 0.75)
                logo.thumbnail((logo_size, logo_size))
                canvas.alpha_composite(logo, (margin_x, (header_height - logo.height) // 2))
            except UnidentifiedImageError:
                logger.warning("Logo file at %s is not a valid image — skipping.", logo_path)
        else:
            logger.info("No logo file at %s — header will show text only.", logo_path)

        date_font = self._decorative_fonts.get_font(size=int(height * 0.026), weight="SemiBold")
        date_text = format_telugu_date(for_date)
        bbox = draw.textbbox((0, 0), date_text, font=date_font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (width - margin_x - text_w, (header_height - (bbox[3] - bbox[1])) // 2 - bbox[1]),
            date_text, font=date_font, fill=COLOR_TEXT_LIGHT,
        )
        return header_height

    def _draw_deity_banner(
        self, draw: ImageDraw.ImageDraw, selected_image: SelectedImage, width: int, cursor_y: int,
    ) -> int:
        banner_height = int(width * 0.09)
        # "శుభోదయం" (Subhodayam / "good morning") — per request, this
        # replaces the earlier "🙏 ఈ రోజు దైవం: <deity>" text entirely,
        # with no deity name appended.
        text = "శుభోదయం"
        font = self._decorative_fonts.get_font(size=int(width * 0.036), weight="Bold")
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            ((width - text_w) // 2, cursor_y + (banner_height - (bbox[3] - bbox[1])) // 2 - bbox[1]),
            text, font=font, fill=COLOR_TEXT_LIGHT,
        )
        return cursor_y + banner_height

    def _draw_deity_image(
        self, canvas: Image.Image, selected_image: SelectedImage,
        width: int, height: int, margin_x: int, cursor_y: int,
    ) -> int:
        image_area_height = int(height * IMAGE_AREA_HEIGHT_FRAC)
        frame_box = (margin_x, cursor_y, width - margin_x, cursor_y + image_area_height)
        frame_w = frame_box[2] - frame_box[0]
        frame_h = frame_box[3] - frame_box[1]
        radius = int(min(frame_w, frame_h) * 0.04)

        draw_drop_shadow(canvas, frame_box, radius=radius)

        with Image.open(selected_image.path) as raw:
            fitted = cover_fit(raw.convert("RGB"), (frame_w, frame_h))
        paste_with_rounded_corners(canvas, fitted, (frame_box[0], frame_box[1]), radius)

        border_draw = ImageDraw.Draw(canvas)
        border_draw.rounded_rectangle(frame_box, radius=radius, outline=COLOR_GOLD, width=6)

        return cursor_y + image_area_height + int(height * 0.02)

    def _draw_panchang_panel(
        self, canvas: Image.Image, draw: ImageDraw.ImageDraw, panchang: PanchangData,
        width: int, height: int, margin_x: int, cursor_y: int,
    ) -> None:
        footer_height = int(height * FOOTER_HEIGHT_FRAC)
        panel_box = (margin_x, cursor_y, width - margin_x, height - footer_height)
        panel_w = panel_box[2] - panel_box[0]
        panel_h = panel_box[3] - panel_box[1]
        radius = int(min(panel_w, panel_h) * 0.04)

        panel_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        panel_draw = ImageDraw.Draw(panel_layer)
        panel_draw.rounded_rectangle(panel_box, radius=radius, fill=COLOR_PANEL_BG, outline=COLOR_PANEL_BORDER, width=4)
        canvas.alpha_composite(panel_layer)

        # Reverted to the main font (not decorative Ponnala) for the panel —
        # Ponnala is a bold display/poster face; at the panel's small text
        # size it read as low-quality/hard to read (confirmed by direct
        # feedback on a real post). Ponnala stays for the large header/
        # banner text where it actually looks good.
        label_font = self._fonts.get_font(size=int(height * 0.0165), weight="Bold")
        value_font = self._fonts.get_font(size=int(height * 0.0165), weight="Regular")

        rows = self._panchang_rows(panchang)
        n_rows = len(rows)
        col_count = 2
        rows_per_col = (n_rows + 1) // col_count
        col_padding = int(panel_w * 0.05)
        col_width = (panel_w - 2 * col_padding) // col_count
        row_height = panel_h // (rows_per_col + 1)

        draw = ImageDraw.Draw(canvas)
        for i, (label, value) in enumerate(rows):
            col = i // rows_per_col
            row = i % rows_per_col
            x = panel_box[0] + col_padding + col * col_width
            y = panel_box[1] + int(panel_h * 0.06) + row * row_height

            draw.text((x, y), f"{label}:", font=label_font, fill=COLOR_TEXT_DARK)
            label_bbox = draw.textbbox((0, 0), f"{label}: ", font=label_font)
            draw.text((x, y + (label_bbox[3] - label_bbox[1]) + 6), value, font=value_font, fill=COLOR_TEXT_DARK)

    def _draw_footer(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        footer_height = int(height * FOOTER_HEIGHT_FRAC)
        text = self._settings.watermark_text
        # Ponnala has zero Latin glyphs — if the watermark text contains
        # any (e.g. the default "Mahanavi Spirituals"), using it would
        # render as tofu boxes. Fall back to the main font in that case
        # rather than silently breaking the footer; switch
        # MAHANAVI_WATERMARK_TEXT to Telugu text to get Ponnala here too.
        if any(ch.isascii() and ch.isalpha() for ch in text):
            font = self._fonts.get_font(size=int(height * 0.017), weight="Medium")
            logger.info(
                "Watermark text contains Latin characters — using the main font "
                "for the footer instead of Ponnala (which has no Latin glyphs). "
                "Set MAHANAVI_WATERMARK_TEXT to Telugu text to use Ponnala here too."
            )
        else:
            font = self._decorative_fonts.get_font(size=int(height * 0.017), weight="Medium")
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        y = height - footer_height + (footer_height - (bbox[3] - bbox[1])) // 2 - bbox[1]
        draw.text(((width - text_w) // 2, y), text, font=font, fill=COLOR_TEXT_LIGHT)

    # --- Helpers -------------------------------------------------------------

    @staticmethod
    def _panchang_rows(panchang: PanchangData) -> list[tuple[str, str]]:
        # Times use plain English digits + AM/PM per explicit request —
        # reverted from the Telugu-numeral 24-hour format. Since the panel
        # is back on the main font (which has full Latin support), there's
        # no compatibility reason to avoid English digits here anymore.
        values = {
            "tithi": translate_tithi(panchang.tithi),
            "nakshatram": translate_nakshatram(panchang.nakshatram),
            "karana": panchang.karana,
            "yoga": panchang.yoga,
            "sunrise": panchang.sunrise.strftime("%I:%M %p"),
            "sunset": panchang.sunset.strftime("%I:%M %p"),
            "moonrise": panchang.moonrise.strftime("%I:%M %p") if panchang.moonrise else "",
            "moonset": panchang.moonset.strftime("%I:%M %p") if panchang.moonset else "",
            "varjyam": panchang.varjyam,
            "rahu_kalam": panchang.rahu_kalam,
            "yamagandam": panchang.yamagandam,
            "gulika_kalam": panchang.gulika_kalam,
            "durmuhurtham": panchang.durmuhurtham,
            "abhijit_muhurtham": panchang.abhijit_muhurtham,
            "amrit_kaal": panchang.amrit_kaal,
        }
        # Skip optional fields with no data (e.g. the dummy provider leaves
        # karana/moonrise/etc. populated, but a real provider might not
        # supply every optional field) rather than showing an empty value.
        return [(PANCHANG_LABELS[key], values[key]) for key in PANCHANG_LABELS if values[key]]

    def _build_output_path(self, selected_image: SelectedImage, for_date: date) -> Path:
        self._settings.output_dir.mkdir(parents=True, exist_ok=True)
        ext = "jpg" if self._settings.image_output_format.upper() == "JPEG" else self._settings.image_output_format.lower()
        filename = f"{for_date.isoformat()}_{selected_image.folder_name}.{ext}"
        return self._settings.output_dir / filename
