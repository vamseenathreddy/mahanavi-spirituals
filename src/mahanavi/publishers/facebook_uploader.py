"""
FacebookUploader: publishes the generated image + caption to a Facebook
Page using the official Graph API (POST /{page-id}/photos).

Setup required (documented in README): create a Meta App, get a
long-lived Page Access Token with pages_manage_posts + pages_read_engagement
permissions for the target Page.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import requests

from mahanavi.core.interfaces import Uploader
from mahanavi.core.models import PublishTarget, SeoContent, UploadResult
from mahanavi.exceptions import FacebookUploadError, RetryExhaustedError
from mahanavi.retry import retry_with_backoff

logger = logging.getLogger(__name__)

# Pin the Graph API version explicitly — Meta deprecates old versions on a
# schedule, so this will eventually need bumping. Check developers.facebook.com
# for the current supported version before deploying.
GRAPH_API_VERSION = "v19.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class FacebookUploader(Uploader):
    """Publishes an image + caption to a Facebook Page via Graph API."""

    TARGET = PublishTarget.FACEBOOK

    def __init__(
        self,
        page_id: str,
        page_access_token: str,
        max_retries: int = 3,
        backoff_seconds: float = 5.0,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        if not page_id or not page_access_token:
            raise FacebookUploadError(
                "FacebookUploader requires both page_id and page_access_token."
            )
        self._page_id = page_id
        self._page_access_token = page_access_token
        self._timeout_seconds = timeout_seconds
        self._session = session or requests.Session()

        self._post_photo = retry_with_backoff(
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            exceptions=(requests.RequestException,),
        )(self._post_photo_uncached)

    def publish(self, image_path: Path, seo: SeoContent) -> UploadResult:
        try:
            payload = self._post_photo(image_path, seo.full_caption())
        except RetryExhaustedError as exc:
            return UploadResult(
                target=PublishTarget.FACEBOOK, success=False,
                error_message=f"Facebook upload failed after retries: {exc}",
            )
        except FacebookUploadError as exc:
            return UploadResult(target=PublishTarget.FACEBOOK, success=False, error_message=str(exc))

        post_id = payload.get("post_id") or payload.get("id")
        post_url = f"https://www.facebook.com/{post_id}" if post_id else None
        logger.info("Published to Facebook Page %s (post_id=%s)", self._page_id, post_id)
        return UploadResult(target=PublishTarget.FACEBOOK, success=True, post_url=post_url)

    def _post_photo_uncached(self, image_path: Path, caption: str) -> dict:
        url = f"{GRAPH_API_BASE}/{self._page_id}/photos"
        with image_path.open("rb") as photo_file:
            response = self._session.post(
                url,
                data={"caption": caption, "access_token": self._page_access_token},
                files={"source": photo_file},
                timeout=self._timeout_seconds,
            )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        if "error" in payload:
            raise FacebookUploadError(f"Facebook Graph API error: {payload['error']}")
        return payload
