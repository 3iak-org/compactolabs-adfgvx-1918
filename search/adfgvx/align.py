"""Minimal edit alignment between a reference string T and an observed string O.

Written by comp-adfgvx 2026-10-31. Pure Python, O(len(T)*len(O)).

Moves
  diag  T[i] against O[j]   cost/type from `pair(t, o)`
  del   T[i] absent from O  cost 1, type DEL
  ins   O[j] absent from T  cost 1, type INS

`align` returns the minimum cost, one canonical optimal alignment (diag preferred, then del,
then ins, tracing back from the end), the number of distinct optimal alignments, and for each
edit type the [min, max] count over ALL optimal alignments, so a reader can see how much of a
type breakdown is forced and how much is tie-breaking.
"""

DEL, INS = "del", "ins"


def census_pair(t, o):
    """Reference = re-encryption of the plaintext ('*' = unknown), observed = log symbols."""
    if t == "*":
        return 0, "wild"
    if o == "-":
        return 0, "lost"      # E4: the log marks the slot as unreadable
    if t == o:
        return 0, "match"
    return 1, "sub"           # E5: wrong symbol


def plain_pair(t, o):
    return (0, "match") if t == o else (1, "sub")


EDIT_TYPES = ("sub", DEL, INS, "lost", "wild")


def align(T, O, pair=census_pair):
    n, m = len(T), len(O)
    INF = 10 ** 9
    # forward costs
    F = [[INF] * (m + 1) for _ in range(n + 1)]
    F[0][0] = 0
    for i in range(n + 1):
        Fi = F[i]
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            best = INF
            if i and j:
                c = F[i - 1][j - 1] + pair(T[i - 1], O[j - 1])[0]
                best = c
            if i:
                c = F[i - 1][j] + 1
                if c < best:
                    best = c
            if j:
                c = Fi[j - 1] + 1
                if c < best:
                    best = c
            Fi[j] = best
    opt = F[n][m]
    # backward costs
    B = [[INF] * (m + 1) for _ in range(n + 1)]
    B[n][m] = 0
    for i in range(n, -1, -1):
        Bi = B[i]
        for j in range(m, -1, -1):
            if i == n and j == m:
                continue
            best = INF
            if i < n and j < m:
                best = B[i + 1][j + 1] + pair(T[i], O[j])[0]
            if i < n:
                c = B[i + 1][j] + 1
                if c < best:
                    best = c
            if j < m:
                c = Bi[j + 1] + 1
                if c < best:
                    best = c
            Bi[j] = best

    def moves(i, j):
        """Optimal moves out of (i, j): (ni, nj, type)."""
        out = []
        if i < n and j < m:
            c, ty = pair(T[i], O[j])
            if F[i][j] + c + B[i + 1][j + 1] == opt:
                out.append((i + 1, j + 1, ty))
        if i < n and F[i][j] + 1 + B[i + 1][j] == opt:
            out.append((i + 1, j, DEL))
        if j < m and F[i][j] + 1 + B[i][j + 1] == opt:
            out.append((i, j + 1, INS))
        return out

    # DP over the DAG of optimal moves, in reverse topological order (i, j descending)
    K = len(EDIT_TYPES)
    idx = {t: k for k, t in enumerate(EDIT_TYPES)}
    cnt = {}
    lo = {}
    hi = {}
    cnt[(n, m)] = 1
    lo[(n, m)] = [0] * K
    hi[(n, m)] = [0] * K
    for i in range(n, -1, -1):
        for j in range(m, -1, -1):
            if (i, j) == (n, m) or F[i][j] + B[i][j] != opt:
                continue
            c = 0
            l = [INF] * K
            h = [-1] * K
            for ni, nj, ty in moves(i, j):
                if (ni, nj) not in cnt:
                    continue
                c += cnt[(ni, nj)]
                ln, hn = lo[(ni, nj)], hi[(ni, nj)]
                for k in range(K):
                    add = 1 if idx.get(ty) == k else 0
                    if ln[k] + add < l[k]:
                        l[k] = ln[k] + add
                    if hn[k] + add > h[k]:
                        h[k] = hn[k] + add
            if c:
                cnt[(i, j)] = c
                lo[(i, j)] = l
                hi[(i, j)] = h
    # canonical traceback (forward, preferring diag, del, ins)
    ops = []
    i = j = 0
    while (i, j) != (n, m):
        mv = moves(i, j)
        ni, nj, ty = mv[0]
        ops.append((ty, i, j))   # i = position in T, j = position in O
        i, j = ni, nj
    ranges = {t: (lo[(0, 0)][k], hi[(0, 0)][k]) for t, k in idx.items()}
    return {"cost": opt, "ops": ops, "n_optimal": cnt[(0, 0)], "ranges": ranges}


def events(ops):
    """Collapse the canonical alignment into events: maximal runs of consecutive DEL (or INS)
    moves are one event each; every 'sub' and every 'lost' is its own event.
    Returns a list of (type, length, T-position, O-position)."""
    ev = []
    for ty, i, j in ops:
        if ty in (DEL, INS):
            if ev and ev[-1][0] == ty and ev[-1][4]:
                t, L, i0, j0, _ = ev[-1]
                ev[-1] = (t, L + 1, i0, j0, True)
                continue
            ev.append((ty, 1, i, j, True))
        elif ty in ("sub", "lost"):
            ev.append((ty, 1, i, j, False))
        else:
            if ev:
                ev[-1] = ev[-1][:4] + (False,)
    return [e[:4] for e in ev]
