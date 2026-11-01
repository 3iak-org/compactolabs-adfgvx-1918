"""R3 / R4: duplicate-message claims.
 R3: p155E (p.152, 104 symbols) = second intercept of the last 104 symbols of solved p139B (nov04).
 R4: p192A (p.189, 90 symbols) = damaged copy of solved p188_.2 (nov13_16).
Own alignment (census.align, affine Gotoh) + own Smith-Waterman (sw.c) + chance models."""
import sys, os, json, random, ctypes, collections, math
import numpy as np
import adfgvx as A, data as D, census as C

_sw = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libsw.so"))
_sw.sw_score.restype = ctypes.c_int
_sw.sw_score.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]

def enc(s): return bytes(A.IDX[c] if c in A.IDX else 6 for c in s)
def sw(a, b): return _sw.sw_score(enc(a), len(a), enc(b), len(b))

def pats(s):  # string -> alignment pattern list for census.align (frozenset of allowed symbols / None)
    return [None if c in "-?" else frozenset(c) for c in s]

def global_align(S, P):
    cost, ops = C.align(pats(S), P)
    return cost, ops

def summarise(ops, S, P):
    m = sum(1 for o in ops if o[0] == "M" and S[o[1]] not in "-?" and P[o[2]] not in "-?")
    x = sum(1 for o in ops if o[0] == "X")
    wild = sum(1 for o in ops if o[0] == "M" and (S[o[1]] in "-?" or P[o[2]] in "-?"))
    dels = [(o[1]) for o in ops if o[0] == "D"]; ins = [(o[2]) for o in ops if o[0] == "I"]
    return dict(exact=m, mismatch=x, wild=wild, ndel=len(dels), nins=len(ins), del_idx=dels, ins_idx=ins)

def freq(strings):
    c = collections.Counter(ch for s in strings for ch in s if ch in A.IDX)
    t = sum(c.values()); return {k: v / t for k, v in c.items()}

def chance_hamming(a, b, f):
    """P(match) at a random aligned pair, and the binomial tail P(>=k matches among n known pairs)."""
    p = sum(v * v for v in f.values())
    return p

def binom_tail(n, k, p):
    from math import comb
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k, n + 1))

def run(claim):
    R = D.by_id()
    tgt, src, shift = claim
    A_ = R[src]["ciphertext"].replace(" ", ""); B_ = R[tgt]["ciphertext"].replace(" ", "")
    allct = {r["id"]: r["ciphertext"].replace(" ", "") for r in D.records() if r["ciphertext"].strip()}
    f = freq(allct.values())
    p = chance_hamming(None, None, f)
    out = {"target": tgt, "source": src, "len_target": len(B_), "len_source": len(A_), "p_match_chance": p}
    # --- local alignment vs every log entry
    sc = {i: sw(B_, c) for i, c in allct.items() if i != tgt}
    top = sorted(sc.items(), key=lambda kv: -kv[1])[:5]
    out["sw_top5"] = top
    out["sw_median"] = float(np.median(list(sc.values()))); out["sw_n"] = len(sc)
    out["sw_max_excluding_source"] = max(v for i, v in sc.items() if i != src)
    # --- shuffle null for SW against the source: composition-preserving shuffles of target
    rng = random.Random(7)
    obs = sw(B_, A_)
    sh = []
    for _ in range(20000):
        l = list(B_); rng.shuffle(l); sh.append(sw("".join(l), A_))
    out["sw_obs"] = obs; out["sw_shuffle_max"] = max(sh); out["sw_shuffle_mean"] = float(np.mean(sh)); out["sw_shuffle_N"] = len(sh)
    out["sw_shuffle_ge_obs"] = sum(1 for s in sh if s >= obs)
    return out, A_, B_, allct, f

if __name__ == "__main__":
    for claim in (("p155E", "p139B", None), ("p192A", "p188_.2", None)):
        out, A_, B_, allct, f = run(claim)
        print(json.dumps(out, indent=1))
