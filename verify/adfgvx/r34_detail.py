"""R3/R4 detail: global alignment edit scripts, chance, decrypt under the solved message's key."""
import sys, json, random, collections
import numpy as np
import adfgvx as A, data as D, census as C
from r34 import pats, summarise, freq, binom_tail, sw

# R3/R4 use plain Levenshtein costs (sub 1, indel 1 per symbol): the census affine costs favour a long
# gap-pair over a cluster of substitutions on near-random strings and mis-describe these duplicates.
C.GAP_OPEN, C.GAP_EXT, C.SUB = 0.0, 1.0, 1.0
R = D.by_id(); K = D.keys()
allct = {r["id"]: r["ciphertext"].replace(" ", "") for r in D.records() if r["ciphertext"].strip()}
F = freq(allct.values()); PM = sum(v * v for v in F.values())

def script(S, P):
    cost, ops = C.align(pats(S), P)
    sm = summarise(ops, S, P)
    # event list
    ev = C.events(ops, pats(S), P)
    ev2 = []
    for e in ev:
        if e[0] == "sub": ev2.append(("sub", ops_at(ops, e)))
    return cost, ops, sm

def ops_at(ops, e): return e[2]

def describe(ops, S, P):
    out = []
    k = 0
    while k < len(ops):
        o = ops[k]
        if o[0] == "X": out.append("sub S[%d]=%s -> P[%d]=%s" % (o[1], S[o[1]], o[2], P[o[2]])); k += 1
        elif o[0] in "DI":
            e = k
            while e < len(ops) and ops[e][0] == o[0]: e += 1
            if o[0] == "D": out.append("gap: S[%d:%d]=%s absent from P (P idx %d)" % (o[1], ops[e-1][1] + 1, S[o[1]:ops[e-1][1]+1], o[2]))
            else: out.append("extra: P[%d:%d]=%s absent from S" % (o[2], ops[e-1][2] + 1, P[o[2]:ops[e-1][2]+1]))
            k = e
        else: k += 1
    return out

def shuffle_null(S, P, N=20000, seed=3):
    """Chance model: composition-preserving shuffles of P; statistic = affine alignment cost (C fast_cost)."""
    rng = random.Random(seed)
    Sp = pats(S)
    obs = C.fast_cost(Sp, P)
    cs = []
    for _ in range(N):
        l = list(P); rng.shuffle(l); cs.append(C.fast_cost(Sp, "".join(l)))
    return obs, min(cs), float(np.mean(cs)), sum(1 for c in cs if c <= obs), N

def exact_vs_chance(sm, n_known):
    k = sm["exact"]; n = sm["exact"] + sm["mismatch"]
    return n, k, PM, n * PM, binom_tail(n, k, PM)

if __name__ == "__main__":
    res = {}
    # ---------------- R3
    A_ = allct["p139B"]; B_ = allct["p155E"]; T = A_[-104:]
    cost, ops, sm = script(T, B_)
    res["R3_global_vs_tail104"] = dict(cost=cost, **{k: v for k, v in sm.items()}, desc=describe(ops, T, B_))
    res["R3_chance"] = dict(zip(("n_compared", "k_exact", "p_match", "expected_exact", "binom_tail_p"), exact_vs_chance(sm, 0)))
    res["R3_shuffle_null_cost"] = dict(zip(("obs_cost", "min", "mean", "n_le_obs", "N"), shuffle_null(T, B_)))
    # positional hamming (no indels) for reference
    res["R3_hamming_tail"] = sum(1 for a, b in zip(T, B_) if a == b and a not in "-?")
    # best window offset by simple hamming across p139B (no indels)
    ham = [(sum(1 for a, b in zip(A_[o:o+104], B_) if a == b), o) for o in range(0, len(A_) - 104 + 1)]
    ham.sort(reverse=True); res["R3_hamming_best_offsets"] = ham[:3]
    # decrypt p155E under nov04 key placed as the tail of a 314-symbol message
    k = K["nov04"]; tr = k["transposition"]; sqr = k["square"]
    pt = R["p139B"]["plaintext"]
    full_log = A_
    placed = "-" * 210 + B_
    dec_placed = A.decrypt(placed, tr, sqr)
    ref = A.decrypt(full_log, tr, sqr)
    known = [(i, a, b) for i, (a, b) in enumerate(zip(dec_placed, ref)) if a != "?"]
    res["R3_placed_decrypt"] = dict(letters_determined=len(known), agree=sum(1 for _, a, b in known if a == b),
                                    disagree=[(i, a, b) for i, a, b in known if a != b], text=dec_placed)
    # standalone decrypt (as a 104-symbol message) under nov04, and under all keys: does anything read?
    import german as G, kern as KK
    lp = KK.to32(G.model("LIT"))
    def per_quad(t):
        segs = G.segments(t); s, n = G.score_classes(segs, lp); return s / max(n, 1)
    stand = {kid: per_quad(A.decrypt(B_, kk["transposition"], kk["square"])) for kid, kk in K.items()}
    res["R3_standalone_decrypt_LIT_perquad"] = {kk: round(v, 3) for kk, v in sorted(stand.items(), key=lambda kv: -kv[1])[:5]}
    res["R3_standalone_nov04"] = A.decrypt(B_, tr, sqr)
    # ---------------- R4
    A_ = allct["p188_.2"]; B_ = allct["p192A"]
    cost, ops, sm = script(A_, B_)
    res["R4_global"] = dict(cost=cost, **sm, desc=describe(ops, A_, B_))
    res["R4_chance"] = dict(zip(("n_compared", "k_exact", "p_match", "expected_exact", "binom_tail_p"), exact_vs_chance(sm, 0)))
    res["R4_shuffle_null_cost"] = dict(zip(("obs_cost", "min", "mean", "n_le_obs", "N"), shuffle_null(A_, B_)))
    k = K["nov13_16"]; tr = k["transposition"]; sqr = k["square"]
    # reconstruct the 96-symbol stream: P symbols at matched positions, '-' at S-only (deleted) positions
    rec = ["-"] * len(A_)
    for o in ops:
        if o[0] in "MX": rec[o[1]] = B_[o[2]]
    rec = "".join(rec)
    res["R4_reconstructed_stream"] = rec
    dec = A.decrypt(rec, tr, sqr); ref = A.decrypt(A_, tr, sqr)
    res["R4_decrypt_of_reconstruction"] = dec; res["R4_decrypt_of_p188_.2"] = ref
    res["R4_published_plaintext_p188_.2"] = R["p188_.2"]["plaintext"]
    det = [(i, a, b) for i, (a, b) in enumerate(zip(dec, ref)) if a != "?"]
    res["R4_letters_determined"] = len(det); res["R4_letters_agree"] = sum(1 for _, a, b in det if a == b)
    res["R4_disagree"] = [(i, a, b) for i, a, b in det if a != b]
    res["R4_standalone_nov13_16"] = A.decrypt(B_, tr, sqr)
    stand = {kid: per_quad(A.decrypt(B_, kk["transposition"], kk["square"])) for kid, kk in K.items()}
    res["R4_standalone_decrypt_LIT_perquad"] = {kk: round(v, 3) for kk, v in sorted(stand.items(), key=lambda kv: -kv[1])[:5]}
    # per-quad score of the published plaintext, for scale
    res["R4_published_perquad_LIT"] = per_quad(R["p188_.2"]["plaintext"])
    json.dump(res, open(sys.argv[1], "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:9000])
