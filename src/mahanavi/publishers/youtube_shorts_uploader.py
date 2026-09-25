"""
YouTubeShortsUploader: uploads a real .mp4 as a YouTube Short via the
OFFICIAL Data API v3 -- genuinely different from
youtube_playwright_uploader.py, which drives a real browser via
Playwright because Community Posts have no API at all. Video uploads
DO have an official, stable API, so we use it directly here instead of
browser automation -- more reliable, and doesn't carry the ToS gray-area
risk documented in youtube_playwright_uploader.py's module docstring.

"Short" isn't an explicit upload flag -- YouTube auto-classifies a
video as a Short based on its properties (vertical, under ~3 minutes).
Our video/assembler.py output (1080x1920, ~10s) already satisfies this.

Prerequisite: run scripts/youtube_shorts_auth_setup.py once first, to
produce the token file this class loads.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Protocol

from mahanavi.config import Settings
from mahanavi.core.models import PublishTarget, UploadResult
from mahanavi.exceptions import YouTubeUploadError

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# "People & Blogs" -- a reasonable general-purpose default for
# devotional/informational content. Override via the category_id
# constructor argument if you want a more specific fit (YouTube's
# category IDs are a fixed list, e.g. "24" Entertainment, "27" Education).
DEFAULT_CATEGORY_ID = "22"


class UploadableSeoContent(Protocol):
    """Structural type both ShortSeoContent (content/alert_seo.py) and
    PuranaVideoSeoContent (content/purana_video_seo.py) satisfy -- this
    uploader genuinely works for any video the API accepts (Shorts
    classification happens automatically based on video properties, not
    an upload flag -- see module docstring), so it isn't tied to one
    specific SEO content type."""
    @property
    def title(self) -> str: ...

    @property
    def hashtags(self) -> list[str]: ...

    def full_caption(self) -> str: ...


class YouTubeShortsUploader:
    """Uploads a video file as a YouTube Short via the official Data API v3."""

    def __init__(self, settings: Settings, category_id: str = DEFAULT_CATEGORY_ID) -> None:
        self._settings = settings
        self._category_id = category_id

    def upload(self, video_path: Path, seo: UploadableSeoContent, privacy_status: str = "public") -> UploadResult:
        if not video_path.exists():
            return UploadResult(
                target=PublishTarget.YOUTUBE, success=False,
                error_message=f"Video file does not exist: {video_path}",
            )

        try:
            youtube = self._build_service()
        except YouTubeUploadError as exc:
            return UploadResult(target=PublishTarget.YOUTUBE, success=False, error_message=str(exc))

        try:
            from googleapiclient.errors import HttpError
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            return UploadResult(
                target=PublishTarget.YOUTUBE, success=False,
                error_message=f"Missing packages: {exc}. Run: pip install google-api-python-client",
            )

        try:
            body = {
                "snippet": {
                    "title": seo.title,
                    "description": seo.full_caption(),
                    "tags": [tag.lstrip("#") for tag in seo.hashtags],
                    "categoryId": self._category_id,
                },
                "status": {
                    "privacyStatus": privacy_status,
                    # Explicitly declared, not left to default -- YouTube
                    # requires every upload to state this. Devotional
                    # content for a general audience, not children's
                    # content -- confirm this matches your channel if you
                    # ever upload something aimed at kids specifically.
                    "selfDeclaredMadeForKids": False,
                },
            }
            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()

        except HttpError as exc:
            return UploadResult(
                target=PublishTarget.YOUTUBE, success=False,
                error_message=f"YouTube Data API upload failed: {exc}",
            )
        except Exception as exc:  # genuinely need to catch anything else the SDK can raise
            return UploadResult(
                target=PublishTarget.YOUTUBE, success=False,
                error_message=f"Unexpected error during Shorts upload: {exc}",
            )

        video_id = response.get("id")
        # /watch?v= (not /shorts/) since this uploader now serves both
        # genuine Shorts AND long-form Puranam videos -- a real upload
        # confirmed the old hardcoded /shorts/ URL was wrong for a
        # 2.66-minute landscape video, which isn't a Short at all.
        # /watch?v= is the universally correct format: YouTube still
        # shows genuine Shorts-eligible content in the Shorts player
        # when opened this way, so nothing is lost for actual Shorts.
        post_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else None
        logger.info("Uploaded video: %s", post_url)
        return UploadResult(target=PublishTarget.YOUTUBE, success=True, post_url=post_url)

    def _build_service(self) -> "Any":  # googleapiclient's Resource type isn't meaningfully annotable
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise YouTubeUploadError(
                "Missing packages. Run: pip install google-api-python-client google-auth-oauthlib google-auth"
            ) from exc

        token_file = self._settings.youtube_token_file
        if not token_file.exists():
            raise YouTubeUploadError(
                f"No saved YouTube API token at {token_file}. "
                "Run `python -m mahanavi.scripts.youtube_shorts_auth_setup` once first."
            )

        credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            token_file.write_text(credentials.to_json(), encoding="utf-8")

        return build("youtube", "v3", credentials=credentials)
