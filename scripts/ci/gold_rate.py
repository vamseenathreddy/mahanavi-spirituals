#!/usr/bin/env python3
"""Fetch today's Hyderabad gold rate (22K / 24K, per gram and per 10 g) and write data/gold.json for the blog ticker."""
import json, re, sys, datetime as dt, urllib.request
from pathlib import Path
URL = "https://www.goodreturns.in/gold-rates/hyderabad.html"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Accept-Language": "en-IN,en;q=0.9"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

def grab(label):
    m = re.search(label + r"[^₹]{0,80}₹\s?([\d,]{4,9})", text)
    return int(m.group(1).replace(",", "")) if m else None

g24, g22 = grab(r"24K Gold /g"), grab(r"22K Gold /g")
if not g24 or not g22:
    m = re.search(r"1\s*₹\s?([\d,]+)[^₹]*?₹\s?([\d,]+)", text)
    if m:
        g24, g22 = int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))
print("parsed", g24, g22, "len", len(html))
if not g24:
    i = text.find("24K"); print("CTX", text[:200] if i < 0 else text[max(0, i-100):i+400])
if not (g24 and g22 and 5000 < g22 < g24 < 40000):
    print("::error::could not parse a sane gold rate"); sys.exit(1)
ist = dt.timezone(dt.timedelta(hours=5, minutes=30))
out = {"city": "Hyderabad", "g24": g24, "g22": g22, "updated": dt.datetime.now(ist).strftime("%Y-%m-%d %H:%M IST"), "source": "goodreturns.in"}
Path("data").mkdir(exist_ok=True)
Path("data/gold.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(out)
