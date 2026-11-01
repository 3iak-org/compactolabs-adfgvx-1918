"""Write results/adfgvx-power.md from the trial records (comp-adfgvx, 2026-11-01).

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/powerreport.py

Reads results/adfgvx-power-trials.jsonl (F1, F2) and results/adfgvx-power-f3.jsonl (F3).
Decision statistic: the PENALISED trigram score of the attack's final key (every trigram
position counts; one containing an unknown letter is charged ln(1/36)); the search objective
skips such positions and is never used to decide. Proposed threshold per family and letter
bin: the MAXIMUM over all null trials of that bin (both nulls pooled), so the estimated
false-positive rate at the threshold is 0/n_null (upper 95% bound 3/n_null, rule of three).
"""
import json
import math
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
import power  # noqa: E402
from census import quant  # noqa: E402
from provenance import header as prov_header  # noqa: E402

BINS = power.BINS
WIDTHS = power.WIDTHS


def load(p):
    p = os.path.join(ROOT, "results", p)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def abin(r):
    """The letter bin of a trial's ACTUAL letter count (nulls are matched to a composition only
    approximately). Thresholds are set and applied by actual letters."""
    n = r["letters"]
    for b in BINS:
        if b[0] <= n <= b[1]:
            return b
    return BINS[-1] if n > BINS[-1][1] else BINS[0]


def bname(b):
    return f"{b[0]}-{b[1]}"


