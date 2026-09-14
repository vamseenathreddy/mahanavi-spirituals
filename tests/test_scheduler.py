from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from apscheduler.triggers.cron import CronTrigger

from mahanavi.config import Settings
from mahanavi.scheduler import JOB_ID, build_scheduler


def _settings(tmp_path: Path) -> Settings:
    images_root = tmp_path / "Images"
    images_root.mkdir(parents=True, exist_ok=True)
    return Settings(
        images_root=images_root,
        output_dir=tmp_path / "out",
        database_path=tmp_path / "db.sqlite",
        log_dir=tmp_path / "logs",
        post_hour=5,
        post_minute=0,
        timezone="Asia/Kolkata",
    )


def test_scheduler_registers_daily_job_at_configured_time(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    fake_pipeline = MagicMock()

    scheduler = build_scheduler(fake_pipeline, settings)
    job = scheduler.get_job(JOB_ID)

    assert job is not None
    assert isinstance(job.trigger, CronTrigger)
    # CronTrigger stores fields; hour/minute should match configured values.
    field_values = {f.name: str(f) for f in job.trigger.fields}
    assert field_values["hour"] == "5"
    assert field_values["minute"] == "0"


def test_scheduler_never_allows_overlapping_runs(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    fake_pipeline = MagicMock()
    scheduler = build_scheduler(fake_pipeline, settings)
    job = scheduler.get_job(JOB_ID)
    assert job.max_instances == 1


def test_scheduler_uses_configured_timezone(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    settings.timezone = "America/New_York"
    fake_pipeline = MagicMock()
    scheduler = build_scheduler(fake_pipeline, settings)
    assert str(scheduler.timezone) == "America/New_York"
