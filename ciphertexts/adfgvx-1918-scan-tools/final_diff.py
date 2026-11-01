"""Diff our reading of each target against creilly's `printed`, on the mapped spans.

usage: final_diff.py BLIND.json RECORDS.json SPANS.json OVERRIDES.json OUT.json
Our string for an id = the concatenation of its spans (OVERRIDES replace the automatic
mapping, each with a stated reason). When an id is the only record on a block, its span is
widened to the whole block, so a run creilly omits (e.g. trailing lost groups) shows as a
difference rather than being aligned away.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from editops import align

blind, recf, spf, ovf, out = sys.argv[1:6]
B = json.load(open(blind)); R = {r["id"]: r for r in json.load(open(recf))}
S = json.load(open(spf)); OV = json.load(open(ovf))
bl = {(p["pdf_page"], b["block_index"]): b for p in B["pages"] for b in p["blocks"]}
share = {}
for k, v in S["blocks"].items():
    share[tuple(map(int, k.split(":")))] = [x["id"] for x in v]

def loc_table(b):
    loc = []
    for li, l in enumerate(b["lines"]):
        gi = 0
        for tok in l.split():
            t = tok.replace("(", "").replace(")", "")
            if not t or any(c.islower() or c.isdigit() for c in t) or "'" in t: continue
            if len(t) >= 7 and sum(c not in "ADFGVX-?" for c in t) >= 2: continue
            for k in range(len(t)): loc.append((li, gi, k, t))
            gi += 1
    return loc

res = {}
for rid, m in S["records"].items():
    if not m["target"]: continue
    spans = OV[rid]["spans"] if rid in OV else m["best"]["spans"]
    how = "override: " + OV[rid]["reason"] if rid in OV else m["best"]["kind"]
    if rid not in OV and len(spans) == 1:
        pg, bi, s0, s1 = spans[0]
        if share.get((pg, bi)) == [rid]:
            spans = [[pg, bi, 0, bl[(pg, bi)]["n_symbols"]]]
    ours = ""; where = []
    for pg, bi, s0, s1 in spans:
        b = bl[(pg, bi)]; L = loc_table(b)
        ours += b["symbols"][s0:s1]
        where += [(pg, bi) + tuple(L[i][:3]) for i in range(s0, s1)]
    theirs = R[rid]["printed"]
    d, ops = align(ours, theirs)
    diffs = []
    for op, i, j in ops:
        if op == "=": continue
        w = where[min(i, len(where) - 1)] if where else None
        diffs.append(dict(op=op, ours=ours[i] if op != "b_only" else "", theirs=theirs[j] if op != "a_only" else "",
                          our_pos=i, their_pos=j, **(dict(page=w[0], block=w[1], line=w[2], group=w[3], k=w[4]) if w else {})))
    res[rid] = dict(set=m["target"], status=m["status"], spans=spans, mapping=how, ours=ours, theirs=theirs,
                    n_ours=len(ours), n_theirs=len(theirs), edit_distance=d, columns=len(ops),
                    equal=len(ops) - len(diffs), diffs=diffs)
json.dump(res, open(out, "w"), indent=1)
for s in ("unsolved", "calibration"):
    e = [v for v in res.values() if v["set"] == s]
    print(s, len(e), "ids; equal", sum(v["equal"] for v in e), "of", sum(v["columns"] for v in e), "columns; edits", sum(v["edit_distance"] for v in e),
          "; ours", sum(v["n_ours"] for v in e), "theirs", sum(v["n_theirs"] for v in e))
