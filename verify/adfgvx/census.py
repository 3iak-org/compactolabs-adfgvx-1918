"""Task 4: independent mutilation census.

For every solved entry (published plaintext + published key):
  1. re-encrypt the plaintext under the key -> the stream S as SENT (with wildcards where the
     plaintext has an unknown letter);
  2. align S against the transcription P (the `printed` field = Childs's log as transcribed);
  3. minimal edit script, typed by 0wwafa PAPER.md section 3's catalogue.

Alignment: Gotoh affine-gap global alignment, my own implementation, costs
   substitution 1.0 ; gap of length k costs 1.0 + 0.05*k (open + per-symbol)
   wildcard in S or unreadable symbol in P ('-','?') matches anything at cost 0.
An 'event' is one substitution or one gap run, so a 20-symbol dropout is one event.

Typing (PAPER.md section 3; the catalogue is applied literally, with my own operational rules):
  E1  deletion run in P (symbols of the sent stream absent from the log), length not 5k
  E2  insertion run in P (extra symbols in the log), length not 5k
  E3  deletion or insertion run whose length is a multiple of 5, at least 5, and which can be
      slid (cost-neutrally) to start on a 5-group boundary of the log
  E4  an unreadable symbol '-' / '?' in the log   [reported separately: costs 0 in alignment]
  E5  substitution of a known symbol
  E6  one-symbol insertion/deletion in the INTERIM stream (before transposition): tried as an
      alternative model; adopted only if it lowers the total event cost
  E7  / E8 key-level (wrong day, key not in list): not typable per message from this data;
      reported as 'no explanation within E1-E6' when the residual cost is large.
"""
import sys, json, collections
import ctypes, os
import adfgvx as A, data as D

_lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "alcost.so"))
_lib.align_cost.restype = ctypes.c_double
_lib.align_cost.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                            ctypes.c_double, ctypes.c_double, ctypes.c_double]


def fast_cost(S, P):
    sm = bytes(63 if x is None else sum(1 << A.IDX[c] for c in x) for x in S)
    pm = bytes(A.IDX[c] if c in A.IDX else 6 for c in P)
    return _lib.align_cost(sm, len(sm), pm, len(pm), GAP_OPEN, GAP_EXT, SUB)

WILD = set("-?_")
GAP_OPEN, GAP_EXT, SUB = 1.0, 0.05, 1.0


