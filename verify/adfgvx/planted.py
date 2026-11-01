"""Planted controls for the R1 solver, built from OTHER solved entries' plaintext (not R entries).
Geometry as in the claim: part A 66 letters (132 symbols), part B 54 letters (108 symbols) with symbols 5..19 lost;
random width-18 key, random square."""
import random, numpy as np
import adfgvx as A, data as D, german as G
def plaintexts():
    out = []
    for r in D.records():
        p = r["plaintext"]
        if p and r["key"] and r["status"] == "Solved" and len(p) >= 130 and not set(p) & set("-?_#"):
            out.append((r["id"], p))
    return out
def make(seed, pool):
    rng = random.Random(seed)
    rid, p = pool[rng.randrange(len(pool))]
    st = rng.randrange(0, len(p) - 120 + 1)
    t = p[st:st + 120]
    syms = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    # digits in text -> map any digit char to one of the 10 digit cells
    cells = syms[:]; rng.shuffle(cells)
    inv = {}
    dig = [c for c in cells if c.isdigit()]
    for ch in set(t):
        if ch.isdigit(): inv[ch] = None
    sq = "".join(cells)
    key = list(range(1, 19)); rng.shuffle(key)
    def enc(txt):
        inter = ""
        for ch in txt:
            k = sq.index(ch); inter += A.LAB[k // 6] + A.LAB[k % 6]
        return A.transpose(inter, key)
    ca = enc(t[:66]); cb = enc(t[66:])
    cb = cb[:5] + "-" * 15 + cb[20:]
    return rid, key, sq, [ca, cb]
