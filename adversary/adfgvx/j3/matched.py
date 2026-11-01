"""J3 test B: a null matched to what the real group has and the shuffle null lacks.
  c0  six real ciphertexts of solved entries, six DIFFERENT keys, none nov07, each cut to a
      member's length (uniform entry with enough length, uniform window);
  c   the same draws with each member's lost-symbol mask ('-' positions) imposed.
Measured with test A's statistic (random transpositions, widths 15-22, square solved), so it
compares real/shuffle/c0/c on equal footing. Output results/matched.tsv"""
import json, os, random, hashlib
from concurrent.futures import ProcessPoolExecutor
from common3 import *
import randt
NDRAW = 30
def bank():
    r = json.load(open(os.path.join(SRC, "ciphertexts/adfgvx-1918-log.records.json")))
    return sorted([(e["id"], e["key"], "".join(c if c in "ADFGVX" else "-" for c in e["printed"]))
                   for e in r if e["status"].startswith("Solved") and e.get("key") and e.get("printed") and e["key"] != "nov07"])
def draw(M, i, B, mask):
    r = random.Random(int(hashlib.sha256(f"adv-j3:matched:{i}".encode()).hexdigest()[:16], 16))
    used, out, src = set(), [], []
    for t in M:
        el = [b for b in B if b[1] not in used and len(b[2]) >= len(t)]
        e = r.choice(el); used.add(e[1]); o = r.randrange(len(e[2]) - len(t) + 1); s = e[2][o:o + len(t)]
        if mask: s = "".join("-" if t[j] == "-" else s[j] for j in range(len(t)))
        out.append(s); src.append(f"{e[0]}:{e[1]}@{o}")
    return out, src
if __name__ == "__main__":
    M = texts(); B = bank(); work = []; srcs = {}
    for i in range(NDRAW):
        for kind, mask in (("c0", False), ("c", True)):
            d, s = draw(M, i, B, mask); work.append((kind, i, d)); srcs[f"{kind}{i}"] = s
    json.dump(srcs, open("results/matched_sources.json", "w"), indent=0)
    with ProcessPoolExecutor(6) as ex, open("results/matched.tsv", "w") as f:
        f.write("kind\ti\twidth\tscore\tpen_frac\n")
        for rows in ex.map(randt.go, work):
            for r in rows: f.write("\t".join(map(str, r)) + "\n")
