"""R1 keyless solver (own design; prereg 'same search family'): stage 1 = hill-climb of the width-W transposition on the
pair-stream index of coincidence (tsearch.c), stage 2 = for the TOPK distinct stage-1 optima, hill-climb the square
on the German LIT quadgram score (kern.c).  Statistic = best (over the TOPK keys) total log10 / scored quadgrams.
Budget = (R1 restarts, TOPK, R2 restarts x kicks)."""
import numpy as np
import adfgvx as A, german as G, kern as K, tsearch as T

_LP = None
def lp():
    global _LP
    if _LP is None: _LP = K.to32(G.model("LIT"))
    return _LP

def codes_of(parts, key):
    out = []
    for c in parts:
        inter = A.untranspose(c, list(key))
        for i in range(0, len(inter) - 1, 2):
            a, b = inter[i], inter[i + 1]
            out.append(A.IDX[a] * 6 + A.IDX[b] if (a in A.IDX and b in A.IDX) else -1)
        out.append(-1)
    return np.array(out, dtype=np.int8)

def nq(codes):
    return sum(1 for i in range(3, len(codes)) if min(codes[i-3:i+1]) >= 0)

def solve(parts, w, r1, topk, r2, k2, seed):
    keys, ics = T.search(parts, w, r1, seed, topk)
    best = (-1e9, None, None, None)
    for j, key in enumerate(keys):
        codes = codes_of(parts, key)
        s, sq = K.hc_square(codes, lp(), r2, k2, seed * 1000 + j)
        m = s / max(nq(codes), 1)
        if m > best[0]: best = (m, list(map(int, key)), sq, float(ics[j]))
    return best

def solve2(parts, w, r1, topk, quick, full_top, full, seed):
    """Two-tier stage 2.  quick=(restarts,kicks) on all topk keys; full=(restarts,kicks) on the best full_top of those."""
    keys, ics = T.search(parts, w, r1, seed, topk)
    cand = []
    for j, key in enumerate(keys):
        codes = codes_of(parts, key)
        s, sq = K.hc_square(codes, lp(), quick[0], quick[1], seed * 1000 + j)
        cand.append((s / max(nq(codes), 1), j))
    cand.sort(reverse=True)
    best = (-1e9, None, None, None)
    for _, j in cand[:full_top]:
        key = keys[j]; codes = codes_of(parts, key)
        s, sq = K.hc_square(codes, lp(), full[0], full[1], seed * 7919 + j)
        m = s / max(nq(codes), 1)
        if m > best[0]: best = (m, list(map(int, key)), sq, float(ics[j]))
    return best
BUDGET = dict(r1=6000, topk=400, quick=(10, 3), full_top=20, full=(100, 20))
def run_budget(parts, w, seed, B=BUDGET):
    return solve2(parts, w, B["r1"], B["topk"], B["quick"], B["full_top"], B["full"], seed)
