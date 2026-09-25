"""
Repositories: the only place that writes raw SQL. Everything else in the
codebase talks to these classes, never to sqlite3 directly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from mahanavi.core.models import PanchangData, UploadResult
from mahanavi.database.db import DatabaseManager
from mahanavi.exceptions import DatabaseError, RecordNotFoundError


class ImageHistoryRepository:
    """
    Tracks which images have been used per weekday-folder, so the image
    selector can avoid repeats until every image in a folder is exhausted.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_used_filenames(self, folder_name: str) -> set[str]:
        """All filenames already used from this folder (across all time)."""
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT DISTINCT filename FROM image_usage WHERE folder_name = ?",
                (folder_name,),
            ).fetchall()
        return {row["filename"] for row in rows}

    def mark_used(self, folder_name: str, filename: str, used_on: date) -> None:
        with self._db.connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO image_usage (folder_name, filename, used_on)
                VALUES (?, ?, ?)
                """,
                (folder_name, filename, used_on.isoformat()),
            )

    def reset_folder_history(self, folder_name: str) -> None:
        """Wipe usage history for a folder once every image has been used —
        called by the ImageSelector (Module 2) at the start of a new cycle."""
        with self._db.connection() as conn:
            conn.execute(
                "DELETE FROM image_usage WHERE folder_name = ?", (folder_name,)
            )


class PuranaHistoryRepository:
    """
    Tracks which of the 18 Puranas have already been used for a long-form
    video, so episode selection can jump randomly between them (per
    explicit request) while never repeating one until all 18 have been
    covered -- same non-repeating-cycle pattern as ImageHistoryRepository,
    just keyed by Purana name instead of image folder.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def get_used_puranas(self) -> set[str]:
        """All Purana names already used (across all time)."""
        with self._db.connection() as conn:
            rows = conn.execute("SELECT DISTINCT purana_name FROM purana_usage").fetchall()
        return {row["purana_name"] for row in rows}

    def mark_used(self, purana_name: str, used_on: date) -> None:
        with self._db.connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO purana_usage (purana_name, used_on) VALUES (?, ?)",
                (purana_name, used_on.isoformat()),
            )

    def reset_history(self) -> None:
        """Wipe usage history once all 18 Puranas have been used, starting
        a fresh non-repeating cycle -- same idea as
        ImageHistoryRepository.reset_folder_history."""
        with self._db.connection() as conn:
            conn.execute("DELETE FROM purana_usage")


@dataclass(slots=True)
class PostLogRecord:
    id: int
    run_date: date
    status: str
    caption: str | None
    generated_image_path: str | None


class PostLogRepository:
    """Persists one row per day's run: chosen image, panchang, caption, status."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def create_pending(self, run_date: date) -> int:
        """Create (or fetch existing) pending row for today; returns post_log id."""
        with self._db.connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO post_log (run_date, status)
                VALUES (?, 'pending')
                """,
                (run_date.isoformat(),),
            )
            row = conn.execute(
                "SELECT id FROM post_log WHERE run_date = ?", (run_date.isoformat(),)
            ).fetchone()
        if row is None:
            raise DatabaseError(f"Failed to create/fetch post_log row for {run_date}")
        return int(row["id"])

    def update_generation_details(
        self,
        post_log_id: int,
        image_path: Path,
        generated_image_path: Path,
        folder_name: str,
        panchang: PanchangData,
        caption: str,
    ) -> None:
        with self._db.connection() as conn:
            conn.execute(
                """
                UPDATE post_log
                SET image_path = ?, generated_image_path = ?, folder_name = ?,
                    panchang_json = ?, caption = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    str(image_path),
                    str(generated_image_path),
                    folder_name,
                    json.dumps(_panchang_to_dict(panchang)),
                    caption,
                    post_log_id,
                ),
            )

    def update_status(self, post_log_id: int, status: str, error_log: str | None = None) -> None:
        with self._db.connection() as conn:
            conn.execute(
                """
                UPDATE post_log
                SET status = ?, error_log = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (status, error_log, post_log_id),
            )

    def get_by_date(self, run_date: date) -> PostLogRecord:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT id, run_date, status, caption, generated_image_path "
                "FROM post_log WHERE run_date = ?",
                (run_date.isoformat(),),
            ).fetchone()
        if row is None:
            raise RecordNotFoundError(f"No post_log entry for {run_date}")
        return PostLogRecord(
            id=row["id"],
            run_date=date.fromisoformat(row["run_date"]),
            status=row["status"],
            caption=row["caption"],
            generated_image_path=row["generated_image_path"],
        )

    def record_upload_result(self, post_log_id: int, result: UploadResult) -> None:
        with self._db.connection() as conn:
            conn.execute(
                """
                INSERT INTO upload_log
                    (post_log_id, target, success, post_url, error_message, screenshot_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    post_log_id,
                    result.target.value,
                    1 if result.success else 0,
                    result.post_url,
                    result.error_message,
                    str(result.screenshot_path) if result.screenshot_path else None,
                ),
            )


def _panchang_to_dict(p: PanchangData) -> dict:
    return {
        "date": p.date_.isoformat(),
        "tithi": p.tithi,
        "nakshatram": p.nakshatram,
        "varjyam": p.varjyam,
        "rahu_kalam": p.rahu_kalam,
        "yamagandam": p.yamagandam,
        "gulika_kalam": p.gulika_kalam,
        "durmuhurtham": p.durmuhurtham,
        "abhijit_muhurtham": p.abhijit_muhurtham,
        "sunrise": p.sunrise.isoformat(),
        "sunset": p.sunset.isoformat(),
        "source": p.source,
    }
