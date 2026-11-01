"""Step 2: every detection unit under every OTHER key in the keys file (13 other Lasry period keys
+ the 8 non-period keys), cap 2, same scorer. Output: results/wrongkeys.tsv"""
import os; from concurrent.futures import ProcessPoolExecutor
from common import *
K = keys(); U = units(); T = [t for t in targets() if t["above"]]
jobs = [job(f"{t['unit']}|{kid}", k["square"], k["transposition"], U[t["unit"]]["text"])
        for t in T for kid, k in K.items() if kid != t["argmax"]]
with ProcessPoolExecutor(6) as ex:
    R = {}
    for r in ex.map(run, [[j] for j in jobs]): R.update(r)
os.makedirs("results", exist_ok=True)
with open("results/wrongkeys.tsv", "w") as f:
    f.write("unit\tkey\tscore\tscore0\tedits\tunknown_frac\tplain\n")
    for tag, r in sorted(R.items()):
        u, kid = tag.split("|"); pl = r["plain"]
        unk = sum(1 for i in range(2, len(pl)) if "-" in pl[i-2:i+1]) / max(1, len(pl) - 2)
        f.write(f"{u}\t{kid}\t{r['score']:.6f}\t{r['score0']:.6f}\t{r['edits']}\t{unk:.3f}\t{pl}\n")
print("unit S thr | best wrong lasry | best wrong any")
for t in T:
    w = {kid: R[f"{t['unit']}|{kid}"]["score"] for kid in K if kid != t["argmax"]}
    las = {k: v for k, v in w.items() if K[k]["source"] == "lasry"}
    bl = max(las, key=las.get); ba = max(w, key=w.get)
    print(f"{t['unit']:14s} S {t['S']:.3f} thr {t['threshold']:.3f} | {bl:9s} {las[bl]:.3f} ({las[bl]-t['S']:+.3f}) | {ba:18s} {w[ba]:.3f} ({w[ba]-t['S']:+.3f})")
