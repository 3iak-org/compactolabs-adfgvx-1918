"""Duplicate screen: is an unread entry another copy of a solved one (or of another unread one)?

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/duplicates.py

DECRYPTION-FREE. It compares log texts only (creilly @ e60da03, field `printed`).

Statistic, for a pair of log texts: the shorter one, X, is aligned in full against the best
substring of the longer one, Y (a fitting alignment; free end gaps in Y). Costs are unit
substitution and unit indel. This is gap-aware (indels are free to fall anywhere) and
best-offset. '-' (a lost slot) matches only '-': as a free wildcard it let heavily gapped texts
fit everything (first run, 2026-11-01). Then d = cost / (slots in X). An entry's score is its smallest d over a
target set.

Null (pair level): every pair of solved entries under DIFFERENT keys ("unrelated": a different
key means a different ciphertext even for the same plaintext). Pairs are binned by the letter
count of the shorter and of the longer text, because a short text fitted inside a long one has
far more freedom. Within a cell, a pair's significance is given two ways:
  - empirical: is d below the cell's null minimum? The expected number of such pairs per entry
    is reported (targets in that cell / null pairs in the cell).
  - approximate [H]: z = (d - cell mean)/cell sd, with a normal lower tail. Bonferroni over the
    entry's targets gives p_entry, and the entry is FLAGGED when p_entry < 0.01. The normal
    tail is an approximation, not a law of these data: it is stated as one, and it is checked
    against the planted controls and the empirical minimum.
The null has a few near-exact cross-key pairs (listed in the output). They contaminate its
extreme tail, so they are removed from the cell statistics and reported instead (d < 0.2 at
>= 30 letters).

Controls: 200 solved entries are mutilated (census profile, plus E5 at the repeated-reception
rate, plus a random truncation of up to 30%) and screened against the solved set, original
included. Recovery = flagged, with the original as best match.
Output: results/adfgvx-duplicates.md
"""
import ctypes
import json
import os
import random
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from census import quant  # noqa: E402
from provenance import header as prov_header  # noqa: E402
import sharing  # noqa: E402

LET = set("ADFGVX")
BINS = [(0, 59), (60, 119), (120, 179), (180, 239), (240, 10 ** 6)]
SEED = 20261101
MINLET = 30   # a pair is scored only if its SHORTER text has at least this many letters
_lib = None


def lib():
    global _lib
    if _lib is None:
        tmp = os.environ.get("TMPDIR", "/tmp")
        so = os.path.join(tmp, "adfgvx-edcost.so")
        src = os.path.join(HERE, "edcost.c")
        if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
            subprocess.check_call(["cc", "-O2", "-shared", "-fPIC", "-o", so, src])
        _lib = ctypes.CDLL(so)
        _lib.fitcost.restype = ctypes.c_int
        _lib.fitcost.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    return _lib


def fit(x, y):
    """Shorter string in full against the best substring of the longer. Returns
    (cost, letters of the shorter, which side is shorter, start, end in the longer)."""
    if len(x) > len(y):
        c, n, _, s, e = fit(y, x)
        return c, n, "target", s, e
    s, e = ctypes.c_int(), ctypes.c_int()
    c = lib().fitcost(x.encode(), len(x), y.encode(), len(y), ctypes.byref(s), ctypes.byref(e))
    return c, len(x), "query", s.value, e.value


def fit_py(x, y):
    """Independent pure-Python fitting cost (no shared code with fitcost), for spot checks."""
    if len(x) > len(y):
        x, y = y, x
    prev = [0] * (len(y) + 1)
    for i, a in enumerate(x, 1):
        cur = [i] + [0] * len(y)
        for j, b in enumerate(y, 1):
            cur[j] = min(prev[j - 1] + (0 if a == b else 1),
                         prev[j] + 1, cur[j - 1] + 1)
        prev = cur
    return min(prev)


