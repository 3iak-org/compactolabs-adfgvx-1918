"""ADFGVX encrypt/decrypt engine (comp-adfgvx, written 2026-10-31 from the cipher's definition).

Conventions
-----------
square : 36-char string, row-major, rows and columns labelled A D F G V X.
         '?' marks a cell whose content is unknown (blank in the published key table).
trans  : list of k column numbers 1..k, in left-to-right order of the columns.
         The column numbered 1 is read out first (irregular columnar: last row may be short).

Symbol alphabet of ciphertext: ADFGVX, plus
  '-'  a symbol the log marks as lost/unreadable (one slot, value unknown),
  '*'  a wildcard produced by encrypting an unknown plaintext character.
Unknown plaintext characters (encrypt input): any char not in the square, e.g. '?', '-', '#', '_'.
"""
LAB = "ADFGVX"
UNKNOWN_PT = "?"          # decrypt output: pair known, cell content unknown
LOST_PT = "-"             # decrypt output: pair contains a lost symbol


def check_key(square, trans):
    assert len(square) == 36, len(square)
    known = [c for c in square if c != "?"]
    assert len(known) == len(set(known)), "duplicate cell in square"
    assert sorted(trans) == list(range(1, len(trans) + 1)), "transposition is not a permutation"


def read_order(trans):
    """Column indices (0-based) in the order they are read out."""
    return sorted(range(len(trans)), key=lambda i: trans[i])


def col_lengths(n, k):
    q, r = divmod(n, k)
    return [q + (1 if i < r else 0) for i in range(k)]


def transpose(interim, trans):
    k = len(trans)
    return "".join(interim[i::k] for i in read_order(trans))


def untranspose(ct, trans):
    k, n = len(trans), len(ct)
    lens = col_lengths(n, k)
    cols = [None] * k
    p = 0
    for i in read_order(trans):
        cols[i] = ct[p:p + lens[i]]
        p += lens[i]
    out = []
    for row in range(lens[0]):
        for i in range(k):
            if row < lens[i]:
                out.append(cols[i][row])
    return "".join(out)


def substitute(pt, square):
    pos = {c: i for i, c in enumerate(square) if c != "?"}
    out = []
    for ch in pt:
        i = pos.get(ch)
        out.append("**" if i is None else LAB[i // 6] + LAB[i % 6])
    return "".join(out)


def unsubstitute(interim, square):
    out = []
    for j in range(0, len(interim) - 1, 2):
        a, b = interim[j], interim[j + 1]
        if a not in LAB or b not in LAB:
            out.append(LOST_PT)
        else:
            c = square[LAB.index(a) * 6 + LAB.index(b)]
            out.append(UNKNOWN_PT if c == "?" else c)
    return "".join(out)


def encrypt(pt, square, trans):
    return transpose(substitute(pt, square), trans)


def decrypt(ct, square, trans):
    """Odd length: the dangling last interim symbol is dropped (reported by caller)."""
    return unsubstitute(untranspose(ct, trans), square)


def clean(s):
    return "".join(ch for ch in s if ch not in " \n\t")
