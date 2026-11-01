"""Compare masknull.tsv with comp's committed J1 half (a) and (b) draws, per target."""
import gzip, json, csv, collections, statistics as st, os
from common import *
def halves(h):
    d = collections.defaultdict(lambda: collections.defaultdict(lambda: -99.0))
    for l in gzip.open(os.path.join(SRC.replace("lead", "lead2") if os.path.isdir(SRC.replace("lead", "lead2")) else SRC, f"results/adfgvx-J1-nulls-{h}.jsonl.gz"), "rt"):
        x = json.loads(l)
        if x.get("meta") or x.get("role") != "target": continue
        for j, s in enumerate(x["score"]): d[x["unit"]][x["i0"] + j] = max(d[x["unit"]][x["i0"] + j], s)
    return {u: list(v.values()) for u, v in d.items()}
A, Bh = halves("a"), halves("b")
C = collections.defaultdict(list)
for r in csv.DictReader(open("results/masknull.tsv"), delimiter="\t"): C[r["unit"]].append(float(r["S"]))
U = units()
print("| unit | lost/n | S | thr | above | a: mean, max | b: mean, max | mask-matched: mean, max, # > thr (of %d) | mask-matched # >= S |" % len(next(iter(C.values()))))
print("|---|---|---|---|---|---|---|---|---|")
tot = 0; n = 0
for t in sorted(targets(), key=lambda t: -U[t["unit"]]["text"].count("-") / len(U[t["unit"]]["text"])):
    u = t["unit"]; tx = U[u]["text"]; c = C[u]; ex = sum(x > t["threshold"] for x in c); tot += ex; n += len(c)
    print(f"| {u} | {tx.count('-')}/{len(tx)} | {t['S']:.3f} | {t['threshold']:.3f} | {'yes' if t['above'] else 'no'} | {st.mean(A[u]):.3f}, {max(A[u]):.3f} | {st.mean(Bh[u]):.3f}, {max(Bh[u]):.3f} | {st.mean(c):.3f}, {max(c):.3f}, {ex} | {sum(x >= t['S'] for x in c)} |")
print(f"\nmask-matched draws above their target's threshold: {tot}/{n} (the J1 null was built so that each target's rate is <= 1/2941)")
