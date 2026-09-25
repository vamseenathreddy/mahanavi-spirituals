from __future__ import annotations

from datetime import date, time
from pathlib import Path

import pytest

from mahanavi.config import Settings
from mahanavi.content.generator import TemplateContentGenerator
from mahanavi.core.models import Deity, PanchangData, SelectedImage

pytestmark = pytest.mark.filterwarnings("ignore")


def _sample_panchang(d: date) -> PanchangData:
    return PanchangData(
        date_=d,
        tithi="Panchami",
        nakshatram="Rohini",
        varjyam="10:12 AM - 11:42 AM",
        rahu_kalam="07:30 AM - 09:00 AM",
        yamagandam="10:30 AM - 12:00 PM",
        gulika_kalam="01:30 PM - 03:00 PM",
        durmuhurtham="08:06 AM - 08:52 AM",
        abhijit_muhurtham="11:48 AM - 12:38 PM",
        sunrise=time(5, 58),
        sunset=time(18, 45),
        source="dummy",
    )


def _selected_image(deity: Deity = Deity.SHIVA) -> SelectedImage:
    return SelectedImage(
        path=Path("/fake/shiva.jpg"),
        folder_name="Monday_Shiva",
        filename="shiva.jpg",
        deity=deity,
    )


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    images_root = tmp_path / "Images"
    images_root.mkdir(parents=True, exist_ok=True)
    return Settings(
        images_root=images_root,
        output_dir=tmp_path / "out",
        database_path=tmp_path / "db.sqlite",
        log_dir=tmp_path / "logs",
    )


def test_generate_produces_all_fields(settings: Settings) -> None:
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    seo = generator.generate(_selected_image(), _sample_panchang(for_date), for_date)

    assert seo.title_telugu
    assert seo.description_telugu
    assert seo.keywords_english
    assert seo.hashtags_telugu
    assert seo.hashtags_trending
    assert seo.alt_text


def test_description_contains_panchang_details(settings: Settings) -> None:
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    panchang = _sample_panchang(for_date)
    seo = generator.generate(_selected_image(), panchang, for_date)

    assert panchang.tithi in seo.description_telugu
    assert panchang.nakshatram in seo.description_telugu
    assert panchang.rahu_kalam in seo.description_telugu


def test_different_deities_produce_different_content(settings: Settings) -> None:
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    panchang = _sample_panchang(for_date)

    shiva_seo = generator.generate(_selected_image(Deity.SHIVA), panchang, for_date)
    hanuman_seo = generator.generate(_selected_image(Deity.HANUMAN), panchang, for_date)

    assert shiva_seo.title_telugu != hanuman_seo.title_telugu
    assert shiva_seo.hashtags_telugu != hanuman_seo.hashtags_telugu


def test_keywords_are_deduplicated(settings: Settings) -> None:
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    seo = generator.generate(_selected_image(), _sample_panchang(for_date), for_date)
    assert len(seo.keywords_english) == len(set(seo.keywords_english))


def test_alt_text_includes_deity_and_date(settings: Settings) -> None:
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    seo = generator.generate(_selected_image(), _sample_panchang(for_date), for_date)
    assert "Shiva" in seo.alt_text
    assert "2026-07-20" in seo.alt_text


def test_trending_hashtags_include_monthly_tag(settings: Settings) -> None:
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    seo = generator.generate(_selected_image(), _sample_panchang(for_date), for_date)
    assert "#PanchangamJuly2026" in seo.hashtags_trending


def test_full_caption_combines_all_text_parts(settings: Settings) -> None:
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    seo = generator.generate(_selected_image(), _sample_panchang(for_date), for_date)
    caption = seo.full_caption()
    assert seo.title_telugu in caption
    assert seo.description_telugu in caption
    for tag in seo.hashtags_telugu:
        assert tag in caption


def test_long_caption_logs_warning_but_does_not_raise(settings: Settings, caplog) -> None:
    settings.seo_max_caption_length = 10  # force overflow
    generator = TemplateContentGenerator(settings)
    for_date = date(2026, 7, 20)
    with caplog.at_level("WARNING"):
        seo = generator.generate(_selected_image(), _sample_panchang(for_date), for_date)
    assert seo is not None
    assert any("exceeding" in record.message for record in caplog.records)
