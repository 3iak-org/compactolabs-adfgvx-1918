/* Cost-only edit distance with the census semantics of align.py:
   diag: T='*' -> 0; O='-' -> 0; equal -> 0; else 1.  del/ins cost 1.
   Build: cc -O2 -shared -fPIC -o edcost.so edcost.c   (comp-adfgvx 2026-10-31) */
#include <stdlib.h>
int edcost(const char *T, int n, const char *O, int m) {
    int *prev = malloc((m + 1) * sizeof(int)), *cur = malloc((m + 1) * sizeof(int));
    for (int j = 0; j <= m; j++) prev[j] = j;
    for (int i = 1; i <= n; i++) {
        cur[0] = i;
        char t = T[i - 1];
        for (int j = 1; j <= m; j++) {
            char o = O[j - 1];
            int c = prev[j - 1] + ((t == '*' || o == '-' || t == o) ? 0 : 1);
            int d = prev[j] + 1, e = cur[j - 1] + 1;
            if (d < c) c = d;
            if (e < c) c = e;
            cur[j] = c;
        }
        int *tmp = prev; prev = cur; cur = tmp;
    }
    int r = prev[m];
    free(prev); free(cur);
    return r;
}

/* Fitting alignment for the duplicate screen: A (the shorter) aligned in full against any
   substring of B (free leading and trailing gaps in B). lostfree=1: '-' on either side matches
   anything; lostfree=0 (the screen's default, via fitcost): '-' matches only '-', because free
   wildcards let heavily gapped texts fit everything. Unit substitution/indel costs.
   Returns the cost; *start and *end receive the matched span [start, end) in B. */
int fitcost_mode(const char *A, int m, const char *B, int n, int *start, int *end, int lostfree) {
    int *prev = malloc((n + 1) * sizeof(int)), *cur = malloc((n + 1) * sizeof(int));
    int *ps = malloc((n + 1) * sizeof(int)), *cs = malloc((n + 1) * sizeof(int));
    for (int j = 0; j <= n; j++) { prev[j] = 0; ps[j] = j; }
    for (int i = 1; i <= m; i++) {
        cur[0] = i; cs[0] = 0;
        char a = A[i - 1];
        for (int j = 1; j <= n; j++) {
            char b = B[j - 1];
            int c = prev[j - 1] + ((a == b || (lostfree && (a == '-' || b == '-'))) ? 0 : 1), s = ps[j - 1];
            int d = prev[j] + 1;
            if (d < c) { c = d; s = ps[j]; }
            int e = cur[j - 1] + 1;
            if (e < c) { c = e; s = cs[j - 1]; }
            cur[j] = c; cs[j] = s;
        }
        int *t = prev; prev = cur; cur = t;
        t = ps; ps = cs; cs = t;
    }
    int best = prev[0], bj = 0;
    for (int j = 1; j <= n; j++) if (prev[j] < best) { best = prev[j]; bj = j; }
    *start = ps[bj]; *end = bj;
    free(prev); free(cur); free(ps); free(cs);
    return best;
}

/* the duplicate screen's default: '-' is an ordinary symbol (matches only '-') */
int fitcost(const char *A, int m, const char *B, int n, int *start, int *end) {
    return fitcost_mode(A, m, B, n, start, end, 0);
}
