"""
One-time setup: log in to YouTube Studio by hand in a real browser window,
then save the authenticated session (cookies/local storage) so
YouTubePlaywrightUploader can reuse it for every automated run without
ever automating the login form itself.

IMPORTANT — about the "Couldn't sign you in / This browser or app may
not be secure" error: Google actively detects and blocks sign-ins from
automation-controlled browsers as a deliberate security measure (this is
not a bug in this script). To reduce the chance of hitting that wall,
this script:
  - uses a PERSISTENT browser profile (saved in
    data/youtube_chrome_profile/) instead of a fresh throwaway one —
    Google is more suspicious of brand-new, stateless browser sessions
  - tries to launch your actual installed Google Chrome (not Playwright's
    bundled test Chromium) via channel="chrome", which is a closer match
    to a normal browser's fingerprint
  - disables the most obvious automation flag Chromium normally exposes

None of this is a guaranteed bypass — Google continuously updates its
detection, and this is exactly the operational risk flagged in
publishers/youtube_playwright_uploader.py. If you still hit the block
after this, the more reliable fallback is exporting cookies from your
own everyday (non-automated) browser, where you're already logged in,
rather than logging in fresh inside any automated browser at all — ask
for help with that if you get stuck here.

Run this:
    python -m mahanavi.scripts.youtube_login_setup

Re-run it whenever the saved session expires (YouTubePlaywrightUploader
will raise a YouTubeUploadError that mentions a login/auth page when this
happens).
"""

from __future__ import annotations

from mahanavi.config import get_settings
from mahanavi.logging_config import configure_logging
from mahanavi.publishers.youtube_playwright_uploader import youtube_profile_dir


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_dir)

    from playwright.sync_api import sync_playwright

    settings.youtube_session_state_file.parent.mkdir(parents=True, exist_ok=True)
    profile_dir = youtube_profile_dir(settings)
    profile_dir.mkdir(parents=True, exist_ok=True)

    print("Opening a browser window — log in to your YouTube/Google account.")
    print("(Using a persistent profile + real Chrome to reduce the chance")
    print(" of Google's automation-detection block — see this script's")
    print(" docstring if you still hit 'This browser or app may not be secure'.)")
    print("Once you can see YouTube Studio's dashboard, come back here and press Enter.")

    with sync_playwright() as playwright:
        try:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",  # your real installed Chrome, not Playwright's test build
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
        except Exception:
            print(
                "Could not launch your real Chrome install (channel='chrome'). "
                "Falling back to Playwright's bundled Chromium — this is more "
                "likely to hit Google's automation block. Run "
                "`playwright install chrome` and re-run this script to use "
                "your real Chrome instead."
            )
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )

        page = context.new_page()
        page.goto("https://studio.youtube.com")

        input("Press Enter here once you're logged in and Studio has loaded... ")

        context.storage_state(path=str(settings.youtube_session_state_file))
        context.close()

    print(f"Session saved to {settings.youtube_session_state_file}")
    print("YouTubePlaywrightUploader will now reuse this session automatically.")


if __name__ == "__main__":
    main()
