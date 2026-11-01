"""Power test of the ADFGVX attacks on PLANTED and SOLVED data only (comp-adfgvx, 2026-11-01).
No unread ciphertext is read: the only things taken from the unread set are the cluster
compositions (member letter counts per derived group, results/adfgvx-clusters.csv) and the
summary damage rates the lead specified (lost marks 3.6/100 slots, odd length 35%).

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/power.py [--pilot]

Families (referee A5):
  F1  unknown square + unknown transposition, joint over a cluster   (jattack MODE 1)
  F2  known square + unknown transposition, joint                    (jattack MODE 2)
  F3  known key + edit search up to a cap, per message               (jattack MODE 3)
Scorer: trigram model trained on the TRAIN side of lm.py's component split; every planted
plaintext comes from the PLANT side (no leakage). Raw per-trial records go to
results/adfgvx-power-trials.jsonl; the report to results/adfgvx-power.md.
"""
import argparse
import csv
import json
import math
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from difflib import SequenceMatcher

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
import lm  # noqa: E402
from engine import encrypt, decrypt, LAB  # noqa: E402
from plant import random_key, census_profiles, mutilate  # noqa: E402
from provenance import header as prov_header  # noqa: E402
import sharing  # noqa: E402

TMP = os.environ.get("TMPDIR", "/tmp")
JAT = os.path.join(TMP, "adfgvx-jattack")
LMT = os.path.join(TMP, "adfgvx-lm3.txt")
WIDTHS = list(range(15, 23))
BINS = [(0, 299), (300, 699), (700, 1299), (1300, 2200)]
E5_RATE = 0.0066          # repeated-reception estimate per symbol per copy
# VARIANT selects the unread-side transcription the plant is scaled to (env ADFGVX_VARIANT):
#   scan    (primary, from 2026-11-01): lost-mark rate and odd-length share computed from the
#           scan transcription's units (search/adfgvx/scan.py, primary reading); compositions
#           from results/adfgvx-clusters-scan.csv minus the units the scan duplicate screen
#           calls near-copies of solved messages (d < 0.2, p_entry < 0.01)
#   creilly (secondary): 0.036 lost per slot, 35% odd, compositions from adfgvx-clusters.csv
VARIANT = os.environ.get("ADFGVX_VARIANT", "scan")
LOST_RATE = 0.036         # unread: lost marks per slot (creilly); scan value set in set_variant
ODD_RATE = 0.35           # unread: share of odd-length entries (creilly)
NEAR_COPY_D = 0.2


def set_variant(v):
    global VARIANT, LOST_RATE, ODD_RATE
    VARIANT = v
    os.environ["ADFGVX_VARIANT"] = v
    if v == "scan":
        import scan
        us, _ = scan.units()
        P = [u["primary"] for u in us]
        LOST_RATE = sum(p.count("-") for p in P) / sum(map(len, P))
        ODD_RATE = sum(len(p) % 2 for p in P) / len(P)
    else:
        LOST_RATE, ODD_RATE = 0.036, 0.35


def near_copies():
    p = os.path.join(ROOT, "results", "adfgvx-duplicates-scan.csv")
    rows = list(csv.DictReader(l for l in open(p) if not l.startswith("#")))
    return {r["unread"] for r in rows if r["d_solved"] and float(r["d_solved"]) < NEAR_COPY_D
            and float(r["p_entry_solved"]) < 0.01}
INTRUDER = 0.03           # wrong-day intruder rate: heading date outside the DERIVED range
INTRUDER_HI = 0.201       # sensitivity: heading date outside the PUBLISHED period
RECOVER = 0.8             # recovered = >= 80% of true-key plaintext characters right
BUDGET = {"F1": dict(SCREENW=2, SCREENR=3, SCREENI=20000, RESTARTS=8, SAITERS=40000,
                     SAT0=0.001, TOPW=2, LAMB=5.0)}
BUDGET["F2"] = dict(SCREENW=2, SCREENR=3, SCREENI=40000, RESTARTS=10, SAITERS=100000, SAT0LM=0.1)


