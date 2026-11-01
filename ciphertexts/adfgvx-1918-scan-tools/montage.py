"""Stack crops of disputed groups into one PNG for adjudication by eye.

usage: montage.py ITEMS.json OUT.png
ITEMS: list of {page, x0, y0, x1, y1, bx0, bx1} in original 300-dpi page pixels; the crop is
the line segment [x0,x1]x[y0,y1]; the disputed group [bx0,bx1] is boxed. Crops are stacked
top to bottom in list order, separated by a black bar, and padded to a common width.
"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crop import page_array, write_png

PDF = os.path.join(os.environ.get("TMPDIR", "/tmp"), "pdf", "childs.pdf")
items = json.load(open(sys.argv[1]))
rows = []
W = max(int(it["x1"]) - int(it["x0"]) for it in items)
for k, it in enumerate(items):
    a = page_array(PDF, it["page"])
    x0, y0, x1, y1 = [int(round(it[c])) for c in ("x0", "y0", "x1", "y1")]
    x0, y0 = max(0, x0), max(0, y0)
    c = a[y0:y1, x0:x1].copy()
    if "bx0" in it:
        bx0, bx1 = int(it["bx0"]) - x0, int(it["bx1"]) - x0
        bx0, bx1 = max(0, bx0), min(c.shape[1] - 1, bx1)
        c[1:3, bx0:bx1] = 0; c[-3:-1, bx0:bx1] = 0
        c[:, bx0:bx0 + 2] = 0; c[:, bx1 - 1:bx1 + 1] = 0
    pad = np.full((c.shape[0], W), 255, np.uint8); pad[:, :c.shape[1]] = c
    # index ticks on the left: k+1 small squares in groups of five
    rows.append(pad)
    rows.append(np.zeros((6, W), np.uint8))
write_png(sys.argv[2], np.vstack(rows))
print(sys.argv[2], len(items))
