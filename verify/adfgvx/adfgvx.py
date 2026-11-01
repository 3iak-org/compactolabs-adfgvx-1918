"""check-adfgvx: independent ADFGVX primitives.

Written from the textbook description of the cipher only (6x6 Polybius square over
ADFGVX; then a keyed columnar transposition with the key given as per-column RANKS).
Nothing here was copied from, or run against, any of the repos whose claims are being
checked.

Conventions (fixed here, validated in step0_validate.py against 595 published readings):
  square   : 36 characters, row-major, rows and columns both labelled A D F G V X.
             '?' marks a cell the key's publisher left unknown.
  trans    : list of w integers; trans[i] is the read-out RANK (1..w) of the column that
             stands at position i (left to right) of the block.  Column with rank 1 is
             transmitted first.
  cipher   : string over ADFGVX plus '-' or '?' for a symbol the operator could not read.
"""
LAB = "ADFGVX"
IDX = {c: i for i, c in enumerate(LAB)}
UNK = "-?"


def col_lengths(n, w):
    """Lengths of the columns, by block position, for a message of n symbols."""
    q, r = divmod(n, w)
    return [q + 1 if i < r else q for i in range(w)]


def untranspose(c, trans):
    """Ciphertext -> interim stream (row-major block read), keeping unknown markers."""
    w = len(trans)
    n = len(c)
    L = col_lengths(n, w)
    order = sorted(range(w), key=lambda i: trans[i])
    cols = [None] * w
    p = 0
    for i in order:
        cols[i] = c[p:p + L[i]]
        p += L[i]
    out = []
    for r in range((n + w - 1) // w):
        for i in range(w):
            if r < L[i]:
                out.append(cols[i][r])
    return "".join(out)


def transpose(s, trans):
    """Interim stream -> ciphertext (inverse of untranspose)."""
    w = len(trans)
    n = len(s)
    L = col_lengths(n, w)
    cols = [[] for _ in range(w)]
    for k, ch in enumerate(s):
        cols[k % w].append(ch)
    order = sorted(range(w), key=lambda i: trans[i])
    return "".join("".join(cols[i]) for i in order)


def pair_cands(a, b, square):
    """Set of letters a (possibly partly unknown) symbol pair can denote."""
    ra = [IDX[a]] if a in IDX else list(range(6))
    cb = [IDX[b]] if b in IDX else list(range(6))
    return {square[6 * r + c] for r in ra for c in cb}


def substitute(interim, square):
    """Interim -> text; a pair with an unknown symbol, or an unknown cell, gives '?'."""
    out = []
    for k in range(0, len(interim) - 1, 2):
        a, b = interim[k], interim[k + 1]
        if a in IDX and b in IDX:
            out.append(square[6 * IDX[a] + IDX[b]])
        else:
            out.append("?")
    return "".join(out)


def decrypt(c, trans, square):
    return substitute(untranspose(c, trans), square)


def encrypt(p, trans, square):
    inv = {}
    for k, ch in enumerate(square):
        if ch != "?":
            inv.setdefault(ch, LAB[k // 6] + LAB[k % 6])
    interim = "".join(inv[ch] for ch in p)
    return transpose(interim, trans)


def transpose_gen(items, trans):
    """transpose() for a list of arbitrary items (used for wildcard patterns)."""
    w = len(trans)
    n = len(items)
    cols = [[] for _ in range(w)]
    for k, it in enumerate(items):
        cols[k % w].append(it)
    order = sorted(range(w), key=lambda i: trans[i])
    out = []
    for i in order:
        out += cols[i]
    return out