def build_tools(write=True):
    src = os.path.join(HERE, "jattack.c")
    if write:
        subprocess.check_call(["cc", "-O2", "-o", JAT + ".tmp", src, "-lm"])
        os.replace(JAT + ".tmp", JAT)
    es, side, tab, N, plant = lm.build(LMT if write else None)
    cnt = Counter(c for e in es if side[e["id"]][0] == "train" for c in e["plaintext"] if c in lm.IDX)
    freq = "".join(sorted(lm.ALPH, key=lambda c: -cnt[c]))
    return es, side, tab, N, plant, freq


def jattack(job):
    import resource
    u0 = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
    out = subprocess.run([JAT, LMT], input=job, capture_output=True, text=True, check=True).stdout
    d = dict(l.split("=", 1) for l in out.splitlines() if "=" in l)
    d["_cpu"] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime - u0
    return d


def compositions():
    f = "adfgvx-clusters-scan.csv" if VARIANT == "scan" else "adfgvx-clusters.csv"
    rows = list(csv.DictReader(l for l in open(os.path.join(ROOT, "results", f))
                               if not l.startswith("#")))
    drop = near_copies() if VARIANT == "scan" else set()
    g = defaultdict(list)
    for r in rows:
        if r["id"] in drop:
            continue
        if int(r["n_letters"]) >= 20:
            g[r["derived_period"]].append(int(r["n_letters"]))
    comps = {b: [] for b in BINS}
    for name, ls in g.items():
        t = sum(ls)
        for b in BINS:
            if b[0] <= t <= b[1]:
                comps[b].append((name, sorted(ls, reverse=True)))
    return comps


def lost_runs():
    """Run lengths of '-' in the SOLVED log texts (the unread are not read)."""
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    runs = []
    for e in rec:
        if e["status"].startswith("Solved") and e["printed"]:
            r = 0
            for ch in e["printed"] + "A":
                if ch == "-":
                    r += 1
                elif r:
                    runs.append(r)
                    r = 0
    return runs


def damage(rng, ct, profiles, runs):
    """Unread-scaled mutilation. Returns (ct, log)."""
    _, evs = rng.choice(profiles)
    n = len(ct)
    n5 = sum(1 for _ in range(n) if rng.random() < E5_RATE)
    ct, log = mutilate(rng, ct, list(evs) + [("E5", 1, None)] * n5)
    target = sum(1 for _ in range(len(ct)) if rng.random() < LOST_RATE)
    c = list(ct)
    while c.count("-") < target and c:
        L = min(rng.choice(runs), max(1, target - c.count("-")))
        p = rng.randrange(max(1, len(c) - L + 1))
        c[p:p + L] = ["-"] * min(L, len(c) - p)
        log.append({"type": "E4", "op": "lost", "pos": p, "len": L})
    ct = "".join(c)
    want_odd = rng.random() < ODD_RATE
    if (len(ct) % 2 == 1) != want_odd:
        p = rng.randrange(len(ct))
        ct = ct[:p] + ct[p + 1:]
        log.append({"type": "E1", "op": "del", "pos": p, "len": 1, "parity": True})
    return ct, log


def take(rng, pool, nchar, used):
    cands = [x for x in pool if x[0] not in used and len(x[1]) >= nchar]
    if cands:
        i, p, _ = rng.choice(cands)
        used.add(i)
        s = rng.randrange(len(p) - nchar + 1)
        return p[s:s + nchar], [i]
    buf, ids = "", []
    while len(buf) < nchar:
        i, p, _ = rng.choice([x for x in pool if x[0] not in used] or pool)
        used.add(i)
        buf += p
        ids.append(i)
    return buf[:nchar], ids


