"""Summaries of r2_null.py (key x gap scan) and r2_null2.py (random keys / shuffles / cross squares)."""
import json, sys, collections
import numpy as np
import data as D
scan = json.load(open(sys.argv[1])); K = D.keys()
for m in ("TEL", "LIT"):
    for q in ("digit", "any"):
        c = np.array(scan["%s|%s|nov10" % (m, q)])
        wrong = {k: np.array(scan["%s|%s|%s" % (m, q, k)]) for k in K if k != "nov10"}
        rows = sorted(((v.max(), k, int(v.argmax())) for k, v in wrong.items()), reverse=True)
        allw = np.concatenate(list(wrong.values()))
        lasry = max(v.max() for k, v in wrong.items() if K[k]["source"] == "lasry")
        print("[%s, '?' cells=%s] claim@160 %.4f, claim best-over-g %.4f (g=%d); best wrong key-over-g %.4f (%s g=%d); best wrong Lasry period key %.4f; z of claim@160 vs %d wrong (key,g) cells = %.1f"
              % (m, q, c[160], c.max(), int(c.argmax()), rows[0][0], rows[0][1], rows[0][2], lasry, len(allw), (c[160] - allw.mean()) / allw.std()))
    c = np.array(scan["%s|digit|nov10" % m])
    print("   %s nov10 scan g=156..166:" % m, [round(float(x), 4) for x in c[156:167]], " positions within 0.006 of best:", [int(i) for i in np.where(c >= c.max() - 0.006)[0]])
    mask = np.ones(len(c), bool); mask[154:168] = False
    j = int(np.argmax(np.where(mask, c, -9)))
    print("   best placement outside g=154..167: g=%d, %.4f per quad = %.1f log10 below best" % (j, c[j], (c.max() - c[j]) * 117))
if len(sys.argv) > 2:
    res = json.load(open(sys.argv[2])); by = collections.defaultdict(list)
    for k, x, s in res: by[k].append(s)
    claim = by["claim"][0]
    for k in ("randkey", "shuffle", "square"):
        v = np.array(by[k]); print("TEL/digit best-over-g, %-8s n=%d mean %.3f sd %.3f max %.3f ; claim %.4f exceeds all: %s ; z=%.1f" % (k, len(v), v.mean(), v.std(ddof=1), v.max(), claim, claim > v.max(), (claim - v.mean()) / v.std(ddof=1)))
# wrong keys whose square is (nearly) fully specified (<=2 unknown cells): the fair null for a completed square
full = [k for k in K if k != "nov10" and K[k]["square"].count("?") <= 2]
for m in ("TEL", "LIT"):
    for q in ("digit", "any"):
        c = np.array(scan["%s|%s|nov10" % (m, q)])
        rows = sorted(((max(scan["%s|%s|%s" % (m, q, k)]), k) for k in full), reverse=True)
        print("fully-specified wrong keys only (%d keys: %s): [%s,%s] claim@160 %.4f ; best wrong %.4f (%s) ; margin %.3f per quad = %.1f log10" % (len(full), ",".join(full), m, q, c[160], rows[0][0], rows[0][1], c[160] - rows[0][0], (c[160] - rows[0][0]) * 117))
