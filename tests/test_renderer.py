from __future__ import annotations

from datetime import date, time
from pathlib import Path

import pytest
from PIL import Image

from mahanavi.config import Settings
from mahanavi.core.models import Deity, PanchangData, SelectedImage
from mahanavi.exceptions import ImageRenderError
from mahanavi.images.renderer import PillowImageRenderer


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


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    images_root = tmp_path / "Images"
    images_root.mkdir(parents=True, exist_ok=True)
    return Settings(
        images_root=images_root,
        output_dir=tmp_path / "generated",
        database_path=tmp_path / "db" / "test.db",
        log_dir=tmp_path / "logs",
        logo_path=None,  # no logo in tests — renderer must handle this gracefully
    )


@pytest.fixture
def fake_deity_image(tmp_path: Path) -> SelectedImage:
    img_path = tmp_path / "shiva_01.jpg"
    Image.new("RGB", (800, 1000), (120, 60, 20)).save(img_path)
    return SelectedImage(
        path=img_path,
        folder_name="Monday_Shiva",
        filename="shiva_01.jpg",
        deity=Deity.SHIVA,
    )


def test_render_produces_correct_size_output(
    settings: Settings, fake_deity_image: SelectedImage
) -> None:
    renderer = PillowImageRenderer(settings)
    for_date = date(2026, 7, 20)
    panchang = _sample_panchang(for_date)

    output_path = renderer.render(fake_deity_image, panchang, for_date)

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.size == (settings.canvas_width, settings.canvas_height)
        assert img.mode == "RGB"


def test_render_filename_includes_date_and_folder(
    settings: Settings, fake_deity_image: SelectedImage
) -> None:
    renderer = PillowImageRenderer(settings)
    for_date = date(2026, 7, 20)
    output_path = renderer.render(fake_deity_image, _sample_panchang(for_date), for_date)

    assert "2026-07-20" in output_path.name
    assert "Monday_Shiva" in output_path.name


def test_render_handles_missing_logo_gracefully(
    settings: Settings, fake_deity_image: SelectedImage
) -> None:
    # settings.logo_path is None in the fixture — should not raise.
    renderer = PillowImageRenderer(settings)
    for_date = date(2026, 7, 21)
    output_path = renderer.render(fake_deity_image, _sample_panchang(for_date), for_date)
    assert output_path.exists()


def test_render_with_portrait_and_landscape_source_images(
    settings: Settings, tmp_path: Path
) -> None:
    """The cover-fit crop must handle both portrait and landscape source images."""
    renderer = PillowImageRenderer(settings)
    for_date = date(2026, 7, 22)

    landscape_path = tmp_path / "wide.jpg"
    Image.new("RGB", (2000, 800), (50, 50, 50)).save(landscape_path)
    landscape_image = SelectedImage(
        path=landscape_path, folder_name="Wednesday_Ganesha",
        filename="wide.jpg", deity=Deity.GANESHA,
    )
    output_path = renderer.render(landscape_image, _sample_panchang(for_date), for_date)
    with Image.open(output_path) as img:
        assert img.size == (settings.canvas_width, settings.canvas_height)


def test_render_raises_image_render_error_for_corrupt_image(
    settings: Settings, tmp_path: Path
) -> None:
    corrupt_path = tmp_path / "corrupt.jpg"
    corrupt_path.write_bytes(b"not actually a jpeg")
    bad_image = SelectedImage(
        path=corrupt_path, folder_name="Monday_Shiva",
        filename="corrupt.jpg", deity=Deity.SHIVA,
    )
    renderer = PillowImageRenderer(settings)
    with pytest.raises(ImageRenderError):
        renderer.render(bad_image, _sample_panchang(date(2026, 7, 20)), date(2026, 7, 20))


def test_missing_font_raises_at_construction(settings: Settings, tmp_path: Path) -> None:
    settings.telugu_font_path = tmp_path / "no_such_font.ttf"
    with pytest.raises(ImageRenderError):
        PillowImageRenderer(settings)
