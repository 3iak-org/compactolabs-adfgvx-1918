"""dev's follow-up (ticket tmvxroux7sf8g): does p062A survive J1(ii) when the edit cap is varied?
p062A under all 22 keys at caps 0-3, and R1 random keys (Lasry blank patterns, same seeds as
randkeys.py) at caps 0, 1 (1000 draws) and 3 (first 200 draws). Output results/capvary.tsv"""
import os
from concurrent.futures import ProcessPoolExecutor
from common import *
import randkeys as RK
U = units(); K = keys(); UNIT = "p062A"
def runcap(a):
    cap, jobs = a; os.environ["J1CAP"] = str(cap); return cap, run(jobs)
if __name__ == "__main__":
    text = U[UNIT]["text"]; work = []
    for cap in (0, 1, 2, 3):
        for kid, k in K.items():
            work.append((cap, [job(f"key|{kid}", k["square"], k["transposition"], text)]))
    t = [x for x in targets() if x["unit"] == UNIT][0]
    r1 = [j for j in RK.draws(t) if j.split("|")[1] == "R1"]
    for cap, n in ((0, 1000), (1, 1000), (3, 200)):
        for i in range(0, n, 10 if cap < 3 else 1):
            work.append((cap, [j.replace("|R1|", "|R1|", 1) for j in r1[i:i + (10 if cap < 3 else 1)]]))
    with ProcessPoolExecutor(6) as ex, open("results/capvary.tsv.part", "w") as f:
        f.write("cap\tkind\tid\tscore\tedits\tplain\n")
        for cap, R in ex.map(runcap, work):
            for tag, r in R.items():
                p = tag.split("|"); kind, ident = (p[0], p[1]) if p[0] == "key" else ("R1", p[2])
                f.write(f"{cap}\t{kind}\t{ident}\t{r['score']:.6f}\t{r['edits'] or '-'}\t{r['plain']}\n"); f.flush()
    os.replace("results/capvary.tsv.part", "results/capvary.tsv")
