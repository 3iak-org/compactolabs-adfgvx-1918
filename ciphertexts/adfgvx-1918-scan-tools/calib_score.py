"""Score the blind reading of the calibration entries against the re-encrypted truth.

usage: calib_score.py TRUTH.json FINAL_DIFF.json OUT.json
Alignment: minimal edit, '*' in the truth matches anything (a position the plaintext does not fix).
Counts per entry: compared symbols (truth not '*'), substitutions, our extra symbols, our
missing symbols, and of the substitutions how many are a printed lost mark '-' on our side.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from editops import align
T = json.load(open(sys.argv[1])); F = json.load(open(sys.argv[2]))
res = {}; tot = dict(symbols_ours=0, fixed_truth=0, equal=0, sub=0, sub_lost_mark=0, ours_extra=0, ours_missing=0)
for rid, t in T.items():
    ours = F[rid]["ours"]; truth = t["truth"]
    d, ops = align(ours, truth)
    rows = []
    for op, i, j in ops:
        if op == "=":
            if truth[j] != "*": tot["equal"] += 1
            continue
        rows.append(dict(op=op, ours=ours[i] if op != "b_only" else "", truth=truth[j] if op != "a_only" else "", our_pos=i, truth_pos=j))
        if op == "sub":
            tot["sub"] += 1; tot["sub_lost_mark"] += ours[i] == "-"
        elif op == "a_only": tot["ours_extra"] += 1
        else: tot["ours_missing"] += 1
    tot["symbols_ours"] += len(ours); tot["fixed_truth"] += sum(c != "*" for c in truth)
    res[rid] = dict(n_ours=len(ours), n_truth=len(truth), wildcards=truth.count("*"), edits=d, diffs=rows)
json.dump(dict(total=tot, entries=res), open(sys.argv[3], "w"), indent=1)
print(tot)
for k, v in res.items():
    if v["diffs"]: print(k, v["diffs"])
