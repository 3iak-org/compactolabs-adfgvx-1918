"""Compare two independent vision readings of the same pages, group by group.

usage: compare_readers.py DIR_A DIR_B OUT.json
Each line of reader A is matched to the best line of reader B on the same page (difflib
ratio >= 0.7 on the group text, parentheses removed), then the groups are aligned by dynamic
programming (pair cost = differing letters + 1.5 * length difference; skip = 2.5).
Reported: per-symbol agreement over paired equal-length groups; every group that differs;
groups only one reader has inside a matched line; lines only one reader has.
"""
import json, glob, os, sys, re, difflib

da, db, out = sys.argv[1:4]

def load(d):
    P = {}
    for f in sorted(glob.glob(os.path.join(d, "agent*.json"))):
        for p in json.load(open(f))["pages"]:
            for b in p["blocks"]:
                for li, l in enumerate(b["lines"]):
                    P.setdefault(p["pdf_page"], []).append(dict(block=b["block_index"], line=li, text=l,
                                                               label=b.get("label"), G=re.sub(r"[()]", "", l).split()))
    return P

A, B = load(da), load(db)
pages = sorted(set(A) & set(B))

def align(G, H):
    n, m = len(G), len(H); INF = 1e9
    D = [[INF] * (m + 1) for _ in range(n + 1)]; Bk = [[None] * (m + 1) for _ in range(n + 1)]; D[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if D[i][j] >= INF: continue
            if i < n and j < m:
                c = sum(x != y for x, y in zip(G[i], H[j])) + 1.5 * abs(len(G[i]) - len(H[j]))
                if D[i][j] + c < D[i + 1][j + 1]: D[i + 1][j + 1] = D[i][j] + c; Bk[i + 1][j + 1] = (i, j, "pair")
            if i < n and D[i][j] + 2.5 < D[i + 1][j]: D[i + 1][j] = D[i][j] + 2.5; Bk[i + 1][j] = (i, j, "a_only")
            if j < m and D[i][j] + 2.5 < D[i][j + 1]: D[i][j + 1] = D[i][j] + 2.5; Bk[i][j + 1] = (i, j, "b_only")
    path = []; i, j = n, m
    while (i, j) != (0, 0):
        pi, pj, t = Bk[i][j]; path.append((t, pi, pj)); i, j = pi, pj
    return path[::-1]

res = dict(diffs=[], a_only_lines=[], b_only_lines=[], stats={})
st = dict(page_list=pages, pages=len(pages), a_symbols=0, compared=0, agree=0, differ=0, group_diffs=0)
for pg in pages:
    usedb = set()
    for la in A[pg]:
        va = " ".join(la["G"]); st["a_symbols"] += len(va.replace(" ", ""))
        best = max(((difflib.SequenceMatcher(None, va, " ".join(lb["G"]), autojunk=False).ratio(), k)
                    for k, lb in enumerate(B[pg])), default=(0, None))
        if best[0] < 0.7:
            res["a_only_lines"].append(dict(page=pg, block=la["block"], line=la["line"], text=la["text"], best=round(best[0], 3)))
            continue
        usedb.add(best[1]); lb = B[pg][best[1]]
        for t, i, j in align(la["G"], lb["G"]):
            if t == "pair":
                g, h = la["G"][i], lb["G"][j]
                if len(g) == len(h):
                    st["compared"] += len(g); d = sum(x != y for x, y in zip(g, h))
                    st["agree"] += len(g) - d; st["differ"] += d
                if g != h:
                    st["group_diffs"] += 1
                    res["diffs"].append(dict(kind="pair", page=pg, a_block=la["block"], a_line=la["line"], a_group=i, a=g,
                                             b_block=lb["block"], b_line=lb["line"], b_group=j, b=h, a_text=la["text"], b_text=lb["text"]))
            elif t == "a_only":
                res["diffs"].append(dict(kind="a_only", page=pg, a_block=la["block"], a_line=la["line"], a_group=i, a=la["G"][i], b=None,
                                         b_block=lb["block"], b_line=lb["line"], a_text=la["text"], b_text=lb["text"]))
            else:
                res["diffs"].append(dict(kind="b_only", page=pg, a_block=la["block"], a_line=la["line"], a_group=i, a=None, b=lb["G"][j],
                                         b_block=lb["block"], b_line=lb["line"], b_group=j, a_text=la["text"], b_text=lb["text"]))
    for k, lb in enumerate(B[pg]):
        if k not in usedb:
            res["b_only_lines"].append(dict(page=pg, block=lb["block"], line=lb["line"], text=lb["text"]))
st["diff_items"] = len(res["diffs"]); st["a_only_lines"] = len(res["a_only_lines"]); st["b_only_lines"] = len(res["b_only_lines"])
res["stats"] = st
json.dump(res, open(out, "w"), indent=1)
print(st)
