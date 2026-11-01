"""Independent Python re-check of e2.c readings (no shared code with e2.c, different decryption
method: column slicing by read-out rank, then pairs by row-major read of the filled grid).
Usage: pycheck.py  - re-scores every row of results/wrongkeys.tsv and the top rows of
results/randkeys.tsv.gz; reports max |diff| of score and any plaintext mismatch."""
import math, sys, csv, gzip
from common import *
AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; L6 = "ADFGVX"
tab = [float(x) for x in open(LMT)]
PEN = math.log(1 / 36)

def edit(ct, edits):
    """apply edits by the jattack rule (positions in the original string, ascending; an edit that
    falls inside or just after a deletion's span is dropped)"""
    es = sorted([(int(p), ty) for ty, p in (e.split("@") for e in edits)], key=lambda x: x[0]) if edits else []
    # stable sort on position keeps the given order for ties, as in the C
    out, i = [], 0; pending = list(es)
    while i <= len(ct):
        while pending and pending[0][0] == i:
            p, ty = pending.pop(0)
            if ty == "ins1": out.append("-")
            elif ty == "ins5": out.extend("-" * 5)
            elif ty == "del1": i += 1
            else: i += 5
        if pending and pending[0][0] < i - 0 and pending[0][0] != i:  # stuck: never applied
            pass
        if i < len(ct): out.append(ct[i])
        i += 1
    return "".join(out)

def decrypt(v, square, perm):
    k = len(perm); n = len(v); q, r = divmod(n, k)
    cols = {}; pos = 0
    for rank in range(1, k + 1):
        c = perm.index(rank); ln = q + (1 if c < r else 0)
        cols[c] = v[pos:pos + ln]; pos += ln
    stream = "".join(cols[c][row] for row in range(q + 1) for c in range(k) if row < len(cols[c]))
    pl = []
    for j in range(len(stream) // 2):
        a, b = stream[2 * j], stream[2 * j + 1]
        if a in L6 and b in L6 and square[L6.index(a) * 6 + L6.index(b)] != "?":
            pl.append(square[L6.index(a) * 6 + L6.index(b)])
        else: pl.append("-")
    return "".join(pl)

def score(pl):
    s = 0
    for i in range(2, len(pl)):
        t = pl[i - 2:i + 1]
        s += PEN if "-" in t else tab[AL.index(t[0]) * 1296 + AL.index(t[1]) * 36 + AL.index(t[2])]
    return s / (len(pl) - 2)

if __name__ == "__main__":
    K = keys(); U = units(); md = 0; bad = 0; n = 0
    for row in csv.DictReader(open("results/wrongkeys.tsv"), delimiter="\t"):
        k = K[row["key"]]
        pl = decrypt(edit(U[row["unit"]]["text"], row["edits"].split(",") if row["edits"] else []), k["square"], k["transposition"])
        md = max(md, abs(score(pl) - float(row["score"]))); bad += pl != row["plain"]; n += 1
    print(f"wrongkeys: {n} rows, max |score diff| {md:.2e}, plaintext mismatches {bad}")
    try:
        rows = list(csv.DictReader(gzip.open("results/randkeys.tsv.gz", "rt"), delimiter="\t"))
    except FileNotFoundError:
        sys.exit()
    rows.sort(key=lambda r: -float(r["score"])); md = 0; bad = 0
    sel = rows[:500] + rows[::50]
    for row in sel:
        pm = list(map(int, row["perm"].split(".")))
        ed = [] if row["edits"] == "-" else row["edits"].split(",")
        pl = decrypt(edit(U[row["unit"]]["text"], ed), row["square"], pm)
        md = max(md, abs(score(pl) - float(row["score"]))); bad += pl != row["plain"]
    print(f"randkeys: {len(sel)} rows (top 500 + every 50th), max |score diff| {md:.2e}, plaintext mismatches {bad}")
