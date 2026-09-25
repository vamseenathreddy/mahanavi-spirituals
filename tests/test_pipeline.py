from __future__ import annotations

from datetime import date, time
from pathlib import Path

import pytest

from mahanavi.core.interfaces import (
    ContentGenerator,
    ImageRenderer,
    ImageSelector,
    Notifier,
    PanchangProvider,
    Uploader,
)
from mahanavi.core.models import (
    Deity,
    PanchangData,
    PublishTarget,
    SeoContent,
    SelectedImage,
    UploadResult,
)
from mahanavi.database.db import DatabaseManager
from mahanavi.database.repositories import PostLogRepository
from mahanavi.exceptions import ImageSelectionError
from mahanavi.pipeline import DailyPipeline


# --- Fakes: each implements exactly one ABC from core/interfaces.py ---------

class FakeImageSelector(ImageSelector):
    def __init__(self, raises: Exception | None = None) -> None:
        self._raises = raises

    def select_for_date(self, for_date: date) -> SelectedImage:
        if self._raises:
            raise self._raises
        return SelectedImage(
            path=Path("/fake/shiva.jpg"), folder_name="Monday_Shiva",
            filename="shiva.jpg", deity=Deity.SHIVA,
        )


class FakePanchangProvider(PanchangProvider):
    def fetch(self, for_date: date) -> PanchangData:
        return PanchangData(
            date_=for_date, tithi="Panchami", nakshatram="Rohini",
            varjyam="v", rahu_kalam="r", yamagandam="y", gulika_kalam="g",
            durmuhurtham="d", abhijit_muhurtham="a",
            sunrise=time(5, 58), sunset=time(18, 45), source="fake",
        )


class FakeImageRenderer(ImageRenderer):
    def render(self, selected_image, panchang, for_date) -> Path:
        return Path("/fake/rendered.jpg")


class FakeContentGenerator(ContentGenerator):
    def generate(self, selected_image, panchang, for_date) -> SeoContent:
        return SeoContent(
            title_telugu="Title", description_telugu="Desc",
            keywords_english=["k"], hashtags_telugu=["#a"],
            hashtags_trending=["#b"], alt_text="alt",
        )


class FakeUploader(Uploader):
    TARGET = PublishTarget.TELEGRAM

    def __init__(self, target: PublishTarget, succeed: bool = True, raise_unexpected: bool = False) -> None:
        self.TARGET = target
        self._succeed = succeed
        self._raise_unexpected = raise_unexpected

    def publish(self, image_path: Path, seo: SeoContent) -> UploadResult:
        if self._raise_unexpected:
            raise RuntimeError("boom — unexpected bug in this publisher")
        return UploadResult(
            target=self.TARGET, success=self._succeed,
            post_url="https://example.com/post" if self._succeed else None,
            error_message=None if self._succeed else "simulated failure",
        )


class RecordingNotifier(Notifier):
    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, message: str, screenshot_path: Path | None = None) -> None:
        self.messages.append(message)


@pytest.fixture
def post_log_repo(tmp_path: Path) -> PostLogRepository:
    db = DatabaseManager(tmp_path / "test.db")
    return PostLogRepository(db)


def _pipeline(
    post_log_repo: PostLogRepository,
    publishers: list[Uploader],
    notifier: RecordingNotifier,
    selector: ImageSelector | None = None,
) -> DailyPipeline:
    return DailyPipeline(
        image_selector=selector or FakeImageSelector(),
        panchang_provider=FakePanchangProvider(),
        image_renderer=FakeImageRenderer(),
        content_generator=FakeContentGenerator(),
        publishers=publishers,
        post_log_repo=post_log_repo,
        notifier=notifier,
    )


