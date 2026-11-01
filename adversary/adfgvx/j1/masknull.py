"""Does the J3 shuffle-null bias reach J1? (dev, ticket tmvxuh7oxv38h)
For every J1 target t: N mask-matched draws = the real printed ciphertext of a solved entry whose
key is NOT among t's candidates (as J1 half (b)), a uniform window of t's length, with t's own
lost-symbol mask ('-' positions) imposed; v2: source windows with no lost symbol of their own
(v1, results/masknull_v1_unclean.tsv, allowed damaged sources and so overstated the damage); scored exactly as S_t (max over t's candidate keys,
cap 2, e2.c). Compared with comp's committed half-(a) (shuffle) and half-(b) draws, and with
threshold_t. Output results/masknull.tsv"""
import os, json, gzip, random, hashlib, collections
from concurrent.futures import ProcessPoolExecutor
from common import *
N = 100
def bank():
    r = json.load(open(os.path.join(SRC, "ciphertexts/adfgvx-1918-log.records.json")))
    return sorted([(e["id"], e["key"], "".join(c if c in "ADFGVX" else "-" for c in e["printed"]))
                   for e in r if e["status"].startswith("Solved") and e.get("key") and e.get("printed")])
def draws(t, text, B):
    el = [b for b in B if b[1] not in t["keys"] and len(b[2]) >= len(text)]
    out = []
    for i in range(N):
        r = random.Random(int(hashlib.sha256(f"adv-j1:mask:{t['unit']}:{i}".encode()).hexdigest()[:16], 16))
        while True:   # v2: the source window must itself be undamaged, so the draw's damage is exactly t's mask
            e = r.choice(el); o = r.randrange(len(e[2]) - len(text) + 1); s = e[2][o:o + len(text)]
            if "-" not in s: break
        out.append(("".join("-" if text[j] == "-" else s[j] for j in range(len(text))), f"{e[0]}@{o}"))
    return out
if __name__ == "__main__":
    K = keys(); U = units(); B = bank(); T = targets(); jobs = []; src = {}
    for t in T:
        for i, (s, so) in enumerate(draws(t, U[t["unit"]]["text"], B)):
            src[(t["unit"], i)] = so
            for kid in t["keys"]:
                k = K[kid]; jobs.append(job(f"{t['unit']}|{i}|{kid}", k["square"], k["transposition"], s))
    with ProcessPoolExecutor(6) as ex:
        R = {}
        for r in ex.map(run, [jobs[i:i + 20] for i in range(0, len(jobs), 20)]): R.update(r)
    best = collections.defaultdict(lambda: -99.0)
    for tag, r in R.items():
        u, i, kid = tag.split("|"); best[(u, int(i))] = max(best[(u, int(i))], r["score"])
    with open("results/masknull.tsv", "w") as f:
        f.write("unit\ti\tsource\tS\n")
        for (u, i), v in sorted(best.items()): f.write(f"{u}\t{i}\t{src[(u, i)]}\t{v:.6f}\n")
