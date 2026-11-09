import datetime as dt
import json

from channels.calendar import gate as cg
from mahanavi.content import ramayana_daily as rd


def _state(tmp_path, days):
    posted = {d: {"row": "x", "video_id": "v", "at": d} for d in days}
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"posted": posted, "used_ids": [s.slug for s in rd.STORIES]}))
    return str(p)


def test_pooja_waits_for_ramayana(tmp_path):
    p = _state(tmp_path, ["2026-11-17"])
    assert cg.ramayana_done_before(dt.date(2026, 11, 18), p)
    assert not cg.ramayana_done_before(dt.date(2026, 11, 17), p)   # last story is today: still the evening slot


def test_pooja_stays_evening_while_ramayana_runs(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"posted": {"2026-11-06": {}}, "used_ids": [rd.STORIES[0].slug]}))
    assert not cg.ramayana_done_before(dt.date(2026, 11, 20), str(p))
