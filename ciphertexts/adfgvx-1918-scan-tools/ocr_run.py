"""Run the template OCR over pages; self-train templates first.

usage: ocr_run.py OUT.json PAGE [PAGE ...]
Writes per page: lines -> words -> {x, y, n, resid, text, score[], margin[]}.
A cell whose best score is < REJECT is '?'; a cell holding only a short horizontal bar is '-'.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from ocr import page_glyphs, big_glyph, classify_fast, SEED, SH, CH, CWIN
from crop import page_array

REJECT = 0.76
TDIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "ocr")

def seed_templates():
    ws, a = page_glyphs(72)
    acc = {}
    for y, txt in SEED.items():
        gl = [w for w in ws if abs(w["y"] - y) < 8 and w["n"] == 5][-8:]
        assert len(gl) == 8, (y, len(gl))
        for w, grp in zip(gl, txt.split()):
            for c, ch in zip(w["cx"], grp):
                acc.setdefault(ch, []).append(big_glyph(a, w["yc"], c)[SH:SH + CH, SH:SH + CWIN])
    return {k: np.mean(v, 0) for k, v in acc.items()}

def is_dash(big):
    g = big[SH:SH + CH, SH:SH + CWIN] > 0.45
    if g.sum() < 15:
        return None  # blank
    rows = np.nonzero(g.sum(1))[0]; cols = np.nonzero(g.sum(0))[0]
    if rows[-1] - rows[0] <= 9 and cols[-1] - cols[0] >= 10 and abs((rows[0] + rows[-1]) / 2 - CH / 2) < 12:
        return True
    return False

def read_page(page, T, adapt=True):
    ws, a = page_glyphs(page)
    bigs = np.array([big_glyph(a, w["yc"], c) for w in ws for c in w["cx"]]) if ws else np.zeros((0, CH + 2 * SH, CWIN + 2 * SH))
    if len(bigs) == 0:
        return [], bigs, []
    chars, S = classify_fast(bigs, T)
    if adapt:   # per-page templates from this page's own confident glyphs (unsupervised)
        o = np.argsort(S, 1); bi = o[:, -1]; sc0 = S[np.arange(len(S)), bi]; mg0 = sc0 - S[np.arange(len(S)), o[:, -2]]
        T2 = {}
        for ci, c in enumerate(chars):
            sel = (bi == ci) & (sc0 > 0.80) & (mg0 > 0.10)
            T2[c] = bigs[sel][:, SH:SH + CH, SH:SH + CWIN].mean(0) if sel.sum() >= 15 else T[c]
        chars, S = classify_fast(bigs, T2)
    order = np.argsort(S, 1)
    best = order[:, -1]; sc = S[np.arange(len(S)), best]; mg = sc - S[np.arange(len(S)), order[:, -2]]
    k = 0; out = []; labels = []
    for w in ws:
        txt = []; scs = []; mgs = []
        for _ in w["cx"]:
            d = is_dash(bigs[k])
            if d:
                ch = "-"
            elif d is None:
                ch = "_"
            else:
                ch = chars[best[k]] if sc[k] >= REJECT else "?"
            txt.append(ch); scs.append(round(float(sc[k]), 3)); mgs.append(round(float(mg[k]), 3))
            labels.append((ch, float(sc[k]), float(mg[k])))
            k += 1
        out.append(dict(scale=round(w["scale"], 4), line=w["line"], y=w["y"], x=w["x"], x1=w["x1"], n=w["n"], resid=round(w["resid"], 1),
                        text="".join(txt), score=scs, margin=mgs))
    return out, bigs, labels

def train(pages, T, rounds=2):
    for r in range(rounds):
        acc = {c: [] for c in T}
        for p in pages:
            _, bigs, labels = read_page(p, T, adapt=False)
            for big, (ch, s, m) in zip(bigs, labels):
                if ch in acc and s > 0.85 and m > 0.12:
                    acc[ch].append(big[SH:SH + CH, SH:SH + CWIN])
        T = {c: (np.mean(v, 0) if len(v) > 20 else T[c]) for c, v in acc.items()}
        print("round", r, {c: len(v) for c, v in acc.items()}, file=sys.stderr)
    return T

if __name__ == "__main__":
    out = sys.argv[1]; pages = [int(p) for p in sys.argv[2:]]
    os.makedirs(TDIR, exist_ok=True)
    tf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_templates.npz")
    if os.path.exists(tf):
        T = dict(np.load(tf))
    else:
        T = train(list(range(60, 232, 6)), seed_templates())
        np.savez(tf, **T)
    res = {}
    for p in pages:
        res[p], _, _ = read_page(p, T)
    json.dump(res, open(out, "w"))
