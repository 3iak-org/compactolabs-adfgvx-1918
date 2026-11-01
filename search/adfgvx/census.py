"""Mutilation census of the solved ADFGVX 1918 log entries, and the survivorship comparison.

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/census.py

For every entry with a key and a plaintext:
  T = encrypt(plaintext, key)       reference ciphertext ('*' where the plaintext character is
                                    unknown: '-', '?', '#', '_' or any non-square character)
  O = the log symbols as printed    ('-' = slot the log shows as lost)
and the minimal edit script O <- T is computed (align.py), with the type breakdown's range over
every optimal alignment.  Edit vocabulary (0wwafa PAPER.md section 3, used as vocabulary only):
  E1 symbols dropped          a run of consecutive deletions whose length is not a multiple of 5
  E2 symbols inserted         a run of consecutive insertions, length not a multiple of 5
  E3 group dropped/duplicated a deletion/insertion run whose length is a multiple of 5
  E4 unreadable mark '-'      a '-' slot against a known symbol (free: position known)
  E5 wrong symbol             substitution
  E6 clerk: 3 symbols for 1   tested separately: does ONE insertion/deletion in the interim text
                              (before transposition) explain O better than the ciphertext edits?
  E7 wrong day, E8 key not in list: not visible in this census (it is conditional on the key).
Outputs: results/adfgvx-mutilation.csv, results/adfgvx-mutilation.tables.md
"""
import ctypes
import json
import math
import os
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from align import align, events, plain_pair  # noqa: E402
from engine import substitute, transpose, decrypt, check_key  # noqa: E402
from provenance import header as prov_header  # noqa: E402

CT = os.path.join(ROOT, "ciphertexts")
RES = os.path.join(ROOT, "results")
LETTERS = set("ADFGVX")


def edcost_lib():
    tmp = os.environ.get("TMPDIR", "/tmp")
    so = os.path.join(tmp, "adfgvx-edcost.so")
    src = os.path.join(HERE, "edcost.c")
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
        subprocess.check_call(["cc", "-O2", "-shared", "-fPIC", "-o", so, src])
    lib = ctypes.CDLL(so)
    lib.edcost.restype = ctypes.c_int
    lib.edcost.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    return lambda T, O: lib.edcost(T.encode(), len(T), O.encode(), len(O))


def lost_pair(t, o):
    """Both sides observed: '-' on either side is free, else unit substitution."""
    if t == "-" or o == "-":
        return 0, "lost"
    return (0, "match") if t == o else (1, "sub")


def method_class(e):
    m = e["method"]
    if m == "period key, as transcribed":
        return "A_as_transcribed"
    if m == "period key, length repaired":
        return "B_length_repaired"
    if m.startswith("known key reading"):
        return "C_page_reread"
    return "D_other"


def in_census(e):
    return bool(e["key"]) and bool(e["plaintext"]) and e["status"].startswith("Solved")


def classify_events(ev, O):
    out = Counter()
    sym = Counter()
    det = []
    for ty, L, i, j in ev:
        if ty == "sub":
            k = "E5"
        elif ty == "lost":
            k = "E4"
        elif ty == "del":
            k = "E3" if L % 5 == 0 else "E1"
        else:
            k = "E3" if L % 5 == 0 else "E2"
            if k == "E3" and j >= L and O[j - L:j] == O[j:j + L]:
                k = "E3"  # duplicated group (insertion equal to the preceding L symbols)
        out[k] += 1
        sym[k] += L
        det.append(f"{k}:{ty}{L}@T{i}/O{j}")
    return out, sym, det


def e6_test(pt, sq, tr, O, ed):
    """Best cost if ONE interim symbol is inserted ('*') or deleted before transposition."""
    I = substitute(pt, sq)
    best = None
    for p in range(len(I) + 1):
        c = ed(transpose(I[:p] + "*" + I[p:], tr), O)
        if best is None or c < best[0]:
            best = (c, "ins", p)
    for p in range(len(I)):
        c = ed(transpose(I[:p] + I[p + 1:], tr), O)
        if c < best[0]:
            best = (c, "del", p)
    return best


