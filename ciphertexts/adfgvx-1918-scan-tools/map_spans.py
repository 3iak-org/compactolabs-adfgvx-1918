"""AFTER the blind commit: map every creilly record on the transcribed pages to a span of
our blocks, allowing (a) a record = part of a block (semi-global alignment), and (b) a record
= two consecutive blocks of one page joined. Then, for each block, list the records sharing it.

usage: map_spans.py BLIND.json RECORDS.json WORKLIST.json OUT.json
For each record: best of
   single block, semi-global      cost = edits / len(record)
   two consecutive blocks joined  cost = edits / len(record) (global alignment)
Records with no printed symbols are skipped. Ties and runners-up are reported.
"""
import json, sys, os
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from semiglobal import semiglobal
from editops import align

blind, recf, wlf, out = sys.argv[1:5]
B = json.load(open(blind)); R = json.load(open(recf)); W = json.load(open(wlf))
targets = {x["id"]: x["set"] for x in W["unsolved"] + W["calibration"]}
pages = {p["pdf_page"]: [b for b in p["blocks"] if b["n_symbols"]] for p in B["pages"]}
recs = [r for r in R if r["pdf_page"] in pages and r["printed"]]

def best_for(r):
    t = r["printed"]; cands = []
    for pg in (r["pdf_page"] - 1, r["pdf_page"], r["pdf_page"] + 1):
        bl = pages.get(pg, [])
        for b in bl:
            if b["n_symbols"] < 0.5 * len(t) and b["n_symbols"] < len(t) - 60: continue
            e, s0, s1 = semiglobal(t, b["symbols"])
            cands.append(dict(kind="span", cost=e / len(t), edits=e, spans=[[pg, b["block_index"], s0, s1]]))
        for b1, b2 in zip(bl, bl[1:]):
            joined = b1["symbols"] + b2["symbols"]
            if abs(len(joined) - len(t)) > 0.25 * len(t): continue
            e, _ = align(joined, t)
            cands.append(dict(kind="join", cost=e / len(t), edits=e,
                              spans=[[pg, b1["block_index"], 0, b1["n_symbols"]], [pg, b2["block_index"], 0, b2["n_symbols"]]]))
    cands.sort(key=lambda c: c["cost"])
    return r["id"], cands[:3]

if __name__ == "__main__":
    with Pool(6) as pool:
        res = dict(pool.map(best_for, recs, chunksize=4))
    out_d = {"records": {}, "blocks": {}}
    for r in recs:
        c = res[r["id"]]
        if not c: continue
        out_d["records"][r["id"]] = dict(target=targets.get(r["id"]), status=r["status"], pdf_page=r["pdf_page"],
                                         len=len(r["printed"]), best=c[0], runners_up=c[1:])
        for sp in c[0]["spans"]:
            out_d["blocks"].setdefault(f"{sp[0]}:{sp[1]}", []).append(dict(id=r["id"], start=sp[2], end=sp[3], cost=round(c[0]["cost"], 4)))
    json.dump(out_d, open(out, "w"), indent=1)
    print(len(out_d["records"]), "records mapped")