def sent_pattern(plain, trans, square):
    """List of allowed-symbol sets (frozenset or None=anything), in transmitted order."""
    cell = {}
    for k, ch in enumerate(square):
        if ch != "?":
            cell.setdefault(ch, []).append((A.LAB[k // 6], A.LAB[k % 6]))
    unk_cells = [(A.LAB[k // 6], A.LAB[k % 6]) for k, ch in enumerate(square) if ch == "?"]
    digit_cells = [(A.LAB[k // 6], A.LAB[k % 6]) for k, ch in enumerate(square) if ch.isdigit()]
    inter = []
    for ch in plain:
        if ch in WILD:
            inter += [None, None]
        elif ch == "#":
            cs = digit_cells + unk_cells
            inter += [frozenset(c[0] for c in cs), frozenset(c[1] for c in cs)]  # loose but sound
        else:
            if ch not in cell:
                inter += [None, None]   # letter not in square (unknown cell): unconstrained
            else:
                a, b = cell[ch][0]
                inter += [frozenset(a), frozenset(b)]
    return A.transpose_gen(inter, trans)


def ok(sset, sym):
    return sym in "-?" or sset is None or sym in sset


def align(S, P):
    """Gotoh. Returns (cost, ops) with ops list of ('M',i,j) match, ('X',i,j) sub, ('D',i) S[i] missing from P, ('I',j) P[j] extra."""
    n, m = len(S), len(P)
    INF = 1e9
    M = [[INF] * (m + 1) for _ in range(n + 1)]   # ends in match/sub
    Dd = [[INF] * (m + 1) for _ in range(n + 1)]  # ends in deletion (consumes S)
    Ii = [[INF] * (m + 1) for _ in range(n + 1)]  # ends in insertion (consumes P)
    M[0][0] = 0.0
    for i in range(1, n + 1):
        Dd[i][0] = GAP_OPEN + GAP_EXT * i
    for j in range(1, m + 1):
        Ii[0][j] = GAP_OPEN + GAP_EXT * j
    for i in range(1, n + 1):
        Si = S[i - 1]
        for j in range(1, m + 1):
            c = 0.0 if ok(Si, P[j - 1]) else SUB
            M[i][j] = min(M[i-1][j-1], Dd[i-1][j-1], Ii[i-1][j-1]) + c
            Dd[i][j] = min(M[i-1][j] + GAP_OPEN + GAP_EXT, Dd[i-1][j] + GAP_EXT, Ii[i-1][j] + GAP_OPEN + GAP_EXT)
            Ii[i][j] = min(M[i][j-1] + GAP_OPEN + GAP_EXT, Ii[i][j-1] + GAP_EXT, Dd[i][j-1] + GAP_OPEN + GAP_EXT)
    best = min((M[n][m], 0), (Dd[n][m], 1), (Ii[n][m], 2))
    cost, st = best
    ops = []
    i, j = n, m
    while i > 0 or j > 0:
        if st == 0:
            c = 0.0 if ok(S[i-1], P[j-1]) else SUB
            ops.append(("M" if c == 0 else "X", i - 1, j - 1))
            prev = M[i][j] - c
            i -= 1; j -= 1
            if i == 0 and j == 0: break
            st = 0 if abs(M[i][j] - prev) < 1e-9 else (1 if abs(Dd[i][j] - prev) < 1e-9 else 2)
        elif st == 1:
            ops.append(("D", i - 1, j))
            cur = Dd[i][j]; i -= 1
            if abs(M[i][j] + GAP_OPEN + GAP_EXT - cur) < 1e-9: st = 0
            elif abs(Dd[i][j] + GAP_EXT - cur) < 1e-9: st = 1
            else: st = 2
        else:
            ops.append(("I", i, j - 1))
            cur = Ii[i][j]; j -= 1
            if abs(M[i][j] + GAP_OPEN + GAP_EXT - cur) < 1e-9: st = 0
            elif abs(Ii[i][j] + GAP_EXT - cur) < 1e-9: st = 2
            else: st = 1
    ops.reverse()
    return cost, ops


def events(ops, S, P):
    """Group ops into events; slide gaps to test E3 boundary alignment."""
    ev = []
    k = 0
    while k < len(ops):
        t = ops[k][0]
        if t in "MX":
            if t == "X": ev.append(("sub", 1, ops[k][2]))
            k += 1; continue
        e = k
        while e < len(ops) and ops[e][0] == t: e += 1
        run = ops[k:e]
        ev.append((t, len(run), k, e))
        k = e
    return ev


def slidable_to_boundary(ops, k, e, S, P, kind):
    """True if the gap run ops[k:e] can be moved cost-neutrally to start at a P index % 5 == 0."""
    L = e - k
    # P-index at which the gap starts
    if kind == "I":
        start = ops[k][2]
    else:
        start = ops[k][2]   # P index where S symbols are skipped = the next P symbol index
    # try shifting by d in range(-L..L): neutral if every symbol swapped across is compatible
    for d in range(-L, L + 1):
        if (start + d) % 5 != 0: continue
        if neutral_shift(ops, k, e, d, S, P, kind): return True
    return False


def neutral_shift(ops, k, e, d, S, P, kind):
    """Shift gap by d positions; allowed only across pure-match ops (no other edits in the way)."""
    L = e - k
    if d == 0: return True
    if d > 0:
        seg = ops[e:e + d]
        if len(seg) < d or any(o[0] != "M" for o in seg): return False
        for o in seg:
            si, pj = o[1], o[2]
            # this matched pair would now be aligned against the symbol L earlier in the gap
            if kind == "D":
                # S[si] is currently matched with P[pj]; after shift, gap S positions move right.
                # S symbol that re-enters = ops[k + idx][1]
                pass
        # compatibility test via direct re-scoring
        return rescored_same(ops, k, e, d, S, P, kind)
    else:
        seg = ops[k + d:k] if k + d >= 0 else None
        if seg is None or len(seg) < -d or any(o[0] != "M" for o in seg): return False
        return rescored_same(ops, k, e, d, S, P, kind)


def rescored_same(ops, k, e, d, S, P, kind):
    L = e - k
    new = list(ops)
    if kind == "I":
        gp = [o[2] for o in ops[k:e]]       # P indices that are extra
        base = ops[k][2]
        new_start = base + d
        if new_start < 0 or new_start + L > len(P): return False
        # S indices aligned across the boundary: P indices outside the new gap map to S in order
        # compute S index of P index p: s(p) = p if p<base else p-L (before shift: S idx)
        old = {o[2]: o[1] for o in ops if o[0] in "MX"}
        sj = sorted(old.items())
        # build mapping with new gap
        pidx = [p for p in range(len(P)) if not (new_start <= p < new_start + L)]
        sidx = [o[1] for o in ops if o[0] in "MX"]
        sidx.sort()
        if len(pidx) != len(sidx): return False
        cost = sum(0 if ok(S[s], P[p]) else 1 for s, p in zip(sidx, pidx))
        oldcost = sum(0 if o[0] == "M" else 1 for o in ops if o[0] in "MX")
        return cost <= oldcost
    else:
        base = ops[k][1]       # first missing S index
        new_start = base + d
        if new_start < 0 or new_start + L > len(S): return False
        sidx = [i for i in range(len(S)) if not (new_start <= i < new_start + L)]
        pidx = sorted(o[2] for o in ops if o[0] in "MX")
        if len(pidx) != len(sidx): return False
        cost = sum(0 if ok(S[s], P[p]) else 1 for s, p in zip(sidx, pidx))
        oldcost = sum(0 if o[0] == "M" else 1 for o in ops if o[0] in "MX")
        return cost <= oldcost


def interim_variants(inter, trans):
    """Yield (label, stream) with exactly one interim-stream deletion or insertion (E6 model)."""
    n = len(inter)
    for q in range(n):
        yield ("del", q), A.transpose_gen(inter[:q] + inter[q + 1:], trans)
    for q in range(n + 1):
        yield ("ins", q), A.transpose_gen(inter[:q] + [None] + inter[q:], trans)


def classify(r, K, field="printed"):
    k = K[r["key"]]
    trans, sq = k["transposition"], k["square"]
    inter = interim_pattern(r["plaintext"], sq)
    S = A.transpose_gen(inter, trans)
    P = r[field].replace(" ", "")
    cost, ops = align(S, P)
    out = {"id": r["id"], "key": r["key"], "n_sent": len(S), "n_log": len(P),
           "cost": cost, "model": "cipher-space"}
    best = (cost, ops, S, "cipher")
    if cost >= 1.5:   # only worth trying E6 when something is wrong
        for lab, S2 in interim_variants(inter, trans):
            c2 = fast_cost(S2, P)
            if c2 + 1.0 < best[0] - 1e-9:   # interim edit itself is one event
                best = (c2 + 1.0, None, S2, ("E6",) + lab)
    cost, ops, S, mod = best
    if ops is None:
        _, ops = align(S, P)
    out["cost"] = cost
    out["model"] = "cipher-space" if mod == "cipher" else "E6:%s@%d" % (mod[1], mod[2])
    evs = events(ops, S, P)
    out["events"] = []
    for e in evs:
        if e[0] == "sub":
            out["events"].append(("E5", 1))
        else:
            t, L, k0, e0 = e
            if L >= 5 and L % 5 == 0 and slidable_to_boundary(ops, k0, e0, S, P, t):
                out["events"].append(("E3", L))
            else:
                out["events"].append(("E1" if t == "D" else "E2", L))
    if mod != "cipher":
        out["events"].append(("E6", 1))
    out["E4"] = sum(1 for c in P if c in "-?")
    out["nE5"] = sum(1 for e in out["events"] if e[0] == "E5")
    out["wild_S"] = sum(1 for x in S if x is None)
    return out


def interim_pattern(plain, square):
    cell = {}
    for kk, ch in enumerate(square):
        if ch != "?":
            cell.setdefault(ch, (A.LAB[kk // 6], A.LAB[kk % 6]))
    digit_cells = [(A.LAB[kk // 6], A.LAB[kk % 6]) for kk, ch in enumerate(square) if ch.isdigit() or ch == "?"]
    inter = []
    for ch in plain:
        if ch in WILD or (ch != "#" and ch not in cell):
            inter += [None, None]
        elif ch == "#":
            inter += [frozenset(c[0] for c in digit_cells), frozenset(c[1] for c in digit_cells)]
        else:
            a, b = cell[ch]
            inter += [frozenset(a), frozenset(b)]
    return inter


if __name__ == "__main__":
    R = D.records(); K = D.keys()
    field = sys.argv[1] if len(sys.argv) > 1 else "printed"
    sol = [r for r in R if r["plaintext"] and r["key"]]
    res = []
    for r in sol:
        res.append(classify(r, K, field))
    json.dump(res, open("census_%s.json" % field, "w"))
    print("done", len(res))
