"""Step 4: is any detection's reading a near-copy of an already-solved plaintext (a repeat
reception), or of the scorer's training text? Longest common substring (unknowns break runs)
of each detection's plaintext with every solved plaintext in records.json."""
import json, os
from common import *
rec = json.load(open(os.path.join(SRC, "ciphertexts/adfgvx-1918-log.records.json")))
solved = [(e["id"], e["plaintext"]) for e in rec if e.get("plaintext") and e["status"].startswith("Solved")]
def lcs(a, b):
    best, bi = 0, ""; prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i-1] == b[j-1] and a[i-1] != "-":
                cur[j] = prev[j-1] + 1
                if cur[j] > best: best, bi = cur[j], a[i-cur[j]:i]
        prev = cur
    return best, bi
print("unit           best_solved   lcs  substring")
for t in targets():
    if not t["above"]: continue
    m = max(((lcs(t["plain"], p), i) for i, p in solved), key=lambda x: x[0][0])
    print(f"{t['unit']:14s} {m[1]:12s} {m[0][0]:4d}  {m[0][1]}")
