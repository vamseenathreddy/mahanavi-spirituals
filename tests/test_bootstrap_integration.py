"""
End-to-end integration test: exercises the REAL image selector, dummy
Panchang provider, real Pillow renderer (real font), real content
generator, and real Telegram/YouTube uploaders — wired together exactly
as bootstrap.build_pipeline does in production. Only the actual network
call (Telegram) and the actual browser (YouTube) are mocked/stubbed;
everything else is genuine.

This is the test that would catch "the pieces work alone but don't fit
together" bugs that the per-module unit tests can't see.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date
from pathlib import Path

import requests_mock
from PIL import Image

from mahanavi.bootstrap import build_pipeline
from mahanavi.config import Settings
from mahanavi.publishers.youtube_playwright_uploader import YouTubePlaywrightUploader


class _FakeKeyboard:
    def __init__(self, page):
        self._page = page

    def type(self, text):
        self._page._typed_text = text


class _FakeYouTubePage:
    def __init__(self):
        self._typed_text = ""
        self.keyboard = _FakeKeyboard(self)

    def goto(self, url, timeout=None): pass
    def get_by_role(self, role, name=None, exact=False): return self
    def get_by_text(self, text): return self
    def get_by_placeholder(self, text): return self
    def locator(self, selector): return self
    def click(self, force=False, timeout=None): pass
    def fill(self, text): pass
    def set_input_files(self, path): pass
    def wait_for(self, timeout=None): pass
    def wait_for_timeout(self, timeout): pass

    def evaluate(self, expression, arg=None):
        if "return el ? el.textContent" in expression:
            return self._typed_text
        if "execCommand('insertText'" in expression and isinstance(arg, dict):
            self._typed_text = arg.get("caption", "")
        if "el.textContent = ''" in expression:
            self._typed_text = ""
        return None

    def screenshot(self, path):
        Path(path).write_bytes(b"fake-png-bytes")


def test_full_pipeline_end_to_end(tmp_path: Path, monkeypatch) -> None:
    # --- Arrange a real folder with a real placeholder deity image ---
    images_root = tmp_path / "Images"
    monday_folder = images_root / "Monday_Shiva"
    monday_folder.mkdir(parents=True)
    Image.new("RGB", (800, 1000), (120, 60, 20)).save(monday_folder / "shiva_01.jpg")

    # --- YouTube: session file present, browser launch stubbed ---
    session_file = tmp_path / "yt_session.json"
    session_file.write_text("{}")
    (tmp_path / "youtube_chrome_profile").mkdir(parents=True, exist_ok=True)

    @contextmanager
    def fake_launch_page(self):
        yield _FakeYouTubePage()

    monkeypatch.setattr(YouTubePlaywrightUploader, "_launch_page", fake_launch_page)

    settings = Settings(
        images_root=images_root,
        output_dir=tmp_path / "generated",
        database_path=tmp_path / "db.sqlite",
        log_dir=tmp_path / "logs",
        logo_path=None,
        panchang_provider="dummy",
        telegram_bot_token="123:ABC",
        telegram_channel_id="@testchannel",
        youtube_session_state_file=session_file,
        youtube_channel_id="UCtestchannel123",
    )

    pipeline = build_pipeline(settings)

    with requests_mock.Mocker() as m:
        m.post(
            "https://api.telegram.org/bot123:ABC/sendPhoto",
            json={"ok": True, "result": {"message_id": 1, "chat": {"username": "testchannel"}}},
        )
        result = pipeline.run_for_date(date(2026, 7, 20))  # a Monday

    # --- Assert the whole chain actually produced a coherent result ---
    assert result.selected_image is not None
    assert result.selected_image.filename == "shiva_01.jpg"
    assert result.panchang is not None
    assert result.generated_image_path is not None
    assert result.generated_image_path.exists()
    with Image.open(result.generated_image_path) as rendered:
        # PlainImageRenderer copies the source image untouched — its size
        # matches the original placeholder (800x1000), not the branded
        # renderer's fixed canvas_width/canvas_height.
        assert rendered.size == (800, 1000)
    assert result.seo is not None
    assert "శివుడు" in result.seo.title_telugu or "Shiva" in result.seo.alt_text

    assert result.overall_success is True
    assert len(result.upload_results) == 2  # YouTube + Telegram
    assert all(r.success for r in result.upload_results)
