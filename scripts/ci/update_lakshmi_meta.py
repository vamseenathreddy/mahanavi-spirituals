"""Update title, description and tags of an already uploaded Lakshmi video (keeps everything else)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lakshmi_meta as m  # noqa: E402
from channels.engine import upload as up  # noqa: E402

vid = sys.argv[1]
yt = up.service(Path("./data/youtube_token.json"))
it = yt.videos().list(part="snippet", id=vid).execute()["items"][0]["snippet"]
body = {"id": vid, "snippet": {"title": m.TITLE, "description": m.DESCRIPTION, "tags": m.TAGS,
                               "categoryId": it["categoryId"], "defaultLanguage": it.get("defaultLanguage", "te")}}
if "defaultAudioLanguage" in it:
    body["snippet"]["defaultAudioLanguage"] = it["defaultAudioLanguage"]
yt.videos().update(part="snippet", body=body).execute()
print("updated", vid, "\nold title:", it["title"], "\nnew title:", m.TITLE)
