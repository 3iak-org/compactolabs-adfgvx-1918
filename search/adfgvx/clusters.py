"""Header clustering of the unread ADFGVX 1918 log entries (comp-adfgvx, 2026-10-31).

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/clusters.py

HEADER EVIDENCE ONLY: the date of the log page, the date/time/call signs in the entry's heading,
the multi-part structure (entries sharing a heading), and the published key-change schedule
(keys.json 'period').  The ciphertext symbols are never read here, except to REPORT each
member's length (symbol count), which is not used to form or rank any group.

Rules (all defined below and calibrated on the SOLVED entries, whose key is known):
  R_page    candidate key periods = {period(page date)}
  R_hdr     {period(d) : d a header date}
  R_lag     R_page U R_hdr U {period(page date - 1)} U {period(d - 1) : d a header date}
  R_lag3    R_lag U {period(d - 2), period(d - 3) : d a header date}
A 'period' with two published keys (13-15 Nov: 20 and 16 columns) contributes both keys.
Primary partition: R_page.  Alternatives: R_lag minus R_page.  A multi-part message (entries
sharing page and heading) is ONE unit: all its parts take the same key.
Output: results/adfgvx-clusters.md, results/adfgvx-clusters.csv
"""
import datetime
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from headers import parse, page_date  # noqa: E402
import periods  # noqa: E402

# Corrections to creilly's header OCR, from a reading of the scan by another chat. Source named.
CALL_OVERRIDES = {"p076A": ({"POT", "NKJ"}, "lit-adfgvx literature/adfgvx.md s.3, read from the scan "
                            "(PDF p.76): 'A) POT v NKJ (2.33 a.m., November 8th)'; creilly OCR 'Et v NKJ'")}
# Net indicator (the RICHI / CHI / RIZI line under a heading). It is NOT in creilly's records.json
# 'header' field; known only where named here.
NET = {
    "p179B1": ("RICHI", "creilly data/messages.json part_label '1 TL RICHI-240'"),
    "p156C3": ("(RI)CHI", "creilly data/messages.json part_label '5 TL (RI)CHI-132'"),
    "p156C6": ("(RI)CHI", "creilly data/messages.json part_label '6 TL (RI)CHI-108'"),
    "p076A": ("RICHI", "lit-adfgvx s.3, scan PDF p.76: 'RICHI-178'"),
    "p173A": ("RICHI", "lit-adfgvx s.3, scan PDF p.173: 'RICHI-' + unreadable handwritten count"),
    "p201D": ("CHI", "lit-adfgvx s.3, scan PDF p.201: 'CHI-170'"),
    "p201A": ("RICHI", "lit-adfgvx s.3, scan PDF p.201: 'RICHI-244 (IWE v KI)'"),
    "p201E": ("RIZI", "lit-adfgvx s.3, scan PDF p.201: three RIZI messages CM/SY v CZ on the page; "
              "this is the unsolved one (identification by call signs and status, ours)"),
}
from provenance import header as prov_header  # noqa: E402

LASRY = ["sep19", "oct04", "oct28", "nov01", "nov04", "nov07", "nov10", "nov13_20", "nov13_16",
         "nov16", "nov19", "nov22", "nov25", "nov28"]
