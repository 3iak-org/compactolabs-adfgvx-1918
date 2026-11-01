"""Print adjudication items k..k+n and render their crops into one montage.
usage: adj_show.py ITEMS.json K N OUT.png"""
import json, sys, os, subprocess
it = json.load(open(sys.argv[1])); k, n, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
sel = it[k:k + n]
for i, x in enumerate(sel):
    print(f"#{k+i} {x['id']} p{x['page']} b{x['block']} L{x['lines']} n={x['n']}")
    print("   ops:", " ".join(f"{o[0]}:{o[1] or '_'}/{o[2] or '_'}@{o[3]}" for o in x["ops"])[:300])
    print("   ours  :", x["ours_ctx"]); print("   theirs:", x["theirs_ctx"])
crops = [x["crop"] for x in sel if x["crop"]]
tmp = out + ".json"; json.dump(crops, open(tmp, "w"))
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, "-I", os.path.join(here, "montage.py"), tmp, out], check=True, stdout=subprocess.DEVNULL)
