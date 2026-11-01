"""R1 extra: square learned from PART 5 ALONE (free hill-climb, LIT model, claimed key) is applied to PART 6.
Only part-6 letters whose symbol pair also occurs in part 5 are scored, so part 6 supplies independent evidence."""
import numpy as np
import adfgvx as A, german as G, kern as K
import r1_null as N, r1_repro as R1
lp = K.to32(G.model("LIT"))
c5 = N.codes_for([N.C5], N.KEY18)
best = None
for seed in range(1, 9):
    s, sq = K.hc_square(c5, lp, 300, 40, seed)
    if best is None or s > best[0]: best = (s, sq)
s, sq = best
ch = lambda x: chr(65 + x) if x < 26 else "0"
print("part-5 only per-quad %.4f" % (s / (len([1 for i in range(3, len(c5)) if min(c5[i-3:i+1]) >= 0]))))
print("part 5 as read from key alone:", "".join(ch(sq[x]) for x in c5 if x >= 0))
print("claimed                      :", R1.P5)
inter6 = A.untranspose(N.C6, N.KEY18)
seen5 = set(int(x) for x in c5 if x >= 0)
out = []; det = 0; agree = 0; cl = R1.P6.upper()
for k in range(0, len(inter6) - 1, 2):
    a, b = inter6[k], inter6[k+1]; i = k // 2
    if a in A.IDX and b in A.IDX:
        code = A.IDX[a] * 6 + A.IDX[b]
        if code in seen5:
            L = ch(sq[code]); det += 1
            ok = (L == cl[i]) or (L == "0" and cl[i].isdigit()); agree += ok
            out.append(L if ok else L.lower() + "!")
        else: out.append(".")
    else: out.append("_")
print("part 6, letters whose pair occurs in part 5 (%d of 54):" % det, " ".join(out))
print("agree with claimed part-6 reading: %d/%d" % (agree, det))
# letters in the claimed part 6 that are NOT confirmed by part 5 (new cells), corrections, fills

# joint (parts 5+6) free-square result, as used in the null: agreement of part 5 with the claimed reading
codes = N.codes_for([N.C5, N.C6], N.KEY18)
best = None
for seed in range(1, 9):
    s, sq = K.hc_square(codes, lp, 400, 40, seed)
    if best is None or s > best[0]: best = (s, sq)
s, sq = best
rd = "".join(ch(sq[x]) for x in codes[:66])
cl = R1.P5
ag = sum(1 for a, b in zip(rd, cl) if a == b or (a == "0" and b.isdigit()))
print("JOINT free-square reading of part 5:", rd)
print("agreement with claimed part 5 (digits treated as one class): %d/66" % ag)
claimed_sq = R1.SQ
cells = [(i, claimed_sq[i], ch(sq[i])) for i in range(36) if claimed_sq[i] != "?"]
print("claimed square cells reproduced by the free square: %d/%d" % (sum(1 for i, a, b in cells if a == b or (a.isdigit() and b == "0")), len(cells)))