def pair_d(args):
    """All pair costs for one query against a target list: [(tid, d, cost, n, side, s, e)]."""
    qid, q, targets = args
    out = []
    for tid, t in targets:
        if min(sum(ch in LET for ch in q), sum(ch in LET for ch in t)) < MINLET:
            continue
        c, n, side, s, e = fit(q, t)
        out.append((tid, c / max(n, 1), c, n, side, s, e))
    return qid, out


SB = [30, 45, 60, 90, 120, 160, 200, 250, 10 ** 6]
LB = [0, 120, 200, 280, 10 ** 6]


def cell(ns, nl):
    i = max(k for k in range(len(SB) - 1) if SB[k] <= ns)
    j = max(k for k in range(len(LB) - 1) if LB[k] <= nl)
    return i, j


def cell_name(c):
    i, j = c
    return f"short {SB[i]}-{SB[i+1]-1 if SB[i+1] < 10**6 else 'up'} / long {LB[j]}-{LB[j+1]-1 if LB[j+1] < 10**6 else 'up'}"


def norm_tail(z):
    import math
    return 0.5 * math.erfc(-z / math.sqrt(2))


def main():
    sharing.be_nice()
    sharing.exclusive()
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    sol = [e for e in rec if e["status"].startswith("Solved") and e["key"] and e["printed"]
           and sum(ch in LET for ch in e["printed"]) >= MINLET]
    SCANMODE = "--scan" in sys.argv
    TAG = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else None
    if "--units" in sys.argv:
        # unread side given as a JSON list of {"id", "printed"} (strand J0 texts); same method,
        # same committed threshold
        un_all = json.load(open(sys.argv[sys.argv.index("--units") + 1]))
        changes = "units from " + sys.argv[sys.argv.index("--units") + 1]
        SCANMODE = True
    elif SCANMODE:
        # unread side = the scan transcription's units (search/adfgvx/scan.py), primary reading;
        # the solved side and the null stay on creilly (the scan re-read only the unread)
        import scan
        su, changes = scan.units()
        un_all = [{"id": u["unit"], "printed": u["primary"]} for u in su]
    else:
        un_all = [e for e in rec if e["status"] == "Unsolved" and e["printed"]]
    un = [e for e in un_all if sum(ch in LET for ch in e["printed"]) >= MINLET]
    too_short = [e["id"] for e in un_all if e not in un]
    S = [(e["id"], e["printed"]) for e in sol]
    key = {e["id"]: e["key"] for e in sol}
    letters = lambda s: sum(ch in LET for ch in s)
    rng = random.Random(SEED)

    # spot check C against Python
    for _ in range(300):
        a = rng.choice(rec)["printed"] or ""
        b = rng.choice(rec)["printed"] or ""
        a, b = a[: rng.randint(0, 120)], b[: rng.randint(0, 160)]
        assert fit(a, b)[0] == fit_py(a, b), (a, b)

    nlet = {e["id"]: letters(e["printed"]) for e in rec if e["printed"]}
    nlet.update({e["id"]: letters(e["printed"]) for e in un_all})
    # null: every unrelated solved pair, once
    jobs = [(e["id"], e["printed"], [(i, t) for i, t in S[k + 1:] if key[i] != e["key"]])
            for k, e in enumerate(sol)]
    with ProcessPoolExecutor(sharing.MAX_JOBS) as ex:
        nullpairs = []
        for qid, out in ex.map(pair_d, jobs, chunksize=4):
            for tid, d, c, n, side, s_, e_ in out:
                nullpairs.append((qid, tid, d, c, n, side, s_, e_))
    contaminated = [p for p in nullpairs if p[2] < 0.2]
    cells = {}
    for qid, tid, d, *_ in nullpairs:
        if d < 0.2:
            continue
        a_, b_ = sorted((nlet[qid], nlet[tid]))
        cells.setdefault(cell(a_, b_), []).append(d)
    stats = {}
    for c, xs in cells.items():
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / max(len(xs) - 1, 1)) ** 0.5
        stats[c] = (len(xs), m, sd, min(xs))

    def score(qid, q, pairs):
        """Per-entry: best pair by approximate p, Bonferroni over targets."""
        best = None
        exp_below_min = 0.0
        n_below_min = 0
        for tid, d, c, n, side, s_, e_ in pairs:
            a_, b_ = sorted((letters(q), nlet[tid]))
            st = stats.get(cell(a_, b_))
            if not st or st[2] == 0:
                continue
            z = (d - st[1]) / st[2]
            pz = norm_tail(z)
            exp_below_min += 1 / st[0]
            n_below_min += d < st[3]
            if best is None or pz < best[0]:
                best = (pz, tid, d, c, n, side, s_, e_, z, cell(a_, b_), d < st[3])
        if best is None:
            return None
        pent = min(1.0, best[0] * len(pairs))
        return {"p_entry": pent, "p_pair": best[0], "tid": best[1], "d": best[2], "cost": best[3],
                "n": best[4], "side": best[5], "span": (best[6], best[7]), "z": best[8],
                "cell": best[9], "below_min": best[10], "n_below_min": n_below_min,
                "exp_below_min": exp_below_min, "n_targets": len(pairs)}

    # calibration: the same per-entry score for every SOLVED entry against its unrelated set
    byq = {}
    for qid, tid, d, c, n, side, s_, e_ in nullpairs:
        byq.setdefault(qid, []).append((tid, d, c, n, side, s_, e_))
        byq.setdefault(tid, []).append((qid, d, c, n, "target" if side == "query" else "query", s_, e_))
    cal = [score(e["id"], e["printed"], byq.get(e["id"], [])) for e in sol]
    cal = [r for r in cal if r]
    cal_fp = sum(1 for r in cal if r["p_entry"] < 0.01)
    cal_fp_clean = sum(1 for r in cal if r["p_entry"] < 0.01 and r["d"] >= 0.2)
    with ProcessPoolExecutor(sharing.MAX_JOBS) as ex:
        upairs = dict(ex.map(pair_d, [(e["id"], e["printed"], S) for e in un], chunksize=2))
    U = [(e["id"], e["printed"]) for e in un]
    with ProcessPoolExecutor(sharing.MAX_JOBS) as ex:
        uupairs = dict(ex.map(pair_d, [(e["id"], e["printed"], [(i, t) for i, t in U if i != e["id"]])
                                       for e in un], chunksize=2))
    n_cmp_us = sum(len(v) for v in upairs.values())
    n_cmp_uu = sum(len(v) for v in uupairs.values())
    # controls
    from plant import census_profiles, mutilate
    prof = census_profiles()
    ctrl = []
    pool = [e for e in sol if letters(e["printed"]) >= 40 and "-" not in e["printed"]]
    for t in range(200):
        e = rng.choice(pool)
        _, evs = rng.choice(prof)
        n5 = sum(1 for _ in range(len(e["printed"])) if rng.random() < 0.0066)
        ct, _ = mutilate(rng, e["printed"], list(evs) + [("E5", 1, None)] * n5)
        cut = int(len(ct) * rng.uniform(0, 0.3))
        ct = ct[cut:] if rng.random() < 0.5 else ct[:len(ct) - cut]
        ctrl.append((f"ctrl{t}:{e['id']}", ct))
    with ProcessPoolExecutor(sharing.MAX_JOBS) as ex:
        cpairs = dict(ex.map(pair_d, [(i, c, S) for i, c in ctrl], chunksize=4))
    for i, c in ctrl:
        nlet[i] = letters(c)

    L = []
    W = L.append
    W("# ADFGVX 1918: duplicate screen of the unread entries\n")
    W(prov_header("", "search/adfgvx/duplicates.py" + (" --scan" if SCANMODE else ""),
                  "transcription: unread = scan transcription (primary); solved = creilly @ e60da03"
                  if SCANMODE else None) if SCANMODE else prov_header("", "search/adfgvx/duplicates.py"))
    if SCANMODE:
        W("**Transcription:** unread side = the SCAN transcription "
          "(ciphertexts/adfgvx-1918-scan-transcription.json, transcribe-adfgvx), as units from "
          + ("search/adfgvx/strandj.py J0, symbol policy of the strand J prereg (non-ADFGVX, "
             "parenthesised, '-' and '?' each one lost symbol). " if TAG == "J0" else
             "search/adfgvx/scan.py, primary reading (policy P1-P5 in its docstring: lost marks, "
             "'?' and non-ADFGVX letters are lost slots; parenthesised symbols and groups kept). ") +
          f"Unit changes against creilly's ids: {changes}. Solved side and null: creilly @ "
          "e60da03 `printed` (the scan re-read only the unread entries and a calibration set).\n")
    else:
        W("**Transcription:** creilly11235/adfgvx-1918 @ e60da03, field `printed` (Childs log as "
          "transcribed from the scan). Schmeh's 2017 text is NOT used here.\n")
    W("Method: see the docstring of `search/adfgvx/duplicates.py`. The screen uses no "
      "decryption and no key: log text against log text.\n")
    W(f"Comparisons (pairs scored, shorter text >= {MINLET} letters): unread x solved "
      f"{n_cmp_us}; unread x unread {n_cmp_uu} (ordered); null: {len(nullpairs)} unrelated "
      f"solved pairs, of which {len(contaminated)} near-exact (d < 0.2) were set aside. A C "
      f"fitting cost was checked against an independent Python one on 300 random pairs.\n")
    W(f"Unread entries with fewer than {MINLET} letters, not screened: "
      f"{', '.join(too_short) or 'none'}.\n")
    W("## 1. Null cells (unrelated solved pairs, near-exact pairs removed)\n")
    W("| cell | pairs | mean d | sd | min d |")
    W("|---|---|---|---|---|")
    for c in sorted(stats):
        n_, m, sd, mn = stats[c]
        W(f"| {cell_name(c)} | {n_} | {m:.3f} | {sd:.3f} | {mn:.3f} |")
    W("\n### Near-exact pairs inside the null (solved, different keys, d < 0.2)\n")
    if contaminated:
        W("These are not chance. They are cross-key copies, joined log rows or mislabelled keys, "
          "and a finding in their own right.\n")
    else:
        W("None. (In a first run that let '-' match anything, eleven such pairs appeared; all "
          "were runs of lost marks matching as wildcards, which is why '-' is now an ordinary "
          "symbol.)\n")
    W("| entry | key | entry | key | d | cost | slots of shorter | span in longer |")
    W("|---|---|---|---|---|---|---|---|")
    for qid, tid, d, c, n, side, s_, e_ in sorted(contaminated, key=lambda p: p[2]):
        W(f"| {qid} | {key[qid]} | {tid} | {key[tid]} | {d:.3f} | {c} | {n} | {s_}-{e_} |")
    W(f"\n### Calibration of p_entry on the solved entries themselves\n")
    W(f"Every solved entry scored against its unrelated solved set, exactly as an unread entry "
      f"is scored: {cal_fp} of {len(cal)} reach p_entry < 0.01 ({100*cal_fp/max(len(cal),1):.1f}%; "
      f"nominal 1%). Of those, {cal_fp - cal_fp_clean} are the near-exact cross-key pairs "
      f"above; the other {cal_fp_clean} are false flags of the approximation.\n")
    W("\n## 2. Controls: mutilated copies of solved entries\n")
    hit = flagged = 0
    for i, c in ctrl:
        r = score(i, c, cpairs[i])
        f = r is not None and r["p_entry"] < 0.01
        flagged += f
        hit += f and r["tid"] == i.split(":")[1]
    W(f"{len(ctrl)} controls (census mutilation profile + E5 at 0.0066/symbol + up to 30% "
      f"truncation), screened against all solved entries, original included. FLAGGED "
      f"(p_entry < 0.01): {flagged}; flagged with the original as best match: {hit} "
      f"({100*hit/len(ctrl):.1f}%).\n")
    W("## 3. Every unread entry\n")
    W("Best pair by approximate p. p_entry = Bonferroni over the entry's targets. 'below min' = "
      "d is below the null minimum of its cell; 'expected' = how many of its targets would be "
      "below their cell minimum by chance (sum of 1/cell size). Span = matched positions in the "
      "longer text; side = which text is the shorter (query = the unread entry).\n")
    W("| unread | letters | vs SOLVED: best | d | cost | side | span | z | p_entry | below min (n / expected) | vs UNREAD: best | d | p_entry | verdict |")
    W("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    flags = []
    csvrows = []
    for e in un:
        r = score(e["id"], e["printed"], upairs[e["id"]])
        ru = score(e["id"], e["printed"], uupairs[e["id"]])
        csvrows.append([e["id"], r["tid"] if r else "", f"{r['d']:.4f}" if r else "",
                        f"{r['p_entry']:.3g}" if r else "", ru["tid"] if ru else "",
                        f"{ru['d']:.4f}" if ru else "", f"{ru['p_entry']:.3g}" if ru else ""])
        v = []
        if r and r["p_entry"] < 0.01:
            v.append("FLAG solved")
        if ru and ru["p_entry"] < 0.01:
            v.append("FLAG unread")
        if v:
            flags.append((e["id"], r, ru, v))
        rs = (f"{r['tid']} | {r['d']:.3f} | {r['cost']} | {r['side']} | {r['span'][0]}-{r['span'][1]} | "
              f"{r['z']:.1f} | {r['p_entry']:.2g} | {r['n_below_min']} / {r['exp_below_min']:.2f}") if r else "| | | | | | |"
        us = (f"{ru['tid']} | {ru['d']:.3f} | {ru['p_entry']:.2g}") if ru else "| |"
        W(f"| {e['id']} | {letters(e['printed'])} | {rs} | {us} | {', '.join(v)} |")
    W("\n## 4. Flagged entries (p_entry < 0.01)\n")
    if not flags:
        W("None.")
    for i, r, ru, v in flags:
        parts = []
        if r and "FLAG solved" in v:
            parts.append(f"solved {r['tid']} (d {r['d']:.3f}, {r['cost']} edits over {r['n']} slots, p_entry {r['p_entry']:.2g})")
        if ru and "FLAG unread" in v:
            parts.append(f"unread {ru['tid']} (d {ru['d']:.3f}, {ru['cost']} edits over {ru['n']} slots, p_entry {ru['p_entry']:.2g})")
        W(f"- **{i}**: " + "; ".join(parts))
    W("\nAn unread-vs-unread pair appears under both of its entries.\n")
    W("## What this screen cannot see\n")
    W("- A RE-ENCIPHERMENT of the same plaintext under another key: different ciphertext, no "
      "match. That needs decryption, which this screen does not do.")
    W("- A copy damaged beyond the controls' mutilation: by construction the controls set the "
      "power, not the truth.")
    W("- Transcription: if creilly's `printed` for one copy is badly transcribed, the match "
      "weakens. Schmeh's text could be screened too; it covers only 22 entries.")
    base = f"adfgvx-duplicates-{TAG}" if TAG else ("adfgvx-duplicates-scan" if SCANMODE else "adfgvx-duplicates")
    with open(os.path.join(ROOT, "results", base + ".csv"), "w") as f:
        f.write("".join("# " + l + "\n" for l in prov_header("", "search/adfgvx/duplicates.py").splitlines()))
        f.write("unread,best_solved,d_solved,p_entry_solved,best_unread,d_unread,p_entry_unread\n")
        f.write("".join(",".join(r) + "\n" for r in csvrows))
    open(os.path.join(ROOT, "results", base + ".md"), "w").write("\n".join(L) + "\n")
    print("\n".join(l for l in L if l.startswith("- **") or "FLAGGED" in l))


if __name__ == "__main__":
    main()
