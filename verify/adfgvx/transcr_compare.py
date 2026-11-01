"""Creilly@e60da03 vs Schmeh-2017 for the R entries; and R1 square: is it a known period square?"""
import json, schmeh as S, data as D, adfgvx as A
R = D.by_id(); K = D.keys()
sm = {}
for (h, s) in S.entries("upper"): sm.setdefault(h, []).append(s)
pairs = {"p156C3": ("Page 153", 0), "p156C6": ("Page 153", 1), "p179B1": ("Page 176", 0), "p155E": ("Page 152", 0), "p192A": ("Page 189", 0)}
out = {}
for rid, (h, i) in pairs.items():
    s = sm[h][i]; c = R[rid]["printed"]
    diff = [(k, c[k], s[k]) for k in range(min(len(c), len(s))) if c[k] != s[k]]
    out[rid] = dict(len_creilly=len(c), len_schmeh=len(s), diffs=diff, lost_creilly=sum(ch in "-?" for ch in c), lost_schmeh=sum(ch == "-" for ch in s))
    print(rid, out[rid])
# gap marked?
print("p179B1 creilly: symbols_in_log %s count_in_log(header) %s; any '-' in printed: %s ; Schmeh: any '-' in entry: %s" % (R["p179B1"]["symbols_in_log"], R["p179B1"]["count_in_log"], "-" in R["p179B1"]["printed"], "-" in sm["Page 176"][0]))
# R1 square: compatible with any known period square?
SQ = "?TXUGI????8?2WO?CMB1?SZ?5NDH?VEA??LR"
for kid, k in K.items():
    if kid == "ours_nov07_18col": continue
    sq = k["square"]
    both = [(a, b) for a, b in zip(SQ, sq) if a != "?" and b != "?"]
    agree = sum(a == b for a, b in both)
    # up to relabelling? ADFGVX squares are fixed by letter labelling, so compare cell by cell.
    print("%-18s known-both %2d agree %2d" % (kid, len(both), agree))
