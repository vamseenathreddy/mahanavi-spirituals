#!/usr/bin/env python3
"""List (default) or delete (--delete) cron-job.org jobs that nothing uses any more: jobs that are disabled, jobs whose
workflow file no longer exists in this repo, and duplicate jobs for the same workflow (the newest-created copy of an
enabled workflow is kept). One API call to list; one per delete.

Usage: CRONJOB_ORG_API_KEY=... python3 scripts/ci/cronjob_prune.py [--delete]"""
from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from cronjob_reschedule import _api_request  # noqa: E402

WF = Path(__file__).resolve().parents[2] / ".github/workflows"


def main() -> int:
    key = os.environ["CRONJOB_ORG_API_KEY"].strip()
    jobs = _api_request("GET", "/jobs", key).get("jobs", [])
    existing = {p.name for p in WF.glob("*.yml")}
    by_file: dict[str, list[dict]] = {}
    for j in jobs:
        m = re.search(r"/workflows/([^/]+)/dispatches", j.get("url", ""))
        j["_wf"] = m.group(1) if m else None
        by_file.setdefault(j["_wf"], []).append(j)
    doomed: list[tuple[dict, str]] = []
    for j in jobs:
        wf = j["_wf"]
        if wf is None:
            continue  # not a workflow dispatch job: never touched
        if wf not in existing:
            doomed.append((j, "workflow file missing"))
        elif not j.get("enabled", True):
            doomed.append((j, "disabled"))
    ids = {j["jobId"] for j, _ in doomed}
    for wf, group in by_file.items():
        live = [j for j in group if wf in existing and j.get("enabled", True) and j["jobId"] not in ids]
        if wf and len(live) > 1:
            live.sort(key=lambda j: j.get("jobId", 0))
            for j in live[:-1]:
                doomed.append((j, f"duplicate of job {live[-1]['jobId']}"))
    print(f"::notice::{len(jobs)} jobs total, {len(doomed)} unused")
    for j, why in doomed:
        print(f"{'DELETE' if '--delete' in sys.argv else 'would delete'} {j['jobId']} {j.get('title')!r} {j['_wf']} ({why})")
    keep = [j for j in jobs if j["jobId"] not in {d['jobId'] for d, _ in doomed}]
    print(f"::notice::keeping {len(keep)} jobs")
    if "--delete" in sys.argv:
        for j, _ in doomed:
            time.sleep(2)
            _api_request("DELETE", f"/jobs/{j['jobId']}", key)
        print(f"::notice::deleted {len(doomed)} jobs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
