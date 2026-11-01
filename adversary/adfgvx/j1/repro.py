"""Step 1: reproduce comp's S_t (claimed key, cap 2) for all 49 targets with e2.c."""
import sys; from concurrent.futures import ProcessPoolExecutor
from common import *
K = keys(); U = units(); T = targets()
jobs = []
for t in T:
    for kid in t["keys"]:
        k = K[kid]; jobs.append(job(f"{t['unit']}|{kid}", k["square"], k["transposition"], U[t["unit"]]["text"]))
with ProcessPoolExecutor(6) as ex:
    R = {}
    for r in ex.map(run, [[j] for j in jobs]): R.update(r)
bad = 0
for t in T:
    for kid in t["keys"]:
        r = R[f"{t['unit']}|{kid}"]; c = t["per_key"][kid]
        d = r["score"] - c["score"]
        flag = "" if abs(d) < 2e-6 and abs(r["score0"] - c["score0"]) < 2e-6 else "  MISMATCH"
        bad += bool(flag)
        print(f"{t['unit']:14s} {kid:18s} mine {r['score']:.6f} comp {c['score']:.6f} s0 {r['score0']:.6f}/{c['score0']:.6f} {r['edits']:22s} {c['edits']}{flag}")
print("mismatches:", bad, "of", len(jobs))
