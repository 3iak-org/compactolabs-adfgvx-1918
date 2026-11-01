"""Template OCR channel for the ADFGVX log scan (second, independent reading).

Templates are bootstrapped from four lines of p.72 read by eye, then refined by
self-training on high-margin glyphs across all pages. Each group cell is classified
by normalised correlation against the templates over small shifts.
"""
import json, sys, os
import numpy as np
from crop import page_array
from ocr_seg import lines, words, cells, glyph, word_yc, page_scale, rescale, CH, CWIN

PDF = os.path.join(os.environ.get("TMPDIR", "/tmp"), "pdf", "childs.pdf")
SEED = {  # p.72, line y-start -> my reading of the groups (label excluded)
    1449: "VDGVF GDVFF GAGGF AFVDD DFFGF DFAGF VVGVF FGGFV",
    1544: "DADFF XFVVX XFGAG GDVVG FGDFV GFDAF FGVGF GXFVF",
    1635: "FGDFA GVDAD ADDFD FFGFD DFDDF GFFGA GDGDG VXXDA",
    1820: "FGGDD DFGXD DXFXF GADGF XDXXF XAAGX ADFAX DAXDV",
}
SH = 4  # shift search radius, px

def page_glyphs(page):
    """All words of all lines with their cell glyphs: list of dicts."""
    a0 = page_array(PDF, page)
    s = page_scale(a0)
    a = rescale(a0, s)
    L, b = lines(a)
    out = []
    for li, (y0, y1) in enumerate(L):
        for wi, w in enumerate(words(b, y0, y1)):
            yc = word_yc(b, y0, y1, w)
            cs, resid = cells(w)
            out.append(dict(page=page, scale=s, line=li, y=y0, x=w[0][0], x1=w[-1][1], word=wi,
                            n=len(cs), resid=float(resid), cx=cs, yc=yc))
    return out, a

def ncc_best(win_big, T):
    """max normalised correlation of template T over shifts within win_big."""
    best = -1
    th, tw = T.shape
    Tz = T - T.mean(); Tn = np.sqrt((Tz * Tz).sum()) + 1e-6
    for dy in range(0, win_big.shape[0] - th + 1):
        for dx in range(0, win_big.shape[1] - tw + 1):
            W = win_big[dy:dy + th, dx:dx + tw]
            Wz = W - W.mean()
            s = (Wz * Tz).sum() / (np.sqrt((Wz * Wz).sum()) + 1e-6) / Tn
            if s > best: best = s
    return best

def big_glyph(a, yc, xc):
    from ocr_seg import glyph as g0
    import ocr_seg
    y0, x0 = int(round(yc - CH / 2)) - SH, int(round(xc - CWIN / 2)) - SH
    H, W = CH + 2 * SH, CWIN + 2 * SH
    win = np.zeros((H, W), np.float32)
    sub = a[max(0, y0):y0 + H, max(0, x0):x0 + W]
    win[max(0, -y0):max(0, -y0) + sub.shape[0], max(0, -x0):max(0, -x0) + sub.shape[1]] = (255 - sub.astype(np.float32)) / 255
    return win

def classify_fast(bigs, T):
    """Vectorised NCC over shifts. bigs: (N,H+2S,W+2S); T: dict ch -> (H,W). Returns (N, nch) scores."""
    chars = sorted(T)
    N = len(bigs)
    S = np.full((N, len(chars)), -1.0, np.float32)
    for ci, c in enumerate(chars):
        t = T[c]; tz = t - t.mean(); tz /= np.sqrt((tz * tz).sum()) + 1e-6
        n = t.size
        for dy in range(2 * SH + 1):
            for dx in range(2 * SH + 1):
                Wd = bigs[:, dy:dy + CH, dx:dx + CWIN].reshape(N, -1)
                Wz = Wd - Wd.mean(1, keepdims=True)
                s = (Wz @ tz.ravel()) / (np.sqrt((Wz * Wz).sum(1)) + 1e-6)
                S[:, ci] = np.maximum(S[:, ci], s)
    return chars, S
