"""
One-time setup: log in to YouTube Studio by hand in a real browser window,
then save the authenticated session (cookies/local storage) so
YouTubePlaywrightUploader can reuse it for every automated run without
ever automating the login form itself.

Run this:
    python -m mahanavi.scripts.youtube_login_setup

Re-run it whenever the saved session expires (YouTubePlaywrightUploader
will raise a YouTubeUploadError that mentions a login/auth page when this
happens).
"""

from __future__ import annotations

from mahanavi.config import get_settings
from mahanavi.logging_config import configure_logging


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_dir)

    from playwright.sync_api import sync_playwright

    settings.youtube_session_state_file.parent.mkdir(parents=True, exist_ok=True)

    print("Opening a browser window — log in to your YouTube/Google account.")
    print("Once you can see YouTube Studio's dashboard, come back here and press Enter.")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://studio.youtube.com")

        input("Press Enter here once you're logged in and Studio has loaded... ")

        context.storage_state(path=str(settings.youtube_session_state_file))
        browser.close()

    print(f"Session saved to {settings.youtube_session_state_file}")
    print("YouTubePlaywrightUploader will now reuse this session automatically.")


if __name__ == "__main__":
    main()
