"""Day-wise god live on Mahanavi Spirituals: one unbroken stream 4:00 AM to about 9:48 AM IST (GitHub job limit is 6 h).
God by IST weekday (channels/live_gods/gods.py WEEK), or argv god override. Disabled via data/lakshmi_live.json enabled=false."""
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lakshmi_meta as m  # noqa: E402
from channels.live_gods import gods as G  # noqa: E402
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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    god = args[0] if args else G.WEEK[now.astimezone(IST).weekday()]
    if god not in cfg.get("approved_gods", []):
        print("god not approved, skip:", god)
        return
    video, thumb = ("build/lakshmi/long.mp4", "build/lakshmi/thumb.jpg") if god == "lakshmi" else (f"build/live/{god}/loop.mp4", f"build/live/{god}/thumb.jpg")
    if not Path(video).exists():
        alert(f"Live for {god} skipped: video missing ({video})")
        raise SystemExit(f"video missing: {video}")
    if not cfg.get("enabled") or today_ist < cfg["start_date"]:
        print("skip", today_ist, cfg)
        return
    start = now.astimezone(IST).replace(hour=4, minute=0, second=0, microsecond=0)
    # Late start (GitHub schedules can be hours late): go live right away if today's 4-8 AM window is still open,
    # otherwise skip. Never wait a day (that blocked the runner until the job timeout on 14 Nov).
    start = start.astimezone(timezone.utc)
    end = start + timedelta(hours=cfg.get("hours", 5.75))
    if now >= end:
        print("window already over")
        return
    yt = up.service(Path("./data/youtube_token.json"))
    go = max(now + timedelta(minutes=3), start)
    if god == "lakshmi":
        title, desc = m.LIVE_TITLE, m.DESCRIPTION.replace("This video contains", "This stream contains")
    else:
        title, desc = G.title(god), G.description(god)
    b = yt.liveBroadcasts().insert(part="snippet,status,contentDetails", body={
        "snippet": {"title": title, "description": desc, "scheduledStartTime": go.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        "contentDetails": {"enableAutoStart": True, "enableAutoStop": True, "enableDvr": True, "latencyPreference": "normal"},
    }).execute()
    bid = b["id"]
    s = yt.liveStreams().insert(part="snippet,cdn,contentDetails", body={
        "snippet": {"title": f"{god}-{today_ist}"},
        "cdn": {"frameRate": "variable", "ingestionType": "rtmp", "resolution": "variable"},
        "contentDetails": {"isReusable": False},
    }).execute()
    yt.liveBroadcasts().bind(part="id,contentDetails", id=bid, streamId=s["id"]).execute()
    ing = s["cdn"]["ingestionInfo"]
    url = f'{ing["ingestionAddress"]}/{ing["streamName"]}'
    print("broadcast", bid, "https://youtu.be/" + bid)
    try:
        yt.thumbnails().set(videoId=bid, media_body=MediaFileUpload(thumb, mimetype="image/jpeg")).execute()
    except Exception as e:
        print("thumb failed:", e)
    try:
        v = yt.videos().list(part="status", id=bid).execute()["items"][0]["status"]
        v["containsSyntheticMedia"] = False
        yt.videos().update(part="status", body={"id": bid, "status": v}).execute()
    except Exception as e:
        print("synthetic flag failed:", e)
    wait = (go - datetime.now(timezone.utc)).total_seconds()
    if wait > 0:
        time.sleep(wait)
    dur = int((end - datetime.now(timezone.utc)).total_seconds())
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-re", "-stream_loop", "-1", "-i", video,
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
        alert(f"{god} live ended with ffmpeg exit {rc} ({today_ist})")
        sys.exit(rc)


def run_test():
    god = next((a for a in sys.argv[1:] if not a.startswith("--")), "shiva")
    video = "build/lakshmi/long.mp4" if god == "lakshmi" else f"build/live/{god}/loop.mp4"
    """Private 2-minute stream to verify live permission and the ffmpeg push. Nothing public."""
    yt = up.service(Path("./data/youtube_token.json"))
    go = datetime.now(timezone.utc) + timedelta(minutes=2)
    b = yt.liveBroadcasts().insert(part="snippet,status,contentDetails", body={
        "snippet": {"title": f"TEST {god} live (private)", "scheduledStartTime": go.strftime("%Y-%m-%dT%H:%M:%S.000Z")},
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
    rc = subprocess.call(["ffmpeg", "-hide_banner", "-loglevel", "warning", "-re", "-stream_loop", "-1", "-i", video,
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
        alert(f"God live failed: {e}")
        raise
