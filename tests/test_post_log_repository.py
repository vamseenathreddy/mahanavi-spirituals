from __future__ import annotations

from datetime import date, time
from pathlib import Path

import pytest

from mahanavi.core.models import Deity, PanchangData, PublishTarget, UploadResult
from mahanavi.database.repositories import PostLogRepository
from mahanavi.exceptions import RecordNotFoundError


def _sample_panchang(d: date) -> PanchangData:
    return PanchangData(
        date_=d,
        tithi="Panchami",
        nakshatram="Rohini",
        varjyam="10:00 AM - 11:30 AM",
        rahu_kalam="07:30 AM - 09:00 AM",
        yamagandam="10:30 AM - 12:00 PM",
        gulika_kalam="01:30 PM - 03:00 PM",
        durmuhurtham="08:00 AM - 08:45 AM",
        abhijit_muhurtham="11:45 AM - 12:30 PM",
        sunrise=time(5, 58),
        sunset=time(18, 45),
        source="dummy",
    )


def test_create_pending_is_idempotent(post_log_repo: PostLogRepository) -> None:
    d = date(2026, 7, 20)
    id1 = post_log_repo.create_pending(d)
    id2 = post_log_repo.create_pending(d)
    assert id1 == id2


def test_get_by_date_missing_raises(post_log_repo: PostLogRepository) -> None:
    with pytest.raises(RecordNotFoundError):
        post_log_repo.get_by_date(date(2099, 1, 1))


def test_full_lifecycle(post_log_repo: PostLogRepository) -> None:
    d = date(2026, 7, 20)
    post_id = post_log_repo.create_pending(d)

    post_log_repo.update_generation_details(
        post_log_id=post_id,
        image_path=Path("/tmp/raw.jpg"),
        generated_image_path=Path("/tmp/generated.jpg"),
        folder_name="Monday_Shiva",
        panchang=_sample_panchang(d),
        caption="Om Namah Shivaya 🙏 #Shiva",
    )
    post_log_repo.update_status(post_id, "success")

    record = post_log_repo.get_by_date(d)
    assert record.status == "success"
    assert record.caption is not None and "Shiva" in record.caption
    assert record.generated_image_path == "/tmp/generated.jpg"


def test_record_upload_result(post_log_repo: PostLogRepository) -> None:
    d = date(2026, 7, 21)
    post_id = post_log_repo.create_pending(d)
    result = UploadResult(
        target=PublishTarget.TELEGRAM,
        success=True,
        post_url="https://t.me/mahanavispirituals/123",
    )
    # Should not raise.
    post_log_repo.record_upload_result(post_id, result)
