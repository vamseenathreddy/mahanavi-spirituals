from __future__ import annotations

from pathlib import Path

import pytest
import requests_mock

from mahanavi.core.models import SeoContent
from mahanavi.exceptions import FacebookUploadError
from mahanavi.publishers.facebook_uploader import GRAPH_API_BASE, FacebookUploader

PAGE_ID = "1234567890"
TOKEN = "fake-page-token"
PHOTOS_URL = f"{GRAPH_API_BASE}/{PAGE_ID}/photos"


def _seo() -> SeoContent:
    return SeoContent(
        title_telugu="T", description_telugu="D",
        keywords_english=["k"], hashtags_telugu=["#a"],
        hashtags_trending=["#b"], alt_text="alt",
    )


def _image(tmp_path: Path) -> Path:
    p = tmp_path / "image.jpg"
    p.write_bytes(b"fake-jpeg-bytes")
    return p


def test_missing_credentials_raise() -> None:
    with pytest.raises(FacebookUploadError):
        FacebookUploader(page_id="", page_access_token=TOKEN)


def test_successful_publish(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(PHOTOS_URL, json={"id": "999", "post_id": "1234567890_999"})
        uploader = FacebookUploader(page_id=PAGE_ID, page_access_token=TOKEN, max_retries=0)
        result = uploader.publish(_image(tmp_path), _seo())

    assert result.success is True
    assert result.post_url == "https://www.facebook.com/1234567890_999"


def test_api_error_response(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(PHOTOS_URL, json={"error": {"message": "Invalid token"}})
        uploader = FacebookUploader(page_id=PAGE_ID, page_access_token=TOKEN, max_retries=0)
        result = uploader.publish(_image(tmp_path), _seo())

    assert result.success is False
    assert "Invalid token" in result.error_message


def test_http_failure_after_retries(tmp_path: Path) -> None:
    with requests_mock.Mocker() as m:
        m.post(PHOTOS_URL, status_code=500)
        uploader = FacebookUploader(page_id=PAGE_ID, page_access_token=TOKEN, max_retries=1, backoff_seconds=0)
        result = uploader.publish(_image(tmp_path), _seo())

    assert result.success is False
    assert m.call_count == 2