def wilson(k, n):
    if n == 0:
        return (0.0, 1.0)
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def cap_rule_table(W):
    """What the proposed cap rule yields, in SYMBOL edits: structural symbols (E1/E2/E3 runs,
    a run of L counts L) per message under the unread-scaled damage model, by length (simulated;
    no unread text). The census's minimal symbol-edit distance is given beside it."""
    power.init_globals(write=False)
    rng = random.Random(7)
    W("| message length (symbols) | simulated messages | p50 | p80 | p90 | p95 | events p90 |")
    W("|---|---|---|---|---|---|---|")
    out = {}
    for n in (60, 100, 150, 200, 250, 300, 400):
        xs, ev = [], []
        for _ in range(2000):
            ct = "".join(rng.choice("ADFGVX") for _ in range(n))
            _, log = power.damage(rng, ct, power.PROFILES, power.RUNS)
            st = [x for x in log if x["type"] in ("E1", "E2", "E3")]
            xs.append(sum(x.get("len", 1) for x in st))
            ev.append(len(st))
        out[n] = xs
        W(f"| {n} | {len(xs)} | {quant(xs,.5):g} | {quant(xs,.8):g} | {quant(xs,.9):g} | "
          f"{quant(xs,.95):g} | {quant(ev,.9):g} |")
    import csv as _csv
    rows = list(_csv.DictReader(l for l in open(os.path.join(ROOT, "results", "adfgvx-mutilation.csv"))
                                if not l.startswith("#")))
    c = [int(r["cost"]) for r in rows]
    W(f"\nFor reference, the census's minimal symbol-edit distance (sub + del + ins; the statistic "
      f"check-adfgvx reproduces on 590/591) over all {len(c)} solved entries: p50 {quant(c,.5):g}, "
      f"p80 {quant(c,.8):g}, p90 {quant(c,.9):g}, p95 {quant(c,.95):g}, max {max(c)}. It counts "
      f"substitutions too, which the edit search does not need to undo, and it is biased low "
      f"(results/adfgvx-mutilation.md).")
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="scan", choices=["scan", "creilly"])
    V = ap.parse_args().variant
    power.set_variant(V)
    T = (load(f"adfgvx-power-trials-F1-{V}.jsonl") + load(f"adfgvx-power-trials-F1-extranull-{V}.jsonl")
         + load(f"adfgvx-power-trials-F2-planted-{V}.jsonl") + load(f"adfgvx-power-trials-F2-null-{V}.jsonl")
         + load(f"adfgvx-power-trials-F2-extranull-{V}.jsonl"))
    F3 = load(f"adfgvx-power-f3-{V}.jsonl")
    L = []
    W = L.append
    W("# ADFGVX 1918: power test of the attacks, planted and solved data only"
      + (" (SECONDARY: creilly-scaled)" if V == "creilly" else "") + "\n")
    W(prov_header("", "search/adfgvx/power.py; search/adfgvx/powerreport.py"))
    if V == "scan":
        W("**Variant: SCAN (primary).** The plant is scaled to the scan transcription of the "
          "unread entries (ciphertexts/adfgvx-1918-scan-transcription.json, as units from "
          f"search/adfgvx/scan.py): {100*power.LOST_RATE:.2f} lost slots per 100 and "
          f"{100*power.ODD_RATE:.1f}% odd length (creilly's text gave 3.59 and 34.9%; the scan "
          "keeps the lost-group runs creilly omits and counts non-ADFGVX letters as lost). "
          "Cluster compositions: the derived groups of results/adfgvx-clusters-scan.csv, "
          f"minus the {len(power.near_copies())} units the scan duplicate screen calls near-copies "
          "of solved messages (d < 0.2, p_entry < 0.01; results/adfgvx-duplicates-scan.csv), "
          "which are not attack targets. The creilly-scaled run is results/adfgvx-power-creilly.md.\n")
    else:
        W("**Variant: CREILLY (secondary).** Plant scaled to creilly's text of the unread entries "
          "(3.6 lost marks per 100 slots, 35% odd); compositions from results/adfgvx-clusters.csv "
          "(all creilly ids). The primary run is results/adfgvx-power.md.\n")
    W("No unread ciphertext was read. From the unread set this uses only the cluster "
      "compositions (member letter counts) and the two summary damage rates above.\n")
    W("**Evidence status.** Every rate here is [S]: sampled, with the trials, the sampling and "
      "the seeds stated, by one implementation (`search/adfgvx/jattack.c`, `power.py`). The "
      "thresholds are empirical maxima over the stated null trials, not proofs.\n")

    summary_at = len(L)
    SUM = []

    # ---------------- setup
    es, side = power.lm.split()
    ntrain = sum(1 for v in side.values() if v[0] == "train")
    W("## Setup\n")
    W(f"- **Leakage split** (`search/adfgvx/lm.py`): the 591 solved plaintexts are linked into "
      f"components by any shared 16-character substring (so repeated receptions and re-sent "
      f"messages stay together), and each component goes to TRAIN or PLANT by a seeded coin "
      f"(seed {power.lm.SEED}). TRAIN: {ntrain} entries, the scorer's only text. PLANT: the "
      f"rest; only those without unknown marks are planted (F1, F2); F3 uses plant-side "
      f"as-transcribed entries under their own key. No planted plaintext, and no near-copy of "
      f"one, is in the scorer's training text.")
    W(f"- **Scorer**: interpolated trigram model on A-Z0-9 (lambdas {power.lm.LAMBDA}), mean "
      f"natural-log probability per trigram.")
    W("- **Planted clusters (F1, F2)**: a random 36-cell square and a random transposition of "
      "the cell's width; one member per member of a real unread group in the cell's letter bin "
      "(group drawn uniformly among the bin's groups), each member's plaintext cut from a "
      "plant-side plaintext to half the member's letter count.")
    W(f"- **Damage, scaled to the unread set**: one census edit profile per message (types and "
      f"run lengths from results/adfgvx-mutilation.csv, random positions); E5 at "
      f"{power.E5_RATE}/symbol (the repeated-reception rate, not the census-visible one); lost "
      f"marks topped up to Poisson({power.LOST_RATE:.4f}/slot) in runs drawn from the SOLVED log's "
      f"run lengths; then the parity forced odd with probability {power.ODD_RATE:.3f} (one extra "
      f"deletion where needed).")
    W(f"- **Wrong-day intruders**: each member is, with probability {power.INTRUDER}, enciphered "
      f"under a different random key (the solved set's heading-date error rate against the "
      f"DERIVED key ranges, results/adfgvx-clusters.md s.1c). Recovery is measured on the "
      f"true-key members only.")
    W(f"- **Recovered** (F1, F2): the attack's key decrypts at least {int(power.RECOVER*100)}% "
      f"of the true-key members' plaintext characters correctly from their UNDAMAGED "
      f"ciphertexts. (F3: the best variant's decryption has difflib ratio >= "
      f"{power.RECOVER} to the true plaintext.)")
    W(f"- **Widths searched**: {WIDTHS[0]}-{WIDTHS[-1]} in every trial, planted and null "
      f"alike; the attack is not told the width.\n")

    # ---------------- F1, F2
    for fam, title in (("F1", "F1: unknown square + unknown transposition, joint over the cluster"),
                       ("F2", "F2: known square + unknown transposition, joint over the cluster")):
        P = [r for r in T if r["family"] == fam and r["kind"] == "planted"]
        N = [r for r in T if r["family"] == fam and r["kind"] != "planted"]
        if not P:
            continue
        W(f"## {title}\n")
        W(f"Budget (identical for planted and null trials): `{power.BUDGET[fam]}`; topw/NC as in "
          f"jattack.c. Planted trials: {len(P)}; null trials: {len(N)} "
          f"({sum(1 for r in N if r['kind']=='wrongperiod')} wrong-period, "
          f"{sum(1 for r in N if r['kind']=='shuffled')} shuffled).\n")
        thr = {}
        W("### Null: best score by letter bin (bin of the null cluster's ACTUAL letter count)\n")
        W("| bin (letters) | wrong-period n | max | p95 | shuffled n | max | p95 | threshold = max of both | FP for a NEW null draw, 1/(n+1) |")
        W("|---|---|---|---|---|---|---|---|---|")
        for b in BINS:
            a = [r["pscore"] for r in N if r["kind"] == "wrongperiod" and abin(r) == b]
            s = [r["pscore"] for r in N if r["kind"] == "shuffled" and abin(r) == b]
            if not (a or s):
                continue
            th = max(a + s)
            thr[b] = th
            n = len(a) + len(s)
            W(f"| {bname(b)} | {len(a)} | {max(a) if a else float('nan'):.3f} | "
              f"{quant(a,.95) if a else float('nan'):.3f} | {len(s)} | "
              f"{max(s) if s else float('nan'):.3f} | {quant(s,.95) if s else float('nan'):.3f} | "
              f"{th:.3f} | {1/(n+1):.4f} |")
        W("\n### Recovery rate by (cluster letters, width): recovered / trials\n")
        W("| bin \\ width | " + " | ".join(map(str, WIDTHS)) + " | all |")
        W("|---" * (len(WIDTHS) + 2) + "|")
        for b in BINS:
            cells = []
            tot = [0, 0]
            for k in WIDTHS:
                rs = [r for r in P if tuple(r["bin"]) == b and r["k"] == k]
                kk = sum(r["recovered"] for r in rs)
                cells.append(f"{kk}/{len(rs)}")
                tot[0] += kk
                tot[1] += len(rs)
            lo, hi = wilson(*tot)
            W(f"| {bname(b)} | " + " | ".join(cells) + f" | {tot[0]}/{tot[1]} ({100*tot[0]/max(tot[1],1):.0f}%, CI {100*lo:.0f}-{100*hi:.0f}) |")
        W("\n### Power at the proposed threshold: recovered AND score above the bin's null maximum\n")
        W("| bin \\ width | " + " | ".join(map(str, WIDTHS)) + " | all |")
        W("|---" * (len(WIDTHS) + 2) + "|")
        for b in BINS:
            cells = []
            tot = [0, 0]
            for k in WIDTHS:
                rs = [r for r in P if tuple(r["bin"]) == b and r["k"] == k]
                kk = sum(1 for r in rs if r["recovered"] and r["pscore"] > thr.get(abin(r), 9))
                cells.append(f"{kk}/{len(rs)}")
                tot[0] += kk
                tot[1] += len(rs)
            lo, hi = wilson(*tot)
            W(f"| {bname(b)} | " + " | ".join(cells) + f" | {tot[0]}/{tot[1]} ({100*tot[0]/max(tot[1],1):.0f}%, CI {100*lo:.0f}-{100*hi:.0f}) |")
        for b in BINS:
            rs = [r for r in P if tuple(r["bin"]) == b]
            if rs and b in thr:
                kk = sum(1 for r in rs if r["recovered"] and r["pscore"] > thr.get(abin(r), 9))
                lo, hi = wilson(kk, len(rs))
                SUM.append((fam, bname(b), kk, len(rs), lo, hi, thr[b],
                            sum(1 for r in N if abin(r) == b)))
        W("\n### Detection is not reading: above-threshold results that are WRONG\n")
        W("A planted cluster IS a single-key cluster, so its best key can beat every null without "
          "being right: a nearly right transposition plus an over-fitted substitution reads as "
          "German-looking text. The threshold therefore certifies shared-key STRUCTURE, not a "
          "reading.\n")
        W("| bin | planted | above threshold | of which recovered | above threshold but wrong (acc < 0.8) | P(correct reading given above threshold) | score range, recovered | score range, wrong-but-above |")
        W("|---|---|---|---|---|---|---|---|")
        for b in BINS:
            rs = [r for r in P if tuple(r["bin"]) == b]
            if not rs or b not in thr:
                continue
            ab = [r for r in rs if r["pscore"] > thr.get(abin(r), 9)]
            ok = [r for r in ab if r["recovered"]]
            bad = [r for r in ab if not r["recovered"]]
            rng_ = lambda xs: f"{min(xs):.3f} to {max(xs):.3f}" if xs else "-"
            W(f"| {bname(b)} | {len(rs)} | {len(ab)} | {len(ok)} | {len(bad)} | "
              f"{(len(ok)/len(ab)) if ab else float('nan'):.2f} | {rng_([r['pscore'] for r in ok])} | "
              f"{rng_([r['pscore'] for r in bad])} |")
        fa = [r for r in P if not r["recovered"] and r["pscore"] > thr.get(abin(r), 9)]
        W(f"\nPlanted trials NOT recovered yet scoring above the threshold (a wrong key that would "
          f"have been reported): {len(fa)}.\n")
        W("### Other measures\n")
        W("| bin | width found = planted | mean accuracy | median CPU s (planted) | median CPU s (null) | max CPU s |")
        W("|---|---|---|---|---|---|")
        for b in BINS:
            rs = [r for r in P if tuple(r["bin"]) == b]
            ns = [r for r in N if abin(r) == b]
            if not rs:
                continue
            W(f"| {bname(b)} | {sum(r['width_found']==r['k'] for r in rs)}/{len(rs)} | "
              f"{sum(r['acc'] for r in rs)/len(rs):.2f} | {quant([r['cpu_s'] for r in rs],.5):.1f} | "
              f"{quant([r['cpu_s'] for r in ns],.5) if ns else float('nan'):.1f} | "
              f"{max(r['cpu_s'] for r in rs + ns):.1f} |")
        W(f"\nTotal CPU: planted {sum(r['cpu_s'] for r in P)/3600:.2f} h, null "
          f"{sum(r['cpu_s'] for r in N)/3600:.2f} h.\n")

    # ---------------- F3
    f3thr = {}
    Pp = Nw = Ns = []
    if F3:
        W("## F3: known key + edit search up to a cap (single messages)\n")
        Pp = [r for r in F3 if r["kind"] == "planted"]
        Nw = [r for r in F3 if r["kind"] == "wrongkey"]
        Ns = [r for r in F3 if r["kind"] == "shuffled"]
        W(f"Messages: plant-side as-transcribed solved entries under one of Lasry's 14 keys "
          f"(their log text is the true ciphertext), damaged as above. Edit alphabet per event: "
          f"delete 1, insert 1 unknown, delete a 5-group, insert 5 unknowns (substitutions are "
          f"not searched: they do not shift the text). Planted {len(Pp)}; null: {len(Nw)} "
          f"wrong-key (the same damaged message under another of the 14 keys, same search) and "
          f"{len(Ns)} shuffled (true key, shuffled ciphertext). Cap 3 on the first "
          f"{power.F3_CAP3_SUBSET} of each.\n")
        caps = sorted({int(k[3:]) for r in F3 for k in r if k.startswith("cap") and isinstance(r[k], dict)})
        W("| cap | variants per message (median) | planted recovered | null max (wrong key) | null max (shuffled) | threshold | n null | power at threshold | FP for a new null draw, 1/(n+1) | median CPU s |")
        W("|---|---|---|---|---|---|---|---|---|---|")
        for c in caps:
            k = f"cap{c}"
            pr = [r for r in Pp if isinstance(r.get(k), dict)]
            nw = [r[k]["score"] for r in Nw if isinstance(r.get(k), dict)]
            ns = [r[k]["score"] for r in Ns if isinstance(r.get(k), dict)]
            th = max(nw + ns)
            f3thr[c] = th
            pw = sum(1 for r in pr if r[k]["recovered"] and r[k]["score"] > th)
            W(f"| {c} | {quant([r[k]['variants'] for r in pr],.5):g} | "
              f"{sum(r[k]['recovered'] for r in pr)}/{len(pr)} | {max(nw):.3f} | {max(ns):.3f} | "
              f"{th:.3f} | {len(nw)+len(ns)} | {pw}/{len(pr)} ({100*pw/len(pr):.0f}%) | "
              f"{1/(len(nw)+len(ns)+1):.4f} | "
              f"{quant([r[k]['cpu'] for r in pr],.5):.2f} |")
        W("\nRecovery by planted structural events (E1/E2/E3 runs, after damage) and cap; "
          "recovered / trials:\n")
        W("| structural events | " + " | ".join(f"cap {c}" for c in caps) + " | at threshold, cap 2 |")
        W("|---" * (len(caps) + 2) + "|")
        for ev in (0, 1, 2, 3):
            rs = [r for r in Pp if (r["n_struct"] == ev if ev < 3 else r["n_struct"] >= 3)]
            if not rs:
                continue
            cells = []
            for c in caps:
                k = f"cap{c}"
                q = [r for r in rs if isinstance(r.get(k), dict)]
                cells.append(f"{sum(r[k]['recovered'] for r in q)}/{len(q)}")
            at = sum(1 for r in rs if r["cap2"]["recovered"] and r["cap2"]["score"] > f3thr.get(2, 9))
            W(f"| {ev if ev < 3 else '3+'} | " + " | ".join(cells) + f" | {at}/{len(rs)} |")
        W("\nRecovery by message length (cap 2):\n")
        W("| length | trials | recovered | at threshold |")
        W("|---|---|---|---|")
        for lo_, hi_ in ((60, 149), (150, 249), (250, 349), (350, 999)):
            rs = [r for r in Pp if lo_ <= r["n"] <= hi_]
            if rs:
                W(f"| {lo_}-{hi_} | {len(rs)} | {sum(r['cap2']['recovered'] for r in rs)} | "
                  f"{sum(1 for r in rs if r['cap2']['recovered'] and r['cap2']['score'] > f3thr[2])} |")
        W("")

    SYMCAPS = (0, 1, 2, 5, 6, 10)
    JUMP = {}
    if F3 and all("bestsym" in r.get("cap2", {}) for r in F3):
        def best_le(c, M):
            """best score and its exact symbol cost among variants with total symbol cost <= M"""
            xs = [(c["bestsym"][z], z) for z in range(min(M, 15) + 1) if c["bestsym"][z] > -98]
            return max(xs) if xs else (-99, 0)
        W("### F3 with the cap in SYMBOL EDITS\n")
        W("check-adfgvx agrees with this census on minimal symbol-edit distance (590/591) but not "
          "on event typing, so the cap is stated in symbols: a variant's cost is the number of "
          "symbols it deletes or inserts (a 5-group edit costs 5). Searched: every variant of at "
          "most 2 edits (the cap-2 run), so the reachable costs are 0, 1, 2, 5, 6, 10. For each "
          "symbol cap M: the best variant of cost <= M; recovered = its decryption has difflib "
          "ratio >= 0.8 to the truth (the variant's edits replayed in Python and checked against "
          "jattack on the overall best); threshold = max over the 400 nulls of their best of cost "
          "<= M.\n")
        W("| symbol cap M | planted recovered | threshold | power at threshold | FP for a new null draw |")
        W("|---|---|---|---|---|")
        symthr = {}
        for M in SYMCAPS:
            nn = [best_le(r["cap2"], M)[0] for r in Nw + Ns]
            th = max(nn)
            symthr[M] = th
            rec_ = pw = 0
            for r in Pp:
                sc, z = best_le(r["cap2"], M)
                ok = r["cap2"]["symratio"][z] >= power.RECOVER
                rec_ += ok
                pw += ok and sc > th
            W(f"| {M} | {rec_}/{len(Pp)} | {th:.3f} | {pw}/{len(Pp)} ({100*pw/len(Pp):.0f}%) | {1/(len(nn)+1):.4f} |")
        W("\nPlanted structural damage in SYMBOLS (E1/E2/E3, after damage), and recovery at each "
          "symbol cap:\n")
        W("| planted symbol edits | messages | " + " | ".join(f"M={M}" for M in SYMCAPS) + " |")
        W("|---" * (len(SYMCAPS) + 2) + "|")
        for lo_, hi_ in ((0, 0), (1, 1), (2, 2), (3, 5), (6, 10), (11, 999)):
            rs = [r for r in Pp if lo_ <= r["n_struct_sym"] <= hi_]
            if not rs:
                continue
            cells = []
            for M in SYMCAPS:
                k_ = 0
                for r in rs:
                    sc, z = best_le(r["cap2"], M)
                    k_ += r["cap2"]["symratio"][z] >= power.RECOVER and sc > symthr[M]
                cells.append(f"{k_}/{len(rs)}")
            W(f"| {lo_}{'' if lo_ == hi_ else '-' + (str(hi_) if hi_ < 999 else 'up')} | {len(rs)} | " + " | ".join(cells) + " |")
        # jump statistic
        W("\n### The edit-jump statistic (adversary baseline: a true key jumps on one edit, a wrong "
          "key creeps)\n")
        W("J = the largest gain in best score from one more edit: max(best(1 edit) - best(0), "
          "best(2 edits) - best(1 edit)), from the cap-2 run; per-trigram natural-log units (the "
          "adversary's +2.4-3.7 is in log10 per quadgram, so the numbers differ, the shape is "
          "the question). Creep = mean gain per edit.\n")
        def J(c):
            b = c["bestev"]
            return max(b[1] - b[0], b[2] - b[1])
        def creep(c):
            b = c["bestev"]
            return (b[2] - b[0]) / 2
        grp = [("planted, >= 1 planted structural event", [r["cap2"] for r in Pp if r["n_struct"] >= 1]),
               ("planted, no structural event", [r["cap2"] for r in Pp if r["n_struct"] == 0]),
               ("null: wrong key", [r["cap2"] for r in Nw]), ("null: shuffled", [r["cap2"] for r in Ns])]
        W("| set | n | J median | J p90 | J max | creep median |")
        W("|---|---|---|---|---|---|")
        for nm, cs in grp:
            js = [J(c) for c in cs]
            W(f"| {nm} | {len(cs)} | {quant(js,.5):.3f} | {quant(js,.9):.3f} | {max(js):.3f} | "
              f"{quant([creep(c) for c in cs],.5):.3f} |")
        jn = [J(r["cap2"]) for r in Nw + Ns]
        jthr = max(jn)
        JUMP.update(thr=jthr, n=len(jn))
        dmg = [r for r in Pp if r["n_struct"] >= 1]
        hit = sum(1 for r in dmg if J(r["cap2"]) > jthr)
        hitrec = sum(1 for r in dmg if J(r["cap2"]) > jthr and r["cap2"]["recovered"])
        both = sum(1 for r in dmg if J(r["cap2"]) > jthr and r["cap2"]["recovered"] and r["cap2"]["score"] > f3thr.get(2, 9))
        W(f"\nJ threshold = the null maximum, {jthr:.3f} (n = {len(jn)} nulls, FP for a new draw "
          f"{1/(len(jn)+1):.4f}). Of the {len(dmg)} planted messages with at least one structural "
          f"event, {hit} have J above it ({hitrec} of them recovered); {both} pass BOTH the J "
          f"threshold and the cap-2 score threshold. Planted messages with no structural event "
          f"need no jump (their cap-0 score already reads) and are not a test of J.\n")
        JUMP.update(hit=hit, n_dmg=len(dmg), both=both)

    # ---------------- summary (inserted near the top)
    S = ["## Summary\n",
         "Power = share of planted clusters whose key is recovered AND whose score beats the "
         "maximum score of every null trial in the same letter bin (the proposed threshold).\n",
         "| family | letters | power | 95% CI | threshold (score) | null trials in bin |",
         "|---|---|---|---|---|---|"]
    for fam, b, kk, n, lo, hi, th, nn in SUM:
        S.append(f"| {fam} | {b} | {kk}/{n} ({100*kk/n:.0f}%) | {100*lo:.0f}-{100*hi:.0f}% | {th:.3f} | {nn} |")
    if F3:
        for c in sorted(f3thr):
            k = f"cap{c}"
            pr = [r for r in Pp if isinstance(r.get(k), dict)]
            pw = sum(1 for r in pr if r[k]["recovered"] and r[k]["score"] > f3thr[c])
            lo, hi = wilson(pw, len(pr))
            S.append(f"| F3 cap {c} | single messages | {pw}/{len(pr)} ({100*pw/len(pr):.0f}%) | "
                     f"{100*lo:.0f}-{100*hi:.0f}% | {f3thr[c]:.3f} | "
                     f"{sum(1 for r in Nw + Ns if isinstance(r.get(k), dict))} |")
    S.append("")
    L[summary_at:summary_at] = S

    # ---------------- cap rule
    W("## Proposed mutilation-cap rule (A1), in SYMBOL edits: what it yields\n")
    W("Rule proposed, not applied: **M(N) = the 90th percentile of structural SYMBOL edits per "
      "message of length N** (E1/E2/E3 runs, a run of L symbols counting L) under the "
      "unread-scaled damage model above, searched as edit sets of at most 2 edits whose total "
      "symbol cost is <= M. Symbol edits are the unit both implementations agree on. The "
      "statistic is fixed by the rule before any unread text is touched; it uses the census "
      "and the unread summary rates only. Simulated (2,000 damaged random messages per "
      "length):\n")
    cap_rule_table(W)
    W("")
    W("## Recommendations for the J prereg (proposed, not applied)\n")
    W("1. **Decision statistic and threshold.** Use the penalised trigram score of the final "
      "key. Fix the threshold per family and per cluster-letter bin as the maximum over the "
      "null trials of that bin (wrong-period and shuffled pooled), exactly as tabulated above. "
      "That is about 200 null trials per bin, so 10/alpha holds at alpha = 0.05 per bin. A "
      "threshold set at the maximum of n nulls has a false-positive rate of 1/(n+1) for a new "
      "null draw (about 0.5% here), per bin and per family; across bins and families these "
      "add, and the trials factor must say so. The "
      "real run must use the identical pipeline, budget, widths and scorer: any change "
      "invalidates the threshold.")
    W("1b. **The nulls are optimised.** Every null trial (wrong-period clusters, shuffled "
      "clusters, F3 wrong keys and shuffles) runs through the identical solver, budget, widths "
      "and edit search as the planted trials, so the thresholds are best-of-optimised-null, "
      "as the adversary baseline requires; random-key nulls are not used.")
    W("2. **Above threshold is a DETECTION, not a reading.** In the planted runs a single-key "
      "cluster can beat every null with a wrong key (tables 'Detection is not reading'). A "
      "reading needs a second, pre-registered gate: reproduction by check-adfgvx from method "
      "and key, the adversary failing to match, and (proposed) the decryption passing a fixed "
      "word-coverage or n-gram criterion calibrated on the 'wrong but above threshold' planted "
      "cases above.")
    W("3. **Mutilation cap in symbol edits,** by the rule in the last section, searched as at "
      "most 2 edits. The rule's M(N) is the 90th percentile in the table there; the search can "
      "only reach total costs 0, 1, 2, 5, 6 and 10, so M maps to the smallest reachable cost >= "
      "M (M = 3, 4 or 5 all map to 5: one 5-group edit, or up to two single-symbol edits). The "
      "symbol-cap table above gives the power at each reachable M. Cap 3 "
      "costs ~200x the CPU per message (2.4e7 variants) and showed no gain in its 20-message "
      "sample. Edit freedom counts as key bits (A2): the variant counts per message are in the "
      "F3 table and belong in the trials factor.")
    if JUMP:
        W(f"3b. **Edit-jump statistic as a second pre-registered test (adversary baseline).** "
          f"J > {JUMP['thr']:.3f} (the max over {JUMP['n']} optimised nulls) was reached by "
          f"{JUMP['hit']}/{JUMP['n_dmg']} damaged planted messages; {JUMP['both']} pass both J and "
          f"the score threshold. It costs nothing extra (same search) and its FP for a new null "
          f"draw is 1/(n+1). With optimised nulls on THIS scorer it is a weak test: shuffled "
          f"nulls jump almost as far as true keys (J table), so it should be pre-registered, if "
          f"at all, as a secondary test with its own null threshold, not as the gate.")
    W("4. **Budget.** The F1 search is budget-limited at the larger odd widths, 21 above all. On "
      "an undamaged 1,500-letter width-21 cluster, the true order scores 0.104 on the phase-A "
      "statistic and the search found only 0.081, so this is a search failure, not missing "
      "information (diagnostic run 2026-11-01, not part of the tables). A negative for a "
      "width-21 key at this budget is a statement about the method, not the cipher. The prereg "
      "should either raise the budget for widths 19-21 and re-run these controls at it, or "
      "state that limit.")
    W("   The maximum is a fragile statistic where the null tail is thin. Example: when nulls "
      "were binned by the composition they were drawn for rather than by their actual letter "
      "count, one 256-letter wrong-period null (-2.647) sat in the 300-699 bin and F2's power "
      "there fell from 38/160 to 13/160. Bin by ACTUAL letters, as here, and fix the rule (max "
      "over the stated nulls) in the prereg; a larger null set per bin would make it steadier.")
    W("5. **Small clusters.** Below 300 cipher letters no F1 or F2 result clears its null, and "
      "F1 gets nothing below 700. Below 300, only a known key (F3, per message) has power.\n")
    W("## What this does not establish\n")
    W("- **Generality.** Every rate is [S], for this scorer, this budget and this damage model. "
      "The scorer is a trigram model on ~30k characters of period text; a larger corpus or "
      "quadgrams could raise power.")
    W("- **The real damage of the unread entries.** The model is the census plus the lead's "
      "two unread summary rates. It has no clerk errors (E6), no keys outside the list (E8), "
      "and intruders only at the 3% derived-range rate; the 20.1% published-period rate was "
      "not run.")
    W("- **The real cluster compositions.** The compositions are the derived groups' letter "
      "counts, including entries the duplicate screen (results/adfgvx-duplicates.md) found to "
      "be copies of solved messages. Removing those shrinks several groups, which moves them "
      "to lower-power bins.")
    W("- **Independence.** One implementation (search/adfgvx/jattack.c, power.py). Not "
      "reproduced by check-adfgvx.")
    W("- **Runtime.** Every number is CPU seconds on a shared 8-core box (load average 25-100 "
      "during the runs); wall time is not meaningful.\n")
    open(os.path.join(ROOT, "results", "adfgvx-power.md" if V == "scan" else "adfgvx-power-creilly.md"),
         "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