def test_all_publishers_succeed_gives_success_status(post_log_repo: PostLogRepository) -> None:
    notifier = RecordingNotifier()
    publishers = [FakeUploader(PublishTarget.YOUTUBE), FakeUploader(PublishTarget.TELEGRAM)]
    pipeline = _pipeline(post_log_repo, publishers, notifier)

    result = pipeline.run_for_date(date(2026, 7, 20))

    assert result.overall_success is True
    record = post_log_repo.get_by_date(date(2026, 7, 20))
    assert record.status == "success"
    assert any("SUCCESS" in m for m in notifier.messages)


def test_one_publisher_failing_gives_partial_status(post_log_repo: PostLogRepository) -> None:
    notifier = RecordingNotifier()
    publishers = [
        FakeUploader(PublishTarget.YOUTUBE, succeed=True),
        FakeUploader(PublishTarget.TELEGRAM, succeed=False),
    ]
    pipeline = _pipeline(post_log_repo, publishers, notifier)

    result = pipeline.run_for_date(date(2026, 7, 20))

    assert result.overall_success is False
    record = post_log_repo.get_by_date(date(2026, 7, 20))
    assert record.status == "partial"
    assert any("PARTIAL" in m for m in notifier.messages)


def test_all_publishers_failing_gives_failed_status(post_log_repo: PostLogRepository) -> None:
    notifier = RecordingNotifier()
    publishers = [
        FakeUploader(PublishTarget.YOUTUBE, succeed=False),
        FakeUploader(PublishTarget.TELEGRAM, succeed=False),
    ]
    pipeline = _pipeline(post_log_repo, publishers, notifier)

    result = pipeline.run_for_date(date(2026, 7, 20))

    record = post_log_repo.get_by_date(date(2026, 7, 20))
    assert record.status == "failed"


def test_early_stage_failure_skips_publishing_entirely(post_log_repo: PostLogRepository) -> None:
    notifier = RecordingNotifier()
    publishers = [FakeUploader(PublishTarget.YOUTUBE)]
    failing_selector = FakeImageSelector(raises=ImageSelectionError("no images"))
    pipeline = _pipeline(post_log_repo, publishers, notifier, selector=failing_selector)

    result = pipeline.run_for_date(date(2026, 7, 20))

    assert result.upload_results == []
    record = post_log_repo.get_by_date(date(2026, 7, 20))
    assert record.status == "failed"
    assert any("FAILED before publishing" in m for m in notifier.messages)


def test_unexpected_publisher_exception_does_not_abort_other_publishers(
    post_log_repo: PostLogRepository,
) -> None:
    notifier = RecordingNotifier()
    publishers = [
        FakeUploader(PublishTarget.YOUTUBE, raise_unexpected=True),
        FakeUploader(PublishTarget.TELEGRAM, succeed=True),
    ]
    pipeline = _pipeline(post_log_repo, publishers, notifier)

    result = pipeline.run_for_date(date(2026, 7, 20))

    assert len(result.upload_results) == 2
    youtube_result = next(r for r in result.upload_results if r.target == PublishTarget.YOUTUBE)
    telegram_result = next(r for r in result.upload_results if r.target == PublishTarget.TELEGRAM)
    assert youtube_result.success is False
    assert "boom" in youtube_result.error_message
    assert telegram_result.success is True


def test_notification_message_includes_caption(post_log_repo: PostLogRepository) -> None:
    notifier = RecordingNotifier()
    publishers = [FakeUploader(PublishTarget.TELEGRAM)]
    pipeline = _pipeline(post_log_repo, publishers, notifier)

    pipeline.run_for_date(date(2026, 7, 20))

    assert any("Title" in m and "Desc" in m for m in notifier.messages)


def test_post_log_records_generation_details(post_log_repo: PostLogRepository) -> None:
    notifier = RecordingNotifier()
    publishers = [FakeUploader(PublishTarget.TELEGRAM)]
    pipeline = _pipeline(post_log_repo, publishers, notifier)

    pipeline.run_for_date(date(2026, 7, 20))

    record = post_log_repo.get_by_date(date(2026, 7, 20))
    assert record.generated_image_path == "/fake/rendered.jpg"
    assert "Title" in record.caption
