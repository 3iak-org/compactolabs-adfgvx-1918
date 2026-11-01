"""Find where a reader's line sits on the page, via the OCR word boxes, and crop a group.

usage: locate.py OCRDIR PAGE "LINE TEXT" GROUP_INDEX OUT.png [--scale S]
The OCR line best matching LINE TEXT gives y; the OCR word best matching the group gives x.
Coordinates are mapped back to the original page (OCR works on a rescaled, deskewed copy,
so the crop is padded generously).
"""
import json, sys, os, difflib, subprocess
ocr_dir, page, text, gi, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]
scale = sys.argv[sys.argv.index("--scale") + 1] if "--scale" in sys.argv else "2"
ws = json.load(open(os.path.join(ocr_dir, f"{page}.json")))[str(page)]
L = {}
for w in ws: L.setdefault(w["y"], []).append(w)
best = max(L, key=lambda y: difflib.SequenceMatcher(None, text, " ".join(w["text"] for w in sorted(L[y], key=lambda w: w["x"])), autojunk=False).ratio())
line = sorted(L[best], key=lambda w: w["x"])
g = text.split()[gi]
w = max(line, key=lambda w: difflib.SequenceMatcher(None, g, w["text"]).ratio() - 0.001 * abs(line.index(w) - gi))
s = w["scale"]
x0, x1 = int(w["x"] * s) - 140, int(w["x1"] * s) + 140
y0, y1 = int((best - 40) * s), int((best + 80) * s)
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, "-I", os.path.join(here, "crop.py"), os.path.join(os.environ["TMPDIR"], "pdf", "childs.pdf"),
                str(page), out, str(x0), str(y0), str(x1), str(y1), "--scale", scale], check=True)
