"""Original-page y of every reader line, from the OCR lines it matched; lines the OCR did not
match are interpolated (least squares on line index) from the matched lines of the same block,
or failing that of the same page. Also the median group-start x per group slot on the page.

usage: line_pos.py OCR_VS_READER1.json OUT.json
"""
import json, sys
import numpy as np
c = json.load(open(sys.argv[1]))
pos = {}; seq = {}
for x in c["lines"]:
    pos[(x["page"], x["block"], x["line"])] = x["y"] * x["scale"]
allk = {(x["page"], x["block"], x["line"]) for x in c["lines"]} | {(x["page"], x["block"], x["line"]) for x in c["unmatched_vision_lines"]}
pages = {}
for k in sorted(allk):
    pages.setdefault(k[0], []).append(k)
out = {}
for pg, ks in pages.items():
    order = sorted(ks, key=lambda k: (k[1], k[2]))
    idx = {k: i for i, k in enumerate(order)}
    known = [(idx[k], pos[k]) for k in order if k in pos]
    for k in order:
        if k in pos:
            y = pos[k]; how = "ocr"
        else:
            same = [(k2[2], pos[k2]) for k2 in order if k2 in pos and k2[1] == k[1]]
            if len(same) >= 2:
                a, b = np.polyfit([s[0] for s in same], [s[1] for s in same], 1); y = a * k[2] + b; how = "block-fit"
            elif same:
                y = same[0][1] + (k[2] - same[0][0]) * 46; how = "block-1"
            else:
                near = sorted(known, key=lambda t: abs(t[0] - idx[k]))[:2]
                if len(near) == 2 and near[0][0] != near[1][0]:
                    a = (near[1][1] - near[0][1]) / (near[1][0] - near[0][0]); y = near[0][1] + a * (idx[k] - near[0][0])
                else:
                    y = None
                how = "page-interp"
        out[f"{pg}:{k[1]}:{k[2]}"] = dict(y=None if y is None else round(float(y), 1), how=how)
json.dump(out, open(sys.argv[2], "w"), indent=0)
print(len(out), "lines;", sum(v["how"] == "ocr" for v in out.values()), "from OCR")
