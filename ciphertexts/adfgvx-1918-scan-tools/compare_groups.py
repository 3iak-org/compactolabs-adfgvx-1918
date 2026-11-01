"""Group-level comparison of the vision reading with the template-OCR reading.

usage: compare_groups.py VISDIR OCRDIR OUT.json
Each vision line is matched to its best OCR line on the same page (difflib ratio on the
group text), then the vision groups and the OCR words are aligned by dynamic programming:
  pair (g, w): cost = #positions where both are confident letters and differ
                      + 1.5 * |len(g) - len(w)|
  skip a vision group: 0.6 (the OCR missed it or merged it)
  skip an OCR word: 0.1 if it has < 4 confident letters (label text, specks), else 3
A line is CONTESTED if a paired group conflicts, or an OCR word with >= 4 confident letters
is left unpaired after the first paired word (a group the reader may have skipped).
Confident = a letter from the OCR (not '?' reject, not '_' blank).
"""
import json, glob, os, sys, re, difflib

vis_dir, ocr_dir, out = sys.argv[1:4]
blocks = []
for f in sorted(glob.glob(os.path.join(vis_dir, "agent*.json"))):
    for p in json.load(open(f))["pages"]:
        for b in p["blocks"]:
            blocks.append((p["pdf_page"], b))

def conf(w):
    return sum(c.isalpha() or c == "-" for c in w)

def align(G, W):
    n, m = len(G), len(W)
    INF = 1e9
    D = [[INF] * (m + 1) for _ in range(n + 1)]; B = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if D[i][j] >= INF: continue
            if i < n and j < m:
                g, w = G[i], W[j]["text"]
                c = sum(1 for a, b in zip(g, w) if b not in "?_" and a != b) + 1.5 * abs(len(g) - len(w))
                if D[i][j] + c < D[i + 1][j + 1]: D[i + 1][j + 1] = D[i][j] + c; B[i + 1][j + 1] = (i, j, "pair")
            if i < n and D[i][j] + 0.6 < D[i + 1][j]: D[i + 1][j] = D[i][j] + 0.6; B[i + 1][j] = (i, j, "skipv")
            if j < m:
                c = 0.1 if conf(W[j]["text"]) < 4 else 3
                if D[i][j] + c < D[i][j + 1]: D[i][j + 1] = D[i][j] + c; B[i][j + 1] = (i, j, "skipo")
    path = []; i, j = n, m
    while (i, j) != (0, 0):
        pi, pj, t = B[i][j]; path.append((t, pi, pj)); i, j = pi, pj
    return path[::-1]

res = dict(lines=[], contested=[], unmatched_vision_lines=[], stats={})
st = dict(vis_symbols=0, paired_symbols=0, compared=0, agree=0, abstain=0, conflict=0, lines=0, lines_matched=0)
cache = {}
for page, b in blocks:
    if page not in cache:
        ws = json.load(open(os.path.join(ocr_dir, f"{page}.json")))[str(page)]
        L = {}
        for w in ws: L.setdefault(w["y"], []).append(w)
        cache[page] = [sorted(v, key=lambda w: w["x"]) for k, v in sorted(L.items())]
    OL = cache[page]
    for li, line in enumerate(b["lines"]):
        G = re.sub(r"[()]", "", line).split()
        st["lines"] += 1; st["vis_symbols"] += sum(map(len, G))
        v = " ".join(G)
        best = max(((difflib.SequenceMatcher(None, v, " ".join(w["text"] for w in ol), autojunk=False).ratio(), oi)
                    for oi, ol in enumerate(OL)), default=(0, None))
        if best[0] < 0.70:
            res["unmatched_vision_lines"].append(dict(page=page, block=b["block_index"], line=li, text=line))
            continue
        st["lines_matched"] += 1
        W = OL[best[1]]
        path = align(G, W)
        issues = []; first_pair = None
        for t, i, j in path:
            if t == "pair":
                first_pair = j if first_pair is None else first_pair
                g, w = G[i], W[j]["text"]
                if len(g) == len(w):
                    st["paired_symbols"] += len(g)
                    for a, c in zip(g, w):
                        st["compared"] += 1
                        if c in "?_": st["abstain"] += 1
                        elif a == c: st["agree"] += 1
                        else: st["conflict"] += 1
                    if any(c not in "?_" and a != c for a, c in zip(g, w)):
                        issues.append(dict(kind="conflict", gi=i, vis=g, ocr=w, x=W[j]["x"], x1=W[j]["x1"]))
                else:
                    if conf(w) >= 3:
                        issues.append(dict(kind="length", gi=i, vis=g, ocr=w, x=W[j]["x"], x1=W[j]["x1"]))
            elif t == "skipo" and first_pair is not None and conf(W[j]["text"]) >= 4:
                issues.append(dict(kind="ocr_extra", gi=i, vis=None, ocr=W[j]["text"], x=W[j]["x"], x1=W[j]["x1"]))
        s = W[0]["scale"]
        rec = dict(page=page, block=b["block_index"], line=li, vis=line,
                   ocr=" ".join(w["text"] for w in W), y=W[0]["y"], scale=s, issues=issues)
        res["lines"].append(rec)
        if issues:
            res["contested"].append(rec)
st["contested_lines"] = len(res["contested"]); st["unmatched_vision_lines"] = len(res["unmatched_vision_lines"])
st["conflict_groups"] = sum(len(r["issues"]) for r in res["contested"])
res["stats"] = st
json.dump(res, open(out, "w"), indent=1)
print(st)
