"""R1 step 2: free-square scoring of the claimed 18-column key vs nulls.
For a given transposition (and given ciphertext parts) we find, by iterated hill-climbing, the 6x6
square that maximises the German quadgram score of the decrypted pair stream (parts 5 and 6 as two
separate texts; lost-symbol letters break the text).  Statistic = best total log10 / number of
scored quadgrams.  Same optimiser, same effort, for the claim and every null."""
import sys, json, random, time, zlib, multiprocessing as mp
import numpy as np
import adfgvx as A, data as D, german as G, kern as K
from r1_repro import KEY18

R = D.by_id()
C5 = R["p156C3"]["ciphertext"].replace(" ", "")
C6 = R["p156C6"]["ciphertext"].replace(" ", "")
_LP = {}

def lp(name):
    if name not in _LP:
        _LP[name] = K.to32(G.model("LIT") if name == "LIT" else G.model("TEL", held_out=("nov07",)))
    return _LP[name]

def codes_for(parts, trans):
    out = []
    for c in parts:
        inter = A.untranspose(c, trans)
        for i in range(0, len(inter) - 1, 2):
            a, b = inter[i], inter[i + 1]
            out.append(A.IDX[a] * 6 + A.IDX[b] if (a in A.IDX and b in A.IDX) else -1)
        out.append(-1)   # break between the two parts
    return np.array(out, dtype=np.int8)

def nquads(codes):
    n = 0
    for i in range(3, len(codes)):
        if min(codes[i-3:i+1]) >= 0: n += 1
    return n

def run(task):
    kind, seed, model, restarts, kicks = task
    rng = random.Random(seed if isinstance(seed, int) else str(seed))
    parts = [C5, C6]; trans = KEY18
    if kind == "claim": pass
    elif kind == "randkey":
        trans = list(range(1, 19)); rng.shuffle(trans)
    elif kind == "shuffle":
        parts = []
        for c in (C5, C6):
            l = [ch for ch in c]; rng.shuffle(l); parts.append("".join(l))   # unknown markers move too
    elif kind == "swap":    # claimed key with 2 positions swapped; seed indexes the pair
        i, j = seed
        trans = list(KEY18); trans[i], trans[j] = trans[j], trans[i]
    codes = codes_for(parts, trans)
    s, sq = K.hc_square(codes, lp(model), restarts, kicks, zlib.crc32(("%s-%s" % (kind, seed)).encode()))
    nq = nquads(codes)
    return kind, seed, model, s, nq, s / max(nq, 1), sq.tolist()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "calib":
        for model in ("LIT", "TEL"):
            for (rs, kk) in ((60, 15), (400, 40)):
                t = time.time()
                with mp.Pool(8) as p:
                    res = p.map(run, [("claim", 100 + s, model, rs, kk) for s in range(8)])
                print(model, rs, kk, "per-quad scores over 8 seeds:", sorted(round(r[5], 4) for r in res), "time %.1f" % (time.time() - t), "nq", res[0][4])

    if mode == "sat":        # saturation check: first 48 random-key nulls re-run at high effort
        tasks = [("randkey", s, "LIT", 400, 40) for s in range(48)]
        with mp.Pool(8) as p:
            res = p.map(run, tasks, chunksize=1)
        json.dump(res, open(sys.argv[2], "w")); print("done")

    if mode == "swaps":      # the 153 two-position swaps of the claimed key only
        restarts, kicks = int(sys.argv[2]), int(sys.argv[3]); out = sys.argv[4]
        tasks = [("swap", (i, j), "LIT", restarts, kicks) for i in range(18) for j in range(i + 1, 18)]
        with mp.Pool(8) as p, open(out, "w") as f:
            for r in p.imap_unordered(run, tasks, chunksize=2):
                f.write(json.dumps(r) + "\n"); f.flush()
        print("done", len(tasks))

    if mode == "nulls2":      # shuffles + swaps only (randkey part already run)
        N = int(sys.argv[2]); restarts, kicks = int(sys.argv[3]), int(sys.argv[4]); out = sys.argv[5]
        tasks = [("shuffle", s, "LIT", restarts, kicks) for s in range(N)]
        tasks += [("swap", (i, j), "LIT", restarts, kicks) for i in range(18) for j in range(i + 1, 18)]
        with mp.Pool(8) as p, open(out, "w") as f:
            for r in p.imap_unordered(run, tasks, chunksize=2):
                f.write(json.dumps(r) + "\n"); f.flush()
        print("done", len(tasks))

    if mode == "nulls":
        N = int(sys.argv[2]); restarts, kicks = int(sys.argv[3]), int(sys.argv[4]); out = sys.argv[5]
        tasks = [("claim", 1000 + s, "LIT", restarts, kicks) for s in range(16)]
        tasks += [("randkey", s, "LIT", restarts, kicks) for s in range(N)]
        tasks += [("shuffle", s, "LIT", restarts, kicks) for s in range(N)]
        tasks += [("swap", (i, j), "LIT", restarts, kicks) for i in range(18) for j in range(i + 1, 18)]
        with mp.Pool(8) as p, open(out, "w") as f:
            for r in p.imap_unordered(run, tasks, chunksize=4):
                f.write(json.dumps(r) + "\n"); f.flush()
        print("done", len(tasks))
