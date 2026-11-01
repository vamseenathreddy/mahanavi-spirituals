"""analytics_probe.py: read-only. Per-day views/subscribers and traffic-source mix for the last N days, using the
saved token's YouTube Analytics access. Prints a clear note if the token lacks the analytics scope.
  python scripts/ci/analytics_probe.py [days]"""
from __future__ import annotations

import datetime as dt
import sys

from mahanavi.config import get_settings


def main() -> int:
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    try:
        from mahanavi.publishers.youtube_analytics_client import build_analytics_service
        svc = build_analytics_service(get_settings())
        end = dt.date.today()
        start = (end - dt.timedelta(days=days)).isoformat()
        q = lambda **kw: svc.reports().query(ids="channel==MINE", startDate=start, endDate=end.isoformat(), **kw).execute()  # noqa: E731
        r = q(metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost", dimensions="day", sort="day")
        print("DAY          views  minutes  subs+  subs-")
        for row in r.get("rows", []):
            print(f"{row[0]}  {int(row[1]):6d} {int(row[2]):8d} {int(row[3]):6d} {int(row[4]):6d}")
        r = q(metrics="views", dimensions="insightTrafficSourceType", sort="-views")
        print("TRAFFIC SOURCES (period):")
        for row in r.get("rows", []):
            print(f"  {row[0]:<22} {int(row[1])}")
        for metric in ("videoThumbnailImpressions", "videoThumbnailImpressionsClickRate"):
            try:
                r = q(metrics=metric, dimensions="day", sort="day")
                print(metric, [(x[0], round(x[1], 3)) for x in r.get("rows", [])][-10:])
            except Exception as exc:  # noqa: BLE001
                print(f"{metric}: unavailable ({str(exc)[:100]})")
                break
    except Exception as exc:  # noqa: BLE001
        print(f"ANALYTICS UNAVAILABLE: {type(exc).__name__}: {str(exc)[:300]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
