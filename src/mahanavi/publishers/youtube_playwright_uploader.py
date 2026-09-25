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
lets you log in by hand, and saves the session as a PERSISTENT Chrome
profile under `youtube_profile_dir(settings)`. This uploader reuses that
same profile (not a disposable one) for every automated run, launching
your real installed Chrome rather than Playwright's generic bundled test
build — a fresh, disposable, generic-Chromium session is exactly what
gets flagged as an "unsupported browser" by Google/YouTube. Re-run the
setup script if the session expires (you'll see YouTubeUploadError
mentioning a login/auth page).

NOTE ON HEADLESS/SERVER DEPLOYMENT: this currently launches with
headless=False, i.e. a visible browser window — fine for manual testing
on your own machine, but it will NOT work as-is on a headless server or
inside Docker without a virtual display (e.g. Xvfb). That's a real,
separate piece of work needed before this runs unattended at 5 AM on a
server — don't assume it's solved just because manual testing works.
"""

from __future__ import annotations

import logging
import re
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


def youtube_profile_dir(settings: Settings) -> Path:
    """Shared with scripts/youtube_login_setup.py so both always agree on
    where the persistent, already-authenticated Chrome profile lives."""
    return settings.youtube_session_state_file.parent / "youtube_chrome_profile"


class PageLike(Protocol):
    """The minimal subset of playwright.sync_api.Page this class needs.

    Defined as a Protocol so tests can pass a lightweight fake instead of
    a real browser — the orchestration logic in _compose_and_post is what
    we actually want covered by fast unit tests; the real Playwright
    launch is a thin, separately-verified wrapper (see _launch_page).
    """

    def goto(self, url: str, timeout: float | None = None) -> None: ...
    def get_by_role(self, role: str, name: str | re.Pattern[str] | None = None, exact: bool = False) -> "LocatorLike": ...
    def get_by_text(self, text: str) -> "LocatorLike": ...
    def get_by_placeholder(self, text: str | re.Pattern[str]) -> "LocatorLike": ...
    def locator(self, selector: str) -> "LocatorLike": ...
    def screenshot(self, path: str) -> None: ...
    def wait_for_timeout(self, timeout: float) -> None: ...
    def evaluate(self, expression: str, arg: object = None) -> object: ...
    keyboard: "KeyboardLike"


class KeyboardLike(Protocol):
    """The minimal subset of playwright.sync_api.Keyboard this class needs.

    Used to type text via raw keyboard dispatch to whatever currently has
    focus, bypassing the target-visibility checks that Locator.fill()
    enforces — needed because the composer's contenteditable box can have
    zero computed height until focused, even though its CSS ::before
    placeholder text still paints visually (confirmed via a real run,
    2026-09-14: Locator.fill() timed out with 'element is not visible'
    despite the element being clearly visible in a screenshot)."""

    def type(self, text: str) -> None: ...


class LocatorLike(Protocol):
    """The minimal subset of playwright.sync_api.Locator this class needs."""

    def click(self, force: bool = False, timeout: float | None = None) -> None: ...
    def fill(self, text: str) -> None: ...
    def set_input_files(self, path: str) -> None: ...
    def wait_for(self, timeout: float | None = None) -> None: ...
    def get_by_role(self, role: str, name: str | re.Pattern[str] | None = None, exact: bool = False) -> "LocatorLike": ...


class YouTubePlaywrightUploader(Uploader):
    """Publishes a Community Post to YouTube Studio via Playwright."""

    TARGET = PublishTarget.YOUTUBE

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def publish(self, image_path: Path, seo: SeoContent) -> UploadResult:
        profile_dir = youtube_profile_dir(self._settings)
        if not profile_dir.exists():
            return UploadResult(
                target=PublishTarget.YOUTUBE,
                success=False,
                error_message=(
                    f"No saved YouTube Chrome profile at {profile_dir}. "
                    "Run `python -m mahanavi.scripts.youtube_login_setup` once to log in manually."
                ),
            )
        if not self._settings.youtube_channel_id:
            return UploadResult(
                target=PublishTarget.YOUTUBE,
                success=False,
                error_message=(
                    "MAHANAVI_YOUTUBE_CHANNEL_ID is not set. Find it in your browser's address "
                    "bar while on your channel (e.g. studio.youtube.com/channel/<THIS_PART>) "
                    "and set it in .env."
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
            # Navigate directly to the composer's real location (confirmed
            # via a real run on 2026-09-14) instead of automating Studio's
            # Create-button dropdown and tracking the new tab it opens.
            url = sel.channel_posts_url(self._settings.youtube_channel_id)  # type: ignore[arg-type]
            page.goto(url, timeout=sel.NAVIGATION_TIMEOUT_MS)

            # Diagnostic screenshot taken unconditionally (not just on
            # failure) so we can see definitively what the composer looks
            # like on load, rather than only finding out indirectly from a
            # downstream timeout.
            page.wait_for_timeout(2000)
            debug_path = str(screenshot_path).replace(".png", "_after_navigate.png")
            page.screenshot(path=debug_path)
            logger.info("Diagnostic screenshot after navigating to composer: %s", debug_path)

            # Activate the composer and type the caption (see
            # _type_caption_with_verification's docstring for the full
            # story of why this needs a real click, not JS .focus()).
            self._type_caption_with_verification(page, caption)

            role, name = sel.ADD_PHOTO_BUTTON_ROLE
            page.get_by_role(role, name=name, exact=True).click()
            page.locator(sel.FILE_INPUT_SELECTOR).set_input_files(str(image_path))
            page.wait_for_timeout(sel.UPLOAD_PROCESSING_TIMEOUT_MS)

            role, name = sel.POST_SUBMIT_BUTTON_ROLE
            page.get_by_role(role, name=name, exact=True).click()
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

    def _type_caption_with_verification(self, page: PageLike, caption: str) -> None:
        """Activate the composer with a REAL click (not JS .focus()), then
        insert the caption via document.execCommand('insertText', ...)
        instead of page.keyboard.type().

        Two separate real-world bugs led here, on the same day:
        1. A real run published successfully with an EMPTY caption even
           though a read-back check reported success -- JS-only
           page.evaluate(...).focus() put text in the DOM but never
           triggered the framework's real click handler, so its OWN
           internal text model (what actually gets submitted) stayed
           empty. Fixed by genuinely clicking the stable-ID placeholder
           instead of just focusing via JS.
        2. After that fix, a real post went out with visibly GARBLED
           Telugu text (mojibake, not a terminal display issue -- this
           was the live published page itself). page.keyboard.type()
           simulates raw physical key-press events, which is a known
           unreliable way to enter non-Latin/complex scripts through
           Chrome DevTools Protocol -- it isn't an actual IME, so Telugu
           text can come out corrupted despite going through correctly
           as a Python string on our end. execCommand('insertText', ...)
           inserts the exact Unicode text directly (no synthetic
           keystrokes to mangle) while still firing the input/beforeinput
           events most frameworks (including this one) listen to for
           two-way data binding -- unlike a raw `textContent =` assignment,
           which doesn't fire those events at all (bug #1's cause)."""
        # Reset any leftover draft from a previous run first -- the
        # persistent Chrome profile can leave the composer already
        # expanded, in which case the placeholder below genuinely doesn't
        # exist (it only shows in the collapsed state). Short timeout is
        # intentional: if there's nothing to cancel, fail fast.
        try:
            role, name = sel.CANCEL_BUTTON_ROLE
            page.get_by_role(role, name=name, exact=True).click(timeout=3000)
            page.wait_for_timeout(500)
            logger.info("Discarded a leftover draft from a previous run.")
        except Exception:
            pass  # composer was already collapsed -- nothing to cancel

        page.locator(sel.POST_ACTIVATE_PLACEHOLDER_SELECTOR).click()
        page.wait_for_timeout(800)

        insert_text_script = (
            "(params) => { "
            "const el = document.querySelector(params.sel); "
            "if (!el) throw new Error('element not found: ' + params.sel); "
            "el.focus(); "
            "document.execCommand('insertText', false, params.caption); "
            "}"
        )
        read_content_script = (
            "(sel) => { "
            "const el = document.querySelector(sel); "
            "return el ? el.textContent : null; "
            "}"
        )

        for attempt, wait_ms in enumerate((300, 1200), start=1):
            if attempt > 1:
                # Retry: explicitly re-click the textbox itself (now that
                # the composer is genuinely expanded, this should have a
                # real rendered size, unlike before activation) --
                # force=True as a safety net in case it's still awkwardly
                # sized.
                page.locator(sel.POST_TEXTBOX_SELECTOR).click(force=True)
                page.wait_for_timeout(wait_ms)

            page.evaluate(insert_text_script, {"sel": sel.POST_TEXTBOX_SELECTOR, "caption": caption})
            page.wait_for_timeout(300)

            actual = page.evaluate(read_content_script, sel.POST_TEXTBOX_SELECTOR)
            # A loose length check, not exact equality -- the framework can
            # legitimately normalize whitespace/newlines on the way in.
            if isinstance(actual, str) and len(actual.strip()) >= len(caption.strip()) * 0.8:
                return
            logger.warning(
                "Caption text verification failed on attempt %d (got %d chars, expected ~%d) -- retrying.",
                attempt, len(actual) if isinstance(actual, str) else 0, len(caption),
            )

        raise YouTubeUploadError(
            "Typed caption did not actually appear in the composer after 2 attempts -- "
            "a previous real run silently published with an empty caption this way. "
            "Studio's composer behavior may have changed; check the diagnostic screenshot."
        )

    # --- Real browser wrapper (not exercised by unit tests) -----------------

    def _launch_page(self) -> "AbstractContextManager[PageLike]":
        """Return a context manager yielding a real Playwright Page using the
        same persistent, already-authenticated Chrome profile that
        scripts/youtube_login_setup.py created. Kept as a thin, separate
        method so unit tests can substitute _compose_and_post's PageLike
        argument without touching this.

        Uses real Chrome (channel="chrome") and a persistent profile rather
        than Playwright's bundled test Chromium in a disposable context —
        the latter is what gets flagged as an "unsupported browser" by
        Google/YouTube. headless=False for now; see the module docstring's
        note on server/Docker deployment before assuming this works
        unattended."""
        from collections.abc import Iterator
        from contextlib import contextmanager
        from playwright.sync_api import sync_playwright

        profile_dir = youtube_profile_dir(self._settings)

        @contextmanager
        def _cm() -> Iterator[PageLike]:
            with sync_playwright() as playwright:
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    channel="chrome",
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                page = context.new_page()
                try:
                    yield cast(PageLike, page)
                finally:
                    context.close()

        return _cm()

    def _build_screenshot_path(self) -> Path:
        self._settings.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._settings.output_dir / f"youtube_post_{timestamp}.png"
