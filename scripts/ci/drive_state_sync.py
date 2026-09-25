#!/usr/bin/env python3
"""
CI helper: sync Mahanavi Spirituals persistent state with Google Drive.

GitHub Actions runners are stateless -- every run starts from a clean
checkout. This script uses one Drive folder as the durable store for the
files that must survive between runs:

  - data/mahanavi.db          (purana / image usage history)
  - data/youtube_token.json   (OAuth refresh token)
  - data/last_run_date.txt    (IST date of the last successful post --
                                used as a same-day double-post guard)

Auth: a Google Cloud SERVICE ACCOUNT (not the interactive OAuth app used
for the actual YouTube upload). Its JSON key is stored as the
GDRIVE_SA_KEY_B64 GitHub secret (base64-encoded) and decoded to a temp
file at the start of each run. The target Drive folder must be shared
with the service account's email as Editor, or nothing below will find it.

Usage:
    python scripts/ci/drive_state_sync.py pull          # Drive -> ./data
    python scripts/ci/drive_state_sync.py push           # ./data -> Drive
    python scripts/ci/drive_state_sync.py check-date      # sets $GITHUB_OUTPUT run=true/false
    python scripts/ci/drive_state_sync.py mark-done        # writes today's IST date locally
"""

from __future__ import annotations

import base64
import io
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]
DATA_DIR = Path("data")
STATE_FILES = ["mahanavi.db", "youtube_token.json", "last_run_date.txt"]


def _drive_client():
    key_b64 = os.environ["GDRIVE_SA_KEY_B64"]
    key_path = Path("/tmp/gdrive_sa_key.json")
    key_path.write_bytes(base64.b64decode(key_b64))
    creds = service_account.Credentials.from_service_account_file(
        str(key_path), scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _folder_id() -> str:
    return os.environ["GDRIVE_FOLDER_ID"]


def _find_file_id(drive, name: str) -> str | None:
    query = f"'{_folder_id()}' in parents and name = '{name}' and trashed = false"
    resp = drive.files().list(q=query, fields="files(id, name)").execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None


def pull() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    drive = _drive_client()
    for name in STATE_FILES:
        file_id = _find_file_id(drive, name)
        if not file_id:
            print(f"[drive-sync] {name}: not found in Drive yet, skipping restore")
            continue
        request = drive.files().get_media(fileId=file_id)
        target = DATA_DIR / name
        with io.FileIO(target, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        print(f"[drive-sync] restored {name} <- Drive")


def push() -> None:
    drive = _drive_client()
    for name in STATE_FILES:
        local_path = DATA_DIR / name
        if not local_path.exists():
            print(f"[drive-sync] {name}: no local file to push, skipping")
            continue
        media = MediaFileUpload(str(local_path), resumable=False)
        file_id = _find_file_id(drive, name)
        if file_id:
            drive.files().update(fileId=file_id, media_body=media).execute()
        else:
            metadata = {"name": name, "parents": [_folder_id()]}
            drive.files().create(body=metadata, media_body=media, fields="id").execute()
        print(f"[drive-sync] pushed {name} -> Drive")


def _today_ist() -> str:
    return datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()


def check_date() -> None:
    marker = DATA_DIR / "last_run_date.txt"
    last = marker.read_text().strip() if marker.exists() else ""
    today = _today_ist()
    should_run = last != today
    print(f"[drive-sync] last posted: {last or '(never)'} | today: {today} | run: {should_run}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as fh:
            fh.write(f"run={'true' if should_run else 'false'}\n")


def mark_done() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "last_run_date.txt").write_text(_today_ist())
    print(f"[drive-sync] marked {_today_ist()} as done")


def main() -> int:
    valid = {"pull": pull, "push": push, "check-date": check_date, "mark-done": mark_done}
    if len(sys.argv) != 2 or sys.argv[1] not in valid:
        print(__doc__)
        return 1
    valid[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
