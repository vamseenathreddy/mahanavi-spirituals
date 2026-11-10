"""calendar_ahead.py: festival list lines for any month (2026-2030) computed from the real sky (Swiss Ephemeris, Hyderabad).

Telugu (amanta) lunar months: a month starts at a new moon and is named after the sidereal sign the sun enters inside it
(Chaitra = sun enters Mesha); a month without a sun ingress is Adhika and carries no festivals. Each festival is a rule
(month, paksha, tithi, time of day at which the tithi must prevail). The date is the first day whose tithi at that time matches.
Solar festivals (Bhogi, Makara Sankranti, Kanuma, Dhanurmasam) come from the sun's ingress.

    PYTHONPATH=src python -m mahanavi.content.calendar_ahead 2027 1 12      # print each month's lines
"""
from __future__ import annotations

import datetime as dt
import sys
from functools import lru_cache

import swisseph as swe

from mahanavi.content.beej_mantras import MONTH_NAME
from mahanavi.panchang.local_provider import HYDERABAD, LocalPanchangProvider

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
_prov = LocalPanchangProvider(*HYDERABAD)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# month index: 0 Chaitra 1 Vaishakha 2 Jyeshtha 3 Ashadha 4 Shravana 5 Bhadrapada 6 Ashwayuja 7 Karthika 8 Margasira 9 Pushya 10 Magha 11 Phalguna
# (month, paksha S/K, tithi 1-15, time basis, Telugu name)
RULES: list[tuple[int, str, int, str, str]] = [
    (0, "S", 1, "sunrise", "ఉగాది"),
    (0, "S", 9, "noon", "శ్రీరామ నవమి"),
    (0, "S", 15, "sunrise", "హనుమాన్ జయంతి"),
    (1, "S", 3, "forenoon", "అక్షయ తృతీయ"),
    (1, "S", 5, "sunrise", "శంకర జయంతి"),
    (1, "S", 14, "pradosha", "నృసింహ జయంతి"),
        (1, "K", 15, "aparahna", "శని జయంతి (అమావాస్య)"),
    (3, "S", 1, "sunrise", "ఆషాఢ మాసం ప్రారంభం"),
    (3, "S", 2, "sunrise", "పూరీ జగన్నాథ రథయాత్ర"),
    (3, "S", 11, "sunrise", "తొలి ఏకాదశి"),
    (3, "S", 15, "noon", "గురు పౌర్ణమి (వ్యాస పూర్ణిమ)"),
    (4, "S", 1, "sunrise", "శ్రావణ మాసం ప్రారంభం"),
    (4, "S", 5, "forenoon", "నాగుల పంచమి"),
    (4, "S", 15, "aparahna+", "రాఖీ పౌర్ణమి"),
    (4, "K", 8, "midnight+", "శ్రీ కృష్ణ జన్మాష్టమి"),
    (4, "K", 15, "aparahna", "పోలాల అమావాస్య"),
    (5, "S", 4, "noon", "వినాయక చవితి"),
    (5, "S", 5, "noon", "రుషి పంచమి"),
    (5, "S", 8, "noon", "రాధాష్టమి"),
    (5, "S", 14, "sunrise", "అనంత చతుర్దశి"),
    (5, "K", 1, "sunrise", "మహాలయ పక్షం ప్రారంభం"),
    (5, "K", 15, "aparahna", "మహాలయ అమావాస్య, ఎంగిలిపూల బతుకమ్మ"),
    (6, "S", 1, "sunrise", "దేవీ శరన్నవరాత్రులు ప్రారంభం"),
    (6, "S", 8, "aparahna", "దుర్గాష్టమి, సద్దుల బతుకమ్మ"),
    (6, "S", 9, "aparahna", "మహా నవమి"),
    (6, "S", 10, "aparahna", "విజయదశమి (దసరా)"),
    (6, "S", 15, "pradosha", "శరద్ పూర్ణిమ"),
    (6, "K", 3, "evening", "అట్ల తద్ది"),
    (6, "K", 13, "pradosha", "ధనత్రయోదశి"),
    (6, "K", 14, "arunodaya", "నరక చతుర్దశి"),
    (6, "K", 15, "pradosha", "దీపావళి (లక్ష్మీ పూజ)"),
    (7, "S", 1, "sunrise", "కార్తీక మాసం ప్రారంభం"),
    (7, "S", 2, "noon", "భగినీ హస్త భోజనం"),
    (7, "S", 4, "noon", "నాగుల చవితి"),
    (7, "S", 6, "noon", "స్కంద షష్ఠి"),
    (7, "S", 11, "sunrise", "ప్రబోధిని ఏకాదశి"),
    (7, "S", 12, "sunrise", "క్షీరాబ్ధి ద్వాదశి (తులసి వివాహం)"),
    (7, "S", 15, "pradosha+", "కార్తీక పౌర్ణమి (జ్వాలా తోరణం)"),
    (7, "K", 8, "midnight", "కాలభైరవ అష్టమి"),
    (7, "K", 15, "aparahna", "కార్తీక అమావాస్య (కార్తీక మాసం ముగింపు)"),
    (8, "S", 1, "sunrise", "మార్గశిర మాసం ప్రారంభం"),
    (8, "S", 6, "noon", "సుబ్రహ్మణ్య షష్ఠి"),
    (8, "S", 11, "sunrise", "ముక్కోటి ఏకాదశి, గీతా జయంతి"),
    (8, "S", 15, "pradosha", "దత్త జయంతి"),
    (9, "S", 15, "pradosha", "పుష్య పౌర్ణమి"),
    (10, "S", 1, "sunrise", "మాఘ మాసం ప్రారంభం"),
    (10, "S", 5, "forenoon", "వసంత పంచమి (శ్రీ పంచమి)"),
    (10, "S", 7, "sunrise", "రథ సప్తమి"),
    (10, "S", 8, "noon", "భీష్మాష్టమి"),
    (10, "S", 11, "sunrise", "భీష్మ ఏకాదశి"),
    (10, "S", 15, "pradosha", "మాఘ పౌర్ణమి"),
    (10, "K", 14, "midnight", "మహా శివరాత్రి"),
    (11, "S", 15, "pradosha", "హోలికా దహనం (కామదహనం)"),
]
# weekday festivals: (month, weekday 0=Mon, name_singular, month_start_name)
WEEKDAYS = [(7, 0, "కార్తీక సోమవారం"), (8, 3, "మార్గశిర లక్ష్మీవారం")]
FILL = {"sankashti": "సంకటహర చతుర్థి", "purnima": "పౌర్ణమి", "shivaratri": "మాస శివరాత్రి", "amavasya": "అమావాస్య"}


