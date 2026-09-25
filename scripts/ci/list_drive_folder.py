#!/usr/bin/env python3
"""One-off diagnostic: list what the service account can see in the
target Drive folder, so we can compare against the filenames the sync
script expects."""
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]

key_json = os.environ["GDRIVE_SA_KEY_JSON"]
key_path = Path("/tmp/gdrive_sa_key_diag.json")
key_path.write_text(key_json, encoding="utf-8")
creds = service_account.Credentials.from_service_account_file(str(key_path), scopes=SCOPES)
drive = build("drive", "v3", credentials=creds, cache_discovery=False)

folder_id = os.environ["GDRIVE_FOLDER_ID"]
print(f"Listing files with parent = {folder_id} ...")
resp = drive.files().list(
    q=f"'{folder_id}' in parents and trashed = false",
    fields="files(id, name, owners(emailAddress), parents)",
    supportsAllDrives=True,
    includeItemsFromAllDrives=True,
).execute()
files = resp.get("files", [])
if not files:
    print("(no files found with that folder as parent)")
for f in files:
    owners = ", ".join(o.get("emailAddress", "?") for o in f.get("owners", []))
    print(f"  name={f['name']!r} id={f['id']} owners=[{owners}] parents={f.get('parents')}")

print()
print("Folder metadata itself:")
meta = drive.files().get(fileId=folder_id, fields="id, name, mimeType, owners(emailAddress)", supportsAllDrives=True).execute()
print(f"  {meta}")
