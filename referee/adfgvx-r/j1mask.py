"""Referee check: J1 per-target null with the target's lost-symbol mask imposed on real
plant-side ciphertext of a non-candidate key (adversary J3 test B construction, applied to J1).
Uses comp's own jattack mode 3 via strandj (read-only archive) so the statistic is identical."""
import sys, os, json, random, hashlib
sys.path.insert(0, os.path.join(sys.argv[1], "search/adfgvx")); os.chdir(sys.argv[1])
import strandj as sj
from concurrent.futures import ThreadPoolExecutor
N = int(sys.argv[2]); OUT = sys.argv[3]
J = sj.j0(); subs = {s["unit"]: s for s in sj.j1_subjects(J)}
T = [json.loads(l) for l in open("results/adfgvx-J1-targets.jsonl")]
T = [t for t in T if not t.get("meta") and t["above"]]
bank = sj.plant_bank(); K = sj.keys(); sj.scorer_setup()
def draws(sub, t):
    elig = [e for e in bank if e["key"] not in sub["keys"]]
    L = len(sub["text"]); out = []
    for i in range(N):
        r = random.Random(int(hashlib.sha256(f"ref-j1mask:{sub['unit']}:{i}".encode()).hexdigest()[:16], 16))
        el = [e for e in elig if len(e["text"]) >= L]
        if el:
            e = r.choice(el); src = e["text"]
        else:
            x = elig[:]; r.shuffle(x); src = "".join(e["text"] for e in x)
        o = r.randrange(len(src) - L + 1); s = src[o:o + L]
        s = "".join("-" if sub["text"][j] == "-" else s[j] for j in range(L))
        out.append(s)
    return out
def work(u):
    sub = subs[u]; ds = draws(sub, None); best = [-99.0] * N
    for k in sub["keys"]:
        for c in range(0, N, 50):
            rs = sj.run_mode3(K[k], ds[c:c + 50])
            for j, r in enumerate(rs): best[c + j] = max(best[c + j], r["score"])
    return u, best
with ThreadPoolExecutor(7) as ex, open(OUT, "w") as f:
    for u, best in ex.map(work, [t["unit"] for t in T]):
        f.write(json.dumps(dict(unit=u, scores=best)) + "\n"); f.flush()
