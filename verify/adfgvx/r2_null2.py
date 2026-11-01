"""R2 extra nulls, TEL(held-out nov10) 'digit' mode, best over all 221 gap positions per trial:
  (a) random 16-column transposition + the claimed (nov10) square          [N random keys]
  (b) nov10 transposition + each OTHER key's square                          [cross-pairing, E7/E8 style]
  (c) shuffled ciphertext (symbols permuted, then the claimed key and gap model)
Statistic = max over g of best-fill per-quad score."""
import sys, json, random, zlib, multiprocessing as mp
import numpy as np
import adfgvx as A, data as D, german as G, kern as K
from r2 import CT, SQ10, T10, stream_with_gap, best_fill
_lp = None
def lp():
    global _lp
    if _lp is None: _lp = K.to32(G.model("TEL", held_out=("nov10",)))
    return _lp

def scan(ct, tr, sq):
    best = -1e9
    for g in range(len(ct) + 1):
        s, _, _ = best_fill(stream_with_gap(ct, g), tr, sq, lp(), "digit")
        best = max(best, s)
    return best

def task(t):
    kind, x = t
    if kind == "randkey":
        rng = random.Random(x); tr = list(range(1, 17)); rng.shuffle(tr); return kind, x, scan(CT, tr, SQ10)
    if kind == "square":
        return kind, x, scan(CT, T10, D.keys()[x]["square"])
    if kind == "shuffle":
        rng = random.Random(x); l = list(CT); rng.shuffle(l); return kind, x, scan("".join(l), T10, SQ10)
    if kind == "claim":
        return kind, x, scan(CT, T10, SQ10)

if __name__ == "__main__":
    N = int(sys.argv[1])
    tasks = [("claim", 0)] + [("randkey", s) for s in range(N)] + [("shuffle", s) for s in range(N)]
    tasks += [("square", k) for k in D.keys() if k != "nov10"]
    with mp.Pool(8) as p:
        res = p.map(task, tasks, chunksize=1)
    json.dump(res, open(sys.argv[2], "w"))
    print("done")