def quant(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * q
    f = math.floor(k)
    c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def fisher_two_sided(a, b, c, d):
    """2x2 table [[a,b],[c,d]]; two-sided exact p (sum of tables no more probable)."""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2

    def p(x):
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)
    p0 = p(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 * (1 + 1e-9)))


def mann_whitney_p(x, y):
    """Two-sided normal-approximation Mann-Whitney U with tie correction."""
    allv = sorted([(v, 0) for v in x] + [(v, 1) for v in y])
    ranks = {}
    i = 0
    n = len(allv)
    tie = 0.0
    R = [0.0, 0.0]
    while i < n:
        j = i
        while j < n and allv[j][0] == allv[i][0]:
            j += 1
        r = (i + j + 1) / 2
        t = j - i
        tie += t ** 3 - t
        for k in range(i, j):
            R[allv[k][1]] += r
        i = j
    n1, n2 = len(x), len(y)
    U = R[0] - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    s2 = n1 * n2 / 12 * ((n + 1) - tie / (n * (n - 1)))
    z = (U - mu) / math.sqrt(s2) if s2 > 0 else 0.0
    return U, z, math.erfc(abs(z) / math.sqrt(2))


def main():
    rec = json.load(open(os.path.join(CT, "adfgvx-1918-log.records.json")))
    keys = {k["id"]: k for k in json.load(open(os.path.join(CT, "adfgvx-1918-log.keys.json")))}
    for k in keys.values():
        check_key(k["square"], k["transposition"])
    ed = edcost_lib()
    rows = []
    for e in rec:
        if not in_census(e):
            continue
        k = keys[e["key"]]
        sq, tr = k["square"], k["transposition"]
        pt = e["plaintext"]
        O = e["printed"]
        T = transpose(substitute(pt, sq), tr)
        fast = len(T) == len(O) and all(t == "*" or o == "-" or t == o for t, o in zip(T, O))
        if fast:
            ops = [("wild" if t == "*" else "lost" if o == "-" else "match", i, i)
                   for i, (t, o) in enumerate(zip(T, O))]
            nl = sum(1 for t, o in zip(T, O) if o == "-" and t != "*")
            nw = T.count("*")
            a = {"cost": 0, "ops": ops, "n_optimal": 1,
                 "ranges": {"sub": (0, 0), "del": (0, 0), "ins": (0, 0),
                            "lost": (nl, nl), "wild": (nw, nw)}}
        else:
            a = align(T, O)
            assert ed(T, O) == a["cost"], (e["id"], ed(T, O), a["cost"])
        ev = events(a["ops"])
        ecnt, esym, det = classify_events(ev, O)
        e6 = None
        if a["cost"] >= 2:
            e6 = e6_test(pt, sq, tr, O, ed)
        nlet = sum(c in LETTERS for c in O)
        rx = tx = None
        page = (e["ciphertext"] or "").replace(" ", "").replace("?", "-")
        if page and page != O:
            rx = ed(T, page)                      # reception: true vs page reading
            tx = align(page, O, lost_pair)["cost"]  # transcription: page reading vs log text
        n_events = ecnt["E1"] + ecnt["E2"] + ecnt["E3"] + ecnt["E5"]
        rows.append({
            "id": e["id"], "childs_page": e["childs_page"], "page_date": e["date"],
            "key": e["key"], "class": method_class(e), "status": e["status"],
            "n_slots": len(O), "n_letters": nlet, "n_lost_marks": O.count("-"),
            "odd_slots": len(O) % 2, "ref_len": len(T), "wildcards": T.count("*"),
            "count_in_log": e["count_in_log"],
            "count_minus_slots": None if e["count_in_log"] is None else e["count_in_log"] - len(O),
            "cost": a["cost"], "n_optimal": a["n_optimal"],
            "sub_min": a["ranges"]["sub"][0], "sub_max": a["ranges"]["sub"][1],
            "del_min": a["ranges"]["del"][0], "del_max": a["ranges"]["del"][1],
            "ins_min": a["ranges"]["ins"][0], "ins_max": a["ranges"]["ins"][1],
            "E1_ev": ecnt["E1"], "E1_sym": esym["E1"], "E2_ev": ecnt["E2"], "E2_sym": esym["E2"],
            "E3_ev": ecnt["E3"], "E3_sym": esym["E3"], "E4": ecnt["E4"], "E5": ecnt["E5"],
            "events": n_events,
            "cost_per_100": round(100 * a["cost"] / max(len(T), 1), 3),
            "events_per_100": round(100 * n_events / max(len(T), 1), 3),
            "page_reading_differs": rx is not None,
            "rx_cost_vs_page": rx, "tx_cost_page_vs_log": tx,
            "e6_best_cost": None if e6 is None else e6[0],
            "e6_move": None if e6 is None else f"{e6[1]}@{e6[2]}",
            "edit_script": " ".join(det),
        })
    cols = list(rows[0].keys())
    with open(os.path.join(RES, "adfgvx-mutilation.csv"), "w") as f:
        f.write(prov_header("#", "search/adfgvx/census.py"))
        f.write("# One row per solved log entry with key and plaintext. See "
                "results/adfgvx-mutilation.md for definitions.\n")
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join("" if r[c] is None else
                             ('"' + str(r[c]) + '"' if isinstance(r[c], str) and ("," in r[c] or " " in r[c]) else str(r[c]))
                             for c in cols) + "\n")
    write_tables(rows, rec)


