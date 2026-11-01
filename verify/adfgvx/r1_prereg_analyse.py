import json, sys, collections, numpy as np
import r1_solver as S, r1_repro as R1, data as D, kern as K, trials
rs = [json.loads(l) for l in open(sys.argv[1])]
by = collections.defaultdict(list)
for r in rs: by[r["kind"]].append(r)
R = D.by_id(); c5 = R["p156C3"]["printed"]; c6 = R["p156C6"]["printed"]
# claimed key scored by the SAME stage 2 (full tier) as the solver
codes = S.codes_of([c5, c6], R1.KEY18)
cl = []
for sd in range(10):
    s, sq = K.hc_square(codes, S.lp(), 100, 20, 900 + sd); cl.append(s / S.nq(codes))
claim = max(cl)
print("claimed key, stage-2 full tier, 10 seeds: max %.4f, found in %d/10" % (claim, sum(abs(x - claim) < 1e-9 for x in cl)))
print("solver budget:", S.BUDGET, "(run with topk 300, full_top 5)")
for k in ("real", "shuffle", "decoy", "planted"):
    v = np.array([r["score"] for r in by[k]])
    print("%-8s n=%3d mean %.4f sd %.4f max %.4f  cpu/run %.1fs" % (k, len(v), v.mean(), v.std(ddof=1) if len(v) > 1 else 0, v.max(), np.mean([r["cpu"] for r in by[k]])))
rk = [r for r in by["real"] if r["key"] == R1.KEY18]
print("real runs that returned the claimed key:", len(rk), "of", len(by["real"]))
nulls = [r["score"] for k in ("shuffle", "decoy") for r in by[k]]
print("search-family null: n=%d, max %.4f ; claimed-key score %.4f exceeds all: %s ; margin %.3f per quad" % (len(nulls), max(nulls), claim, claim > max(nulls), claim - max(nulls)))
pl = [r["score"] for r in by["planted"]]
print("power: planted (true key unknown to solver) best-found scores vs null max: %d of %d planted exceed null max" % (sum(x > max(nulls) for x in pl), len(pl)))
