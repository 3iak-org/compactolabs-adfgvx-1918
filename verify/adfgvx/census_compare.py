"""Compare my census with comp-adfgvx's results/adfgvx-mutilation.csv (read only AFTER my census was committed: 50b772c)."""
import csv, json, sys, collections
mine = {r["id"]: r for r in json.load(open("census_printed.json"))}
rows = [l for l in open(sys.argv[1]) if not l.startswith("#")]
comp = {r["id"]: r for r in csv.DictReader(rows)}
common = sorted(set(mine) & set(comp))
print("mine %d, comp %d, common %d, only-mine %s, only-comp %s" % (len(mine), len(comp), len(common), sorted(set(mine) - set(comp)), sorted(set(comp) - set(mine))))
def mytypes(r):
    c = collections.Counter(); s = collections.Counter()
    for t, L in r["events"]: c[t] += 1; s[t] += L
    return c, s
agree_ev = agree_all = 0; dis = []
for i in common:
    c, s = mytypes(mine[i]); k = comp[i]
    mev = sum(c[t] for t in ("E1", "E2", "E3", "E5", "E6")); cev = int(k["events"])
    mine_t = tuple(c[t] for t in ("E1", "E2", "E3", "E5")); comp_t = tuple(int(k[x]) for x in ("E1_ev", "E2_ev", "E3_ev", "E5"))
    msym = sum(L for t, L in mine[i]["events"] if t in ("E1", "E2", "E3", "E5")); csym = int(k["cost"])
    if mev == cev: agree_ev += 1
    if mine_t == comp_t and msym == csym: agree_all += 1
    else: dis.append((i, mine[i]["key"], k["class"], mev, cev, mine_t, comp_t, msym, csym, k["page_reading_differs"]))
print("same number of events: %d/%d ; identical type counts and symbol-cost: %d/%d" % (agree_ev, len(common), agree_all, len(common)))
byclass = collections.Counter(d[2] for d in dis); print("disagreements by comp class:", dict(byclass))
for d in dis: print(d)
