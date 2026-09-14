from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import pytest

from mahanavi.config import Settings
from mahanavi.core.models import SeoContent
from mahanavi.exceptions import YouTubeUploadError
from mahanavi.publishers.youtube_playwright_uploader import YouTubePlaywrightUploader


class FakeLocator:
    def __init__(self, log: list[str], name: str, fail_on: set[str] | None = None) -> None:
        self._log = log
        self._name = name
        self._fail_on = fail_on or set()

    def _maybe_fail(self, action: str) -> None:
        if action in self._fail_on:
            raise RuntimeError(f"simulated failure on {action}:{self._name}")

    def click(self) -> None:
        self._maybe_fail("click")
        self._log.append(f"click:{self._name}")

    def fill(self, text: str) -> None:
        self._maybe_fail("fill")
        self._log.append(f"fill:{self._name}")

    def set_input_files(self, path: str) -> None:
        self._maybe_fail("set_input_files")
        self._log.append(f"set_input_files:{self._name}:{path}")

    def wait_for(self, timeout: float | None = None) -> None:
        self._maybe_fail("wait_for")
        self._log.append(f"wait_for:{self._name}")


class FakePage:
    def __init__(self, fail_on: set[str] | None = None) -> None:
        self.log: list[str] = []
        self.screenshots: list[str] = []
        self._fail_on = fail_on or set()

    def goto(self, url: str, timeout: float | None = None) -> None:
        self.log.append(f"goto:{url}")

    def get_by_role(self, role: str, name: str | None = None) -> FakeLocator:
        return FakeLocator(self.log, f"role:{role}:{name}", self._fail_on)

    def get_by_text(self, text: str) -> FakeLocator:
        return FakeLocator(self.log, f"text:{text}", self._fail_on)

    def get_by_placeholder(self, text: str) -> FakeLocator:
        return FakeLocator(self.log, f"placeholder:{text}", self._fail_on)

    def locator(self, selector: str) -> FakeLocator:
        return FakeLocator(self.log, f"selector:{selector}", self._fail_on)

    def screenshot(self, path: str) -> None:
        self.screenshots.append(path)

    def wait_for_timeout(self, timeout: float) -> None:
        self.log.append(f"wait_for_timeout:{timeout}")


def _settings(tmp_path: Path, session_exists: bool = True) -> Settings:
    images_root = tmp_path / "Images"
    images_root.mkdir(parents=True, exist_ok=True)
    session_file = tmp_path / "yt_session.json"
    if session_exists:
        session_file.write_text("{}")
    return Settings(
        images_root=images_root,
        output_dir=tmp_path / "out",
        database_path=tmp_path / "db.sqlite",
        log_dir=tmp_path / "logs",
        youtube_session_state_file=session_file,
    )


def _seo() -> SeoContent:
    return SeoContent(
        title_telugu="T", description_telugu="D",
        keywords_english=["k"], hashtags_telugu=["#a"],
        hashtags_trending=["#b"], alt_text="alt",
    )


def test_missing_session_file_returns_failure_without_launching_browser(tmp_path: Path) -> None:
    settings = _settings(tmp_path, session_exists=False)
    uploader = YouTubePlaywrightUploader(settings)
    result = uploader.publish(tmp_path / "img.jpg", _seo())

    assert result.success is False
    assert "youtube_login_setup" in result.error_message


def test_compose_and_post_happy_path_calls_expected_sequence(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    uploader = YouTubePlaywrightUploader(settings)
    page = FakePage()
    screenshot_path = tmp_path / "shot.png"

    uploader._compose_and_post(page, tmp_path / "img.jpg", "caption text", screenshot_path)

    assert any(entry.startswith("goto:") for entry in page.log)
    assert any("Create" in entry for entry in page.log)
    assert any("fill:placeholder" in entry for entry in page.log)
    assert any("set_input_files" in entry for entry in page.log)
    assert str(screenshot_path) in page.screenshots


def test_compose_and_post_failure_raises_youtube_upload_error_and_screenshots(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    uploader = YouTubePlaywrightUploader(settings)
    page = FakePage(fail_on={"click"})  # simulate a selector that no longer exists
    screenshot_path = tmp_path / "failure.png"

    with pytest.raises(YouTubeUploadError):
        uploader._compose_and_post(page, tmp_path / "img.jpg", "caption", screenshot_path)

    # A failure screenshot should still have been attempted.
    assert str(screenshot_path) in page.screenshots


def test_publish_success_via_launch_page_override(tmp_path: Path, monkeypatch) -> None:
    settings = _settings(tmp_path)
    uploader = YouTubePlaywrightUploader(settings)
    fake_page = FakePage()

    @contextmanager
    def fake_launch_page():
        yield fake_page

    monkeypatch.setattr(uploader, "_launch_page", fake_launch_page)
    result = uploader.publish(tmp_path / "img.jpg", _seo())

    assert result.success is True
    assert result.screenshot_path is not None


def test_publish_failure_via_launch_page_override(tmp_path: Path, monkeypatch) -> None:
    settings = _settings(tmp_path)
    uploader = YouTubePlaywrightUploader(settings)
    fake_page = FakePage(fail_on={"click"})

    @contextmanager
    def fake_launch_page():
        yield fake_page

    monkeypatch.setattr(uploader, "_launch_page", fake_launch_page)
    result = uploader.publish(tmp_path / "img.jpg", _seo())

    assert result.success is False
    assert result.screenshot_path is not None
    assert "Studio's UI changed" in result.error_message
