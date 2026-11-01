"""J3 test C: my own joint search (a3 JOINT: widths 15-22, 1 restart x 15000 annealed
transposition moves each, square refitted per move, then a full square solve) on the real group
(3 seeds), 12 shuffles (randt.shuffled) and 12 matched draws (matched 'c'). Output results/joint.tsv"""
import os
from concurrent.futures import ProcessPoolExecutor
from common3 import *
import randt, matched
def go(a):
    kind, i, msgs, seed = a
    r = a3(msgs, [f"JOINT {w} 1 15000 0.01" for w in range(15, 23)], seed)
    b = max(r, key=lambda x: x["score"]); return kind, i, b["w"], b["score"], b["perm"], b["square"], b["plain"]
if __name__ == "__main__":
    M = texts(); B = matched.bank()
    work = [("real", s, M, 500 + s) for s in range(3)] + [("shuf", i, randt.shuffled(M, i), 600 + i) for i in range(12)] \
         + [("c", i, matched.draw(M, i, B, True)[0], 700 + i) for i in range(12)]
    with ProcessPoolExecutor(6) as ex, open("results/joint.tsv.part", "w") as f:
        f.write("kind\ti\twidth\tscore\tperm\tsquare\tplain\n")
        for row in ex.map(go, work): f.write("\t".join(map(str, row)) + "\n"); f.flush()
    os.replace("results/joint.tsv.part", "results/joint.tsv")
