#!/usr/bin/env python3
"""Build content/campaign/shorts_plan.json: 4 Shorts a day, 24 Nov to 4 Dec 2026 (IST), for the Chatrai sarpanch campaign."""
import datetime as dt
import json
from pathlib import Path

SLOGANS = ["రైతు బిడ్డ", "కష్టాన్ని నమ్ముకున్న వ్యక్తి", "అందరి మంచి కోరుకునే మనిషి", "మన కూటమి అభ్యర్థి, గెలిపించండి!",
           "మన ఊరి బిడ్డ, మన ఇంటి మనిషి", "మన ఊరికి మన అభ్యర్థి", "సేవ చేసే చేయి", "మీ మాట వినే నాయకుడు",
           "మన ఊరి భవిష్యత్తు కోసం మీ మద్దతు", "గెలిపించండి!"]
EN = ["Farmer's son", "A man who trusts hard work", "A man who wants good for everyone", "Our coalition candidate",
      "Our village's son", "Our candidate for our village", "The hand that serves", "A leader who listens to you",
      "Your support for our village's future", "Vote and win!"]
SLOTS = ["07:00", "12:00", "18:00", "21:00"]
TODAY_SLOTS = ["13:00", "15:30", "18:00", "21:00"]   # first day starts mid-day
START, END = dt.date(2026, 11, 24), dt.date(2026, 12, 4)
SONG = ("🎵 పూర్తి పాట ఈ ఛానల్‌లో చూడండి: \"గడ్డం ప్రభాకర్ రెడ్డి గారికే మీ ఓటు | Chatrai Sarpanch Candidate Campaign Song\"\n"
        "Watch the full campaign song on this channel: \"Chatrai Sarpanch Candidate Campaign Song\"")
HASH = ("#Shorts #Chatrai #చాట్రాయి #Sarpanch #సర్పంచ్ #TDP #తెలుగుదేశం #JanaSena #BJP #NDA #కూటమి #GaddamPrabhakarReddy "
        "#గడ్డంప్రభాకర్రెడ్డి #రైతుబిడ్డ #ChatraiVillage #APPanchayatElections #PanchayatElections #CampaignSong #TeluguSong")
TAGS = ["Gaddam Prabhakar Reddy", "గడ్డం ప్రభాకర్ రెడ్డి", "Chatrai", "చాట్రాయి", "Chatrai sarpanch", "సర్పంచ్ అభ్యర్థి", "sarpanch election",
        "TDP", "Jana Sena", "BJP", "కూటమి", "AP panchayat elections", "Telugu campaign song", "ప్రచార గీతం", "రైతు బిడ్డ", "Shorts"]


def main() -> None:
    plan, g, d = [], 0, START
    while d <= END:
        for s, slot in enumerate(TODAY_SLOTS if d == START else SLOTS, 1):
            te, en = SLOGANS[g % 10], EN[g % 10]
            title = f"{te} | గడ్డం ప్రభాకర్ రెడ్డి | Chatrai Sarpanch #Shorts"
            if len(title) > 95:
                title = f"{te} | గడ్డం ప్రభాకర్ రెడ్డి #Shorts"
            plan.append({
                "date": d.isoformat(), "slot": slot, "file": f"shorts/short_d{(d - START).days:02d}_s{s}.mp4", "n": g + 1,
                "title": f"{title[:90]} {g + 1}",
                "description": (f"{te}\n\nచాట్రాయి గ్రామపంచాయతీ సర్పంచ్ అభ్యర్థి శ్రీ గడ్డం ప్రభాకర్ రెడ్డి గారికే మీ అమూల్యమైన ఓటు వేసి ఆశీర్వదించవలసిందిగా ప్రార్థన. "
                                f"కూటమి బలపరిచిన అభ్యర్థి, శ్రీ మండపాటి బసవరెడ్డి గారు బలపరిచిన అభ్యర్థి.\n\n"
                                f"{en}. Gaddam Prabhakar Reddy, coalition-supported (TDP, Jana Sena, BJP) candidate for Sarpanch of Chatrai Gram Panchayat, Andhra Pradesh. "
                                f"Please bless him with your valuable vote.\n\n{SONG}\n\n🔔 Subscribe for more Chatrai campaign videos.\n\n{HASH}"),
                "title_en": f"{en} | Gaddam Prabhakar Reddy for Sarpanch, Chatrai #Shorts {g + 1}"[:100],
                "description_en": f"{en}. Gaddam Prabhakar Reddy, coalition-supported candidate for Sarpanch of Chatrai Gram Panchayat, Andhra Pradesh.\n\n{HASH}",
                "tags": TAGS})
            g += 1
        d += dt.timedelta(days=1)
    Path("content/campaign/shorts_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(plan), "entries", plan[0]["date"], "to", plan[-1]["date"])


if __name__ == "__main__":
    main()
