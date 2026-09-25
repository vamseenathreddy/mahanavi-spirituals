"""
DailyPipeline: the orchestrator that runs one full day's content pipeline:

    select image -> fetch panchang -> render image -> generate SEO
    -> publish to every configured platform -> log everything -> notify

Design notes:
- Every dependency is injected via the constructor (all typed against the
  ABCs in core/interfaces.py), so this class doesn't know or care whether
  it's talking to the dummy or real Panchang provider, Playwright or a
  future YouTube API uploader, etc.
- Each stage (selection, panchang, rendering, SEO) is independently
  try/excepted against its own domain exception. A failure at any of
  these stages aborts the run (there's nothing to publish without an
  image, panchang, rendered file, or caption) — but is still logged and
  notified, not raised out to crash the scheduler.
- Publishing is different: each publisher is attempted independently, so
  one platform failing (e.g. YouTube session expired) never blocks the
  others (e.g. Telegram still goes out). Overall status is success only
  if every publisher succeeded, partial if some did, failed if none did
  or if the pipeline never reached publishing.
"""

from __future__ import annotations

import logging
import traceback
from datetime import date
from pathlib import Path

from mahanavi.core.interfaces import (
    ContentGenerator,
    ImageRenderer,
    ImageSelector,
    Notifier,
    PanchangProvider,
    Uploader,
)
from mahanavi.core.models import DailyRunResult, PublishTarget, SeoContent, UploadResult
from mahanavi.database.repositories import PostLogRepository
from mahanavi.exceptions import (
    ContentGenerationError,
    ImageRenderError,
    ImageSelectionError,
    PanchangFetchError,
)

logger = logging.getLogger(__name__)


class DailyPipeline:
    """Orchestrates one full day's devotional-content run."""

    def __init__(
        self,
        image_selector: ImageSelector,
        panchang_provider: PanchangProvider,
        image_renderer: ImageRenderer,
        content_generator: ContentGenerator,
        publishers: list[Uploader],
        post_log_repo: PostLogRepository,
        notifier: Notifier,
    ) -> None:
        self._image_selector = image_selector
        self._panchang_provider = panchang_provider
        self._image_renderer = image_renderer
        self._content_generator = content_generator
        self._publishers = publishers
        self._post_log_repo = post_log_repo
        self._notifier = notifier

    def run_for_date(self, for_date: date) -> DailyRunResult:
        logger.info("=== Starting daily pipeline run for %s ===", for_date)
        result = DailyRunResult(run_date=for_date)
        post_log_id = self._post_log_repo.create_pending(for_date)

        try:
            result.selected_image = self._image_selector.select_for_date(for_date)
            result.panchang = self._panchang_provider.fetch(for_date)
            result.generated_image_path = self._image_renderer.render(
                result.selected_image, result.panchang, for_date
            )
            result.seo = self._content_generator.generate(
                result.selected_image, result.panchang, for_date
            )
        except (ImageSelectionError, PanchangFetchError, ImageRenderError, ContentGenerationError) as exc:
            logger.error("Pipeline aborted before publishing: %s", exc)
            self._post_log_repo.update_status(post_log_id, "failed", error_log=str(exc))
            self._notifier.notify(
                f"❌ Mahanavi Spirituals: {for_date} run FAILED before publishing.\nReason: {exc}"
            )
            return result

        self._post_log_repo.update_generation_details(
            post_log_id=post_log_id,
            image_path=result.selected_image.path,
            generated_image_path=result.generated_image_path,
            folder_name=result.selected_image.folder_name,
            panchang=result.panchang,
            caption=result.seo.full_caption(),
        )

        for publisher in self._publishers:
            upload_result = self._publish_safely(publisher, result.generated_image_path, result.seo)
            result.upload_results.append(upload_result)
            self._post_log_repo.record_upload_result(post_log_id, upload_result)

        status = self._overall_status(result.upload_results)
        self._post_log_repo.update_status(post_log_id, status)

        self._notifier.notify(
            self._build_notification_message(result, status),
            screenshot_path=self._first_screenshot(result.upload_results),
        )

        logger.info("=== Finished daily pipeline run for %s: status=%s ===", for_date, status)
        return result

    # --- Helpers ---------------------------------------------------------------

    def _publish_safely(self, publisher: Uploader, image_path: Path, seo: SeoContent) -> UploadResult:
        """Run one publisher, converting even unexpected exceptions into a
        failed UploadResult rather than letting one platform's bug abort
        every other platform's publish attempt."""
        try:
            return publisher.publish(image_path, seo)
        except Exception as exc:  # noqa: BLE001 - deliberately broad: isolate publisher failures
            logger.error(
                "Unexpected error from publisher %s: %s\n%s",
                type(publisher).__name__, exc, traceback.format_exc(),
            )
            target = getattr(publisher, "TARGET", PublishTarget.YOUTUBE)
            return UploadResult(target=target, success=False, error_message=str(exc))

    @staticmethod
    def _overall_status(upload_results: list[UploadResult]) -> str:
        if not upload_results:
            return "failed"
        successes = sum(1 for r in upload_results if r.success)
        if successes == len(upload_results):
            return "success"
        if successes == 0:
            return "failed"
        return "partial"

    @staticmethod
    def _first_screenshot(upload_results: list[UploadResult]) -> Path | None:
        for r in upload_results:
            if r.screenshot_path is not None:
                return r.screenshot_path
        return None

    @staticmethod
    def _build_notification_message(result: DailyRunResult, status: str) -> str:
        icon = {"success": "✅", "partial": "⚠️", "failed": "❌"}.get(status, "ℹ️")
        lines = [f"{icon} Mahanavi Spirituals: {result.run_date} run finished — status: {status.upper()}"]
        if result.selected_image:
            lines.append(f"Deity: {result.selected_image.deity.value} ({result.selected_image.filename})")
        for r in result.upload_results:
            mark = "✅" if r.success else "❌"
            detail = r.post_url or r.error_message or ""
            lines.append(f"{mark} {r.target.value}: {detail}")
        if result.seo:
            lines.append(f"\nCaption:\n{result.seo.full_caption()}")
        return "\n".join(lines)
