"""R2 rows for the '?'-cell rule (ticket tmvx8ahcmci0o item 3).  ONE headline rule, stated:
   HEADLINE  = 'mask': every '?' cell of every key (claim included, so the claimant's 5 fills are NOT used) is unknown and the
               letters that land on it are masked.  Nobody gets cell-filling freedom, which is the only rule under which the claim
               and the nulls are treated identically without assuming what a blank cell holds.
   Other rows (reported as they come):
   'digit'   = every '?' cell of every key is a digit (the claimant's 2017-comment fill, 5-9, applied as a RULE to all keys: the claim has 5 such cells, a wrong key has 0-14).
   'complete'= mask rule, but only wrong keys with <= 2 '?' cells (complete squares) are in the null.
Gap masking (C3) applies in all rows.  Scorers: TEL (nov10 held out; solved-entry null with the entry's own period held out) and LIT.
Budget: exhaustive; per (entry,key): 21 lengths x (n+1) gap positions (4,600 for a 220-symbol entry); p179B1: 22 keys; solved null: 58 entries x 21 keys."""
import sys, json, numpy as np
import data as D, german as G, kern as K, gapscan as GS, trials
NQMIN = 40
Ks = D.keys(); R = D.by_id()
def lpm(model, ho=()): return K.to32(G.model("TEL", held_out=ho) if model == "TEL" else G.model("LIT"))
def cls(sq, rule):
    c = GS.cls_of_square(sq)
    if rule == "digit": c = np.where(c < 0, 26, c).astype(np.int32)
    return c
def best(ct, key, l32, rule):
    k = Ks[key]; out = GS.scan(ct, k["transposition"], cls(k["square"], rule), l32)
    with np.errstate(all="ignore"): mean = np.where(out[:, :, 1] >= NQMIN, out[:, :, 0] / out[:, :, 1], -np.inf)
    return out, mean
if __name__ == "__main__":
    ct = R["p179B1"]["printed"]
    sel = [r["row"] if False else r["id"] for r in json.load(open("results/r2_prereg_solved.json"))]
    # solved ids from the committed prereg run
    solved = json.load(open("results/r2_prereg_solved.json"))
    trials.log(phase="prereg-run", entry="R2", task="'?'-cell rule rows: mask (headline), digit, complete-only; TEL+LIT; same 58 solved entries", scorer_commit="50b772c", nqmin=NQMIN)
    res = {}
    for model in ("TEL", "LIT"):
        l_claim = lpm(model, ("nov10",))
        for rule in ("mask", "digit"):
            o, m = best(ct, "nov10", l_claim, rule)
            row = dict(claim=float(m[20, 160]), nq=int(o[20, 160, 1]), masked=int(o[20, 160, 2]))
            L, g = np.unravel_index(np.argmax(m), m.shape); row["best_nov10"] = (int(L), int(g), float(m[L, g]))
            wrong = {}
            for k in Ks:
                if k == "nov10": continue
                o2, m2 = best(ct, k, l_claim, rule); wrong[k] = float(m2.max())
            row["wrong_p179B1"] = wrong
            # solved entries
            sw = {}
            for e in solved:
                own = e["own"]; l_e = lpm(model, (own,)) if model == "TEL" else l_claim
                for k in Ks:
                    if k == own: continue
                    o3, m3 = best(R[e["id"]]["printed"], k, l_e, rule); sw["%s|%s" % (e["id"], k)] = float(m3.max())
            row["wrong_solved"] = sw
            res["%s|%s" % (model, rule)] = row
            print(model, rule, "done", flush=True)
    json.dump(res, open(sys.argv[1], "w"))
    comp = [k for k in Ks if k != "nov10" and Ks[k]["square"].count("?") <= 2]
    print("\ncomplete-square wrong keys:", comp)
    for key, row in res.items():
        w = row["wrong_p179B1"]; sv = np.array([v for v in row["wrong_solved"].values() if np.isfinite(v)])
        wc = max(w[k] for k in comp); scc = np.array([v for kk, v in row["wrong_solved"].items() if kk.split("|")[1] in comp and np.isfinite(v)])
        print("%-10s claim %.4f (nq %d, masked %d) | best nov10 %s | p179B1 wrong: all-21 best %.4f, complete-only best %.4f | solved null (%d finite cases) max %.4f, complete-only max %.4f"
              % (key, row["claim"], row["nq"], row["masked"], row["best_nov10"], max(w.values()), wc, len(sv), sv.max(), scc.max()))
