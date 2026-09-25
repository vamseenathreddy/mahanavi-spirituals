"""
InstagramUploader: publishes to an Instagram Business/Creator account via
the Graph API's two-step flow:
    1. POST /{ig-user-id}/media       (create a media container)
    2. POST /{ig-user-id}/media_publish  (publish that container)

IMPORTANT — a real constraint of this API, not a design choice of ours:
Instagram's Graph API requires `image_url` to be a **publicly reachable
URL**; it does not accept direct file uploads. That means your generated
images need to be hosted somewhere public (e.g. nginx serving
`data/generated/`, or uploaded to S3/Cloudflare R2 first) before this
uploader can use them. Set MAHANAVI_INSTAGRAM_IMAGE_PUBLIC_BASE_URL to
that public base URL — this class only constructs
`{base_url}/{image_path.name}` and does not host anything itself.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import requests

from mahanavi.core.interfaces import Uploader
from mahanavi.core.models import PublishTarget, SeoContent, UploadResult
from mahanavi.exceptions import InstagramUploadError, RetryExhaustedError
from mahanavi.retry import retry_with_backoff

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v19.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

_CONTAINER_POLL_ATTEMPTS = 5
_CONTAINER_POLL_DELAY_SECONDS = 3.0


class InstagramUploader(Uploader):
    """Publishes an image + caption to Instagram via the Graph API."""

    TARGET = PublishTarget.INSTAGRAM

    def __init__(
        self,
        ig_user_id: str,
        access_token: str,
        image_public_base_url: str,
        max_retries: int = 3,
        backoff_seconds: float = 5.0,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        if not ig_user_id or not access_token:
            raise InstagramUploadError(
                "InstagramUploader requires both ig_user_id and access_token."
            )
        if not image_public_base_url:
            raise InstagramUploadError(
                "InstagramUploader requires MAHANAVI_INSTAGRAM_IMAGE_PUBLIC_BASE_URL — "
                "Instagram's API only accepts a public image URL, not a file upload."
            )
        self._ig_user_id = ig_user_id
        self._access_token = access_token
        self._image_public_base_url = image_public_base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._session = session or requests.Session()

        self._create_container = retry_with_backoff(
            max_retries=max_retries, backoff_seconds=backoff_seconds,
            exceptions=(requests.RequestException,),
        )(self._create_container_uncached)
        self._publish_container = retry_with_backoff(
            max_retries=max_retries, backoff_seconds=backoff_seconds,
            exceptions=(requests.RequestException,),
        )(self._publish_container_uncached)

    def publish(self, image_path: Path, seo: SeoContent) -> UploadResult:
        image_url = f"{self._image_public_base_url}/{image_path.name}"
        try:
            container_id = self._create_container(image_url, seo.full_caption())
            self._wait_until_container_ready(container_id)
            media_id = self._publish_container(container_id)
        except RetryExhaustedError as exc:
            return UploadResult(
                target=PublishTarget.INSTAGRAM, success=False,
                error_message=f"Instagram upload failed after retries: {exc}",
            )
        except InstagramUploadError as exc:
            return UploadResult(target=PublishTarget.INSTAGRAM, success=False, error_message=str(exc))

        post_url = f"https://www.instagram.com/p/{media_id}/" if media_id else None
        logger.info("Published to Instagram account %s (media_id=%s)", self._ig_user_id, media_id)
        return UploadResult(target=PublishTarget.INSTAGRAM, success=True, post_url=post_url)

    def _create_container_uncached(self, image_url: str, caption: str) -> str:
        url = f"{GRAPH_API_BASE}/{self._ig_user_id}/media"
        response = self._session.post(
            url,
            data={"image_url": image_url, "caption": caption, "access_token": self._access_token},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        if "error" in payload:
            raise InstagramUploadError(f"Instagram container creation failed: {payload['error']}")
        return str(payload["id"])

    def _wait_until_container_ready(self, container_id: str) -> None:
        """Poll the container's status_code until FINISHED (or give up after a few tries)."""
        url = f"{GRAPH_API_BASE}/{container_id}"
        for attempt in range(_CONTAINER_POLL_ATTEMPTS):
            response = self._session.get(
                url, params={"fields": "status_code", "access_token": self._access_token},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            status = response.json().get("status_code")
            if status == "FINISHED":
                return
            if status == "ERROR":
                raise InstagramUploadError(f"Instagram container {container_id} failed processing.")
            logger.info(
                "Instagram container %s status=%s (attempt %d/%d) — waiting.",
                container_id, status, attempt + 1, _CONTAINER_POLL_ATTEMPTS,
            )
            time.sleep(_CONTAINER_POLL_DELAY_SECONDS)
        raise InstagramUploadError(
            f"Instagram container {container_id} did not finish processing in time."
        )

    def _publish_container_uncached(self, container_id: str) -> str:
        url = f"{GRAPH_API_BASE}/{self._ig_user_id}/media_publish"
        response = self._session.post(
            url,
            data={"creation_id": container_id, "access_token": self._access_token},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        if "error" in payload:
            raise InstagramUploadError(f"Instagram publish failed: {payload['error']}")
        return str(payload["id"])