def _jd(t: dt.datetime) -> float:
    u = t.astimezone(dt.timezone.utc)
    return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)


def _lons(t: dt.datetime) -> tuple[float, float]:
    jd = _jd(t)
    flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    return swe.calc_ut(jd, swe.SUN, flag)[0][0], swe.calc_ut(jd, swe.MOON, flag)[0][0]


def tithi(t: dt.datetime) -> int:
    s, m = _lons(t)
    return int(((m - s) % 360) // 12) + 1


def _at(d: dt.date, basis: str) -> dt.datetime:
    rise = _prov._rise_set(d, swe.CALC_RISE)  # noqa: SLF001
    sset = _prov._rise_set(d, swe.CALC_SET)  # noqa: SLF001
    day0 = dt.datetime(d.year, d.month, d.day, tzinfo=IST)
    return {
        "sunrise": rise, "arunodaya": rise - dt.timedelta(minutes=96), "forenoon": day0 + dt.timedelta(hours=10),
        "noon": day0 + dt.timedelta(hours=12), "aparahna": day0 + dt.timedelta(hours=15), "pradosha": sset + dt.timedelta(minutes=45),
        "evening": day0 + dt.timedelta(hours=20), "midnight": day0 + dt.timedelta(hours=23, minutes=45),
    }[basis]


def _new_moon_after(t: dt.datetime) -> dt.datetime:
    def phase(x: dt.datetime) -> float:
        s, m = _lons(x)
        return (m - s) % 360
    a = t
    while phase(a + dt.timedelta(hours=6)) > phase(a) or phase(a) > 300:   # advance until just before the wrap
        a += dt.timedelta(hours=6)
        if phase(a) < 12 and phase(a) < phase(a - dt.timedelta(hours=6)):
            break
    lo, hi = a - dt.timedelta(hours=12), a + dt.timedelta(hours=12)
    for _ in range(40):
        mid = lo + (hi - lo) / 2
        if (_lons(mid)[1] - _lons(mid)[0]) % 360 > 180:   # before the new moon the phase is near 360
            lo = mid
        else:
            hi = mid
    return hi


@lru_cache(maxsize=1)
def lunar_months() -> tuple[tuple[dt.datetime, int | None], ...]:
    """(new moon time, month index or None for Adhika) from mid 2026 to 2030."""
    nms = []
    t = dt.datetime(2026, 6, 1, tzinfo=IST)
    while t < dt.datetime(2030, 3, 1, tzinfo=IST):
        nm = _new_moon_after(t)
        nms.append(nm)
        t = nm + dt.timedelta(days=20)
    out = []
    for i in range(len(nms) - 1):
        s0 = int(_lons(nms[i])[0] // 30)
        s1 = int(_lons(nms[i + 1])[0] // 30)
        out.append((nms[i], None if s0 == s1 else (s0 + 1) % 12))
    return tuple(out)


def month_of(t: dt.datetime) -> int | None:
    cur = None
    for nm, idx in lunar_months():
        if nm <= t:
            cur = idx
        else:
            break
    return cur


def _day_for(rule: tuple[int, str, int, str, str], lo: dt.date, hi: dt.date) -> list[dt.date]:
    month, pak, n, basis, _ = rule
    last = basis.endswith("+")      # two days match: take the later one (Rakhi, Janmashtami, Karthika Purnima follow the later day)
    basis = basis.rstrip("+")
    target = n if pak == "S" else n + 15
    out, d = [], lo
    while d <= hi:
        t = _at(d, basis)
        if tithi(t) == target and month_of(t) == month:
            out.append(d)
        d += dt.timedelta(days=1)
    # a tithi that prevails at the basis time on two days: the first day; a skipped tithi: the day it ends in
    if out:
        return out[-1:] if last else out[:1]
    d = lo - dt.timedelta(days=1)       # a skipped tithi (it starts and ends between two basis times): the later day
    while d < hi:
        t0, t1 = _at(d, basis), _at(d + dt.timedelta(days=1), basis)
        if tithi(t0) == (target - 2) % 30 + 1 and tithi(t1) == target % 30 + 1 and month_of(t1) == month and d + dt.timedelta(days=1) >= lo:
            return [d + dt.timedelta(days=1)]
        d += dt.timedelta(days=1)
    return []


def _ingress(deg: float, lo: dt.date, hi: dt.date) -> dt.date | None:
    """Day on which the sun enters the sidereal longitude `deg` (the day itself when it happens before sunset, else the next)."""
    d = lo
    while d < hi:
        a = _lons(dt.datetime(d.year, d.month, d.day, tzinfo=IST))[0]
        b = _lons(dt.datetime(d.year, d.month, d.day, tzinfo=IST) + dt.timedelta(days=1))[0]
        if (a % 360) < deg <= (b % 360) or (a > 359 and deg == 0):
            t0, t1 = dt.datetime(d.year, d.month, d.day, tzinfo=IST), dt.datetime(d.year, d.month, d.day, tzinfo=IST) + dt.timedelta(days=1)
            for _ in range(30):
                mid = t0 + (t1 - t0) / 2
                if _lons(mid)[0] % 360 >= deg:
                    t1 = mid
                else:
                    t0 = mid
            sset = _prov._rise_set(t1.astimezone(IST).date(), swe.CALC_SET)  # noqa: SLF001
            return t1.date() if t1 < sset else t1.date() + dt.timedelta(days=1)
        d += dt.timedelta(days=1)
    return None


def month_events(year: int, month: int) -> list[tuple[dt.date, str]]:
    first = dt.date(year, month, 1)
    last = (dt.date(year + (month == 12), month % 12 + 1, 1)) - dt.timedelta(days=1)
    ev: list[tuple[dt.date, str]] = []
    for rule in RULES:
        for d in _day_for(rule, first, last):
            ev.append((d, rule[4]))
    # Varalakshmi Vratam: the last Friday of Shravana shukla paksha (the Friday on or just before Shravana Purnima)
    def shukla4(x: dt.date) -> bool:
        t = _at(x, "sunrise")
        return month_of(t) == 4 and tithi(t) <= 15
    for i in range((last - first).days + 1):
        d = first + dt.timedelta(days=i)
        if d.weekday() == 4 and shukla4(d) and not shukla4(d + dt.timedelta(days=7)):
            ev.append((d, "వరలక్ష్మీ వ్రతం"))
    # weekday festivals inside their lunar month
    for m_idx, wd, name in WEEKDAYS:
        days = [first + dt.timedelta(days=i) for i in range((last - first).days + 1)]
        days = [d for d in days if d.weekday() == wd and month_of(_at(d, "sunrise")) == m_idx]
        if days:
            ev.append((days[0], name + "|" + ",".join(str(d.day) for d in days)))
    # solar festivals
    sank = _ingress(270.0, dt.date(year, 1, 1) if month == 1 else first, last)
    if sank:
        ev += [(sank - dt.timedelta(days=1), "భోగి"), (sank, "మకర సంక్రాంతి"), (sank + dt.timedelta(days=1), "కనుమ"),
               (sank + dt.timedelta(days=2), "ముక్కనుమ")]
    dh = _ingress(240.0, first, last)
    if dh:
        ev.append((dh, "ధనుర్మాసం ప్రారంభం (గోదా రంగనాథ పూజ)"))
    return sorted((e for e in ev if first <= e[0] <= last), key=lambda x: x[0])


def festival_lines(year: int, month: int, from_day: int = 1, fill_min: int = 7) -> list[str]:
    from mahanavi.content import calendar_days as cal

    mname = MONTH_NAME[month - 1][0]
    by_day: dict[dt.date, list[str]] = {}
    lines_wd: list[tuple[dt.date, str]] = []
    for d, name in month_events(year, month):
        if d.day < from_day:
            continue
        if "|" in name:
            label, days = name.split("|")
            nums = [x for x in days.split(",") if int(x) >= from_day]
            if nums:
                lines_wd.append((d, f"{', '.join(nums)} {mname} · {label}"))
            continue
        by_day.setdefault(d, []).append(name)
    rows = [(d, f"{d.day} {mname} · {', '.join(v)}") for d, v in by_day.items()] + lines_wd
    if len(rows) < fill_min:     # quiet month: add the main vratas so the card is never thin
        have = {d for d, _ in rows}
        for d, k in cal.month_items(year, month, tuple(FILL)):
            if d.day >= from_day and d not in have and len(rows) < fill_min:
                rows.append((d, f"{d.day} {mname} · {FILL[k]}"))
                have.add(d)
    rows.sort(key=lambda x: x[0])
    return [r for _, r in rows][:14]


if __name__ == "__main__":
    y, m0, m1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    for m in range(m0, m1 + 1):
        print(f"--- {y}-{m:02d}")
        print("\n".join(festival_lines(y, m)))
