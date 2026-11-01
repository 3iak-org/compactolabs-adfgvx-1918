"""Parse the OCR'd header lines of the Childs log (comp-adfgvx, 2026-10-31).

Header evidence only: the entry's letter, call signs, time and date as printed in its heading,
and the date of the log page it is filed under.  Never the ciphertext.

OCR substitutions tolerated in day numbers: l I i -> 1, O o -> 0, S -> 5 or 8 (ambiguous), B -> 8.
Every ambiguity is kept as a SET of candidate dates, never silently resolved.
"""
import datetime
import re

MONTHS = [("sep", 9), ("oct", 10), ("oot", 10), ("teber", 10), ("tober", 10), ("nov", 11),
          ("noe", 11), ("dec", 12)]
OCR_DIGIT = {"l": ["1"], "I": ["1"], "i": ["1"], "O": ["0"], "o": ["0"], "S": ["5", "8"],
             "B": ["8"], "$": ["5", "8"]}


def page_date(s):
    """records.json 'date' field, e.g. '26 October 1918'."""
    d, m, y = s.split()
    if not d.isdigit():
        return None   # Childs p.180 is filed under '? November 1918'
    mon = {"September": 9, "October": 10, "November": 11, "December": 12}[m]
    return datetime.date(int(y), mon, int(d))


def _month(tok):
    t = tok.lower()
    for k, v in MONTHS:
        if k in t:
            return v
    if re.match(r"^no[a-z.]*", t) and len(t) >= 5:
        return 11
    return None


def _day_candidates(tok):
    """'llth' -> {11}; 'Sth' -> {5, 8}; '24tn' -> {24}; '4%h' -> {4}."""
    m = re.match(r"^([0-9lIiOoSB$]{1,2})", tok)
    if not m:
        return set()
    core = m.group(1)
    opts = [""]
    for ch in core:
        alts = [ch] if ch.isdigit() else OCR_DIGIT.get(ch, [])
        opts = [o + a for o in opts for a in alts]
    out = set()
    for o in opts:
        if o and o.isdigit() and 1 <= int(o) <= 31:
            out.add(int(o))
    return out


TIME_RE = re.compile(r"(\d{1,3})[.,:-](\d{2})\s*[,.]?\s*([apAP])?")
SPLIT_CALLS = re.compile(r"\s+[vV]\s+|\s+v(?=\S)|(?<=\S)[vV]\s+|(?<=[-A-Z0-9\u2019'?])v(?=[-A-Z0-9\u2018'_])"
                         r"|\s+de\s+|\s+w\s*-|_")


def _month_positions(h):
    out = []
    for m in re.finditer(r"[A-Za-z]+", h):
        mo = _month(m.group(0))
        if mo:
            out.append((m.start(), m.end(), mo))
    return out


def parse(header, page):
    """Returns dict: letter, calls_from, calls_to, time (h, m) or None, dates (set of
    datetime.date), date_note (list of strings)."""
    h = (header or "").strip().lstrip('"')
    out = {"raw": header, "letter": None, "calls_from": None, "calls_to": None, "time": None,
           "dates": set(), "date_note": []}
    m = re.match(r"^\(?([A-Za-z0-9]{1,2})[)}]\s*", h)
    if m:
        out["letter"] = m.group(1)
        h = h[m.end():]
    # where the time/date part starts: the earliest of a time pattern, a month word, or a
    # bracket opening onto one of them
    cut = len(h)
    tm = TIME_RE.search(h)
    mp = _month_positions(h)
    sl = re.search(r"\((\d{1,2})/(\d{1,2})\)", h)
    for pos in ([tm.start()] if tm else []) + ([mp[0][0]] if mp else []) + ([sl.start()] if sl else []):
        cut = min(cut, pos)
    b = h.rfind("(", 0, cut)
    if b >= 0 and not re.search(r"[A-Za-z]{2}", h[b + 1:cut]):
        cut = b
    left, right = h[:cut], h[cut:]
    calls = [c.strip(" ,()") for c in SPLIT_CALLS.split(left.strip()) if c.strip(" ,()")]
    if len(calls) >= 2:
        out["calls_from"], out["calls_to"] = calls[0], calls[1]
    elif calls:
        out["calls_from"] = calls[0]
    if tm and tm.start() >= cut:
        hh, mi = int(tm.group(1)), int(tm.group(2))
        ap = (tm.group(3) or "").lower()
        if hh > 24 or mi > 59:
            out["date_note"].append("time unreadable")
        else:
            if ap == "p" and hh < 12:
                hh += 12
            if ap == "a" and hh == 12:
                hh = 0
            out["time"] = (hh, mi)
    mon, day = None, set()
    if sl:
        day, mon = {int(sl.group(1))}, int(sl.group(2))
    elif mp:
        mon = mp[0][2]
        tail = h[mp[0][1]:]
        # the day: digits glued to the month word, else the first of the next three tokens
        # that reads as a day
        glued = re.match(r"^[a-z.]*?(\d[\dlIS]?)", tail)
        cands = [glued.group(1)] if glued and not tail.startswith(" ") else []
        cands += [t for t in re.split(r"[\s,.()]+", tail) if t][:3]
        for t in cands:
            day = _day_candidates(t)
            if day:
                break
    else:
        for t in re.split(r"[\s,.()]+", right):
            if re.match(r"^[0-9lIS]{1,2}(st|nd|rd|th|d)$", t) and page is not None:
                day = _day_candidates(t)
                mon = page.month
                out["date_note"].append("month missing, page month assumed")
                break
    if mon and day:
        for d in sorted(day):
            try:
                out["dates"].add(datetime.date(1918, mon, d))
            except ValueError:
                out["date_note"].append(f"impossible date {mon}/{d}")
        if len(day) > 1:
            out["date_note"].append("day ambiguous in OCR: " + "/".join(map(str, sorted(day))))
    else:
        out["date_note"].append("no header date")
    return out
