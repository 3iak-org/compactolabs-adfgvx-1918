"""R1 under the prereg: search-family null.  Budget B (same for the real entry and every null).
 real    : parts 5,6 (creilly = Schmeh, identical), 5 seeds
 shuffle : 100 runs, known symbols shuffled within each part among known positions; the 15-symbol hole stays at 5..19
 decoy   : 100 runs, decoys_r1.json (committed at f821aa8 before any decoy was scored)
 planted : 24 runs (power), from other entries' plaintext
Width 18 only (see REPORT for the width-trial caveat)."""
import sys, json, random, time, zlib, multiprocessing as mp
import data as D, trials, r1_solver as S, planted as P

B = dict(S.BUDGET); B["full_top"] = 5; B["topk"] = 300
R = D.by_id()
C5 = R["p156C3"]["printed"]; C6 = R["p156C6"]["printed"].replace("?", "-")
dec = json.load(open("decoys_r1.json"))["decoys"]
pool = P.plaintexts()

def parts_for(kind, i):
    if kind == "real": return [C5, C6]
    if kind == "shuffle":
        rng = random.Random("shuf%d" % i); out = []
        for c in (C5, C6):
            known = [k for k, ch in enumerate(c) if ch != "-"]; sy = [c[k] for k in known]; rng.shuffle(sy)
            l = list(c)
            for k, ch in zip(known, sy): l[k] = ch
            out.append("".join(l))
        return out
    if kind == "decoy":
        d = dec[i]; a = R[d["part5_from"]]["printed"][:132]; b = R[d["part6_from"]]["printed"][:108]
        return [a, b[:5] + "-" * 15 + b[20:]]
    if kind == "planted":
        rid, key, sq, parts = P.make(i, pool); return parts

def job(t):
    kind, i = t
    parts = parts_for(kind, i); t0 = time.process_time()
    m, key, sq, ic = S.run_budget(parts, 18, zlib.crc32(("%s%d" % (kind, i)).encode()) % 100000, B)
    return dict(kind=kind, i=i, score=m, key=key, ic=ic, cpu=time.process_time() - t0)

if __name__ == "__main__":
    out = sys.argv[1]; nn = int(sys.argv[2])
    trials.log(phase="prereg-run", entry="R1", task="search-family null (stage1 IC hill-climb width 18 + stage2 square hill-climb, LIT)", budget=B, n_real=3, n_shuffle=nn, n_decoy=nn, n_planted=12, note="restarted with smaller budget after first launch (aborted, results kept as r1_prereg_aborted) because the box was saturated; budget identical for real and null runs", decoys_commit="f821aa8", scorer_commit="50b772c", transcription="creilly@e60da03 == Schmeh2017 for p156C3/C6 (identical)")
    tasks = [("real", i) for i in range(3)]
    for i in range(nn):
        tasks += [("shuffle", i), ("decoy", i)]
        if i < 12: tasks += [("planted", i)]
    with mp.Pool(8) as p, open(out, "w") as f:
        for r in p.imap_unordered(job, tasks, chunksize=1):
            f.write(json.dumps(r) + "\n"); f.flush()
