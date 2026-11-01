"""R2: p.176 GGDAA (p179B1): claimed nov10 key + one 20-symbol block lost at position 160.

Claim (creilly README 'Message 2305'; data/messages.json): square 4ARUT1OIFSKN35BZPVLD6JMXCWHQ2E7G08Y9,
transposition 9 12 7 11 3 8 16 6 14 2 10 15 5 13 1 4, block of 20 lost symbols after log symbol 160,
reading AN X O X H X L XX 11 X ARMEE X ALPENKORPS RAUM X PETERREVE X VERBASZ XX 217 X 216 X 9 X R X D X
LINIE X NAGYBESKIEREK X VERSECZ X VERSECZ X VON SERBEN BESETZT X.
"""
import sys, json, collections
import numpy as np
import adfgvx as A, data as D, german as G, kern as K

SQ10 = "4ARUT1OIFSKN35BZPVLD6JMXCWHQ2E7G08Y9"     # messages.json (blank cells filled 5..9)
T10 = [9, 12, 7, 11, 3, 8, 16, 6, 14, 2, 10, 15, 5, 13, 1, 4]
ROWS = "_NXOXHXL _X11XARM _EXALPEN _ORPSRAU _XPETERR _VEXVERB _SZXX217 _216X9XR _DXLINIE _NAGYBES __EREKXV __SECZXV __SECZXV __SERBEN __SETZTX".split()
READ = "".join(ROWS)           # 120 letters, '_' = lost-symbol letter
FILL = "DFFXXDXXVVXDXXXVXXAF"   # messages.json lost_block.fill
CT = D.by_id()["p179B1"]["ciphertext"].replace(" ", "")

def stream_with_gap(ct, g, n=20):
    return ct[:g] + "-" * n + ct[g:]

def masks_for(stream, trans, square, qmode):
    """per-letter class bitmask. qmode: how '?' (unknown) square cells behave: 'digit' or 'any'."""
    inter = A.untranspose(stream, trans)
    ms = []
    for i in range(0, len(inter) - 1, 2):
        a, b = inter[i], inter[i + 1]
        ra = [A.IDX[a]] if a in A.IDX else range(6)
        cb = [A.IDX[b]] if b in A.IDX else range(6)
        m = 0
        for r in ra:
            for c in cb:
                ch = square[6 * r + c]
                if ch == "?":
                    m |= (1 << 26) if qmode == "digit" else (1 << 27) - 1
                else:
                    m |= 1 << G.cls_of_plain(ch)
        ms.append(m)
    return ms

def best_fill(stream, trans, square, lp, qmode="digit"):
    ms = masks_for(stream, trans, square, qmode)
    s, out = K.vit_fill(ms, lp)
    txt = "".join(chr(65 + c) if c < 26 else "0" for c in out)
    return s / (len(ms) - 3), s, txt

if __name__ == "__main__":
    # 1. round trip of the claimed reading
    full = CT[:160] + FILL + CT[160:]
    dec = A.decrypt(full, T10, SQ10)
    print("claimed fill inserted at 160 -> decrypt:", dec)
    print("reading from README          :", READ.replace("_", "?"))
    mism = [(i, a, b) for i, (a, b) in enumerate(zip(dec, READ)) if b != "_" and a != b]
    print("letters where claimed reading != decrypt(claimed fill) (README letters that are not '_'):", mism)
    lpL = K.to32(G.model("LIT"))
    s, sc, txt = best_fill(stream_with_gap(CT, 160), T10, SQ10, lpL)
    print("my own best fill (LIT)  @160 under nov10: per-quad %.4f total %.3f" % (s, sc)); print(txt)
