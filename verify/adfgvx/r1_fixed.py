"""R1 fixed-key rows (additional to the search-family null).  The claimed transposition is GIVEN; the square is searched
(stage-2 full tier: 100 restarts x 20 kicks, one seed per input).  Inputs: claim; 100 random width-18 keys on the real
ciphertext; 100 shuffles (hole fixed) under the claimed key; the 100 committed decoys (decoys_r1.json) under the claimed key.
Budget identical on every row: 100x20 per input."""
import sys, json, random, zlib, multiprocessing as mp
import numpy as np
import data as D, trials, r1_solver as S, kern as K, r1_repro as R1
import r1_run as RR
def job(t):
    kind, i = t
    key = R1.KEY18
    if kind == "claim": parts = [RR.C5, RR.C6]
    elif kind == "randkey":
        rng = random.Random("rk%d" % i); key = list(range(1, 19)); rng.shuffle(key); parts = [RR.C5, RR.C6]
    elif kind == "shuffle": parts = RR.parts_for("shuffle", i)
    elif kind == "decoy": parts = RR.parts_for("decoy", i)
    codes = S.codes_of(parts, key)
    s, sq = K.hc_square(codes, S.lp(), 100, 20, zlib.crc32(("%s%d" % (kind, i)).encode()) % 100000)
    return dict(kind=kind, i=i, score=s / max(S.nq(codes), 1), nq=S.nq(codes))
if __name__ == "__main__":
    n = int(sys.argv[2])
    trials.log(phase="prereg-run", entry="R1", task="fixed-key rows: claimed key given, square searched 100x20", n=n, rows=["claim x10 seeds", "randkey", "shuffle", "decoy"], scorer_commit="50b772c")
    tasks = [("claim", i) for i in range(10)] + [(k, i) for i in range(n) for k in ("randkey", "shuffle", "decoy")]
    with mp.Pool(8) as p: res = p.map(job, tasks, chunksize=2)
    json.dump(res, open(sys.argv[1], "w"))
    claim = max(r["score"] for r in res if r["kind"] == "claim")
    for k in ("randkey", "shuffle", "decoy"):
        v = np.array([r["score"] for r in res if r["kind"] == k]); print("%-8s n=%d mean %.4f sd %.4f max %.4f ; claim %.4f exceeds all: %s margin %.3f" % (k, len(v), v.mean(), v.std(ddof=1), v.max(), claim, claim > v.max(), claim - v.max()))
