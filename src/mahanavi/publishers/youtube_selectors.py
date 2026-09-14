"""
Selectors/locators for automating YouTube Studio's Community Post flow.

*** READ THIS BEFORE RELYING ON THIS MODULE IN PRODUCTION ***

YouTube Studio's UI is an unversioned, frequently-changing single-page app.
I have no way to browse studio.youtube.com from this environment to verify
today's actual DOM structure, so the locators below are a best-effort
starting point based on Studio's general, long-standing patterns (visible
button text and ARIA roles, which tend to be more stable than internal CSS
class names). Treat this file as a template you WILL need to adjust:

    1. Run `python -m mahanavi.publishers.youtube_debug_snapshot` (see
       below) or simply open studio.youtube.com yourself, open a Community
       post composer, and use browser DevTools ("Inspect Element") to
       confirm each control's visible text/role.
    2. Update the values below to match. Nothing else in the codebase
       needs to change — youtube_playwright_uploader.py only references
       these constants.

Preferring Playwright's role/text-based locators (get_by_role, get_by_text)
over raw CSS selectors is deliberate: Studio's CSS class names are
machine-generated and change often, while visible button labels and ARIA
roles change far less frequently.
"""

from __future__ import annotations

STUDIO_BASE_URL = "https://studio.youtube.com"

# Text/role locators — verify against the live UI (see module docstring).
CREATE_BUTTON_ROLE = ("button", "Create")
CREATE_POST_MENU_ITEM_TEXT = "Create post"
POST_TEXTAREA_PLACEHOLDER = "Talk to your viewers"
ADD_PHOTO_BUTTON_ROLE = ("button", "Add photo")
FILE_INPUT_SELECTOR = "input[type='file']"
POST_SUBMIT_BUTTON_ROLE = ("button", "Post")
POST_CONFIRMATION_TEXT = "Post published"

# Timeouts (milliseconds) — Studio can be slow to load; generous by default.
NAVIGATION_TIMEOUT_MS = 45_000
ACTION_TIMEOUT_MS = 20_000
UPLOAD_PROCESSING_TIMEOUT_MS = 30_000
