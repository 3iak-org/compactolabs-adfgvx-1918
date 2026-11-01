"""Turn the creilly diff into adjudication items: runs of differences, grouped by printed line,
each with a full-width crop box of the line(s) involved and both readings in context.

usage: adj_items.py FINAL_DIFF.json LINEPOS.json OUT.json
"""
import json, sys
fd = json.load(open(sys.argv[1])); lp = json.load(open(sys.argv[2]))
items = []
for rid, v in sorted(fd.items()):
    ds = v["diffs"]
    runs = []
    for x in ds:
        if runs and ((x["op"] != "b_only" and x["our_pos"] <= runs[-1]["eo"] + 2) or (x["op"] == "b_only" and x["our_pos"] <= runs[-1]["eo"] + 2)) \
                and x.get("line") == runs[-1]["line_last"] and x.get("block") == runs[-1]["block"]:
            r = runs[-1]; r["eo"] = max(r["eo"], x["our_pos"]); r["et"] = max(r["et"], x["their_pos"]); r["ops"].append(x)
        else:
            runs.append(dict(so=x["our_pos"], eo=x["our_pos"], st=x["their_pos"], et=x["their_pos"], ops=[x],
                             page=x.get("page"), block=x.get("block"), line=x.get("line"), line_last=x.get("line")))
    for r in runs:
        lines = sorted({o.get("line") for o in r["ops"]})
        ctx = 8
        o0, o1 = max(0, r["so"] - ctx), r["eo"] + ctx + 1
        t0, t1 = max(0, r["st"] - ctx), r["et"] + ctx + 1
        y = lp.get(f'{r["page"]}:{r["block"]}:{lines[0]}', {}).get("y") if r["page"] else None
        y2 = lp.get(f'{r["page"]}:{r["block"]}:{lines[-1]}', {}).get("y") if r["page"] else None
        items.append(dict(id=rid, set=v["set"], page=r["page"], block=r["block"], lines=lines,
                          ops=[(o["op"], o["ours"], o["theirs"], o["our_pos"], o["their_pos"]) for o in r["ops"]],
                          ours_ctx=v["ours"][o0:o1], theirs_ctx=v["theirs"][t0:t1], ours_at=o0, theirs_at=t0,
                          n=len(r["ops"]),
                          crop=None if y is None else dict(page=r["page"], x0=170, x1=2380, y0=y - 22, y1=(y2 or y) + 62)))
json.dump(items, open(sys.argv[3], "w"), indent=1)
print(len(items), "items")