def planted_cluster(rng, comp, k, pool, profiles, runs, intruder):
    sq, tr = random_key(rng, k)
    used = set()
    msgs = []
    for L in comp:
        pt, ids = take(rng, pool, max(10, L // 2), used)
        intr = rng.random() < intruder
        if intr:
            s2, t2 = random_key(rng, rng.choice(WIDTHS))
            true = encrypt(pt, s2, t2)
        else:
            true = encrypt(pt, sq, tr)
        ct, log = damage(rng, true, profiles, runs)
        msgs.append({"pt": pt, "from": ids, "true": true, "ct": ct, "edits": log, "intruder": intr})
    return {"square": sq, "trans": tr, "msgs": msgs}


def accuracy(cl, sq, tr):
    """Share of true-key plaintext characters that the recovered key decrypts correctly from the
    TRUE (undamaged) ciphertexts."""
    ok = tot = 0
    for m in cl["msgs"]:
        if m["intruder"]:
            continue
        d = decrypt(m["true"], sq, tr)
        ok += sum(1 for a, b in zip(d, m["pt"]) if a == b)
        tot += len(m["pt"])
    return ok / tot if tot else 0.0


def ratio(cl, sq, tr):
    """Alignment-invariant accuracy: difflib ratio of decrypted true ciphertext to plaintext,
    weighted by length, true-key members only (catches keys equivalent up to a shift)."""
    num = den = 0
    for m in cl["msgs"]:
        if m["intruder"]:
            continue
        d = decrypt(m["true"], sq, tr)
        num += SequenceMatcher(None, d, m["pt"], autojunk=False).ratio() * len(m["pt"])
        den += len(m["pt"])
    return num / den if den else 0.0


def job_text(mode, msgs, seed, freq, square=None):
    b = BUDGET["F1" if mode == 1 else "F2"]
    s = f"MODE {mode}\nWIDTHS {' '.join(map(str, WIDTHS))}\nSEED {seed}\nFREQ {freq}\n"
    s += "".join(f"{k} {v}\n" for k, v in b.items())
    if square:
        s += f"SQUARE {square}\n"
    s += "".join(f"MSG {m}\n" for m in msgs)
    return s


def run_trial(t):
    """t: dict(kind, family, ...). Returns the record."""
    t0 = time.time()
    rng = random.Random(t["seed"])
    rec = dict(t)
    if t["kind"] == "planted":
        cl = planted_cluster(rng, t["comp"], t["k"], POOL, PROFILES, RUNS, t["intruder"])
        msgs = [m["ct"] for m in cl["msgs"]]
        d = jattack(job_text(1 if t["family"] == "F1" else 2, msgs, t["seed"], FREQ,
                             cl["square"] if t["family"] == "F2" else None))
        sq = d["best_square"]
        tr = list(map(int, d["best_trans"].split()))
        acc = accuracy(cl, sq, tr) if len(tr) == t["k"] else 0.0
        rec.update(score=float(d["best_score"]), pscore=float(d["best_pscore"]),
                   found_trans=d["best_trans"], found_square=sq,
                   ratio=ratio(cl, sq, tr),
                   width_found=int(d["best_width"]), acc=acc,
                   recovered=acc >= RECOVER, trans_exact=(tr == cl["trans"]),
                   n_intruders=sum(m["intruder"] for m in cl["msgs"]),
                   n_edits=sum(len([x for x in m["edits"] if x["type"] != "E4"]) for m in cl["msgs"]),
                   letters=sum(len(m["ct"]) for m in cl["msgs"]))
    elif t["kind"] == "shuffled":
        cl = planted_cluster(rng, t["comp"], t["k"], POOL, PROFILES, RUNS, t["intruder"])
        msgs = ["".join(rng.sample(m["ct"], len(m["ct"]))) for m in cl["msgs"]]
        d = jattack(job_text(1 if t["family"] == "F1" else 2, msgs, t["seed"], FREQ,
                             cl["square"] if t["family"] == "F2" else None))
        rec.update(score=float(d["best_score"]), pscore=float(d["best_pscore"]),
                   width_found=int(d["best_width"]), letters=sum(map(len, msgs)))
    elif t["kind"] == "wrongperiod":
        # A3: real solved log texts, every member from a DIFFERENT key
        keys = list(NULLPOOL_KEYS)   # local copy: shuffling the global list made each null
        rng.shuffle(keys)            # depend on which trials its worker had run before
        msgs, keys_used = [], []
        for L, key in zip(t["comp"], keys):
            cands = sorted(NULLPOOL[key], key=lambda e: abs(len(e) - L))[:5]
            msgs.append(rng.choice(cands))
            keys_used.append(key)
        sq = None
        if t["family"] == "F2":
            # a real period square, its blank cells filled with the unused symbols (shuffled), so
            # the null is scored like the planted trials' complete squares: blank cells would
            # let the search route pairs into unscored cells
            sq = list(KEYS[keys_used[0]]["square"])
            free = [c for c in lm.ALPH if c not in sq]
            rng.shuffle(free)
            sq = "".join(free.pop() if c == "?" else c for c in sq)
        d = jattack(job_text(1 if t["family"] == "F1" else 2, msgs, t["seed"], FREQ, sq))
        rec.update(score=float(d["best_score"]), pscore=float(d["best_pscore"]),
                   width_found=int(d["best_width"]), letters=sum(map(len, msgs)), keys=keys_used)
    rec["wall_s"] = time.time() - t0
    rec["cpu_s"] = d["_cpu"]
    rec.pop("comp", None)
    return rec


def init_globals(write=False):
    """write=True only in the parent: compiles jattack and writes the LM table once."""
    global POOL, PROFILES, RUNS, FREQ, NULLPOOL, NULLPOOL_KEYS, KEYS
    set_variant(os.environ.get("ADFGVX_VARIANT", "scan"))
    es, side, tab, N, plant, FREQ = build_tools(write)
    POOL = plant
    PROFILES = census_profiles()
    RUNS = lost_runs()
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    KEYS = {k["id"]: k for k in json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.keys.json")))}
    NULLPOOL = defaultdict(list)
    for e in rec:
        if e["status"].startswith("Solved") and e["key"] and e["printed"] and len(e["printed"]) >= 20:
            NULLPOOL[e["key"]].append(e["printed"])
    NULLPOOL_KEYS = sorted(NULLPOOL)


POOL = PROFILES = RUNS = FREQ = NULLPOOL = NULLPOOL_KEYS = KEYS = None


def plan(pilot):
    comps = compositions()
    rng = random.Random(20261101)
    trials = []
    seed = 1000
    n_cell = 2 if pilot else 20
    n_null = 4 if pilot else 200
    for fam in ("F1", "F2"):
        for b in BINS:
            if not comps[b]:
                continue
            for k in (WIDTHS if not pilot else [16, 19]):
                for _ in range(n_cell):
                    name, comp = rng.choice(comps[b])
                    seed += 1
                    trials.append(dict(kind="planted", family=fam, bin=list(b), group=name, comp=comp,
                                       k=k, seed=seed, intruder=INTRUDER))
        for kind in ("wrongperiod", "shuffled"):
            for _ in range(n_null):
                b = rng.choice([b for b in BINS if comps[b]])
                name, comp = rng.choice(comps[b])
                comp = comp[:len(NULLPOOL_KEYS)]
                seed += 1
                trials.append(dict(kind=kind, family=fam, bin=list(b), group=name, comp=comp,
                                   k=rng.choice(WIDTHS), seed=seed, intruder=INTRUDER))
    return trials


EXTRA_PER_BIN = 50   # per null kind per bin, on top of plan(): brings every bin to ~200 nulls


def plan_extra():
    """Extra null trials, stratified by bin, in their own seed block (900001...) so that adding
    them does not move any seed of plan()."""
    comps = compositions()
    rng = random.Random(20261103)
    trials = []
    seed = 900000
    for fam in ("F1", "F2"):
        for kind in ("wrongperiod", "shuffled"):
            for b in BINS:
                if not comps[b]:
                    continue
                for _ in range(EXTRA_PER_BIN):
                    name, comp = rng.choice(comps[b])
                    comp = comp[:len(NULLPOOL_KEYS)]
                    seed += 1
                    trials.append(dict(kind=kind, family=fam, bin=list(b), group=name, comp=comp,
                                       k=rng.choice(WIDTHS), seed=seed, intruder=INTRUDER, extra=True))
    return trials


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--families", default="F1,F2")
    ap.add_argument("--jobs", type=int, default=sharing.MAX_JOBS)
    ap.add_argument("--kinds", default="planted,wrongperiod,shuffled")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--extra", action="store_true", help="run plan_extra() instead of plan()")
    ap.add_argument("--variant", default="scan", choices=["scan", "creilly"])
    a = ap.parse_args()
    sharing.be_nice()
    sharing.exclusive()
    a.jobs = sharing.jobs(a.jobs)
    set_variant(a.variant)
    init_globals(write=True)
    base = plan_extra() if a.extra else plan(a.pilot)
    trials = [t for t in base if t["family"] in a.families.split(",")
              and t["kind"] in a.kinds.split(",")]
    fams = "-".join(a.families.split(","))
    out = os.path.join(ROOT, "results", f"adfgvx-power-trials-{fams}{a.suffix}-{a.variant}" + ("-pilot" if a.pilot else "") + ".jsonl")
    t0 = time.time()
    with ProcessPoolExecutor(a.jobs, initializer=init_globals) as ex, open(out + ".part", "w") as f:
        for i, r in enumerate(ex.map(run_trial, trials, chunksize=1)):
            f.write(json.dumps(r) + "\n")
            f.flush()
    os.replace(out + ".part", out)
    print(f"{len(trials)} trials in {time.time() - t0:.0f} s wall -> {out}")


if __name__ == "__main__" and "--f3" not in sys.argv:
    main()


# ---------------------------------------------------------------- F3: known key + edit search
F3_CAPS = (0, 1, 2)
F3_CAP3_SUBSET = 20
F3_N = 200


def f3_pool():
    """Plant-side, as-transcribed solved entries under one of Lasry's 14 keys, >= 60 letters,
    no lost marks: their log text IS the true ciphertext under a known key."""
    es, side = lm.split()
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    lasry = ["sep19", "oct04", "oct28", "nov01", "nov04", "nov07", "nov10", "nov13_20",
             "nov13_16", "nov16", "nov19", "nov22", "nov25", "nov28"]
    out = []
    for e in rec:
        if (e["id"] in side and side[e["id"]][0] == "plant" and e["method"] == "period key, as transcribed"
                and e["key"] in lasry and e["printed"] and "-" not in e["printed"]
                and len(e["printed"]) >= 60 and len(e["printed"]) % 2 == 0):
            out.append(e)
    return out, lasry


def apply_edits_py(ct, edits):
    """Same semantics as jattack.c apply_edits: positions refer to the ORIGINAL string; at each
    position insertions are emitted before the symbol, deletions skip it."""
    ed = sorted(((int(p), t) for t, p in (x.split("@") for x in edits if x)), key=lambda z: z[0])
    out, i, ei = [], 0, 0
    n = len(ct)
    while i <= n:
        while ei < len(ed) and ed[ei][0] == i:
            t = ed[ei][1]
            if t == "ins1":
                out.append("-")
            elif t == "ins5":
                out.extend("-" * 5)
            elif t == "del1":
                i += 1
            else:
                i += 5
            ei += 1
        if i < n:
            out.append(ct[i])
        i += 1
    return "".join(out)


def symcap_ratios(ct, key, truth, d):
    """difflib ratio of the best variant at each symbol cost 0..15 (exact cost)."""
    res = []
    for ed in d["msg0_bestsymedits"].split(";"):
        v = apply_edits_py(ct, ed.split(",") if ed else [])
        pl = decrypt(v, key["square"], key["transposition"])
        res.append(SequenceMatcher(None, pl, truth, autojunk=False).ratio())
    return res


def f3_job(ct, key, cap):
    return (f"MODE 3\nSQUARE {key['square']}\nTRANS {len(key['transposition'])} "
            f"{' '.join(map(str, key['transposition']))}\nCAP {cap}\nMSG {ct}\n")


def run_f3(t):
    rng = random.Random(t["seed"])
    e = F3POOL[t["idx"]]
    key = KEYS[e["key"]]
    truth = decrypt(e["printed"], key["square"], key["transposition"])
    ct, log = damage(rng, e["printed"], PROFILES, RUNS)
    n_struct = sum(1 for x in log if x["type"] in ("E1", "E2", "E3"))
    rec = dict(t, id=e["id"], key=e["key"], n=len(e["printed"]), n_struct=n_struct,
               n_struct_sym=sum(x.get("len", 1) for x in log if x["type"] in ("E1", "E2", "E3")))
    caps = list(F3_CAPS) + ([3] if t["cap3"] else [])
    for cap in caps:
        if t["kind"] == "planted":
            d = jattack(f3_job(ct, key, cap))
            pl = d["msg0_plain"]
            ratio = SequenceMatcher(None, pl, truth, autojunk=False).ratio()
            # replay check: the Python edit/decrypt of the overall best must equal jattack's
            v = apply_edits_py(ct, d["msg0_edits"].strip().split(",") if d["msg0_edits"].strip() else [])
            dec = decrypt(v, key["square"], key["transposition"]).replace("?", "-")
            assert dec == pl, ("edit replay mismatch", e["id"], cap)
            rec[f"cap{cap}"] = dict(score=float(d["msg0_score"]), score0=float(d["msg0_score0"]),
                                    ratio=ratio, recovered=ratio >= RECOVER, edits=d["msg0_edits"].strip(),
                                    variants=int(d["msg0_variants"]), cpu=d["_cpu"],
                                    bestev=list(map(float, d["msg0_bestev"].split(","))),
                                    bestsym=list(map(float, d["msg0_bestsym"].split(","))),
                                    symratio=symcap_ratios(ct, key, truth, d))
        elif t["kind"] == "wrongkey":
            wk = KEYS[t["wrong"]]
            d = jattack(f3_job(ct, wk, cap))
            rec[f"cap{cap}"] = dict(score=float(d["msg0_score"]), variants=int(d["msg0_variants"]), cpu=d["_cpu"],
                                    bestev=list(map(float, d["msg0_bestev"].split(","))),
                                    bestsym=list(map(float, d["msg0_bestsym"].split(","))))
        else:  # shuffled under the true key
            sh = "".join(rng.sample(ct, len(ct)))
            d = jattack(f3_job(sh, key, cap))
            rec[f"cap{cap}"] = dict(score=float(d["msg0_score"]), variants=int(d["msg0_variants"]), cpu=d["_cpu"],
                                    bestev=list(map(float, d["msg0_bestev"].split(","))),
                                    bestsym=list(map(float, d["msg0_bestsym"].split(","))))
    return rec


F3POOL = None


def init_f3(write=False):
    global F3POOL
    init_globals(write)
    F3POOL, _ = f3_pool()


def main_f3(jobs):
    set_variant(os.environ.get("ADFGVX_VARIANT", "scan"))
    sharing.be_nice()
    sharing.exclusive()
    jobs = sharing.jobs(jobs)
    init_f3(write=True)
    pool, lasry = f3_pool()
    rng = random.Random(20261102)
    trials = []
    seed = 500000
    for i in range(F3_N):
        seed += 1
        trials.append(dict(kind="planted", family="F3", idx=rng.randrange(len(pool)), seed=seed,
                           cap3=i < F3_CAP3_SUBSET))
    for i in range(F3_N):
        seed += 1
        idx = rng.randrange(len(pool))
        wrong = rng.choice([k for k in lasry if k != pool[idx]["key"]])
        trials.append(dict(kind="wrongkey", family="F3", idx=idx, wrong=wrong, seed=seed,
                           cap3=i < F3_CAP3_SUBSET))
    for i in range(F3_N):
        seed += 1
        trials.append(dict(kind="shuffled", family="F3", idx=rng.randrange(len(pool)), seed=seed,
                           cap3=i < F3_CAP3_SUBSET))
    out = os.path.join(ROOT, "results", f"adfgvx-power-f3-{VARIANT}.jsonl")
    with ProcessPoolExecutor(jobs, initializer=init_f3) as ex, open(out + ".part", "w") as f:
        for r in ex.map(run_f3, trials, chunksize=2):
            f.write(json.dumps(r) + "\n")
            f.flush()
    os.replace(out + ".part", out)
    print(f"F3: {len(trials)} trials, pool {len(pool)} messages -> {out}")


if __name__ == "__main__" and "--f3" in sys.argv:
    main_f3(int(os.environ.get("F3JOBS", str(sharing.MAX_JOBS))))
