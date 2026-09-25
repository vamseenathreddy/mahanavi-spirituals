from __future__ import annotations

from pathlib import Path

import pytest
import requests_mock

from mahanavi.core.models import SeoContent
from mahanavi.exceptions import InstagramUploadError
from mahanavi.publishers.instagram_uploader import GRAPH_API_BASE, InstagramUploader

IG_USER_ID = "17841400000000000"
TOKEN = "fake-ig-token"
PUBLIC_BASE_URL = "https://example.com/images"
MEDIA_URL = f"{GRAPH_API_BASE}/{IG_USER_ID}/media"
PUBLISH_URL = f"{GRAPH_API_BASE}/{IG_USER_ID}/media_publish"
CONTAINER_ID = "container123"
STATUS_URL = f"{GRAPH_API_BASE}/{CONTAINER_ID}"


def _seo() -> SeoContent:
    return SeoContent(
        title_telugu="T", description_telugu="D",
        keywords_english=["k"], hashtags_telugu=["#a"],
        hashtags_trending=["#b"], alt_text="alt",
    )


def _image(tmp_path: Path) -> Path:
    p = tmp_path / "shiva.jpg"
    p.write_bytes(b"fake-jpeg-bytes")
    return p


def _uploader(**overrides) -> InstagramUploader:
    kwargs = dict(
        ig_user_id=IG_USER_ID, access_token=TOKEN,
        image_public_base_url=PUBLIC_BASE_URL, max_retries=0, backoff_seconds=0,
    )
    kwargs.update(overrides)
    return InstagramUploader(**kwargs)


def test_missing_credentials_raise() -> None:
    with pytest.raises(InstagramUploadError):
        InstagramUploader(ig_user_id="", access_token=TOKEN, image_public_base_url=PUBLIC_BASE_URL)


def test_missing_public_base_url_raises() -> None:
    with pytest.raises(InstagramUploadError):
        InstagramUploader(ig_user_id=IG_USER_ID, access_token=TOKEN, image_public_base_url="")


def test_successful_publish(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(MEDIA_URL, json={"id": CONTAINER_ID})
        m.get(STATUS_URL, json={"status_code": "FINISHED"})
        m.post(PUBLISH_URL, json={"id": "published_media_id"})

        result = _uploader().publish(_image(tmp_path), _seo())

    assert result.success is True
    assert result.post_url == "https://www.instagram.com/p/published_media_id/"

    # Verify the constructed image_url used the public base URL + filename.
    from urllib.parse import parse_qs

    create_request = m.request_history[0]
    body_params = parse_qs(create_request.text)
    assert body_params["image_url"] == [f"{PUBLIC_BASE_URL}/shiva.jpg"]


def test_container_error_status_raises(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(MEDIA_URL, json={"id": CONTAINER_ID})
        m.get(STATUS_URL, json={"status_code": "ERROR"})

        result = _uploader().publish(_image(tmp_path), _seo())

    assert result.success is False
    assert "failed processing" in result.error_message


def test_container_creation_api_error(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(MEDIA_URL, json={"error": {"message": "bad image url"}})
        result = _uploader().publish(_image(tmp_path), _seo())

    assert result.success is False
    assert "bad image url" in result.error_message
