"""Summary table: per detection, S, comp's threshold, best wrong key, and the random-key
families' max / count >= S."""
import gzip, csv, sys, collections, os
from common import *
T = [t for t in targets() if t["above"]]
K = keys()
W = collections.defaultdict(dict)
for r in csv.DictReader(open("results/wrongkeys.tsv"), delimiter="\t"):
    W[r["unit"]][r["key"]] = (float(r["score"]), r["edits"], float(r["unknown_frac"]))
path = "results/randkeys.tsv.gz"
R = collections.defaultdict(list)
for r in csv.DictReader(gzip.open(path, "rt"), delimiter="\t"):
    try: R[(r["unit"], r["family"])].append(float(r["score"]))
    except (TypeError, ValueError): pass
fams = ["R0", "R1", "HS", "HT"]
print(f"source: {path}")
hdr = "| unit | key | S | thr | S-thr | best wrong period key (of 13) | best other key (of 8) | " + " | ".join(f"{f}: n, max, #>=S" for f in fams) + " |"
print(hdr); print("|" + "---|" * (hdr.count("|") - 1))
for t in T:
    w = W[t["unit"]]
    las = max((v[0], k) for k, v in w.items() if K[k]["source"] == "lasry")
    oth = max((v[0], k) for k, v in w.items() if K[k]["source"] != "lasry")
    cells = []
    for f in fams:
        xs = R[(t["unit"], f)]
        cells.append(f"{len(xs)}, {max(xs):.3f}, {sum(x >= t['S'] for x in xs)}" if xs else "-")
    mark = lambda v: f"**{v[1]} {v[0]:.3f}**" if v[0] >= t["S"] else f"{v[1]} {v[0]:.3f}"
    print(f"| {t['unit']} | {t['argmax']} | {t['S']:.3f} | {t['threshold']:.3f} | {t['S']-t['threshold']:+.3f} | {mark(las)} | {mark(oth)} | " + " | ".join(cells) + " |")
