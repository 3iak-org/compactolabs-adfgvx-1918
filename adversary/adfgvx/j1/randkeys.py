"""Step 3: the REAL ciphertext of each detection under random keys (the random-key null of
CLAUDE.md test 3, which the J1 null does not contain), cap 2, same scorer.
Families, per unit, seeds fixed (SEED, unit, family, i):
  R0  uniform random square (no blanks), transposition uniform of width w, w from a uniformly
      chosen Lasry key;
  R1  as R0, but the square carries the blank pattern (count and cells) of that Lasry key;
  HS  the CLAIMED key's square + a uniform random transposition of the claimed width;
  HT  the CLAIMED key's transposition + a uniform random square with the claimed key's blanks.
Output: results/randkeys.tsv (one line per draw)."""
import os, random, hashlib, sys
from concurrent.futures import ProcessPoolExecutor
from common import *
SEED = 20261101
N = dict(R0=1000, R1=1000, HS=300, HT=300)
AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
K = keys(); U = units(); T = [t for t in targets() if t["above"]]
LAS = [k for k in K.values() if k["source"] == "lasry"]

def rng(*p): return random.Random(int(hashlib.sha256(":".join(map(str, (SEED,) + p)).encode()).hexdigest()[:16], 16))
def rsq(r, blanks):
    s = list(AL); r.shuffle(s)
    for i in blanks: s[i] = "?"
    return "".join(s)
def rperm(r, w):
    p = list(range(1, w + 1)); r.shuffle(p); return p
def bl(sq): return [i for i, c in enumerate(sq) if c == "?"]

def draws(t):
    ck = K[t["argmax"]]; text = U[t["unit"]]["text"]; out = []
    for fam, n in N.items():
        for i in range(n):
            r = rng(t["unit"], fam, i)
            if fam in ("R0", "R1"):
                tk = r.choice(LAS); sq = rsq(r, bl(tk["square"]) if fam == "R1" else []); pm = rperm(r, tk["width"])
                desc = tk["id"]
            elif fam == "HS":
                sq = ck["square"]; pm = rperm(r, ck["width"]); desc = "perm"
            else:
                sq = rsq(r, bl(ck["square"])); pm = ck["transposition"]; desc = "sq"
            out.append(job(f"{t['unit']}|{fam}|{i}|{desc}|{sq}|{'.'.join(map(str, pm))}", sq, pm, text))
    return out

if __name__ == "__main__":
    jobs = [j for t in T for j in draws(t)]
    chunks = [jobs[i:i + 40] for i in range(0, len(jobs), 40)]
    os.makedirs("results", exist_ok=True)
    tmp = "results/randkeys.tsv.part"
    with ProcessPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as ex, open(tmp, "w") as f:
        f.write("unit\tfamily\ti\ttemplate\tsquare\tperm\tscore\tscore0\tedits\tplain\n")
        for k, R in enumerate(ex.map(run, chunks)):
            for tag, r in R.items():
                f.write("\t".join(tag.split("|")) + f"\t{r['score']:.6f}\t{r['score0']:.6f}\t{r['edits'] or '-'}\t{r['plain']}\n")
            if k % 50 == 0: print(k, "/", len(chunks), flush=True)
    os.replace(tmp, "results/randkeys.tsv")
    print("done", len(jobs))
