"""R2 under the prereg (C3 masking, all 21 wrong keys, every gap position and every length 0-20).
Scorer PRIMARY = TEL (Gutenberg + 1918 telegram plaintext of all OTHER key periods; the entry's own period held out).
SECONDARY = LIT.  Statistic per placement = mean log10 quadgram probability over quadgrams lying entirely in UNMASKED
letters (a letter is masked if either symbol is a filled/unknown one or its square cell is unknown), computed only if >= NQMIN
quadgrams.  Unknown square cells (incl. the 5 blank cells of nov10 that the claimant filled) are masked everywhere.
Claim = (nov10, L=20, g=160) on p179B1."""
import sys, json, numpy as np
import data as D, german as G, kern as K, gapscan as GS, trials
NQMIN = 40
Ks = D.keys(); R = D.by_id()
def lp(model, heldout=()): return K.to32(G.model(model, held_out=heldout) if model == "TEL" else G.model("LIT"))
def best_placements(ct, key, lp32):
    sc = Ks[key]; cls = GS.cls_of_square(sc["square"])
    out = GS.scan(ct, sc["transposition"], cls, lp32)      # [L,g,3]
    with np.errstate(all="ignore"):
        mean = np.where(out[:, :, 1] >= NQMIN, out[:, :, 0] / out[:, :, 1], -np.inf)
    return out, mean

if __name__ == "__main__":
    mode = sys.argv[1]
    ct = R["p179B1"]["printed"]
    if mode == "claim":
        res = {}
        for model in ("TEL", "LIT"):
            l32 = lp(model, ("nov10",))
            out, mean = best_placements(ct, "nov10", l32)
            claim = mean[20, 160]
            res[model] = dict(claim=float(claim), claim_nq=int(out[20, 160, 1]), claim_masked=int(out[20, 160, 2]), claim_total=float(out[20, 160, 0]))
            L, g = np.unravel_index(np.argmax(mean), mean.shape)
            res[model]["best_under_nov10"] = dict(L=int(L), g=int(g), score=float(mean[L, g]))
            order = np.dstack(np.unravel_index(np.argsort(-mean, axis=None), mean.shape))[0][:8]
            res[model]["top8_nov10"] = [(int(a), int(b), float(mean[a, b])) for a, b in order]
            res[model]["L20_g150_170"] = [round(float(mean[20, g]), 4) for g in range(150, 171)]
            wrong = {}
            for k in Ks:
                if k == "nov10": continue
                o2, m2 = best_placements(ct, k, l32)
                Lw, gw = np.unravel_index(np.argmax(m2), m2.shape)
                wrong[k] = dict(best=float(m2[Lw, gw]), L=int(Lw), g=int(gw), nq=int(o2[Lw, gw, 1]), source=Ks[k]["source"], n_placements=int(np.isfinite(m2).sum()))
            res[model]["wrong"] = wrong
        json.dump(res, open(sys.argv[2], "w"), indent=1)
        for model in res:
            w = res[model]["wrong"]; bw = max(w.items(), key=lambda kv: kv[1]["best"])
            print(model, "claim %.4f (nq %d, masked %d)" % (res[model]["claim"], res[model]["claim_nq"], res[model]["claim_masked"]), "| best under nov10 any (L,g):", res[model]["best_under_nov10"], "| best wrong key:", bw[0], bw[1])

    if mode == "solved":
        import random
        periods = ["nov01", "nov04", "nov07", "nov13_16", "nov10", "nov22"]
        cand = sorted(r["id"] for r in D.records() if r["status"] == "Solved" and r["plaintext"] and r["key"] in periods
                      and 200 <= len(r["printed"]) <= 250 and not set(r["printed"]) & set("-?") and r["id"] != "p179B1")
        random.Random(20261101).shuffle(cand); sel = cand[:100]
        trials.log(phase="prereg-run", entry="R2", task="solved-entry null: gap search (L 0-20, every g) under every wrong key, masked, TEL own-period-held-out", entries=sel, n_cand=len(cand), nqmin=NQMIN, scorer_commit="50b772c")
        res = []
        models = {}
        for rid in sel:
            r = R[rid]; own = r["key"]
            if own not in models: models[own] = lp("TEL", (own,))
            row = {"id": rid, "own": own, "len": len(r["printed"]), "wrong": {}}
            for k in Ks:
                if k == own: continue
                o, m = best_placements(r["printed"], k, models[own])
                row["wrong"][k] = float(m.max())
            # reference: the entry under its own key, best (L,g) -- should be L=0
            o, m = best_placements(r["printed"], own, models[own]); row["own_best"] = float(m[0].max())
            res.append(row)
        json.dump(res, open(sys.argv[2], "w"))
        allw = np.array([v for row in res for v in row["wrong"].values()])
        print("solved-entry null: %d entries x %d wrong keys = %d (entry,key) maxima; max %.4f; 99th pct %.4f; mean %.4f" % (len(res), len(Ks) - 1, len(allw), allw.max(), np.percentile(allw, 99), allw.mean()))