def dist_table(W, rows, field, label):
    xs = [r[field] for r in rows]
    W(f"| {label} | {len(xs)} | {sum(xs)} | {sum(xs)/len(xs):.3f} | {quant(xs,.5):g} | "
      f"{quant(xs,.9):g} | {quant(xs,.95):g} | {quant(xs,.99):g} | {max(xs):g} |")


def write_tables(rows, rec):
    L = []
    W = L.append
    W("# ADFGVX 1918 mutilation census: generated tables\n")
    W(prov_header("", "search/adfgvx/census.py"))
    W("Narrative, definitions and limits: `results/adfgvx-mutilation.md`. Per-message rows: "
      "`results/adfgvx-mutilation.csv`.\n")
    classes = sorted(set(r["class"] for r in rows))
    W("## 1. The census set\n")
    W("| class | messages | reference symbols | wildcard symbols |")
    W("|---|---|---|---|")
    for c in classes + ["ALL"]:
        rs = [r for r in rows if c == "ALL" or r["class"] == c]
        W(f"| {c} | {len(rs)} | {sum(r['ref_len'] for r in rs)} | {sum(r['wildcards'] for r in rs)} |")
    W("\n## 2. Edits per message (symbol edits = minimal cost; events = E1+E2+E3+E5 runs)\n")
    for c in classes + ["ALL"]:
        rs = [r for r in rows if c == "ALL" or r["class"] == c]
        W(f"\n### {c} ({len(rs)} messages)\n")
        W("| statistic | n | sum | mean | median | p90 | p95 | p99 | max |")
        W("|---|---|---|---|---|---|---|---|---|")
        dist_table(W, rs, "cost", "symbol edits")
        dist_table(W, rs, "events", "events")
        dist_table(W, rs, "cost_per_100", "symbol edits per 100 symbols")
        dist_table(W, rs, "events_per_100", "events per 100 symbols")
        dist_table(W, rs, "E4", "E4 lost marks")
    W("\n## 3. Histogram of events per message\n")
    W("| events | " + " | ".join(classes) + " | ALL |")
    W("|---" * (len(classes) + 2) + "|")
    mx = max(r["events"] for r in rows)
    for v in range(mx + 1):
        cs = [sum(1 for r in rows if r["class"] == c and r["events"] == v) for c in classes]
        tot = sum(cs)
        if tot:
            W(f"| {v} | " + " | ".join(map(str, cs)) + f" | {tot} |")
    W("\n## 4. By type (canonical alignment; [min, max] over all optimal alignments in brackets)\n")
    W("| class | E1 ev (sym) | E2 ev (sym) | E3 ev (sym) | E4 | E5 | sub [min,max] | del [min,max] | ins [min,max] |")
    W("|---|---|---|---|---|---|---|---|---|")
    for c in classes + ["ALL"]:
        rs = [r for r in rows if c == "ALL" or r["class"] == c]
        s = lambda f: sum(r[f] for r in rs)
        W(f"| {c} | {s('E1_ev')} ({s('E1_sym')}) | {s('E2_ev')} ({s('E2_sym')}) | "
          f"{s('E3_ev')} ({s('E3_sym')}) | {s('E4')} | {s('E5')} | "
          f"[{s('sub_min')},{s('sub_max')}] | [{s('del_min')},{s('del_max')}] | "
          f"[{s('ins_min')},{s('ins_max')}] |")
    amb = [r for r in rows if r["n_optimal"] > 1 and (r["sub_min"] != r["sub_max"] or r["del_min"] != r["del_max"])]
    W(f"\nMessages whose type breakdown is NOT forced (sub or del count differs between optimal "
      f"alignments): {len(amb)}. Messages with more than one optimal alignment: "
      f"{sum(1 for r in rows if r['n_optimal'] > 1)} (mostly the position of an indel inside a "
      f"run of equal symbols, which does not change the counts).\n")
    W("## 5. E6 test (one interim-text insertion/deletion) on every message with cost >= 2\n")
    t = [r for r in rows if r["e6_best_cost"] is not None]
    better = [r for r in t if r["e6_best_cost"] + 1 < r["cost"]]
    W(f"Tested: {len(t)}. Explained better by one E6 event plus residual edits "
      f"(e6 cost + 1 < ciphertext cost): {len(better)}.\n")
    if better:
        W("| id | ciphertext-edit cost | E6 move | residual cost after E6 |")
        W("|---|---|---|---|")
        for r in sorted(better, key=lambda r: r["id"]):
            W(f"| {r['id']} | {r['cost']} | {r['e6_move']} | {r['e6_best_cost']} |")
    W("\n## 6. Outliers (top 15 by symbol edits, and every message with events_per_100 > p99)\n")
    p99 = quant([r["events_per_100"] for r in rows], .99)
    out = sorted(rows, key=lambda r: (-r["cost"], r["id"]))[:15]
    out += [r for r in rows if r["events_per_100"] > p99 and r not in out]
    W("| id | page | class | ref len | log slots | header count | cost | events | ev/100 | E1 | E2 | E3 sym | E5 | E4 | edit script (canonical) |")
    W("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in out:
        es = r["edit_script"]
        if len(es) > 160:
            es = es[:160] + " ..."
        W(f"| {r['id']} | {r['childs_page']} | {r['class']} | {r['ref_len']} | {r['n_slots']} | "
          f"{r['count_in_log']} | {r['cost']} | {r['events']} | {r['events_per_100']} | "
          f"{r['E1_ev']} | {r['E2_ev']} | {r['E3_sym']} | {r['E5']} | {r['E4']} | `{es}` |")
    # header count check (reconstruction-free)
    W("\n## 7. Header count against received length (reconstruction-free)\n")
    W("`count_in_log` is the symbol count the log heading gives (creilly's field); `n_slots` the "
      "symbols the log shows, '-' slots included. A mismatch is a length mutilation (or a count "
      "or transcription slip) seen without any decryption.\n")
    W("| class | with count | count = slots | count > slots | count < slots | mean |count - slots| |")
    W("|---|---|---|---|---|---|")
    for c in classes + ["ALL"]:
        rs = [r for r in rows if (c == "ALL" or r["class"] == c) and r["count_minus_slots"] is not None]
        if not rs:
            continue
        d = [r["count_minus_slots"] for r in rs]
        W(f"| {c} | {len(rs)} | {sum(x == 0 for x in d)} | {sum(x > 0 for x in d)} | "
          f"{sum(x < 0 for x in d)} | {sum(abs(x) for x in d)/len(d):.2f} |")
    rs = [r for r in rows if r["count_minus_slots"] is not None]
    agree = sum(1 for r in rs if r["count_minus_slots"] == r["ref_len"] - r["n_slots"])
    W(f"\nOf {len(rs)} census messages with a header count, the header count equals the "
      f"reference length (re-encrypted plaintext) for "
      f"{sum(1 for r in rs if r['count_in_log'] == r['ref_len'])}, and header-minus-log equals "
      f"reference-minus-log for {agree}.\n")
    survivorship(W, rows, rec)
    class_c(W, rows)
    repeats(W, rows, rec)
    open(os.path.join(RES, "adfgvx-mutilation.tables.md"), "w").write("\n".join(L) + "\n")


SCHMEH_OPEN = ["p076A", "p155E", "p156C3", "p156C6", "p161D", "p173A", "p179B1", "p192A", "p201D"]


def survivorship(W, rows, rec):
    W("## 8. Survivorship check: solved against unsolved, header-free statistics of the log text\n")
    W("Statistics of the PRINTED log text only (no decryption): odd slot count, odd letter count, "
      "share of entries with any '-' mark, '-' marks per 100 slots, header count mismatch, "
      "length. Solved = the census set. Unsolved = status 'Unsolved' in records.json. Schmeh-9 = "
      "the 2017 open list as mapped in results/adfgvx-transcription-diff.md (153a/b and "
      "176-GGDAA are now 'Solved' in creilly and are included for reference). Tests: Fisher "
      "exact (two-sided) for rates, Mann-Whitney U (normal approximation, two-sided) for "
      "lengths.\n")
    by = {e["id"]: e for e in rec}
    census_ids = {r["id"] for r in rows}

    def stats(ids):
        es = [by[i] for i in ids if by[i]["printed"]]
        n = len(es)
        sl = [len(e["printed"]) for e in es]
        le = [sum(c in LETTERS for c in e["printed"]) for e in es]
        odd_s = sum(x % 2 for x in sl)
        odd_l = sum(x % 2 for x in le)
        gap = sum(1 for e in es if "-" in e["printed"])
        marks = sum(e["printed"].count("-") for e in es)
        wc = [e for e in es if e["count_in_log"] is not None]
        mis = sum(1 for e in wc if e["count_in_log"] != len(e["printed"]))
        return dict(n=n, sl=sl, le=le, odd_s=odd_s, odd_l=odd_l, gap=gap, marks=marks,
                    tot=sum(sl), wc=len(wc), mis=mis)
    unsolved = [e["id"] for e in rec if e["status"] == "Unsolved"]
    groups = [("Solved (census)", sorted(census_ids)), ("Unsolved", unsolved),
              ("Schmeh-9", SCHMEH_OPEN)]
    S = {g: stats(ids) for g, ids in groups}
    W("| set | n | odd slot count | odd letter count | any '-' | '-' per 100 slots | header count != slots | median slots | mean slots |")
    W("|---|---|---|---|---|---|---|---|---|")
    for g, _ in groups:
        s = S[g]
        W(f"| {g} | {s['n']} | {s['odd_s']} ({100*s['odd_s']/s['n']:.1f}%) | "
          f"{s['odd_l']} ({100*s['odd_l']/s['n']:.1f}%) | {s['gap']} ({100*s['gap']/s['n']:.1f}%) | "
          f"{100*s['marks']/s['tot']:.2f} | {s['mis']}/{s['wc']} ({100*s['mis']/max(s['wc'],1):.1f}%) | "
          f"{quant(s['sl'],.5):g} | {sum(s['sl'])/s['n']:.1f} |")
    a, b = S["Solved (census)"], S["Unsolved"]
    W("\nSolved vs Unsolved:\n")
    W(f"- odd slot count: Fisher p = {fisher_two_sided(a['odd_s'], a['n']-a['odd_s'], b['odd_s'], b['n']-b['odd_s']):.3g}")
    W(f"- odd letter count: Fisher p = {fisher_two_sided(a['odd_l'], a['n']-a['odd_l'], b['odd_l'], b['n']-b['odd_l']):.3g}")
    W(f"- any '-' mark: Fisher p = {fisher_two_sided(a['gap'], a['n']-a['gap'], b['gap'], b['n']-b['gap']):.3g}")
    W(f"- header count mismatch: Fisher p = {fisher_two_sided(a['mis'], a['wc']-a['mis'], b['mis'], b['wc']-b['mis']):.3g}")
    U, z, p = mann_whitney_p(a["sl"], b["sl"])
    W(f"- slot count: Mann-Whitney z = {z:.2f}, p = {p:.3g}")
    W("\nHeader count minus log slots (reconstruction-free length damage; available for the "
      "unread entries too). Header counts are themselves noisy: see section 7, where class A "
      "entries decrypt perfectly yet some disagree with their header count.\n")
    W("| set | with count | d = 0 | 1 <= abs(d) <= 2 | 3..10 | 11..40 | > 40 | median abs(d) | d > 0 (fewer symbols than announced) |")
    W("|---|---|---|---|---|---|---|---|---|")
    for g, ids in groups:
        es = [by[i] for i in ids if by[i]["printed"] and by[i]["count_in_log"] is not None]
        d = [e["count_in_log"] - len(e["printed"]) for e in es]
        ad = [abs(x) for x in d]
        W(f"| {g} | {len(d)} | {sum(x == 0 for x in ad)} | {sum(1 <= x <= 2 for x in ad)} | "
          f"{sum(3 <= x <= 10 for x in ad)} | {sum(11 <= x <= 40 for x in ad)} | "
          f"{sum(x > 40 for x in ad)} | {quant(ad, .5):g} | {sum(x > 0 for x in d)} |")
    W("\nLength distribution (slots), deciles:\n")
    W("| set | p10 | p25 | p50 | p75 | p90 | min | max |")
    W("|---|---|---|---|---|---|---|---|")
    for g, _ in groups:
        s = S[g]["sl"]
        W(f"| {g} | {quant(s,.1):g} | {quant(s,.25):g} | {quant(s,.5):g} | {quant(s,.75):g} | "
          f"{quant(s,.9):g} | {min(s)} | {max(s)} |")



def class_c(W, rows):
    W("\n## 9. Class C: transcription error against reception error\n")
    W("For entries whose page was re-read (records.json `ciphertext` differs from `printed`), "
      "the total edit cost (true vs log text) splits into reception (true vs page reading, "
      "census costs) and transcription (page reading vs log text, '-' free on either side). "
      "The unsolved entries have no page re-reading: what an attack meets is the log text, so "
      "the TOTAL is the relevant figure, and the split says how much of it the Bean scan could "
      "remove.\n")
    rs = [r for r in rows if r["page_reading_differs"]]
    W("| id | class | ref len | total (true vs log) | reception (true vs page) | transcription (page vs log) |")
    W("|---|---|---|---|---|---|")
    for r in sorted(rs, key=lambda r: -r["cost"]):
        W(f"| {r['id']} | {r['class']} | {r['ref_len']} | {r['cost']} | {r['rx_cost_vs_page']} | "
          f"{r['tx_cost_page_vs_log']} |")
    if rs:
        W(f"\nSums over {len(rs)} entries: total {sum(r['cost'] for r in rs)}, reception "
          f"{sum(r['rx_cost_vs_page'] for r in rs)}, transcription "
          f"{sum(r['tx_cost_page_vs_log'] for r in rs)}. Medians: total "
          f"{quant([r['cost'] for r in rs], .5):g}, reception "
          f"{quant([r['rx_cost_vs_page'] for r in rs], .5):g}, transcription "
          f"{quant([r['tx_cost_page_vs_log'] for r in rs], .5):g}.\n")


def repeats(W, rows, rec):
    """Repeated receptions: reconstruction-free error rates."""
    by = {e["id"]: e for e in rec}
    cen = [by[r["id"]] for r in rows]
    W("\n## 10. Repeated receptions: an error rate that needs no reconstruction\n")
    W("Pairs of census entries under the SAME key whose plaintexts have the SAME length and agree "
      "position by position on at least a fraction f of positions (an unknown character "
      "counts as agreeing) are taken to be two copies of one cryptogram (a second intercept or a "
      "repeat). The true ciphertext of both is then the same string, so the two LOG texts can be "
      "compared directly, with no decryption and no repair: every disagreement is an error in "
      "at least one copy. Alignment: unit costs, '-' free on either side. Per-copy rate = "
      "disagreements / (2 x symbols), which assumes the two copies' errors are independent and "
      "never coincide (so it is if anything an underestimate).\n")
    W("This matters because in class A the plaintext was obtained by decrypting the log text "
      "itself, so a wrong symbol (E5) re-encrypts to itself and is invisible to sections 2-4.\n")

    def agree(a, b):
        return sum(1 for x, y in zip(a, b) if x == y or x in "-?#_" or y in "-?#_") / len(a)
    allpairs = []
    for i in range(len(cen)):
        for j in range(i + 1, len(cen)):
            a, b = cen[i], cen[j]
            if a["key"] != b["key"] or len(a["plaintext"]) != len(b["plaintext"]):
                continue
            ag = agree(a["plaintext"], b["plaintext"])
            if ag < 0.8:
                continue
            al = align(a["printed"], b["printed"], lost_pair)
            sub = sum(1 for op in al["ops"] if op[0] == "sub")
            ev = events(al["ops"])
            indel_ev = sum(1 for e in ev if e[0] in ("del", "ins"))
            indel_sym = sum(e[1] for e in ev if e[0] in ("del", "ins"))
            n = min(len(a["printed"]), len(b["printed"]))
            allpairs.append((ag, a["id"], b["id"], a["key"], n, sub, indel_ev, indel_sym,
                             a["printed"] == b["printed"]))
    W("| f (plaintext agreement) | pairs | symbols (min of pair) | substitutions | indel events (symbols) | per-copy substitution rate per 100 | per-copy indel events per 100 |")
    W("|---|---|---|---|---|---|---|")
    for f in (0.8, 0.9, 0.95):
        ps = [p for p in allpairs if p[0] >= f]
        N = sum(p[4] for p in ps)
        S = sum(p[5] for p in ps)
        IE = sum(p[6] for p in ps)
        IS = sum(p[7] for p in ps)
        W(f"| {f} | {len(ps)} | {N} | {S} | {IE} ({IS}) | {100*S/(2*N):.3f} | {100*IE/(2*N):.3f} |")
    W("\nEvery pair at f >= 0.8:\n")
    W("| agreement | copy 1 | copy 2 | key | symbols | substitutions | indel events | indel symbols |")
    W("|---|---|---|---|---|---|---|---|")
    for p in sorted(allpairs, key=lambda p: (-p[0], p[1])):
        W(f"| {p[0]:.3f} | {p[1]} | {p[2]} | {p[3]} | {p[4]} | {p[5]} | {p[6]} | {p[7]} |")
    # what the census itself sees for the same copies
    ids = {p[1] for p in allpairs if p[0] >= 0.9} | {p[2] for p in allpairs if p[0] >= 0.9}
    rr = [r for r in rows if r["id"] in ids]
    W(f"\nThe main census, on the same {len(rr)} copies, records {sum(r['E5'] for r in rr)} "
      f"substitutions (E5) in total. The difference is the reconstruction bias for E5, "
      f"measured.\n")


if __name__ == "__main__":
    main()
