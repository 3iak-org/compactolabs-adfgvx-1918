"""R2 null: the same gap model (one block of 20 lost symbols inserted at every position 0..220)
under EVERY key in keys.json, best-fill (Viterbi) scored.  Statistic = best total log10 / (120-3)."""
import sys, json
import numpy as np
import adfgvx as A, data as D, german as G, kern as K
from r2 import CT, SQ10, T10, stream_with_gap, best_fill

if __name__ == "__main__":
    Ks = D.keys()
    models = {"LIT": K.to32(G.model("LIT")), "TEL": K.to32(G.model("TEL", held_out=("nov10",)))}
    out = {}
    for mname, lp in models.items():
        for qmode in ("digit", "any"):
            for kid, k in Ks.items():
                sq = SQ10 if kid == "nov10" else k["square"]
                tr = k["transposition"]
                sc = []
                for g in range(0, len(CT) + 1):
                    s, tot, _ = best_fill(stream_with_gap(CT, g), tr, sq, lp, qmode)
                    sc.append(s)
                out["%s|%s|%s" % (mname, qmode, kid)] = sc
            print(mname, qmode, "done", flush=True)
    json.dump(out, open(sys.argv[1], "w"))
