"""Read-only: print id | views | privacy | title for every upload on the channel."""
from pathlib import Path
from channels.engine import upload as up

yt = up.service(Path("./data/youtube_token.json"))
ch = yt.channels().list(part="contentDetails,snippet", mine=True).execute()["items"][0]
print("CHANNEL", ch["snippet"]["title"])
pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
ids, tok = [], None
while True:
    r = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok).execute()
    ids += [i["contentDetails"]["videoId"] for i in r["items"]]
    tok = r.get("nextPageToken")
    if not tok:
        break
for k in range(0, len(ids), 50):
    r = yt.videos().list(part="snippet,statistics,status", id=",".join(ids[k:k+50])).execute()
    for v in r["items"]:
        print("V|%s|%s|%s|%s" % (v["id"], v["statistics"].get("viewCount", 0), v["status"]["privacyStatus"], v["snippet"]["title"]))
