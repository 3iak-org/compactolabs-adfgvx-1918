import json, sys, os, collections, numpy as np
import math
files = sys.argv[1:]
rs = [json.loads(l) for f in files for l in open(f)]
by = collections.defaultdict(list)
for r in rs: by[r[0]].append(r)
claim = sorted(r[5] for r in by["claim"])
c = max(claim)
print("claim per-quad best over %d runs: %.4f (total %.2f, nquads %d)  worst-run %.4f" % (len(claim), c, max(r[3] for r in by["claim"]), by["claim"][0][4], min(claim)))
for k in ("randkey", "shuffle"):
    v = np.array([r[5] for r in by[k]])
    z = (c - v.mean()) / v.std(ddof=1)
    # Gumbel (max) tail fit to the upper tail: use scipy gumbel_r on all values
    # Gumbel(max) by method of moments (a model assumption: [H])
    scale = v.std(ddof=1) * math.sqrt(6) / math.pi; loc = v.mean() - 0.5772157 * scale
    p_g = 1 - math.exp(-math.exp(-(c - loc) / scale))
    print("%-8s n=%d mean %.4f sd %.4f max %.4f | claim exceeds all: %s | z=%.1f | Gumbel-extrapolated P(null>=claim)=%.2e [H]" % (k, len(v), v.mean(), v.std(ddof=1), v.max(), c > v.max(), z, p_g))
sw = np.array([r[5] for r in by["swap"]]) if "swap" in by else np.array([])
if len(sw):
    print("swap (two positions of the claimed key exchanged): n=%d  best %.4f  mean %.4f  claim-minus-best-swap %.4f" % (len(sw), sw.max(), sw.mean(), c - sw.max()))
    print("  best swaps:", sorted([(round(r[5], 4), r[1]) for r in by["swap"]], reverse=True)[:5])
