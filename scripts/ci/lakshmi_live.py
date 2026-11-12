"""Daily Lakshmi Ashtottara live loop on Mahanavi Spirituals: 4:00-8:00 AM IST until data/lakshmi_live.json is disabled."""
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lakshmi_meta as m  # noqa: E402
from channels.engine import upload as up  # noqa: E402
from googleapiclient.http import MediaFileUpload  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))


def alert(msg):
    try:
        from mahanavi.config import get_settings
        from mahanavi.notifications.telegram_alert import send_telegram_alert
        send_telegram_alert(msg, get_settings())
    except Exception as e:
        print("alert failed:", e)


def main():
    test = "--test" in sys.argv
    if test:
        return run_test()
    cfg = json.loads(Path("data/lakshmi_live.json").read_text())
    now = datetime.now(timezone.utc)
    today_ist = now.astimezone(IST).date().isoformat()
    if not cfg.get("enabled") or today_ist < cfg["start_date"]:
        print("skip", today_ist, cfg)
        return
    start = now.astimezone(IST).replace(hour=4, minute=0, second=0, microsecond=0)
    if start < now.astimezone(IST) - timedelta(hours=2):
        start += timedelta(days=1)
    start = start.astimezone(timezone.utc)
    end = start + timedelta(hours=cfg.get("hours", 4))
    if now >= end:
        print("window already over")
        return
    yt = up.service(Path("./data/youtube_token.json"))
    go = max(now + timedelta(minutes=3), start)
    title = m.LIVE_TITLE
    desc = m.DESCRIPTION.replace("This video contains", "This stream contains")
    b = yt.liveBroadcasts().insert(part="snippet,status,contentDetails", body={
        "snippet": {"title": title, "description": desc, "scheduledStartTime": go.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        "contentDetails": {"enableAutoStart": True, "enableAutoStop": True, "enableDvr": True, "latencyPreference": "normal"},
    }).execute()
    bid = b["id"]
    s = yt.liveStreams().insert(part="snippet,cdn,contentDetails", body={
        "snippet": {"title": f"lakshmi-{today_ist}"},
        "cdn": {"frameRate": "variable", "ingestionType": "rtmp", "resolution": "variable"},
        "contentDetails": {"isReusable": False},
    }).execute()
    yt.liveBroadcasts().bind(part="id,contentDetails", id=bid, streamId=s["id"]).execute()
    ing = s["cdn"]["ingestionInfo"]
    url = f'{ing["ingestionAddress"]}/{ing["streamName"]}'
    print("broadcast", bid, "https://youtu.be/" + bid)
    try:
        yt.thumbnails().set(videoId=bid, media_body=MediaFileUpload("build/lakshmi/thumb.jpg", mimetype="image/jpeg")).execute()
    except Exception as e:
        print("thumb failed:", e)
    try:
        v = yt.videos().list(part="status", id=bid).execute()["items"][0]["status"]
        v["containsSyntheticMedia"] = True
        yt.videos().update(part="status", body={"id": bid, "status": v}).execute()
    except Exception as e:
        print("synthetic flag failed:", e)
    wait = (go - datetime.now(timezone.utc)).total_seconds()
    if wait > 0:
        time.sleep(wait)
    dur = int((end - datetime.now(timezone.utc)).total_seconds())
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-re", "-stream_loop", "-1", "-i", "build/lakshmi/long.mp4",
           "-t", str(dur), "-vf", "scale=1280:720,fps=30", "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3000k",
           "-maxrate", "3000k", "-bufsize", "6000k", "-g", "60", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-f", "flv", url]
    rc = subprocess.call(cmd)
    print("ffmpeg exit", rc)
    try:
        yt.liveBroadcasts().transition(part="status", id=bid, broadcastStatus="complete").execute()
    except Exception as e:
        print("transition:", e)
    if rc != 0:
        alert(f"Lakshmi live loop ended with ffmpeg exit {rc} ({today_ist})")
        sys.exit(rc)


def run_test():
    """Private 2-minute stream to verify live permission and the ffmpeg push. Nothing public."""
    yt = up.service(Path("./data/youtube_token.json"))
    go = datetime.now(timezone.utc) + timedelta(minutes=2)
    b = yt.liveBroadcasts().insert(part="snippet,status,contentDetails", body={
        "snippet": {"title": "TEST Lakshmi live (private)", "scheduledStartTime": go.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False},
        "contentDetails": {"enableAutoStart": True, "enableAutoStop": True},
    }).execute()
    s = yt.liveStreams().insert(part="snippet,cdn,contentDetails", body={
        "snippet": {"title": "lakshmi-test"},
        "cdn": {"frameRate": "variable", "ingestionType": "rtmp", "resolution": "variable"},
        "contentDetails": {"isReusable": False},
    }).execute()
    yt.liveBroadcasts().bind(part="id,contentDetails", id=b["id"], streamId=s["id"]).execute()
    ing = s["cdn"]["ingestionInfo"]
    url = f'{ing["ingestionAddress"]}/{ing["streamName"]}'
    rc = subprocess.call(["ffmpeg", "-hide_banner", "-loglevel", "warning", "-re", "-stream_loop", "-1", "-i", "build/lakshmi/long.mp4",
                          "-t", "150", "-vf", "scale=1280:720,fps=30", "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3000k",
                          "-maxrate", "3000k", "-bufsize", "6000k", "-g", "60", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-f", "flv", url])
    print("TEST ffmpeg exit", rc, "broadcast", b["id"])
    try:
        yt.liveBroadcasts().transition(part="status", id=b["id"], broadcastStatus="complete").execute()
    except Exception as e:
        print("transition:", e)
    try:
        yt.videos().delete(id=b["id"]).execute()
        print("test broadcast deleted")
    except Exception as e:
        print("delete:", e)
    sys.exit(rc)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        alert(f"Lakshmi live loop failed: {e}")
        raise