MON = {"Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
LETTERS = set("ADFGVX")
ALIAS = {"Z0N": "ZON", "20N": "ZON", "UXS": "UKS", "LF": "LP", "UP": "LP", "VLP": "LP",
         "XYZ": "XYZ", "KQW": "KOW", "POT": "POT"}


def period_of(s):
    m = re.match(r"(\w{3}) (\d+)-(?:(\w{3}) )?(\d+)", s)
    a = datetime.date(1918, MON[m.group(1)], int(m.group(2)))
    b = datetime.date(1918, MON[m.group(3) or m.group(1)], int(m.group(4)))
    return a, b


def norm_call(c):
    if not c:
        return None
    s = re.sub(r"[^A-Za-z0-9]", "", c).upper()
    if not s or set(s) <= {"-"}:
        return None
    return ALIAS.get(s, s)


def calls_of(h):
    out = set()
    for f in (h["calls_from"], h["calls_to"]):
        if not f:
            continue
        for part in re.split(r"[,\s()]+", f):
            if part.upper() in ("FUER", "FUR"):
                continue
            n = norm_call(part)
            if n and len(n) >= 2 and not n.isdigit():
                out.add(n)
    return out


class Schedule:
    def __init__(self, keys):
        self.per = {k["id"]: period_of(k["period"]) for k in keys if k["id"] in LASRY}

    def keys_on(self, d):
        if d is None:
            return set()
        return {k for k, (a, b) in self.per.items() if a <= d <= b}

    def label(self, d):
        ks = self.keys_on(d)
        if ks:
            return "+".join(sorted(ks, key=LASRY.index))
        return f"no-known-key({d.isoformat()})" if d else "no-date"


def candidates(sched, pdate, hdates, rule):
    one = datetime.timedelta(days=1)
    c = set()
    if rule in ("R_page", "R_lag", "R_lag3"):
        c |= sched.keys_on(pdate)
    if rule in ("R_hdr", "R_lag", "R_lag3"):
        for d in hdates:
            c |= sched.keys_on(d)
    if rule in ("R_lag", "R_lag3"):
        if pdate:
            c |= sched.keys_on(pdate - one)
        for d in hdates:
            c |= sched.keys_on(d - one)
    if rule == "R_lag3":
        for d in hdates:
            c |= sched.keys_on(d - 2 * one) | sched.keys_on(d - 3 * one)
    return c


def main():
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    keys = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.keys.json")))
    sched = Schedule(keys)
    for e in rec:
        e["_pd"] = page_date(e["date"])
        e["_h"] = parse(e["header"], e["_pd"])
        e["_calls"] = calls_of(e["_h"])
        e["_unit"] = (e["childs_page"], e["header"])
        if e["id"] in CALL_OVERRIDES:
            e["_calls"] = set(CALL_OVERRIDES[e["id"]][0])
    L = []
    W = L.append
    W("# ADFGVX 1918: header clustering of the unread entries\n")
    W(prov_header("", "search/adfgvx/clusters.py" + (" --scan" if SCANMODE else ""),
                  "transcription: unread = SCAN transcription units (search/adfgvx/scan.py; heading, "
                  "heading date, page date and net as read from the page); solved (calibration) = "
                  "creilly @ e60da03" if SCANMODE else
                  "transcription: creilly11235/adfgvx-1918 @ e60da03 (headings: creilly's OCR)"))
    W("Header evidence only (page date, heading date/time/call signs, multi-part structure, the "
      "published key schedule). No ciphertext symbol is read to form a group; lengths are "
      "reported for the lead's planning only. Rules and their calibration are in the docstring "
      "of `search/adfgvx/clusters.py` and in section 1.\n")

    # ---- 1. calibration on solved
    sol = [e for e in rec if e["status"].startswith("Solved") and e["key"] in LASRY]
    W("## 1. Calibration: how well does header evidence predict the key of a SOLVED entry?\n")
    W(f"{len(sol)} solved entries under one of Lasry's 14 period keys. For each rule: coverage = "
      f"share whose true key is in the candidate set; mean set size; exact = set is exactly the "
      f"true key.\n")
    W("| rule | coverage | mean candidate keys | exact (single, correct) |")
    W("|---|---|---|---|")
    cal = {}
    for rule in ("R_page", "R_hdr", "R_lag", "R_lag3"):
        cov = sz = ex = 0
        miss = []
        for e in sol:
            c = candidates(sched, e["_pd"], e["_h"]["dates"], rule)
            cov += e["key"] in c
            sz += len(c)
            ex += c == {e["key"]}
            if e["key"] not in c:
                miss.append(e)
        cal[rule] = miss
        W(f"| {rule} | {cov}/{len(sol)} ({100*cov/len(sol):.1f}%) | {sz/len(sol):.2f} | "
          f"{ex} ({100*ex/len(sol):.1f}%) |")
    W("\nThe 13-15 Nov period has two published keys, so every rule gives two candidates there; "
      "'exact' is impossible for those entries by construction.\n")
    W("Header date minus page date, solved entries with one header date (days):\n")
    off = Counter()
    for e in sol:
        if e["_pd"] and len(e["_h"]["dates"]) == 1:
            off[(next(iter(e["_h"]["dates"])) - e["_pd"]).days] += 1
    W("| offset | " + " | ".join(str(k) for k in sorted(off)) + " |")
    W("|---" * (len(off) + 1) + "|")
    W("| entries | " + " | ".join(str(off[k]) for k in sorted(off)) + " |")
    W(f"\nEntries the widest rule (R_lag3) still misses: "
      f"{', '.join(e['id'] + ' (' + e['key'] + ', page ' + str(e['_pd']) + ', heading ' + repr(e['header']) + ')' for e in cal['R_lag3'])}.\n")
    # multi-part consistency
    units = defaultdict(list)
    for e in rec:
        units[e["_unit"]].append(e)
    mp = [u for u in units.values() if len(u) > 1]
    mp_s = [u for u in mp if all(e["status"].startswith("Solved") and e["key"] for e in u)]
    same = sum(1 for u in mp_s if len({e["key"] for e in u}) == 1)
    W(f"Multi-part messages (entries sharing page and heading): {len(mp)}. Of the {len(mp_s)} "
      f"whose parts are all solved, {same} have every part under one key.\n")
    diff = [u for u in mp_s if len({e['key'] for e in u}) > 1]
    for u in diff:
        W(f"- parts under different keys: " + ", ".join(f"{e['id']}={e['key']}" for e in u))
    # 13-15 Nov: which key by call sign
    W("\n13-15 Nov, the two published keys by call sign (solved entries):\n")
    cc = defaultdict(Counter)
    for e in sol:
        if e["key"] in ("nov13_20", "nov13_16"):
            for c in sorted(e["_calls"]) or ["(none)"]:
                cc[c][e["key"]] += 1
    W("| call sign | nov13_20 | nov13_16 |")
    W("|---|---|---|")
    for c in sorted(cc, key=lambda c: -sum(cc[c].values())):
        W(f"| {c} | {cc[c]['nov13_20']} | {cc[c]['nov13_16']} |")

    # ---- 1b. key periods derived from the solved entries
    per = periods.derive(sol)
    W("\n## 1b. Key periods derived from the SOLVED entries (the cluster unit)\n")
    W(f"For each of Lasry's 14 period keys, when it was actually seen: the range of log-page "
      f"dates and of heading dates of the solved entries read under it, after setting aside "
      f"outliers more than {periods.OUT_DAYS} days from the key's median (listed). First and "
      f"last use are by heading date and time. Source: creilly @ e60da03 records.json (status "
      f"and key per entry; heading OCR parsed by search/adfgvx/headers.py).\n")
    W("| key | published | solved entries | page dates | heading dates | first use (heading) | last use (heading) | outliers (page) | outliers (heading) |")
    W("|---|---|---|---|---|---|---|---|---|")
    fmt_t = lambda t: f"{t[0]:02d}:{t[1]:02d}" if t else "--:--"
    for k in LASRY:
        r = per.get(k)
        if not r:
            continue
        a, b = sched.per[k]
        W(f"| {k} | {a:%d %b}-{b:%d %b} | {r['n']} | "
          f"{r['page'][0]:%d %b}-{r['page'][1]:%d %b} | {r['hdr'][0]:%d %b}-{r['hdr'][1]:%d %b} | "
          f"{r['first'][0]:%d %b} {fmt_t(r['first'][1])} ({r['first'][2]}) | "
          f"{r['last'][0]:%d %b} {fmt_t(r['last'][1])} ({r['last'][2]}) | "
          f"{', '.join(r['out_page']) or '-'} | {', '.join(r['out_hdr']) or '-'} |")
    W("\nBoundaries between consecutive keys (13-15 Nov's two keys are one period):\n")
    W("| from | to | last page date of 'from' | first page date of 'to' | page overlap | last heading of 'from' | first heading of 'to' | heading overlap |")
    W("|---|---|---|---|---|---|---|---|")
    seq = [k for k in LASRY if k in per and k != "nov13_16"]
    for x, y in zip(seq, seq[1:]):
        if x == "nov13_20":
            pass
        rx, ry = per[x], per[y]
        po = (rx["page"][1] - ry["page"][0]).days + 1
        ho = (rx["hdr"][1] - ry["hdr"][0]).days + 1
        W(f"| {x} | {y} | {rx['page'][1]:%d %b} | {ry['page'][0]:%d %b} | "
          f"{max(po, 0)} day(s) | {rx['last'][0]:%d %b} {fmt_t(rx['last'][1])} | "
          f"{ry['first'][0]:%d %b} {fmt_t(ry['first'][1])} | {max(ho, 0)} day(s) |")
    W("\nKeys outside the 14 with solved traffic, single net or single message: "
      + "; ".join(f"{k}: " + ", ".join(f"{e['id']} (page {e['_pd']}, heading {','.join(map(str, sorted(e['_h']['dates'])))})"
                                      for e in rec if e["key"] == k)
                  for k in ("chi_2017_comments", "dec09_history", "ours_nov07_18col"))
      + ". They are net-specific (CHI, a December keyword, creilly's p.153 key) and are not used "
        "as periods; an entry on a CHI net is a candidate for them by net, not by date.\n")
    # leave-one-out calibration of the derived rule
    loo = Counter()
    for e in sol:
        pe = periods.derive(sol, exclude_id=e["id"])
        c, basis = periods.assign(pe, e["_pd"], e["_h"]["dates"])
        loo["n"] += 1
        loo["covered"] += e["key"] in c
        loo["single_correct"] += c == {e["key"]}
        loo["ambiguous"] += len(c) > 1
        loo["none"] += not c
        loo["size"] += len(c)
    W(f"Calibration of the derived rule, leave-one-out over the {loo['n']} solved entries (each "
      f"entry's own date removed before its key's range is derived): true key among the "
      f"candidates {loo['covered']} ({100*loo['covered']/loo['n']:.1f}%); exactly the true key "
      f"{loo['single_correct']} ({100*loo['single_correct']/loo['n']:.1f}%); ambiguous "
      f"{loo['ambiguous']} ({100*loo['ambiguous']/loo['n']:.1f}%; includes every 13-15 Nov "
      f"entry, whose two keys share a period); no candidate {loo['none']}; mean "
      f"{loo['size']/loo['n']:.2f} candidates.\n")

    # ---- 1c. header-date error rate
    W("## 1c. Header-date error rate on the solved set (sets the wrong-day intruder rate)\n")
    W("How often a solved entry's HEADING date lies outside its actual key's period. Two "
      "definitions of the period: the published one (Lasry et al., keys.json) and the derived "
      "one (section 1b, leave-one-out heading range). Entries with no single parsed heading date "
      "are counted separately. The same for the log PAGE date, for comparison.\n")
    def err_table(datefn, name):
        rows_ = Counter()
        mags = Counter()
        for e in sol:
            ds = datefn(e)
            if ds is None:
                rows_["no date"] += 1
                continue
            a, b = sched.per[e["key"]]
            pe = periods.derive(sol, exclude_id=e["id"]).get(e["key"], {})
            inpub = any(a <= d <= b for d in ds)
            rng_ = pe.get("hdr" if name == "heading" else "page")
            inder = rng_ is not None and any(rng_[0] <= d <= rng_[1] for d in ds)
            rows_["n"] += 1
            rows_["out_pub"] += not inpub
            rows_["out_der"] += not inder
            if not inpub:
                d = min(ds)
                off = (d - b).days if d > b else (d - a).days
                mags[off] += 1
        return rows_, mags
    hdr_err, hdr_mag = err_table(lambda e: e["_h"]["dates"] if len(e["_h"]["dates"]) == 1 else None, "heading")
    pg_err, pg_mag = err_table(lambda e: {e["_pd"]} if e["_pd"] else None, "page")
    W("| date used | entries with the date | outside published period | outside derived (LOO) range | no usable date |")
    W("|---|---|---|---|---|")
    for nm, r in (("heading date", hdr_err), ("page date", pg_err)):
        W(f"| {nm} | {r['n']} | {r['out_pub']} ({100*r['out_pub']/r['n']:.1f}%) | "
          f"{r['out_der']} ({100*r['out_der']/r['n']:.1f}%) | {r['no date']} |")
    W("\nHeading dates outside the published period, by days past its end (+) or before its "
      "start (-):\n")
    W("| days | " + " | ".join(f"{k:+d}" for k in sorted(hdr_mag)) + " |")
    W("|---" * (len(hdr_mag) + 1) + "|")
    W("| entries | " + " | ".join(str(hdr_mag[k]) for k in sorted(hdr_mag)) + " |")
    W(f"\nRead: a solved entry's heading date falls outside its key's published period "
      f"{100*hdr_err['out_pub']/hdr_err['n']:.1f}% of the time, almost always AFTER it "
      f"(a key stayed in use after its nominal end, or the heading gives the intercept time of "
      f"a message enciphered earlier). Against the observed (derived) ranges it is "
      f"{100*hdr_err['out_der']/hdr_err['n']:.1f}%. These are the two candidate wrong-day "
      f"intruder rates for the power tests; the page date's rates are lower.\n")

    # ---- network evidence
    period_calls = Counter()
    other_calls = Counter()
    for e in rec:
        if e["status"].startswith("Solved") and e["key"] in LASRY:
            period_calls.update(e["_calls"])
        elif e["status"].startswith("Solved") and e["key"]:
            other_calls.update(e["_calls"])

    # ---- 2. the unread entries
    if SCANMODE:
        un = scan_records()
    else:
        un = [e for e in rec if e["status"] == "Unsolved"]
    W(f"\n## 2. The unread entries ({len(un)} with status 'Unsolved')\n")
    W("Per entry: page date, heading date(s) and time, call signs (normalised; aliases "
      f"{ALIAS}), the R_page key (primary), the R_lag alternatives, and whether any of its call "
      "signs ever occurs in solved period-key traffic ('net: yes/no'). 'flag' marks a heading "
      "date that is not the page date or the next day (the solved entries' usual offsets, "
      "section 1), an unreadable heading date, or an OCR-ambiguous day.\n")
    rows = []
    for e in un:
        h = e["_h"]
        pdate = e["_pd"]
        prim = candidates(sched, pdate, set(), "R_page")
        lag = candidates(sched, pdate, h["dates"], "R_lag") - prim
        lag3 = candidates(sched, pdate, h["dates"], "R_lag3") - prim - lag
        hd = sorted(h["dates"])
        flags = []
        if not hd:
            flags.append("no heading date")
        elif pdate and any((d - pdate).days not in (0, 1) for d in hd):
            flags.append("heading/page offset " + "/".join(f"{(d - pdate).days:+d}" for d in hd))
        if len(hd) > 1:
            flags.append("OCR day ambiguous")
        flags += [n for n in h["date_note"] if n not in ("no header date",) and "ambiguous" not in n]
        net = any(c in period_calls for c in e["_calls"])
        dc, dbasis = periods.assign(per, pdate, h["dates"])
        dlabel = periods.label(per, dc, pdate)
        if SCANMODE and e["_net"][0] == "CHI":
            # net is a clustering variable: CHI traffic is read only under CHI keys (p.187,
            # chi_2017_comments), never under a period key; RIZI is read under nov13_16 in the
            # scan's calibration set, so RIZI stays with the period groups
            dc, dbasis, dlabel = set(), "net CHI", "CHI net (no period key; date candidates: " + dlabel + ")"
        pr = e["printed"] or ""
        rows.append({
            "id": e["id"], "childs_page": e["childs_page"], "page_date": str(pdate) if pdate else "?",
            "heading": e["header"], "heading_dates": ",".join(map(str, hd)),
            "time": f"{h['time'][0]:02d}:{h['time'][1]:02d}" if h["time"] else "",
            "calls": " ".join(sorted(e["_calls"])), "part": e["part"],
            "unit": f"p{e['childs_page']}|{e['header']}",
            "primary": "+".join(sorted(prim, key=LASRY.index)) or sched.label(pdate),
            "alt_lag": "+".join(sorted(lag, key=LASRY.index)),
            "alt_lag3": "+".join(sorted(lag3, key=LASRY.index)),
            "derived_period": dlabel, "derived_basis": dbasis,
            "derived_candidates": "+".join(sorted(dc, key=LASRY.index)),
            "net": e["_net"][0] if SCANMODE else NET.get(e["id"], ("unknown", "indicator line not in creilly's transcription"))[0],
            "net_source": e["_net"][1] if SCANMODE else NET.get(e["id"], ("unknown", "indicator line not in creilly's transcription"))[1],
            "net_known": net, "flags": "; ".join(flags),
            "n_slots": len(pr), "n_letters": sum(c in LETTERS for c in pr),
            "n_lost": pr.count("-"), "count_in_log": e["count_in_log"],
        })
    import csv
    with open(os.path.join(ROOT, "results", f"adfgvx-clusters{SUFFIX}.csv"), "w", newline="") as f:
        for l in prov_header("#", "search/adfgvx/clusters.py" + (" --scan" if SCANMODE else "")).splitlines():
            f.write(l + "\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- 3. groups
    W("## 3. Groups: one per key period derived from the solved entries (section 1b)\n")
    W("Each unread entry is assigned by the derived rule (page-date range and heading-date range "
      "of each key, intersected where both apply). An entry the rule cannot place in one period "
      "is grouped as 'ambiguous between X and Y' or 'gap between X and Y'. The published-period "
      "rule (R_page) and its R_lag alternatives are kept as columns.\n")
    groups = defaultdict(list)
    for r in rows:
        groups[r["derived_period"]].append(r)

    def gkey(g):
        rs = groups[g]
        return min(r["page_date"] for r in rs)
    unit_rows = defaultdict(list)
    for r in rows:
        unit_rows[r["unit"]].append(r)
    for g in sorted(groups, key=gkey):
        rs = sorted(groups[g], key=lambda r: (r["childs_page"], r["id"]))
        tl = sum(r["n_letters"] for r in rs)
        us = {r["unit"] for r in rs}
        movable = [u for u in us if unit_rows[u][0]["alt_lag"]]
        W(f"\n### {g}: {len(rs)} entries, {len(us)} messages, {tl} cipher letters "
          f"({sum(r['n_lost'] for r in rs)} lost marks)\n")
        if g in sched.per:
            a, b = sched.per[g]
            W(f"Published period {a:%d %b}-{b:%d %b}. ")
        elif g.startswith("ambiguous") and set(g.split()[2::2]) == {"nov13_20", "nov13_16"}:
            W("Two published keys share this period (20 and 16 columns); the group is the union of "
              "two candidate key-groups, and which entry takes which key is open. ")
        elif g.startswith("ambiguous"):
            W("The derived rule cannot separate these keys for these entries. ")
        elif g.startswith("gap"):
            W("No solved entry under any of the 14 keys has a page or heading date here. ")
        else:
            W("No published key covers this date. ")
        W(f"Messages with an R_lag alternative (could belong to another group): {len(movable)} of "
          f"{len(us)}; alternative assignments for this group's messages: "
          f"{prod([1 + len(unit_rows[u][0]['alt_lag'].split('+')) if unit_rows[u][0]['alt_lag'] else 1 for u in us])}.\n")
        W("| id | page | page date | heading date | time | calls | net | part | letters | lost | header count | R_page | R_lag alt | calls seen in period traffic | flags |")
        W("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in rs:
            W(f"| {r['id']} | {r['childs_page']} | {r['page_date']} | {r['heading_dates']} | "
              f"{r['time']} | {r['calls']} | {r['net']} | {r['part'] if r['part'] is not None else ''} | "
              f"{r['n_letters']} | {r['n_lost']} | {r['count_in_log'] if r['count_in_log'] is not None else ''} | "
              f"{r['primary']} | {r['alt_lag']} | {'yes' if r['net_known'] else 'NO'} | {r['flags']} |")

    # ---- 4. partitions count
    W("\n## 4. How many partitions are plausible?\n")
    units = {}
    for r in rows:
        units[r["unit"]] = r
    n_units = len(units)
    sizes_lag = []
    sizes_lag3 = []
    for u, r in units.items():
        prim = [x for x in r["primary"].split("+") if x in LASRY]
        p = len(prim) if prim else 1
        a = len(r["alt_lag"].split("+")) if r["alt_lag"] else 0
        a3 = len(r["alt_lag3"].split("+")) if r["alt_lag3"] else 0
        sizes_lag.append(p + a)
        sizes_lag3.append(p + a + a3)
    from math import log10
    W(f"Units (messages; parts of one message move together): {n_units}.\n")
    W("| rule | messages with >1 candidate key | partitions (product of candidate counts) | log10 | with an 'off-list key' option per message (x(c+1)) |")
    W("|---|---|---|---|---|")
    sizes_der = [len(u["derived_candidates"].split("+")) if u["derived_candidates"] else 1 for u in units.values()]
    for name, sz in (("derived (section 1b)", sizes_der), ("R_page (13-15 Nov counts 2)", [len([x for x in u['primary'].split('+') if x in LASRY]) or 1 for u in units.values()]),
                     ("R_lag", sizes_lag), ("R_lag3", sizes_lag3)):
        P = prod(sz)
        P8 = prod([s + 1 for s in sz])
        W(f"| {name} | {sum(1 for s in sz if s > 1)} | {P} | {log10(P):.1f} | 10^{log10(P8):.1f} |")
    W("\nEvery partition is a trial for the joint attack (referee A4): the prereg should fix one "
      "rule from this table, and the trials factor should carry its partition count.\n")

    # ---- 5. page/heading disagreements
    W("## 5. Page date against heading date (all unread entries flagged)\n")
    W("| id | page | page date | heading | heading date(s) | flag |")
    W("|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (r["childs_page"], r["id"])):
        if r["flags"]:
            W(f"| {r['id']} | {r['childs_page']} | {r['page_date']} | `{r['heading']}` | "
              f"{r['heading_dates']} | {r['flags']} |")
    W("\n## 6. Call signs of the unread entries never seen in solved period-key traffic\n")
    nn = Counter()
    for e in un:
        for c in e["_calls"]:
            if c not in period_calls:
                nn[c] += 1
    W("| call sign | unread entries | solved entries under a non-period key |")
    W("|---|---|---|")
    for c, n in nn.most_common():
        W(f"| {c} | {n} | {other_calls.get(c, 0)} |")
    W("\nAn entry whose call signs are all outside period-key traffic is the profile of a "
      "different key net (0wwafa's E8; e.g. p.153 FKR v CGH read under a new 18-column key). "
      "Such entries are kept in their date group above, marked 'net: NO'.\n")
    W("\n## 7b. Net indicator per unread entry\n")
    W("The line under each heading (RICHI-n, CHI-n, RIZI-n) names the net. It is not part of "
      "creilly's `header` field. Known values and their sources:\n")
    W("| id | net | source |")
    W("|---|---|---|")
    for r in rows:
        if r["net"] != "unknown":
            W(f"| {r['id']} | {r['net']} | {r['net_source']} |")
    W(f"\nThe other {sum(1 for r in rows if r['net'] == 'unknown')} unread entries: unknown. "
      "Reading the indicator from the scan for each of them is a transcription job, not done "
      "here. Call-sign overrides applied: " + "; ".join(f"{k}: {v[1]}" for k, v in CALL_OVERRIDES.items()) + ".\n")
    W("\n## 8. Where Schmeh's nine open messages fall\n")
    W("Mapping from results/adfgvx-transcription-diff.md (our own matching). Status is creilly's.\n")
    W("| Schmeh | log id | creilly status | page date | heading date | primary (R_page) | R_lag alternatives |")
    W("|---|---|---|---|---|---|---|")
    by = {e["id"]: e for e in rec}
    for lab, i in SCHMEH9:
        e = by[i]
        pd_ = e["_pd"]
        prim = candidates(sched, pd_, set(), "R_page")
        lag = candidates(sched, pd_, e["_h"]["dates"], "R_lag") - prim
        W(f"| {lab} | {i} | {e['status']} | {pd_} | {','.join(map(str, sorted(e['_h']['dates'])))} | "
          f"{'+'.join(sorted(prim, key=LASRY.index)) or sched.label(pd_)} | "
          f"{'+'.join(sorted(lag, key=LASRY.index))} |")
    # partial / duplicates for completeness
    W("## 7. Not in the unread pool, listed for completeness\n")
    for e in rec:
        if e["status"] in ("Partially solved", "Duplicate entry", "No cipher text"):
            W(f"- {e['id']} (p.{e['childs_page']}, {e['status']}, key {e['key']}): `{e['header']}`")
    # ---- summary first (computed; inserted after the provenance block)
    S = []
    S.append("## Summary\n")
    nsingle = sum(1 for g in groups if not g.startswith(("ambiguous", "gap")))
    namb = sum(len(groups[g]) for g in groups if g.startswith("ambiguous"))
    S.append(f"- **Unit = key period derived from the solved entries** (section 1b). {len(un)} unread "
             f"entries ({n_units} messages) fall into {nsingle} single-key periods and "
             f"{len(groups) - nsingle} ambiguous groups; {namb} entries are 'ambiguous between' "
             f"keys (every 13-15 Nov entry among them, since two keys share that period). "
             f"Leave-one-out on the solved entries, the derived rule contains the true key "
             f"{100*loo['covered']/loo['n']:.1f}% of the time (exactly it {100*loo['single_correct']/loo['n']:.1f}%).")
    S.append(f"- **Header-date error rate** (section 1c): a solved entry's heading date lies outside "
             f"its key's PUBLISHED period {hdr_err['out_pub']}/{hdr_err['n']} = "
             f"{100*hdr_err['out_pub']/hdr_err['n']:.1f}%, nearly always 1-3 days after it; outside "
             f"the DERIVED range {100*hdr_err['out_der']/hdr_err['n']:.1f}%. Page date: "
             f"{100*pg_err['out_pub']/pg_err['n']:.1f}% / {100*pg_err['out_der']/pg_err['n']:.1f}%.")
    big = sorted(groups, key=lambda g: -sum(r["n_letters"] for r in groups[g]))[:4]
    S.append("- Largest groups (cipher letters, entries): " + "; ".join(
        f"{g} {sum(r['n_letters'] for r in groups[g])} ({len(groups[g])})" for g in big) + ".")
    S.append(f"- Plausible partitions of the {n_units} messages: {prod(sizes_der)} "
             f"(10^{log10(prod(sizes_der)):.1f}) under the derived rule; "
             f"{prod([len([x for x in u['primary'].split('+') if x in LASRY]) or 1 for u in units.values()])} under R_page "
             f"(published periods; only the two 13-15 Nov keys open); 10^{log10(prod(sizes_lag)):.1f} under R_lag; "
             f"10^{log10(prod(sizes_lag3)):.1f} under R_lag3; before any off-list key (E8) option.")
    if SCANMODE:
        S.append("- Net per unit (scan label line): " + ", ".join(f"{k} {v}" for k, v in
                 Counter(r["net"] for r in rows).most_common()) + ". CHI units form their own "
                 "group (CHI is read only under CHI keys); RIZI units stay in the period groups "
                 "(the scan's calibration set reads RIZI under nov13_16). Unit changes against "
                 f"creilly's ids: {scan_records.changes}.")
    else:
        S.append(f"- Net indicator (RICHI/CHI/RIZI) is known for {sum(1 for r in rows if r['net'] != 'unknown')} "
                 f"of the {len(rows)} unread entries only: it is not in creilly's transcription. p201D "
                 f"(Childs p.198) is CHI, per lit-adfgvx's reading of the scan.")
    nflag = sum(1 for r in rows if r["flags"])
    S.append(f"- {nflag} entries carry a date flag (section 5). Page 73 (p076A, POT v NKJ per the "
             f"scan) is filed under 26 Oct, in the gap between oct04 and oct28 where no solved "
             f"entry exists, and headed 8 Nov: the derived rule places it in nov07 on its heading "
             f"date alone.")
    S.append(f"- {sum(1 for r in rows if not r['net_known'])} entries have no call sign ever seen "
             f"in solved period-key traffic (section 6).")
    S.append("- Multi-part messages were treated as one unit; on the solved entries every "
             f"multi-part message ({same}/{len(mp_s)}) has all its parts under one key.\n")
    cut = next(i for i, l in enumerate(L) if l.startswith("Header evidence only"))
    L[cut + 1:cut + 1] = S
    open(os.path.join(ROOT, "results", f"adfgvx-clusters{SUFFIX}.md"), "w").write("\n".join(L) + "\n")


SCHMEH9 = [("Page 73", "p076A"), ("Page 152", "p155E"), ("Page 153 (VFVAX)", "p156C3"),
           ("Page 153 (AXVAA)", "p156C6"), ("Page 158", "p161D"), ("Page 170", "p173A"),
           ("Page 176 (GGDAA)", "p179B1"), ("Page 189", "p192A"), ("Page 198", "p201D")]


SCANMODE = "--scan" in sys.argv
SUFFIX = "-scan" if SCANMODE else ""


def scan_records():
    """Unread side from the scan transcription's units, shaped like records.json entries."""
    import scan
    us, changes = scan.units()
    out = []
    for u in us:
        d, m = u["page_date"]
        pdate = datetime.date(1918, m, d)
        h = parse(u["heading"], pdate)
        if u["heading_date"]:
            hd, hm = u["heading_date"]
            h["dates"] = {datetime.date(1918, hm, hd)}   # the scan's reading of the heading date
            h["date_note"] = [n for n in h["date_note"] if "date" not in n]
        out.append({"id": u["unit"], "childs_page": u["childs_page"], "header": u["heading"],
                    "part": None, "count_in_log": u["header_count"], "printed": u["primary"],
                    "status": "Unsolved", "_pd": pdate, "_h": h, "_calls": calls_of(h),
                    "_unit": (u["childs_page"], u["heading"]),
                    "_net": (u["net"] or "none printed", "scan transcription label line")})
    scan_records.changes = changes
    return out


def prod(xs):
    p = 1
    for x in xs:
        p *= x
    return p


if __name__ == "__main__":
    main()
