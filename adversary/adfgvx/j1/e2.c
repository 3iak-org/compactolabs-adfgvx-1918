/* e2.c - adv-adfgvx, 2026-11-01. Same-freedom attack on strand J1 (READ-KNOWN-KEY).
   Written from the prereg's definition of the J1 statistic, not from comp's search code:
     S = max over edit sets of <= 2 edits {del1@p, ins1@p, del5@5j, ins5@5j} of the mean, over
     every plaintext trigram position i >= 2, of ln P(c_i | c_{i-2} c_{i-1}), a position with an
     unknown letter (lost symbol or blank cell) charged ln(1/36).
   One deliberate match to jattack's behaviour (checked by reproducing comp's S on all 64
   (target, candidate key) pairs, 0 mismatches): edit positions index the ORIGINAL string and are
   applied in ascending position order (ties in the order del1, ins1, del5, ins5); a second edit
   whose position lies strictly inside a deletion's span, or equals the deletion's position, is
   silently dropped (so e.g. ins1@p after del1@p is just del1@p, while del1@p,ins1@p+1 is a
   substitution of symbol p by an unknown). Matching this keeps my variant set equal to comp's,
   not a superset, so the adversary gets exactly the claim's freedom.
   Usage: e2 LMTABLE [CAP 0..3, default 2] < jobs ; job line: TAG SQUARE36 K p1..pK CIPHERTEXT ('-' = lost)
   Output: TAG best score0 edits plain                                                     */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 1400
#define PEN (-3.58351893845611)
static double LM[46656];
static const char *AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
static int sym(char c) { switch (c) { case 'A': return 0; case 'D': return 1; case 'F': return 2;
    case 'G': return 3; case 'V': return 4; case 'X': return 5; default: return 6; } }
static int sqv[36], K, rank_[64], order[64];

/* decrypt v[0..n) and score */
static double score(const signed char *v, int n, char *plainout) {
    static signed char grid[MAXN];
    int q = n / K, r = n % K, pos = 0;
    /* read-out: the column with rank 1 is read first */
    for (int t = 0; t < K; t++) {
        int c = order[t], len = q + (c < r ? 1 : 0);
        for (int row = 0; row < len; row++) grid[row * K + c] = v[pos++];
    }
    int m = n / 2; double s = 0; int p2 = -1, p1 = -1;
    for (int j = 0; j < m; j++) {
        int a = grid[2 * j], b = grid[2 * j + 1];
        int c = (a < 6 && b < 6) ? sqv[a * 6 + b] : -1;
        if (plainout) plainout[j] = c >= 0 ? AL[c] : '-';
        if (j >= 2) s += (p2 >= 0 && p1 >= 0 && c >= 0) ? LM[p2 * 1296 + p1 * 36 + c] : PEN;
        p2 = p1; p1 = c;
    }
    if (plainout) plainout[m] = 0;
    return m > 2 ? s / (m - 2) : -99.0;
}

typedef struct { int ty, p; } E;   /* 0 del1 1 ins1 2 del5 3 ins5 */
static int build(const signed char *ct, int n, E *e, int ne, signed char *out) {
    /* the same exchange sort as jattack (not stable for ties when ne = 3, so copied as such) */
    for (int a = 0; a < ne; a++) for (int b = a + 1; b < ne; b++)
        if (e[b].p < e[a].p) { E t = e[a]; e[a] = e[b]; e[b] = t; }
    int o = 0, i = 0, k = 0;
    while (i <= n) {
        while (k < ne && e[k].p == i) {
            if (e[k].ty == 1) out[o++] = 6;
            else if (e[k].ty == 3) { for (int z = 0; z < 5; z++) out[o++] = 6; }
            else if (e[k].ty == 0) i += 1; else i += 5;
            k++;
        }
        if (i < n) out[o++] = ct[i];
        i++;
    }
    return o;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    for (int i = 0; i < 46656; i++) if (fscanf(f, "%lf", &LM[i]) != 1) return 2;
    fclose(f);
    int cap = argc > 2 ? atoi(argv[2]) : 2;
    static char line[8192], tag[256], sq[64], txt[MAXN], best_plain[MAXN];
    while (fgets(line, sizeof line, stdin)) {
        char *s = strtok(line, " \t\n"); if (!s) continue;
        strcpy(tag, s); strcpy(sq, strtok(NULL, " \t\n")); K = atoi(strtok(NULL, " \t\n"));
        for (int i = 0; i < K; i++) rank_[i] = atoi(strtok(NULL, " \t\n"));
        for (int i = 0; i < K; i++) order[rank_[i] - 1] = i;
        strcpy(txt, strtok(NULL, " \t\n"));
        for (int i = 0; i < 36; i++) { const char *p = strchr(AL, sq[i]); sqv[i] = (sq[i] != '?' && p) ? (int)(p - AL) : -1; }
        int n = strlen(txt); static signed char ct[MAXN], buf[MAXN];
        for (int i = 0; i < n; i++) ct[i] = sym(txt[i]);
        static E cand[4 * MAXN]; int nc = 0;
        for (int p = 0; p < n; p++) cand[nc++] = (E){0, p};
        for (int p = 0; p <= n; p++) cand[nc++] = (E){1, p};
        for (int p = 0; p + 5 <= n; p += 5) cand[nc++] = (E){2, p};
        for (int p = 0; p <= n; p += 5) cand[nc++] = (E){3, p};
        double s0 = score(ct, n, NULL), best = s0; E be[3]; int bn = 0;
        if (cap >= 1) for (int a = 0; a < nc; a++) {
            E e[3] = {cand[a]};
            int L = build(ct, n, e, 1, buf); double v = score(buf, L, NULL);
            if (v > best) { best = v; bn = 1; be[0] = cand[a]; }
            if (cap >= 2) for (int b = a + 1; b < nc; b++) {
                e[0] = cand[a]; e[1] = cand[b];
                L = build(ct, n, e, 2, buf); v = score(buf, L, NULL);
                if (v > best) { best = v; bn = 2; be[0] = cand[a]; be[1] = cand[b]; }
                if (cap >= 3) for (int c = b + 1; c < nc; c++) {
                    e[0] = cand[a]; e[1] = cand[b]; e[2] = cand[c];
                    L = build(ct, n, e, 3, buf); v = score(buf, L, NULL);
                    if (v > best) { best = v; bn = 3; be[0] = cand[a]; be[1] = cand[b]; be[2] = cand[c]; }
                }
            }
        }
        E e2[3] = {be[0], be[1], be[2]};
        int L = build(ct, n, e2, bn, buf); score(buf, L, best_plain);
        printf("%s %.6f %.6f ", tag, best, s0);
        const char *nm[4] = {"del1", "ins1", "del5", "ins5"};
        if (!bn) printf("-");
        for (int i = 0; i < bn; i++) printf("%s%s@%d", i ? "," : "", nm[be[i].ty], be[i].p);
        printf(" %s\n", best_plain); fflush(stdout);
    }
    return 0;
}
