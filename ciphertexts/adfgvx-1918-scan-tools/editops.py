"""Minimal edit alignment (Levenshtein, unit costs) with traceback; '*' in b matches anything."""
def align(a, b):
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        ai = a[i - 1]; Di = D[i]; Dp = D[i - 1]
        for j in range(1, m + 1):
            c = 0 if (ai == b[j - 1] or b[j - 1] == "*") else 1
            Di[j] = min(Dp[j - 1] + c, Dp[j] + 1, Di[j - 1] + 1)
    ops = []; i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + (0 if (a[i - 1] == b[j - 1] or b[j - 1] == "*") else 1):
            ops.append(("=" if (a[i - 1] == b[j - 1] or b[j - 1] == "*") else "sub", i - 1, j - 1)); i -= 1; j -= 1
        elif i > 0 and D[i][j] == D[i - 1][j] + 1:
            ops.append(("a_only", i - 1, j)); i -= 1
        else:
            ops.append(("b_only", i, j - 1)); j -= 1
    return D[n][m], ops[::-1]
