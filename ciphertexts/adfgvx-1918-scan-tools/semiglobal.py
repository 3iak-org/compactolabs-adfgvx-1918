"""Semi-global alignment: the whole of `t` against the best-matching substring of `s`.
Returns (edits, start, end) with s[start:end] the matched span."""
def semiglobal(t, s):
    n, m = len(t), len(s)
    prev = [0] * (m + 1)            # free start anywhere in s
    start = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m; cst = [0] * (m + 1)
        ti = t[i - 1]
        for j in range(1, m + 1):
            a = prev[j - 1] + (0 if ti == s[j - 1] else 1); sa = start[j - 1]
            b = prev[j] + 1; sb = start[j]
            c = cur[j - 1] + 1; sc = cst[j - 1]
            if a <= b and a <= c: cur[j], cst[j] = a, sa
            elif b <= c: cur[j], cst[j] = b, sb
            else: cur[j], cst[j] = c, sc
        cst[0] = 0
        prev, start = cur, cst
    j = min(range(m + 1), key=lambda j: prev[j])
    return prev[j], start[j], j
