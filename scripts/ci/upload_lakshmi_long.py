"""Upload the Lakshmi Ashtottara long video to Mahanavi Spirituals as a scheduled release."""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lakshmi_meta as m  # noqa: E402
from channels.engine import upload as up  # noqa: E402
from googleapiclient.http import MediaFileUpload  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish-at", required=True, help="UTC ISO, e.g. 2026-11-12T22:15:00Z")
    ap.add_argument("--token", default="./data/youtube_token.json")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    when = datetime.strptime(a.publish_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if when <= datetime.now(timezone.utc):
        raise SystemExit("publish time is in the past")
    video = Path("build/lakshmi/long.mp4")
    thumb = Path("build/lakshmi/thumb.jpg")
    print(f"video {video.stat().st_size/1e6:.0f} MB, publish {when.isoformat()}")
    print(m.TITLE)
    if a.dry_run:
        return
    yt = up.service(Path(a.token))
    vid = up.upload_video(yt, str(video), m.TITLE, m.DESCRIPTION, m.TAGS, publish_at=when, language="te", category_id="10")
    print("uploaded", vid)
    from mahanavi.publishers.blogger_publisher import post_for_video
    print("blog post:", post_for_video(vid, m.TITLE, m.DESCRIPTION, a.publish_at))
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
        print("thumbnail set")
    except Exception as e:  # channel may lack custom-thumbnail permission
        print("thumbnail failed:", e)
    print(f"https://youtu.be/{vid}")


if __name__ == "__main__":
    main()
