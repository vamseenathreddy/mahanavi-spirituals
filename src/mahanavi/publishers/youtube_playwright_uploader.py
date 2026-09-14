"""
YouTubePlaywrightUploader: publishes a Community Post (image + text) to
YouTube Studio via browser automation.

WHY PLAYWRIGHT INSTEAD OF THE OFFICIAL API: as of this writing, the
YouTube Data API v3 has no endpoint for creating Community posts — it's a
Studio-only feature. Verify this is still true before deploying (Google
does occasionally expand API coverage); if a Data API endpoint exists for
this, use that instead — it will be far more reliable than a browser
automation script.

RISK YOU SHOULD KNOW ABOUT: automating a personal Google/YouTube account
sits in a gray area of YouTube's Terms of Service around automated access,
and can trigger security challenges (CAPTCHA, "unusual activity" holds) or,
in rarer cases, account restrictions — this risk exists independent of how
carefully this code is written. Using a persistent authenticated session
(see below) rather than automating the login form itself reduces — but
does not eliminate — that risk. Consider this a "use at your own risk,
monitor the account" component, not a guaranteed-safe integration.

SESSION SETUP: this class does NOT automate logging in (deliberately —
automating Google's login form is both fragile and more likely to trigger
a security challenge). Instead, log in manually once using the companion
script `scripts/youtube_login_setup.py`, which opens a real browser window,
lets you log in by hand, and saves the authenticated session (cookies) to
`settings.youtube_session_state_file`. This uploader then reuses that
session for every automated run. Re-run the setup script if the session
expires (you'll see YouTubeUploadError mentioning a login/auth page).
"""

from __future__ import annotations

import logging
from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from typing import Protocol, cast

from mahanavi.config import Settings
from mahanavi.core.interfaces import Uploader
from mahanavi.core.models import PublishTarget, SeoContent, UploadResult
from mahanavi.exceptions import YouTubeUploadError
from mahanavi.publishers import youtube_selectors as sel

logger = logging.getLogger(__name__)


class PageLike(Protocol):
    """The minimal subset of playwright.sync_api.Page this class needs.

    Defined as a Protocol so tests can pass a lightweight fake instead of
    a real browser — the orchestration logic in _compose_and_post is what
    we actually want covered by fast unit tests; the real Playwright
    launch is a thin, separately-verified wrapper (see _launch_page).
    """

    def goto(self, url: str, timeout: float | None = None) -> None: ...
    def get_by_role(self, role: str, name: str | None = None) -> "LocatorLike": ...
    def get_by_text(self, text: str) -> "LocatorLike": ...
    def get_by_placeholder(self, text: str) -> "LocatorLike": ...
    def locator(self, selector: str) -> "LocatorLike": ...
    def screenshot(self, path: str) -> None: ...
    def wait_for_timeout(self, timeout: float) -> None: ...


class LocatorLike(Protocol):
    """The minimal subset of playwright.sync_api.Locator this class needs."""

    def click(self) -> None: ...
    def fill(self, text: str) -> None: ...
    def set_input_files(self, path: str) -> None: ...
    def wait_for(self, timeout: float | None = None) -> None: ...


class YouTubePlaywrightUploader(Uploader):
    """Publishes a Community Post to YouTube Studio via Playwright."""

    TARGET = PublishTarget.YOUTUBE

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def publish(self, image_path: Path, seo: SeoContent) -> UploadResult:
        if not self._settings.youtube_session_state_file.exists():
            return UploadResult(
                target=PublishTarget.YOUTUBE,
                success=False,
                error_message=(
                    f"No saved YouTube session at {self._settings.youtube_session_state_file}. "
                    "Run `python -m mahanavi.scripts.youtube_login_setup` once to log in manually."
                ),
            )

        screenshot_path = self._build_screenshot_path()
        try:
            with self._launch_page() as page:
                self._compose_and_post(page, image_path, seo.full_caption(), screenshot_path)
        except YouTubeUploadError as exc:
            return UploadResult(
                target=PublishTarget.YOUTUBE, success=False,
                error_message=str(exc), screenshot_path=screenshot_path,
            )

        logger.info("Published YouTube Community Post; screenshot at %s", screenshot_path)
        return UploadResult(target=PublishTarget.YOUTUBE, success=True, screenshot_path=screenshot_path)

    # --- Orchestration logic (unit-testable with a fake PageLike) -----------

    def _compose_and_post(
        self, page: PageLike, image_path: Path, caption: str, screenshot_path: Path,
    ) -> None:
        try:
            page.goto(sel.STUDIO_BASE_URL, timeout=sel.NAVIGATION_TIMEOUT_MS)

            role, name = sel.CREATE_BUTTON_ROLE
            page.get_by_role(role, name=name).click()
            page.get_by_text(sel.CREATE_POST_MENU_ITEM_TEXT).click()

            page.get_by_placeholder(sel.POST_TEXTAREA_PLACEHOLDER).fill(caption)

            role, name = sel.ADD_PHOTO_BUTTON_ROLE
            page.get_by_role(role, name=name).click()
            page.locator(sel.FILE_INPUT_SELECTOR).set_input_files(str(image_path))
            page.wait_for_timeout(sel.UPLOAD_PROCESSING_TIMEOUT_MS)

            role, name = sel.POST_SUBMIT_BUTTON_ROLE
            page.get_by_role(role, name=name).click()
            page.get_by_text(sel.POST_CONFIRMATION_TEXT).wait_for(timeout=sel.ACTION_TIMEOUT_MS)  # type: ignore[attr-defined]

            page.screenshot(path=str(screenshot_path))

        except Exception as exc:
            try:
                page.screenshot(path=str(screenshot_path))
            except Exception:  # pragma: no cover - best-effort diagnostic only
                logger.warning("Could not capture failure screenshot.")
            raise YouTubeUploadError(
                f"YouTube Community Post automation failed at runtime: {exc}. "
                "This usually means Studio's UI changed — check the failure "
                f"screenshot at {screenshot_path} and update publishers/youtube_selectors.py."
            ) from exc

    # --- Real browser wrapper (not exercised by unit tests) -----------------

    def _launch_page(self) -> "AbstractContextManager[PageLike]":
        """Return a context manager yielding a real Playwright Page using the
        saved session state. Kept as a thin, separate method so unit tests can
        substitute _compose_and_post's PageLike argument without touching this."""
        from collections.abc import Iterator
        from contextlib import contextmanager
        from playwright.sync_api import sync_playwright

        @contextmanager
        def _cm() -> Iterator[PageLike]:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(
                    storage_state=str(self._settings.youtube_session_state_file)
                )
                page = context.new_page()
                try:
                    yield cast(PageLike, page)
                finally:
                    context.close()
                    browser.close()

        return _cm()

    def _build_screenshot_path(self) -> Path:
        self._settings.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._settings.output_dir / f"youtube_post_{timestamp}.png"
