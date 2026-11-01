"""Segmentation for the template OCR channel: page -> lines -> words -> character cells."""
import numpy as np

INK = 120          # grey level below which a pixel is ink (bleed-through is lighter)

def edge_mask(a):
    """Columns at the binding edge that are dark down most of the page."""
    b = a < INK
    frac = b.mean(0)
    m = np.zeros(a.shape[1], bool)
    m[:200] = frac[:200] > 0.15
    # extend mask to the right edge of the dark strip, plus margin
    if m.any():
        last = np.nonzero(m)[0].max()
        m[:last + 25] = True
    return m

def runs(on, mingap=1):
    out = []; i = 0; n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]: j += 1
            out.append([i, j]); i = j
        else:
            i += 1
    merged = []
    for r in out:
        if merged and r[0] - merged[-1][1] < mingap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return merged

def lines(a):
    b = a < INK
    b[:, edge_mask(a)] = False
    prof = b.sum(1)
    rs = runs(prof > 12, mingap=3)
    out = []
    for y0, y1 in rs:
        if y1 - y0 < 20:
            continue
        # k touching lines (single spacing ~44 px pitch): split at the weakest rows
        k = max(1, int(round((y1 - y0 + 6) / 44.0)))
        cuts = [y0]
        for j in range(1, k):
            c = y0 + int(round(j * (y1 - y0) / k))
            lo, hi = max(cuts[-1] + 18, c - 10), min(y1 - 18, c + 10)
            if hi > lo:
                c = lo + int(np.argmin(prof[lo:hi]))
            cuts.append(c)
        cuts.append(y1)
        out += [(cuts[j], cuts[j + 1]) for j in range(k)]
    return out, b

def word_yc(b, y0, y1, w):
    """Vertical centre of a word's ink (capitals share a height)."""
    band = b[max(0, y0 - 6):y1 + 6, w[0][0]:w[-1][1]]
    rows = np.nonzero(band.sum(1) >= 2)[0]
    if len(rows) == 0:
        return (y0 + y1) / 2
    return max(0, y0 - 6) + (rows[0] + rows[-1]) / 2

def words(b, y0, y1, gap=18):
    """Runs of ink columns in a line band, merged when the gap is < gap px."""
    band = b[max(0, y0 - 6):y1 + 6]
    col = band.sum(0)
    rs = runs(col > 0, mingap=1)
    rs = [r for r in rs if band[:, r[0]:r[1]].sum() >= 25]   # drop specks
    ws = []
    for r in rs:
        if ws and r[0] - ws[-1][-1][1] < gap:
            ws[-1].append(r)
        else:
            ws.append([r])
    return ws

PITCH = 27.5       # px per character at 300 dpi, measured on p.72 (2 extra chars = 55 px)
CW = 23            # typical ink width of one capital

def cells(word, pitch=PITCH, cw=CW):
    x0, x1 = word[0][0], word[-1][1]
    W = x1 - x0
    n = max(1, int(round((W - cw) / pitch)) + 1)
    cx = (x0 + x1) / 2
    return [cx + (k - (n - 1) / 2) * pitch for k in range(n)], W - ((n - 1) * pitch + cw)

CH, CWIN = 52, 34  # glyph window height and width

def glyph(a, yc, xc):
    """Inverted grey window centred on (yc, xc), float 0..1 (ink = 1)."""
    y0, x0 = int(round(yc - CH / 2)), int(round(xc - CWIN / 2))
    win = np.zeros((CH, CWIN), np.float32)
    sub = a[max(0, y0):y0 + CH, max(0, x0):x0 + CWIN]
    win[max(0, -y0):max(0, -y0) + sub.shape[0], max(0, -x0):max(0, -x0) + sub.shape[1]] = (255 - sub.astype(np.float32)) / 255
    return win


def page_scale(a):
    """Width of a 5-letter group on this page relative to p.72 (133 px)."""
    L, b = lines(a)
    ws = []
    for y0, y1 in L:
        ws += [w[-1][1] - w[0][0] for w in words(b, y0, y1)]
    ws = np.array([w for w in ws if 95 <= w <= 175])
    if len(ws) < 20:
        return 1.0
    h = np.bincount(ws, minlength=176).astype(float)
    h = np.convolve(h, np.ones(5), "same")
    return float(np.argmax(h)) / 133.0

def rescale(a, s):
    """Resample so that this page's glyphs match p.72's size (bilinear)."""
    if abs(s - 1) < 0.015:
        return a
    H, W = a.shape
    h, w = int(H / s), int(W / s)
    ys = np.arange(h) * s; xs = np.arange(w) * s
    y0 = np.clip(ys.astype(int), 0, H - 2); x0 = np.clip(xs.astype(int), 0, W - 2)
    fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    A = a.astype(np.float32)
    out = (A[y0][:, x0] * (1 - fy) * (1 - fx) + A[y0 + 1][:, x0] * fy * (1 - fx)
           + A[y0][:, x0 + 1] * (1 - fy) * fx + A[y0 + 1][:, x0 + 1] * fy * fx)
    return out.astype(np.uint8)

