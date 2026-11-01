"""Key periods derived from the SOLVED entries, and the header-date error rate (comp-adfgvx).

The published periods (keys.json 'period', Lasry et al. 2017) say when a key was meant to be in
force. The solved entries say when each key was actually seen: on which log pages (page date),
and under which heading dates (the intercept date). This module derives each key's observed
range from them, robustly, and assigns any entry to a period by header evidence alone.

Robust range: an entry is an OUTLIER for its key if its date is more than OUT_DAYS from the
key's median date (on the same scale, page or heading). Outliers are listed and are not used
for the range. They are mostly repeats sent days later (e.g. p214B = p148B under nov04 on
22 Nov).
"""
import datetime
from statistics import median

LASRY = ["sep19", "oct04", "oct28", "nov01", "nov04", "nov07", "nov10", "nov13_20", "nov13_16",
         "nov16", "nov19", "nov22", "nov25", "nov28"]
OUT_DAYS = 4


def _ord(d):
    return d.toordinal()


def derive(entries, exclude_id=None):
    """entries: solved records with '_pd' (page date) and '_h' (parsed heading).
    Returns {key: dict(n, page=(min,max), hdr=(min,max), out_page=[ids], out_hdr=[ids],
    first=(date,time,id), last=(date,time,id))}."""
    by = {}
    for e in entries:
        if e["key"] not in LASRY or e["id"] == exclude_id:
            continue
        by.setdefault(e["key"], []).append(e)
    out = {}
    for k, es in by.items():
        pds = [e["_pd"] for e in es if e["_pd"]]
        hds = [(min(e["_h"]["dates"]), e) for e in es if len(e["_h"]["dates"]) == 1]
        r = {"n": len(es), "out_page": [], "out_hdr": []}
        if pds:
            m = median(_ord(d) for d in pds)
            keep = [d for d in pds if abs(_ord(d) - m) <= OUT_DAYS]
            r["out_page"] = [e["id"] for e in es if e["_pd"] and abs(_ord(e["_pd"]) - m) > OUT_DAYS]
            r["page"] = (min(keep), max(keep))
        if hds:
            m = median(_ord(d) for d, _ in hds)
            keep = [(d, e) for d, e in hds if abs(_ord(d) - m) <= OUT_DAYS]
            r["out_hdr"] = [e["id"] for d, e in hds if abs(_ord(d) - m) > OUT_DAYS]
            r["hdr"] = (min(d for d, _ in keep), max(d for d, _ in keep))
            tkey = lambda de: (de[0], de[1]["_h"]["time"] or (12, 0))
            f = min(keep, key=tkey)
            l_ = max(keep, key=tkey)
            r["first"] = (f[0], f[1]["_h"]["time"], f[1]["id"])
            r["last"] = (l_[0], l_[1]["_h"]["time"], l_[1]["id"])
        out[k] = r
    return out


def assign(per, pdate, hdates):
    """Candidate keys for an entry from derived ranges. Intersection of page-range and
    heading-range candidates when both exist and overlap, else their union."""
    kp = {k for k, r in per.items() if "page" in r and pdate and r["page"][0] <= pdate <= r["page"][1]}
    kh = {k for k, r in per.items() if "hdr" in r and any(r["hdr"][0] <= d <= r["hdr"][1] for d in hdates)}
    if kp and kh and (kp & kh):
        return kp & kh, "page+heading"
    if kp or kh:
        return kp | kh, "page or heading" if (kp and kh) else ("page" if kp else "heading")
    return set(), "none"


def label(per, cands, pdate):
    if len(cands) == 1:
        return next(iter(cands))
    if cands:
        return "ambiguous between " + " and ".join(sorted(cands, key=LASRY.index))
    # gap: the nearest keys before and after on page dates
    if not pdate:
        return "no date"
    before = [k for k, r in per.items() if "page" in r and r["page"][1] < pdate]
    after = [k for k, r in per.items() if "page" in r and r["page"][0] > pdate]
    b = max(before, key=lambda k: per[k]["page"][1]) if before else "start"
    a = min(after, key=lambda k: per[k]["page"][0]) if after else "end"
    return f"gap between {b} and {a}"
