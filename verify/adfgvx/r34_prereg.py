"""R3/R4 under the prereg (B2, C7).  Statistics, fixed before running:
  S1 = Smith-Waterman local score (match +2, mismatch -2, gap -3; lost symbol scores 0)   [best offset, gap aware]
  S2 = semi-global Levenshtein distance of the open entry (all of it) against any substring of the other entry
  S3 = best ungapped offset: matches among compared known pairs (>= 40 compared)
Null population: every OTHER solved entry in the log (status Solved*, ciphertext present), excluding the twin;
reported (a) over all of them, (b) over the subset with the twin's key, (c) over the subset logged on the twin's date.
Both transcriptions of the open entry are scored (creilly@e60da03; Schmeh 2017 with lowercase/dash rules of schmeh.py)."""
import sys, json, ctypes, os
import numpy as np
import adfgvx as A, data as D, schmeh as SM, trials
from r34 import sw
_l = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "liblev.so"))
_l.semiglobal.restype = ctypes.c_int; _l.semiglobal.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p]
_l.best_hamming.restype = ctypes.c_int; _l.best_hamming.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
def enc(s): return bytes(A.IDX[c] if c in A.IDX else 6 for c in s)
def stats(q, t):
    be = ctypes.c_int(0); d = _l.semiglobal(enc(q), len(q), enc(t), len(t), ctypes.byref(be))
    o = ctypes.c_int(0); c = ctypes.c_int(0); h = _l.best_hamming(enc(q), len(q), enc(t), len(t), ctypes.byref(o), ctypes.byref(c))
    return dict(S1=sw(q, t), S2=d, S3=h, S3_cmp=c.value, S3_off=o.value)
R = D.by_id()
solved = [r for r in D.records() if r["status"].startswith("Solved") and r["printed"].strip()]
def run(open_id, twin_id, schmeh_head, variants):
    twin = R[twin_id]; res = {"open": open_id, "twin": twin_id, "twin_key": twin["key"], "twin_date": twin["date"]}
    sm = SM.entries("upper")
    for name, q in variants.items():
        st_twin = stats(q, twin["printed"])
        rows = []
        for r in solved:
            if r["id"] in (twin_id, open_id): continue
            s = stats(q, r["printed"]); s["id"] = r["id"]; s["key"] = r["key"]; s["date"] = r["date"]; rows.append(s)
        out = {"twin": st_twin, "n_null_all": len(rows)}
        for label, sub in (("all", rows), ("same_key", [x for x in rows if x["key"] == twin["key"]]), ("same_date", [x for x in rows if x["date"] == twin["date"]])):
            if not sub: continue
            out[label] = dict(n=len(sub), S1_max=max(x["S1"] for x in sub), S1_ge_twin=sum(x["S1"] >= st_twin["S1"] for x in sub),
                               S2_min=min(x["S2"] for x in sub), S2_le_twin=sum(x["S2"] <= st_twin["S2"] for x in sub),
                               S3_max=max(x["S3"] for x in sub), S3_ge_twin=sum(x["S3"] >= st_twin["S3"] for x in sub),
                               S1_top3=sorted(((x["S1"], x["id"]) for x in sub), reverse=True)[:3])
        res[name] = out
    return res
if __name__ == "__main__":
    sm = {h: s for h, s in SM.entries("upper")}
    sml = {h: s for h, s in SM.entries("lost")}
    r3 = {"creilly": R["p155E"]["printed"], "schmeh_v_as_V": sm["Page 152"], "schmeh_v_as_lost": sml["Page 152"]}
    r4 = {"creilly": R["p192A"]["printed"], "schmeh": sm["Page 189"]}
    trials.log(phase="prereg-run", entry="R3/R4", task="duplicate statistics S1 SW, S2 semiglobal Levenshtein, S3 best ungapped offset vs every other solved entry", variants3=list(r3), variants4=list(r4), n_solved=len(solved), scorer_commit="n/a (no German scoring)")
    out = {"R3": run("p155E", "p139B", None, r3), "R4": run("p192A", "p188_.2", None, r4)}
    json.dump(out, open(sys.argv[1], "w"), indent=1)
    for k in out:
        for v in out[k]:
            if isinstance(out[k][v], dict) and "twin" in out[k][v]:
                x = out[k][v]; print(k, v, "twin", x["twin"], "| all:", {a: b for a, b in x["all"].items() if a != "S1_top3"}, x["all"]["S1_top3"], "| same_key n=%d S1>=twin %d S2<=twin %d S3>=twin %d" % (x["same_key"]["n"], x["same_key"]["S1_ge_twin"], x["same_key"]["S2_le_twin"], x["same_key"]["S3_ge_twin"]))
