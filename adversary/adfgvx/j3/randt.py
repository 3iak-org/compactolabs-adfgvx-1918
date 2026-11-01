"""J3 test A: real group vs shuffled group with NO transposition search: random transpositions
(widths 15-22) and the square solved for each by a3's annealer. If the real group already beats
its shuffles here, the J3 margin can come from what the shuffle null destroys (the bursts of lost
symbols) rather than from a key. Also: fraction of trigram positions charged PEN.
Output results/randt.tsv: draw kind, index, width, score, pen_frac."""
import random, hashlib, os, sys
from concurrent.futures import ProcessPoolExecutor
from common3 import *
NSH = 30; PER_W = 6; WIDTHS = range(15, 23)
def shuffled(M, i):
    r = random.Random(int(hashlib.sha256(f"adv-j3:shuffle:{i}".encode()).hexdigest()[:16], 16)); out = []
    for t in M:
        l = list(t); r.shuffle(l); out.append("".join(l))
    return out
def go(a):
    kind, i, msgs = a
    res = a3(msgs, [f"RANDT {w} {PER_W}" for w in WIDTHS], 1000 + i)
    rows = []
    for x in res:
        pl = x["plain"].split("|"); P = sum(max(0, len(p) - 2) for p in pl)
        pen = sum(1 for p in pl for j in range(2, len(p)) if "-" in p[j-2:j+1]) / P
        rows.append((kind, i, x["w"], x["score"], pen))
    return rows
if __name__ == "__main__":
    M = texts()
    work = [("real", i, M) for i in range(NSH)] + [("shuf", i, shuffled(M, i)) for i in range(NSH)]
    os.makedirs("results", exist_ok=True)
    with ProcessPoolExecutor(6) as ex, open("results/randt.tsv", "w") as f:
        f.write("kind\ti\twidth\tscore\tpen_frac\n")
        for rows in ex.map(go, work):
            for r in rows: f.write("\t".join(map(str, r)) + "\n")
