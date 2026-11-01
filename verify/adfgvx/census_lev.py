"""Unit-cost (Levenshtein) edit distance per message, with the SAME wildcard rule, to compare with comp's `cost`."""
import csv, json, sys
import census as C, adfgvx as A, data as D
C.GAP_OPEN, C.GAP_EXT, C.SUB = 0.0, 1.0, 1.0
R = D.records(); K = D.keys()
rows = [l for l in open(sys.argv[1]) if not l.startswith("#")]
comp = {r["id"]: r for r in csv.DictReader(rows)}
lev = {}
for r in R:
    if not (r["plaintext"] and r["key"]): continue
    k = K[r["key"]]
    S = A.transpose_gen(C.interim_pattern(r["plaintext"], k["square"]), k["transposition"])
    P = r["printed"]
    lev[r["id"]] = C.fast_cost(S, P)
json.dump(lev, open("census_lev.json", "w"))
common = sorted(set(lev) & set(comp))
eq = [i for i in common if abs(lev[i] - float(comp[i]["cost"])) < 1e-6]
print("Levenshtein cost (mine, vs printed) == comp's cost on %d/%d" % (len(eq), len(common)))
dif = [(i, lev[i], comp[i]["cost"], comp[i]["class"], comp[i]["page_reading_differs"]) for i in common if i not in eq]
for d in dif: print(d)
