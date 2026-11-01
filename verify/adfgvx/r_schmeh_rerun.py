"""B4: re-run R1 and R2 on Schmeh's 2017 transcription, and compare my plain decrypts with comp-adfgvx's (results/adfgvx-R-decrypt.md, C4)."""
import re, json, zlib, numpy as np
import schmeh as SM, data as D, adfgvx as A, r1_solver as S, r1_repro as R1, r1_run as RR, r2_prereg as P2, gapscan as GS, kern as K, german as G, trials
sm = {}
for h, s in SM.entries("upper"): sm.setdefault(h, []).append(s)
R = D.by_id()
c5, c6, g176 = sm["Page 153"][0], sm["Page 153"][1], sm["Page 176"][0]
assert c5 == R["p156C3"]["printed"] and c6 == R["p156C6"]["printed"] and g176 == R["p179B1"]["printed"]
print("Schmeh strings identical to creilly's for p156C3, p156C6, p179B1 (asserted)")
trials.log(phase="prereg-run", entry="R1,R2", task="B4 re-run on Schmeh 2017 strings (identical to creilly's by assertion): reproduction, claimed-key score, 3 real solver runs, R2 masked scan", scorer_commit="50b772c")
# R1 reproduction
d5 = A.decrypt(c5, R1.KEY18, R1.SQ); d6 = A.decrypt(c6, R1.KEY18, R1.SQ)
print("R1 part5 decrypt == claimed:", d5 == R1.P5.upper()); print("R1 part6 decrypt:", d6)
# real solver runs on Schmeh strings: must equal the committed rows (same seeds, same inputs)
old = {(r["kind"], r["i"]): r for r in map(json.loads, open("results/r1_prereg.jsonl"))}
same = 0
for i in range(3):
    m, key, sq, ic = S.run_budget([c5, c6.replace("?", "-")], 18, zlib.crc32(("real%d" % i).encode()) % 100000, RR.B)
    same += abs(m - old[("real", i)]["score"]) < 1e-12 and key == old[("real", i)]["key"]
print("R1 real solver runs on Schmeh strings identical to committed creilly runs: %d/3" % same)
# R2 on Schmeh string
l32 = P2.lp("TEL", ("nov10",))
o, m = P2.best_placements(g176, "nov10", l32)
print("R2 (Schmeh string) TEL mask: claim %.4f, nq %d, masked %d" % (m[20, 160], o[20, 160, 1], o[20, 160, 2]))
old2 = json.load(open("results/r2_prereg_claim.json"))["TEL"]
print("   equals committed creilly value:", abs(m[20, 160] - old2["claim"]) < 1e-12)
# C4: comp's plain decrypts
txt = open("../../results/adfgvx-R-decrypt.md").read()
blocks = re.findall(r"```\n(.*?)\n```", txt, re.S)
def mark(ct, trans, sq):
    inter = A.untranspose(ct, trans); out = ""
    for i in range(0, len(inter) - 1, 2):
        a, b = inter[i], inter[i + 1]
        if a not in A.IDX or b not in A.IDX: out += "-"
        else:
            ch = sq[6 * A.IDX[a] + A.IDX[b]]; out += "?" if ch == "?" else ch
    return out
mine = [mark(c5, R1.KEY18, R1.SQ), mark(c6, R1.KEY18, R1.SQ),
        mark(g176[:160] + "-" * 20 + g176[160:], D.keys()["nov10"]["transposition"], R1.SQ and "4ARUT1OIFSKN35BZPVLD6JMXCWHQ2E7G08Y9"),
        mark(g176[:160] + "-" * 20 + g176[160:], D.keys()["nov10"]["transposition"], D.keys()["nov10"]["square"])]
theirs = [b.strip() for b in blocks]
for i, (a, b) in enumerate(zip(mine, theirs[:4])): print("C4 block %d identical to comp-adfgvx: %s" % (i, a == b))
