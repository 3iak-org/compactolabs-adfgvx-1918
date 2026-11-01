"""Aggregate census_<field>.json into tables + a per-message TSV (the file comp-adfgvx's census is compared to)."""
import sys, json, collections, statistics as st
import data as D
field = sys.argv[1] if len(sys.argv) > 1 else "printed"
res = json.load(open("census_%s.json" % field))
R = D.by_id()
for r in res:
    r["method"] = R[r["id"]]["method"]; r["status"] = R[r["id"]]["status"]
    r["plain_len"] = len(R[r["id"]]["plaintext"])
    r["nev"] = len(r["events"])
    r["wild_frac"] = r["wild_S"] / max(r["n_sent"], 1)
TYPES = ["E1", "E2", "E3", "E4", "E5", "E6"]
def tbl(rows, label):
    n = len(rows); sym = sum(r["n_sent"] for r in rows)
    ev = sum(r["nev"] for r in rows)
    byt = collections.Counter(); syms = collections.Counter()
    for r in rows:
        for t, L in r["events"]:
            byt[t] += 1; syms[t] += L
    e4 = sum(r["E4"] for r in rows)
    dist = collections.Counter(min(r["nev"], 6) for r in rows)
    lines = ["**%s**: %d messages, %d sent symbols" % (label, n, sym),
             "- messages with 0 events: %d (%.1f%%)" % (dist[0], 100 * dist[0] / n),
             "- events (E1,E2,E3,E5,E6 counted; E4 separate): %d total = %.3f per message = %.3f per 100 sent symbols" % (ev, ev / n, 100 * ev / sym),
             "- distribution of events per message: " + ", ".join("%s:%d" % (("6+" if k == 6 else k), dist[k]) for k in range(0, 7)),
             "- by type (events / symbols affected): " + ", ".join("%s %d/%d" % (t, byt[t], syms[t]) for t in ["E1", "E2", "E3", "E5", "E6"]),
             "- unreadable symbols '-'/'?' in the log (E4): %d = %.3f per 100 logged symbols" % (e4, 100 * e4 / sum(r["n_log"] for r in rows))]
    return "\n".join(lines)
out = []
out.append(tbl(res, "ALL solved entries with plaintext+key"))
out.append(tbl([r for r in res if r["wild_frac"] < 0.1], "wildcard fraction < 10% of sent symbols"))
out.append(tbl([r for r in res if r["method"] == "period key, as transcribed"], "method = as transcribed (no repair)"))
out.append(tbl([r for r in res if r["method"] != "period key, as transcribed"], "all other methods"))
out.append(tbl([r for r in res if r["method"] == "period key, length repaired"], "method = length repaired"))
# per key period
rows = []
for k in sorted({r["key"] for r in res}):
    sub = [r for r in res if r["key"] == k]
    rows.append("| %s | %d | %d | %.2f | %.2f |" % (k, len(sub), sum(r["n_sent"] for r in sub), sum(r["nev"] for r in sub) / len(sub), 100 * sum(r["nev"] for r in sub) / sum(r["n_sent"] for r in sub)))
out.append("| key | n msgs | sent symbols | events/msg | events/100 sym |\n|---|---|---|---|---|\n" + "\n".join(rows))
# length-class
for lo, hi in ((0, 100), (100, 200), (200, 300), (300, 10**6)):
    sub = [r for r in res if lo <= r["n_sent"] < hi]
    if sub: out.append("sent length %d-%d: n=%d, events/100sym %.2f, any-event fraction %.2f" % (lo, hi, len(sub), 100 * sum(r["nev"] for r in sub) / sum(r["n_sent"] for r in sub), sum(1 for r in sub if r["nev"]) / len(sub)))
# worst
w = sorted(res, key=lambda r: -r["cost"])[:12]
out.append("worst by alignment cost:\n" + "\n".join("- %s (%s) sent %d log %d cost %.2f %s %s" % (r["id"], r["key"], r["n_sent"], r["n_log"], r["cost"], r["model"], r["events"]) for r in w))
open("census_summary_%s.md" % field, "w").write("\n\n".join(out) + "\n")
print("\n\n".join(out))
import os
os.makedirs("results", exist_ok=True)
with open("results/census_check_%s.tsv" % field, "w") as f:
    f.write("id\tkey\tn_sent\tn_log\tmodel\tcost\tn_events\tevents\tE4_unreadable\twild_S\n")
    for r in sorted(res, key=lambda r: r["id"]):
        f.write("\t".join(map(str, [r["id"], r["key"], r["n_sent"], r["n_log"], r["model"], round(r["cost"], 2), r["nev"], ";".join("%s:%d" % tuple(e) for e in r["events"]), r["E4"], r["wild_S"]])) + "\n")
