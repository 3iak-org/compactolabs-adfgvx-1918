"""My German period scorer (check-adfgvx design; nothing shared with the claimants).

Alphabet: 26 letters (Ae->AE, Oe->OE, Ue->UE, sz->SS) + one digit class (index 26).
Model: interpolated character quadgram, log10 p(c_i | c_{i-3..i-1}), scored over each
unbroken segment; the first three letters of a segment are not scored.

Two models, named in every result:
  LIT : Project Gutenberg German prose only (list in GUTENBERG below, ids recorded),
        digit class gets a flat floor.  Honest weakness: telegraphic style, X as stop and
        digits are all rare in it, so genuine 1918 text scores low.
  TEL : LIT counts (weight 1) + the published plaintexts of the OTHER key periods in
        creilly's records.json (weight W_TEL each char), i.e. the key period under test is
        held out, so the claimed reading is never in its own training data.
"""
import os, re, glob, json, unicodedata
import numpy as np
import data as D

GUTENBERG = [2229, 2230, 22367, 5323, 34811, 7205, 2407, 2403, 19460, 7500, 2404, 6343, 22465, 9950]
V = 27
CORPUS_DIR = os.path.join(D.TMP, "corpus")
W_TEL = 30.0

def norm_text(t):
    t = t.upper().replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE").replace("ß", "SS").replace("ẞ", "SS")
    out = []
    for ch in t:
        if "A" <= ch <= "Z": out.append(ord(ch) - 65)
        elif ch.isdigit(): out.append(26)
        # everything else (space, punctuation) is simply dropped: running letters
    return out

def cls_of_plain(ch):
    if "A" <= ch <= "Z": return ord(ch) - 65
    if ch.isdigit(): return 26
    return -1   # unknown / break

def gutenberg_ids():
    return [i for i in GUTENBERG if os.path.exists(os.path.join(CORPUS_DIR, "pg%d.txt" % i))]

def load_lit_stream():
    segs = []
    for i in gutenberg_ids():
        t = open(os.path.join(CORPUS_DIR, "pg%d.txt" % i), encoding="utf-8", errors="ignore").read()
        a = t.find("*** START"); b = t.find("*** END")
        if a >= 0: t = t[t.find("\n", a):]
        if b >= 0: t = t[: t.find("*** END")]
        # digits in the prose (years, page numbers) are dropped: digit statistics come from telegrams only
        segs.append(np.array([c for c in norm_text(t) if c != 26], dtype=np.int8))
    return segs

def build(held_out_periods=()):
    """Return logp4 array [27,27,27,27] float64 (log10)."""
    C4 = np.zeros((V,) * 4); 
    lit = load_lit_stream()
    for s in lit:
        s = s.astype(np.int64)
        idx = ((s[:-3] * V + s[1:-2]) * V + s[2:-1]) * V + s[3:]
        C4 += np.bincount(idx, minlength=V ** 4).reshape((V,) * 4)
    K = D.keys()
    tel = []
    for r in D.records():
        if r["plaintext"] and r["key"] and r["key"] not in held_out_periods and r["key"] not in ("ours_nov07_18col",):
            # split at unknown chars
            seg = []
            for ch in r["plaintext"]:
                c = cls_of_plain(ch)
                if c < 0:
                    if len(seg) >= 4: tel.append(seg)
                    seg = []
                else: seg.append(c)
            if len(seg) >= 4: tel.append(seg)
    if held_out_periods is not None and tel:
        for s in tel:
            s = np.asarray(s, dtype=np.int64)
            idx = ((s[:-3] * V + s[1:-2]) * V + s[2:-1]) * V + s[3:]
            C4 += W_TEL * np.bincount(idx, minlength=V ** 4).reshape((V,) * 4)
    return _smooth(C4)

def build_lit():
    C4 = np.zeros((V,) * 4)
    for s in load_lit_stream():
        s = s.astype(np.int64)
        idx = ((s[:-3] * V + s[1:-2]) * V + s[2:-1]) * V + s[3:]
        C4 += np.bincount(idx, minlength=V ** 4).reshape((V,) * 4)
    return _smooth(C4)

def _smooth(C4):
    C3 = C4.sum(axis=0)          # counts of (b,c,d)
    C2 = C3.sum(axis=0)          # (c,d)
    C1 = C2.sum(axis=0)          # d
    p1 = (C1 + 1.0) / (C1.sum() + V)
    def cond(Cn):
        tot = Cn.sum(axis=-1, keepdims=True)
        return np.where(tot > 0, Cn / np.maximum(tot, 1), 0.0), tot
    p2, t2 = cond(C2)
    p3, t3 = cond(C3)
    p4, t4 = cond(C4)
    # interpolate with confidence: lambda = n/(n+k)
    k = 8.0
    P2 = (t2 / (t2 + k)) * p2 + (k / (t2 + k)) * p1
    P3 = (t3 / (t3 + k)) * p3 + (k / (t3 + k)) * P2[None, :, :] if False else None
    # broadcast properly
    P2b = P2[None, :, :]                              # [b?]: index (c,d) -> shape (1,V,V) for (b,c,d)
    P3 = (t3 / (t3 + k)) * p3 + (k / (t3 + k)) * P2b
    P3b = P3[None, :, :, :]
    P4 = (t4 / (t4 + k)) * p4 + (k / (t4 + k)) * P3b
    # digit class: fixed prior mass 0.02 mixed in everywhere (prose has no digits; telegrams ~2%),
    # letters share the rest by unigram frequency.  10% of the mass is this context-free prior.
    pl = np.append(p1[:26] / p1[:26].sum() * 0.98, 0.02)
    P4 = 0.9 * P4 + 0.1 * pl
    return np.log10(P4)

def score_classes(seg_list, logp4):
    """Sum of log10 p over every full quadgram inside each segment.  Returns (sum, n)."""
    tot, n = 0.0, 0
    for s in seg_list:
        for i in range(3, len(s)):
            tot += logp4[s[i - 3], s[i - 2], s[i - 1], s[i]]; n += 1
    return tot, n

def segments(text):
    """Text with unknown markers -> list of class-index segments."""
    segs, cur = [], []
    for ch in text:
        c = cls_of_plain(ch)
        if c < 0:
            if cur: segs.append(cur)
            cur = []
        else: cur.append(c)
    if cur: segs.append(cur)
    return segs

_cache = {}
def model(name, held_out=()):
    key = (name, tuple(sorted(held_out)))
    if key not in _cache:
        path = os.path.join(D.TMP, "model_%s_%s.npy" % (name, "_".join(sorted(held_out)) or "none"))
        if os.path.exists(path): _cache[key] = np.load(path)
        else:
            _cache[key] = build_lit() if name == "LIT" else build(held_out)
            np.save(path, _cache[key])
    return _cache[key]

if __name__ == "__main__":
    print("gutenberg ids present:", gutenberg_ids())
    m = model("LIT")
    print("LIT built", m.shape)
    # sanity: German vs shuffled
    import random
    txt = "ANORDNUNGENVOMZWEITENNOVEMBERBEZIEHENLASSENSOWEITNOCHNICHTGESCHEHEN"
    s = segments(txt); print("per-quadgram German:", score_classes(s, m)[0] / score_classes(s, m)[1])
    t = list(txt); random.shuffle(t); s = segments("".join(t)); print("shuffled:", score_classes(s, m)[0] / score_classes(s, m)[1])
