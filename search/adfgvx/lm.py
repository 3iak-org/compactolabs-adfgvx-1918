"""Train/plant split of the solved plaintexts, and the trigram scorer (comp-adfgvx, 2026-11-01).

LEAKAGE RULE. A plaintext used to PLANT a control must never be in the scorer's training text,
and neither may any near-copy of it (a repeated reception, a repeat transmission, a re-sent
message). So the split is by COMPONENT: two solved entries are linked when their plaintexts
share any 16-character substring (unknown marks excluded), and every component goes wholly to
one side. Components are assigned by a seeded coin (SEED), half to each side.
  - plant side: only the plaintexts with no unknown mark (`- ? # _`) are used to plant.
  - train side: every plaintext, unknown marks treated as context breaks.

Scorer: interpolated trigram over the 36 symbols A-Z0-9,
  P(c | a b) = L3 f(abc)/f(ab) + L2 f(bc)/f(b) + L1 f(c)/N + L0 / 36,
natural log, written as a 36^3 table (index a*1296 + b*36 + c) for the C attack.
Score of a text = mean log P over its trigrams that contain no unknown character.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
IDX = {c: i for i, c in enumerate(ALPH)}
SEED = 20261101
LAMBDA = (0.6, 0.3, 0.09, 0.01)
LINK = 16


def solved_plaintexts():
    rec = json.load(open(os.path.join(ROOT, "ciphertexts", "adfgvx-1918-log.records.json")))
    return [e for e in rec if e["plaintext"] and e["status"].startswith("Solved")]


def split():
    es = solved_plaintexts()
    parent = list(range(len(es)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    seen = {}
    for i, e in enumerate(es):
        p = e["plaintext"]
        for k in range(len(p) - LINK + 1):
            g = p[k:k + LINK]
            if any(c not in IDX for c in g):
                continue
            if g in seen:
                a, b = find(i), find(seen[g])
                if a != b:
                    parent[a] = b
            else:
                seen[g] = i
    comps = {}
    for i in range(len(es)):
        comps.setdefault(find(i), []).append(i)
    rng = random.Random(SEED)
    side = {}
    for root in sorted(comps, key=lambda r: min(es[i]["id"] for i in comps[r])):
        s = "plant" if rng.random() < 0.5 else "train"
        for i in comps[root]:
            side[es[i]["id"]] = (s, min(es[j]["id"] for j in comps[root]), len(comps[root]))
    return es, side


def clean(p):
    return all(c in IDX for c in p)


def train_table(texts):
    n1 = [0] * 36
    n2 = [0] * 1296
    n3 = [0] * 46656
    for t in texts:
        for i, c in enumerate(t):
            if c not in IDX:
                continue
            n1[IDX[c]] += 1
            if i >= 1 and t[i - 1] in IDX:
                n2[IDX[t[i - 1]] * 36 + IDX[c]] += 1
                if i >= 2 and t[i - 2] in IDX:
                    n3[IDX[t[i - 2]] * 1296 + IDX[t[i - 1]] * 36 + IDX[c]] += 1
    N = sum(n1)
    # context counts for conditional probabilities
    c2 = [0] * 1296   # count of bigram ab as a context (followed by anything)
    for a in range(36):
        for b in range(36):
            c2[a * 36 + b] = sum(n3[a * 1296 + b * 36 + c] for c in range(36))
    c1 = [sum(n2[b * 36 + c] for c in range(36)) for b in range(36)]
    L3, L2, L1, L0 = LAMBDA
    tab = [0.0] * 46656
    for a in range(36):
        for b in range(36):
            for c in range(36):
                p = L0 / 36 + L1 * n1[c] / N
                if c1[b]:
                    p += L2 * n2[b * 36 + c] / c1[b]
                else:
                    p += L2 / 36
                if c2[a * 36 + b]:
                    p += L3 * n3[a * 1296 + b * 36 + c] / c2[a * 36 + b]
                else:
                    p += L3 / 36
                tab[a * 1296 + b * 36 + c] = math.log(p)
    return tab, N


def score(text, tab):
    s, n = 0.0, 0
    for i in range(2, len(text)):
        a, b, c = text[i - 2], text[i - 1], text[i]
        if a in IDX and b in IDX and c in IDX:
            s += tab[IDX[a] * 1296 + IDX[b] * 36 + IDX[c]]
            n += 1
    return s / n if n else float("-inf")


def build(out_table):
    es, side = split()
    train = [e["plaintext"] for e in es if side[e["id"]][0] == "train"]
    tab, N = train_table(train)
    if out_table:
        tmp = out_table + f".tmp{os.getpid()}"
        with open(tmp, "w") as f:
            f.write("\n".join(f"{x:.6f}" for x in tab) + "\n")
        os.replace(tmp, out_table)   # atomic: readers never see a half-written table
    plant = [(e["id"], e["plaintext"], e["key"]) for e in es
             if side[e["id"]][0] == "plant" and clean(e["plaintext"])]
    return es, side, tab, N, plant


if __name__ == "__main__":
    es, side, tab, N, plant = build(sys.argv[1])
    print(len(es), "solved;", sum(1 for v in side.values() if v[0] == "train"), "train entries,",
          N, "train chars;", len(plant), "clean plant plaintexts,", sum(len(p) for _, p, _ in plant), "chars")
