"""
TemplateContentGenerator: composes SEO-optimized Telugu title, description,
English keywords, Telugu hashtags, trending hashtags, and alt text for a
day's post.

Design: all deity-specific devotional phrasing lives in content/data.py.
This module only assembles those building blocks with the day's Panchang
details and date — no devotional wording is hardcoded here, so a Telugu
speaker can revise the vocabulary in one file without touching assembly
logic.
"""

from __future__ import annotations

import logging
from datetime import date

from mahanavi.content.data import (
    DEITY_CONTENT,
    GENERAL_ENGLISH_KEYWORDS,
    GENERAL_TELUGU_HASHTAGS,
    TRENDING_DEVOTIONAL_HASHTAGS,
    DeityContent,
)
from mahanavi.core.interfaces import ContentGenerator
from mahanavi.core.models import PanchangData, SeoContent, SelectedImage
from mahanavi.exceptions import ContentGenerationError
from mahanavi.images.telugu_text import format_telugu_date
from mahanavi.config import Settings

logger = logging.getLogger(__name__)


class TemplateContentGenerator(ContentGenerator):
    """Assembles SEO content from deity-specific templates + today's Panchang."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def generate(
        self,
        selected_image: SelectedImage,
        panchang: PanchangData,
        for_date: date,
    ) -> SeoContent:
        try:
            deity_content = DEITY_CONTENT[selected_image.deity]
        except KeyError as exc:
            raise ContentGenerationError(
                f"No content template registered for deity: {selected_image.deity}. "
                "Add an entry to DEITY_CONTENT in content/data.py."
            ) from exc

        date_telugu = format_telugu_date(for_date)

        title = self._build_title(deity_content.blessing_phrase, date_telugu)
        description = self._build_description(deity_content, panchang, date_telugu)
        keywords = self._build_keywords(deity_content)
        telugu_hashtags = GENERAL_TELUGU_HASHTAGS + deity_content.telugu_hashtags
        trending_hashtags = self._build_trending_hashtags(for_date)
        alt_text = self._build_alt_text(selected_image, panchang, for_date)

        seo = SeoContent(
            title_telugu=title,
            description_telugu=description,
            keywords_english=keywords,
            hashtags_telugu=telugu_hashtags,
            hashtags_trending=trending_hashtags,
            alt_text=alt_text,
        )

        caption_length = len(seo.full_caption())
        if caption_length > self._settings.seo_max_caption_length:
            logger.warning(
                "Generated caption is %d characters, exceeding the configured "
                "soft limit of %d. Verify this fits your target platform's "
                "current caption limit before publishing.",
                caption_length, self._settings.seo_max_caption_length,
            )

        return seo

    # --- Section builders ---------------------------------------------------

    def _build_title(self, blessing_phrase: str, date_telugu: str) -> str:
        return f"{blessing_phrase} | {date_telugu} తెలుగు పంచాంగం | {self._settings.channel_name}"

    def _build_description(self, deity_content: DeityContent, panchang: PanchangData, date_telugu: str) -> str:
        lines = [
            deity_content.blessing_phrase,
            "",
            f"📅 {date_telugu} రోజు పంచాంగం వివరాలు:",
            f"తిథి: {panchang.tithi}",
            f"నక్షత్రం: {panchang.nakshatram}",
            f"సూర్యోదయం: {panchang.sunrise.strftime('%I:%M %p')}",
            f"సూర్యాస్తమయం: {panchang.sunset.strftime('%I:%M %p')}",
            f"రాహు కాలం: {panchang.rahu_kalam}",
            f"యమగండం: {panchang.yamagandam}",
            f"గుళిక కాలం: {panchang.gulika_kalam}",
            f"దుర్ముహూర్తం: {panchang.durmuhurtham}",
            f"అభిజిత్ ముహూర్తం: {panchang.abhijit_muhurtham}",
            f"వర్జ్యం: {panchang.varjyam}",
            "",
            deity_content.mantra,
            "",
            "🙏 మీ రోజు శుభంగా జరగాలని కోరుకుంటూ...",
            f"👉 మా ఛానల్‌ను సబ్‌స్క్రైబ్ చేయండి - {self._settings.channel_name}",
        ]
        return "\n".join(lines)

    def _build_keywords(self, deity_content: DeityContent) -> list[str]:
        combined = GENERAL_ENGLISH_KEYWORDS + deity_content.english_keywords
        return _dedupe_preserve_order(combined)

    def _build_trending_hashtags(self, for_date: date) -> list[str]:
        monthly_tag = f"#Panchangam{for_date.strftime('%B%Y')}"
        return _dedupe_preserve_order(TRENDING_DEVOTIONAL_HASHTAGS + [monthly_tag])

    def _build_alt_text(
        self, selected_image: SelectedImage, panchang: PanchangData, for_date: date
    ) -> str:
        return (
            f"Lord {selected_image.deity.value} devotional image — "
            f"Telugu Panchangam for {for_date.isoformat()}, "
            f"{panchang.tithi} tithi, {panchang.nakshatram} nakshatram — "
            f"{self._settings.channel_name}"
        )


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
