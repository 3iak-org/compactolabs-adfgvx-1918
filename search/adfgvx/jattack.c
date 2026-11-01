/* jattack.c: ADFGVX attacks for the power test (comp-adfgvx, 2026-11-01).
   Written from the cipher's definition; no other solver's code was read.

   cc -O2 -o jattack jattack.c -lm
   ./jattack LMTABLE < job.txt

   Job (one directive per line):
     MODE 1|2|3        1: unknown square + unknown transposition, joint over all MSGs
                       2: known SQUARE, unknown transposition, joint
                       3: known SQUARE + TRANS, search edit sets of size <= CAP per MSG
     WIDTHS k1 k2 ...  candidate widths (modes 1, 2)
     SQUARE s36        36 cells row-major ADFGVX x ADFGVX, '?' = blank cell (modes 2, 3)
     TRANS k c1..ck    column numbers left to right, column 1 read first (mode 3)
     CAP m             (mode 3) 0..3
     RESTARTS r        hill-climb restarts per width (IC phase, mode 1; LM phase, mode 2)
     TOPW n            (mode 1) widths carried from the IC phase to the substitution phase
     FREQ s36          (mode 1) plaintext symbols by descending training frequency
     SEED s
     MSG ciphertext    ADFGVX letters, '-' = lost symbol
   Output: key=value lines. 'score' is the mean natural-log trigram probability per scored
   trigram of the decryption (higher is better).

   Method (stated, so the prereg can name it):
   mode 1  phase A: for each width, RESTARTS random column orders, each annealed (SAITERS
           iterations, linear cooling from SAT0; swap / reverse / block-move moves on the read
           order and swap / rotate moves on physical columns and column-pair slots) first on
           the index of coincidence of the interim PAIRS pooled over all messages, then on
           pair IC + LAMB x IC of adjacent cell bigrams (substitution-free; it sees the order of
           column pairs), each anneal ending in a greedy climb. The NC=4 best distinct orders
           per width are kept. With SCREENW n, a cheaper pass (SCREENR restarts x SCREENI
           iterations) over every width comes first, and only the n widths with the highest
           statistic get the full budget.
           phase B: for the TOPW widths with the highest IC, solve the 36-cell substitution
           by hill climbing (swaps) on the trigram score from a frequency-rank start plus
           random restarts; then alternate (transposition hill climb on the trigram score
           with the substitution fixed, substitution re-solve) up to 3 times.
   mode 2  KNOWN square: the order is annealed directly on the trigram score of the decryption
           (screen over every width, then the full budget on the SCREENW best; SAT0LM).
   mode 3  every set of <= CAP edits from {delete 1 at p, insert 1 unknown at p,
           delete a 5-group at 5j, insert 5 unknowns at 5j}, decrypt, score; best kept. The mode-3
           score charges ln(1/36) for every trigram position containing an unknown letter.
*/
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXM 64
#define MAXN 1200
#define MAXK 32
static double LM[46656];
static int nmsg = 0, mlen[MAXM];
static signed char msg[MAXM][MAXN];   /* 0..5 symbols, 6 = lost */
static int widths[16], nw = 0, mode = 1, cap = 0, restarts = 20, topw = 3;
static int sq[36];                    /* cell -> plaintext 0..35, -1 blank */
static int haveSq = 0, tk = 0, tperm[MAXK];
static int freqorder[36];
static unsigned long long rs = 88172645463325252ULL;
static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }
static const char *LAB = "ADFGVX";
static const char *ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

static int symidx(char c) { const char *p = strchr(LAB, c); return p ? (int)(p - LAB) : 6; }
static int alidx(char c) { const char *p = strchr(ALPH, c); return (p && c) ? (int)(p - ALPH) : -1; }

/* interim of one message under read order ord[0..k-1] (ord[t] = column read t-th) */
static void untrans(const signed char *ct, int n, const int *ord, int k, signed char *out) {
    int q = n / k, r = n % k, p = 0;
    for (int t = 0; t < k; t++) {
        int c = ord[t], L = q + (c < r);
        for (int row = 0; row < L; row++) out[row * k + c] = ct[p++];
    }
}

static signed char work[MAXM][MAXN];
static int cells[MAXM][MAXN / 2 + 1], ncell[MAXM];

static void make_cells(const int *ord, int k) {
    for (int m = 0; m < nmsg; m++) {
        untrans(msg[m], mlen[m], ord, k, work[m]);
        int h = mlen[m] / 2;
        for (int j = 0; j < h; j++) {
            int a = work[m][2 * j], b = work[m][2 * j + 1];
            cells[m][j] = (a < 6 && b < 6) ? a * 6 + b : -1;
        }
        ncell[m] = h;
    }
}

static double pair_ic(const int *ord, int k) {
    long cnt[36] = {0}, T = 0;
    double s = 0;
    make_cells(ord, k);
    for (int m = 0; m < nmsg; m++)
        for (int j = 0; j < ncell[m]; j++) {
            int c = cells[m][j];
            if (c >= 0) { s += 2.0 * cnt[c]; cnt[c]++; T++; }   /* sum n(n-1) incrementally */
        }
    if (T < 2) return 0;
    return s / ((double)T * (T - 1));
}

/* pair IC plus LAMB x IC of adjacent CELL bigrams (substitution-free; sees the order of
   column pairs, which the pair IC alone cannot for an even width) */
static double lamb = 5.0;
static double pair_ic2(const int *ord, int k) {
    double a = pair_ic(ord, k);   /* also fills cells[] */
    static long bc[1296];
    static int touched[MAXM * MAXN / 2];
    int nt = 0;
    long T = 0;
    double s = 0;
    for (int m = 0; m < nmsg; m++)
        for (int j = 0; j + 1 < ncell[m]; j++)
            if (cells[m][j] >= 0 && cells[m][j + 1] >= 0) {
                int x = cells[m][j] * 36 + cells[m][j + 1];
                if (!bc[x]) touched[nt++] = x;
                s += 2.0 * bc[x]; bc[x]++; T++;
            }
    for (int i = 0; i < nt; i++) bc[touched[i]] = 0;
    if (T < 2) return a;
    return a + lamb * s / ((double)T * (T - 1));
}

/* trigram score of current cells under map (cell -> plaintext, -1 unknown) */
static double lm_score(const int *map, long *ntri) {
    double s = 0; long n = 0;
    for (int m = 0; m < nmsg; m++) {
        int a = -1, b = -1;
        for (int j = 0; j < ncell[m]; j++) {
            int c = cells[m][j] >= 0 ? map[cells[m][j]] : -1;
            if (a >= 0 && b >= 0 && c >= 0) { s += LM[a * 1296 + b * 36 + c]; n++; }
            a = b; b = c;
        }
    }
    if (ntri) *ntri = n;
    return n ? s / n : -99.0;
}

/* DECISION statistic (all modes): mean over EVERY trigram position of every message; a
   position whose trigram contains an unknown letter is charged ln(1/36). The search objective
   (lm_score) skips such positions; as a decision statistic that lets heavily gapped or shuffled
   clusters score above real German (found 2026-11-01), so it is never used to decide. */
static double lm_pscore(const int *map) {
    double s = 0; long n = 0;
    for (int m = 0; m < nmsg; m++) {
        int a = -1, b = -1;
        for (int j = 0; j < ncell[m]; j++) {
            int c = cells[m][j] >= 0 ? map[cells[m][j]] : -1;
            if (j >= 2) { s += (a >= 0 && b >= 0 && c >= 0) ? LM[a * 1296 + b * 36 + c] : -3.58351893845611; n++; }
            a = b; b = c;
        }
    }
    return n ? s / n : -99.0;
}

static void random_order(int *ord, int k) {
    for (int i = 0; i < k; i++) ord[i] = i;
    for (int i = k - 1; i > 0; i--) { int j = rnd() % (i + 1); int t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
}

/* generic hill climb on a column order; f evaluates an order */
typedef double (*ordfun)(const int *, int, const int *);
static double eval_ic(const int *ord, int k, const int *map) { (void)map; return pair_ic(ord, k); }
static double eval_ic2(const int *ord, int k, const int *map) { (void)map; return pair_ic2(ord, k); }
static double eval_lm(const int *ord, int k, const int *map) { make_cells(ord, k); return lm_score(map, NULL); }

static int climb_blocks = 1;
static double climb(int *ord, int k, ordfun f, const int *map) {
    double best = f(ord, k, map);
    int tmp[MAXK], improved = 1;
    while (improved) {
        improved = 0;
        /* swaps */
        for (int i = 0; i < k; i++) for (int j = i + 1; j < k; j++) {
            int t = ord[i]; ord[i] = ord[j]; ord[j] = t;
            double v = f(ord, k, map);
            if (v > best + 1e-12) { best = v; improved = 1; }
            else { t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
        }
        /* move one element from i to j */
        for (int i = 0; i < k; i++) for (int j = 0; j < k; j++) {
            if (i == j) continue;
            memcpy(tmp, ord, sizeof(int) * k);
            int x = ord[i];
            if (i < j) { memmove(ord + i, ord + i + 1, sizeof(int) * (j - i)); ord[j] = x; }
            else { memmove(ord + j + 1, ord + j, sizeof(int) * (i - j)); ord[j] = x; }
            double v = f(ord, k, map);
            if (v > best + 1e-12) { best = v; improved = 1; }
            else memcpy(ord, tmp, sizeof(int) * k);
        }
        /* move a block ord[i..j] (length 2..k-1) so that it starts at position p */
        if (climb_blocks) for (int i = 0; i < k; i++) for (int j = i + 1; j < k && j - i + 1 < k; j++) {
            int len = j - i + 1;
            for (int p = 0; p + len <= k; p++) {
                if (p == i) continue;
                memcpy(tmp, ord, sizeof(int) * k);
                int rest[MAXK], nr = 0, blk[MAXK];
                for (int a = 0; a < k; a++) { if (a >= i && a <= j) blk[a - i] = tmp[a]; else rest[nr++] = tmp[a]; }
                int o = 0;
                for (int a = 0; a < p; a++) ord[o++] = rest[a];
                for (int a = 0; a < len; a++) ord[o++] = blk[a];
                for (int a = p; a < nr; a++) ord[o++] = rest[a];
                double v = f(ord, k, map);
                if (v > best + 1e-12) { best = v; improved = 1; }
                else memcpy(ord, tmp, sizeof(int) * k);
            }
        }
        /* reverse a segment */
        for (int i = 0; i < k; i++) for (int j = i + 2; j < k; j++) {
            memcpy(tmp, ord, sizeof(int) * k);
            for (int a = i, b = j; a < b; a++, b--) { int t = ord[a]; ord[a] = ord[b]; ord[b] = t; }
            double v = f(ord, k, map);
            if (v > best + 1e-12) { best = v; improved = 1; }
            else memcpy(ord, tmp, sizeof(int) * k);
        }
    }
    return best;
}

/* simulated annealing on a column order: random swap / block-move / reverse moves,
   Metropolis acceptance, linear cooling from t0 to 0 over iters, then a greedy finish */
static int sa_iters = 20000;
static double sa_t0 = 0.002;
/* value-space move: relabel PHYSICAL columns. For an even width, swap or rotate whole pair
   slots (2a,2a+1); for any width, swap two physical columns or rotate a run of them. */
static void value_move(int *ord, int k) {
    int rel[MAXK];
    for (int c = 0; c < k; c++) rel[c] = c;
    int kind = rnd() % 2;
    if (k % 2 == 0 && rnd() % 2) {
        int h = k / 2, a = rnd() % h, b = rnd() % h;
        if (a == b) b = (a + 1) % h;
        if (kind == 0) { rel[2 * a] = 2 * b; rel[2 * a + 1] = 2 * b + 1; rel[2 * b] = 2 * a; rel[2 * b + 1] = 2 * a + 1; }
        else {   /* rotate pair slots a..b by one */
            if (a > b) { int t = a; a = b; b = t; }
            for (int x = a; x <= b; x++) { int y = (x == b) ? a : x + 1; rel[2 * x] = 2 * y; rel[2 * x + 1] = 2 * y + 1; }
        }
    } else {
        int a = rnd() % k, b = rnd() % k;
        if (a == b) b = (a + 1) % k;
        if (kind == 0) { rel[a] = b; rel[b] = a; }
        else { if (a > b) { int t = a; a = b; b = t; } for (int x = a; x <= b; x++) rel[x] = (x == b) ? a : x + 1; }
    }
    for (int t = 0; t < k; t++) ord[t] = rel[ord[t]];
}
static void random_move(int *ord, int k) {
    if (rnd() % 2) { value_move(ord, k); return; }
    int kind = rnd() % 3, i = rnd() % k, j = rnd() % k;
    if (i == j) j = (i + 1) % k;
    if (i > j) { int t = i; i = j; j = t; }
    if (kind == 0) { int t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
    else if (kind == 1) { for (int a = i, b = j; a < b; a++, b--) { int t = ord[a]; ord[a] = ord[b]; ord[b] = t; } }
    else {
        int len = j - i + 1, rest[MAXK], nr = 0, blk[MAXK], tmp[MAXK];
        if (len >= k) return;
        memcpy(tmp, ord, sizeof(int) * k);
        for (int a = 0; a < k; a++) { if (a >= i && a <= j) blk[a - i] = tmp[a]; else rest[nr++] = tmp[a]; }
        int p = rnd() % (nr + 1), o = 0;
        for (int a = 0; a < p; a++) ord[o++] = rest[a];
        for (int a = 0; a < len; a++) ord[o++] = blk[a];
        for (int a = p; a < nr; a++) ord[o++] = rest[a];
    }
}
static double anneal(int *ord, int k, ordfun f, const int *map, double t0) {
    double cur = f(ord, k, map), best = cur;
    int bo[MAXK], tmp[MAXK];
    memcpy(bo, ord, sizeof(int) * k);
    for (int it = 0; it < sa_iters; it++) {
        double T = t0 * (1.0 - (double)it / sa_iters);
        memcpy(tmp, ord, sizeof(int) * k);
        random_move(ord, k);
        double v = f(ord, k, map);
        if (v >= cur || (T > 0 && exp((v - cur) / T) * 4294967296.0 > (double)rnd() * 2.0)) {
            cur = v;
            if (v > best) { best = v; memcpy(bo, ord, sizeof(int) * k); }
        } else memcpy(ord, tmp, sizeof(int) * k);
    }
    memcpy(ord, bo, sizeof(int) * k);
    climb_blocks = 0;               /* the anneal explored block moves; finish greedily */
    double v = climb(ord, k, f, map);
    climb_blocks = 1;
    return v;
}

/* substitution solve on current cells */
static double solve_sub(int *map, int nrest) {
    long cnt[36] = {0};
    for (int m = 0; m < nmsg; m++) for (int j = 0; j < ncell[m]; j++) if (cells[m][j] >= 0) cnt[cells[m][j]]++;
    int bycnt[36];
    for (int i = 0; i < 36; i++) bycnt[i] = i;
    for (int i = 0; i < 36; i++) for (int j = i + 1; j < 36; j++)
        if (cnt[bycnt[j]] > cnt[bycnt[i]]) { int t = bycnt[i]; bycnt[i] = bycnt[j]; bycnt[j] = t; }
    int bestmap[36]; double bestv = -1e9;
    for (int r = 0; r < nrest; r++) {
        int cur[36];
        if (r == 0) for (int i = 0; i < 36; i++) cur[bycnt[i]] = freqorder[i];
        else {
            int perm[36]; for (int i = 0; i < 36; i++) perm[i] = i;
            for (int i = 35; i > 0; i--) { int j = rnd() % (i + 1); int t = perm[i]; perm[i] = perm[j]; perm[j] = t; }
            for (int i = 0; i < 36; i++) cur[i] = perm[i];
        }
        double v = lm_score(cur, NULL);
        int improved = 1;
        while (improved) {
            improved = 0;
            for (int i = 0; i < 36; i++) {
                if (!cnt[i]) continue;
                for (int j = 0; j < 36; j++) {
                    if (j == i) continue;
                    int t = cur[i]; cur[i] = cur[j]; cur[j] = t;
                    double w = lm_score(cur, NULL);
                    if (w > v + 1e-12) { v = w; improved = 1; }
                    else { t = cur[i]; cur[i] = cur[j]; cur[j] = t; }
                }
            }
        }
        if (v > bestv) { bestv = v; memcpy(bestmap, cur, sizeof bestmap); }
    }
    memcpy(map, bestmap, sizeof bestmap);
    return bestv;
}

static void print_result(const char *tag, const int *ord, int k, const int *map, double sc, double ic) {
    int perm[MAXK];
    for (int t = 0; t < k; t++) perm[ord[t]] = t + 1;
    printf("%s_width=%d\n%s_trans=", tag, k, tag);
    for (int i = 0; i < k; i++) printf("%d%c", perm[i], i + 1 < k ? ' ' : '\n');
    printf("%s_score=%.6f\n%s_ic=%.6f\n%s_square=", tag, sc, tag, ic, tag);
    for (int c = 0; c < 36; c++) putchar(map[c] >= 0 ? ALPH[map[c]] : '?');
    putchar('\n');
    make_cells(ord, k);
    printf("%s_pscore=%.6f\n", tag, lm_pscore(map));
    for (int m = 0; m < nmsg; m++) {
        printf("%s_plain%d=", tag, m);
        for (int j = 0; j < ncell[m]; j++) putchar(cells[m][j] >= 0 && map[cells[m][j]] >= 0 ? ALPH[map[cells[m][j]]] : '-');
        putchar('\n');
    }
}

#define NC 4
static int cord[16][NC][MAXK]; static double cic[16][NC]; static int cidx[16];
static int screenw = 0, screenr = 4, screeni = 20000;
static void phaseA(void) {
    if (screenw > 0 && screenw < nw) {
        /* stage 0: a cheap pass over every width; keep the screenw best by pair IC + bigram IC */
        double sv[16]; int si[16];
        int sr = restarts, sii = sa_iters;
        restarts = screenr; sa_iters = screeni;
        for (int w = 0; w < nw; w++) {
            int k = widths[w], ord[MAXK]; sv[w] = -1; si[w] = w;
            for (int r = 0; r < restarts; r++) {
                random_order(ord, k);
                anneal(ord, k, eval_ic, NULL, sa_t0);
                double v = anneal(ord, k, eval_ic2, NULL, sa_t0);
                if (v > sv[w]) sv[w] = v;
            }
            printf("screen_width%d=%.6f\n", k, sv[w]);
        }
        restarts = sr; sa_iters = sii;
        for (int i = 0; i < nw; i++) for (int j = i + 1; j < nw; j++) if (sv[si[j]] > sv[si[i]]) { int t = si[i]; si[i] = si[j]; si[j] = t; }
        int keep[16]; for (int i = 0; i < screenw; i++) keep[i] = widths[si[i]];
        nw = screenw; for (int i = 0; i < nw; i++) widths[i] = keep[i];
    }
    for (int w = 0; w < nw; w++) {
        int k = widths[w], ord[MAXK];
        for (int c = 0; c < NC; c++) cic[w][c] = -1;
        for (int r = 0; r < restarts; r++) {
            random_order(ord, k);
            anneal(ord, k, eval_ic, NULL, sa_t0);
            double v = anneal(ord, k, eval_ic2, NULL, sa_t0);
            int dup = 0;
            for (int c = 0; c < NC; c++) if (fabs(cic[w][c] - v) < 1e-12) dup = 1;
            if (dup) continue;
            int worst = 0;
            for (int c = 1; c < NC; c++) if (cic[w][c] < cic[w][worst]) worst = c;
            if (v > cic[w][worst]) { cic[w][worst] = v; memcpy(cord[w][worst], ord, sizeof(int) * k); }
        }
        double b = -1; for (int c = 0; c < NC; c++) if (cic[w][c] > b) b = cic[w][c];
        printf("ic2_width%d=%.6f\n", k, b);
    }
    double bic[16];
    for (int i = 0; i < nw; i++) { cidx[i] = i; bic[i] = -1; for (int c = 0; c < NC; c++) if (cic[i][c] > bic[i]) bic[i] = cic[i][c]; }
    for (int i = 0; i < nw; i++) for (int j = i + 1; j < nw; j++) if (bic[cidx[j]] > bic[cidx[i]]) { int t = cidx[i]; cidx[i] = cidx[j]; cidx[j] = t; }
}

static void mode1(void) {
    phaseA();
    double gbest = -1e9; int gk = 0, gord[MAXK], gmap[36];
    for (int c = 0; c < topw && c < nw; c++) {
        int w = cidx[c], k = widths[w];
        for (int cc = 0; cc < NC; cc++) {
            if (cic[w][cc] < 0) continue;
            int ord[MAXK], map[36];
            memcpy(ord, cord[w][cc], sizeof(int) * k);
            make_cells(ord, k);
            double sc = solve_sub(map, 4);
            for (int it = 0; it < 4; it++) {
                double s2 = climb(ord, k, eval_lm, map);
                make_cells(ord, k);
                double s3 = solve_sub(map, 2);
                double nb = s3 > s2 ? s3 : s2;
                if (nb < sc + 1e-9) break;
                sc = nb;
            }
            make_cells(ord, k);
            sc = lm_score(map, NULL);
            if (sc > gbest) { gbest = sc; gk = k; memcpy(gord, ord, sizeof(int) * k); memcpy(gmap, map, sizeof gmap); }
        }
        printf("cand%d_width=%d\n", c, k);
    }
    print_result("best", gord, gk, gmap, gbest, pair_ic(gord, gk));
}

/* mode 2: KNOWN square. The trigram score of the decryption is informative by itself, so the
   order is annealed on it directly: a cheap screen over every width (SCREENR x SCREENI), then
   the full budget (RESTARTS x SAITERS) on the SCREENW best widths; temperature SAT0LM. */
static double sa_t0lm = 0.05;
static void mode2(void) {
    int keepw[16], nk = nw;
    for (int i = 0; i < nw; i++) keepw[i] = widths[i];
    if (screenw > 0 && screenw < nw) {
        double sv[16]; int si[16], sii = sa_iters;
        sa_iters = screeni;
        for (int w = 0; w < nw; w++) {
            int k = widths[w], ord[MAXK]; sv[w] = -1e9; si[w] = w;
            for (int r = 0; r < screenr; r++) {
                random_order(ord, k);
                double v = anneal(ord, k, eval_lm, sq, sa_t0lm);
                if (v > sv[w]) sv[w] = v;
            }
            printf("screen_width%d=%.6f\n", k, sv[w]);
        }
        sa_iters = sii;
        for (int i = 0; i < nw; i++) for (int j = i + 1; j < nw; j++) if (sv[si[j]] > sv[si[i]]) { int t = si[i]; si[i] = si[j]; si[j] = t; }
        nk = screenw;
        for (int i = 0; i < nk; i++) keepw[i] = widths[si[i]];
    }
    double gbest = -1e9; int gk = 0, gord[MAXK];
    for (int w = 0; w < nk; w++) {
        int k = keepw[w], ord[MAXK];
        for (int r = 0; r < restarts; r++) {
            random_order(ord, k);
            double v = anneal(ord, k, eval_lm, sq, sa_t0lm);
            if (v > gbest) { gbest = v; gk = k; memcpy(gord, ord, sizeof(int) * k); }
        }
    }
    print_result("best", gord, gk, sq, gbest, pair_ic(gord, gk));
}

/* ---- mode 3 ---- */
typedef struct { int type, pos; } Edit;   /* 0 del1, 1 ins1, 2 del5, 3 ins5 */
static int apply_edits(const signed char *ct, int n, const Edit *e, int ne, signed char *out) {
    /* edits refer to positions in the ORIGINAL string; apply left to right with an offset */
    int o = 0, i = 0;
    Edit s[4]; memcpy(s, e, sizeof(Edit) * ne);
    for (int a = 0; a < ne; a++) for (int b = a + 1; b < ne; b++)
        if (s[b].pos < s[a].pos) { Edit t = s[a]; s[a] = s[b]; s[b] = t; }
    int ei = 0;
    while (i <= n) {
        while (ei < ne && s[ei].pos == i) {
            if (s[ei].type == 1) out[o++] = 6;
            else if (s[ei].type == 3) for (int z = 0; z < 5; z++) out[o++] = 6;
            else if (s[ei].type == 0) i += 1;
            else i += 5;
            ei++;
        }
        if (i < n) out[o++] = ct[i];
        i++;
        if (o >= MAXN - 8) break;
    }
    return o;
}

/* Mode 3 score: mean over EVERY trigram position of the decryption; a position whose trigram
   contains an unknown letter is charged PEN = ln(1/36). Without the charge, inserting unknowns
   lets the edit search drop the trigrams that score badly (found 2026-11-01: a wrong key with
   2 edits reached -1.04 per trigram, above real German). */
#define PEN (-3.58351893845611)
static double score_single(const signed char *ct, int n, const int *ord, int k) {
    signed char tmp[MAXN];
    untrans(ct, n, ord, k, tmp);
    double s = 0; long pos = 0; int a = -1, b = -1, j2 = 0;
    for (int j = 0; j + 1 < n; j += 2, j2++) {
        int x = tmp[j], y = tmp[j + 1];
        int c = (x < 6 && y < 6) ? sq[x * 6 + y] : -1;
        if (j2 >= 2) { s += (a >= 0 && b >= 0 && c >= 0) ? LM[a * 1296 + b * 36 + c] : PEN; pos++; }
        a = b; b = c;
    }
    return pos ? s / pos : -99.0;
}

static void mode3(void) {
    int ord[MAXK];
    for (int i = 0; i < tk; i++) ord[tperm[i] - 1] = i;
    for (int m = 0; m < nmsg; m++) {
        int n = mlen[m];
        Edit cand[3 * MAXN]; int nc = 0;
        for (int p = 0; p < n; p++) cand[nc++] = (Edit){0, p};
        for (int p = 0; p <= n; p++) cand[nc++] = (Edit){1, p};
        for (int p = 0; p + 5 <= n; p += 5) cand[nc++] = (Edit){2, p};
        for (int p = 0; p <= n; p += 5) cand[nc++] = (Edit){3, p};
        signed char buf[MAXN];
        double s0 = score_single(msg[m], n, ord, tk), best = s0;
        Edit be[3]; int bne = 0; long nvar = 1;
        Edit e[3];
        /* best score by exact number of edits (events) and by exact total SYMBOL cost
           (del1/ins1 = 1 symbol, del5/ins5 = 5), for the jump statistic and a symbol cap */
        double bev[4] = {s0, -99, -99, -99}, bsym[16];
        Edit bse[16][3]; int bsn[16];
        for (int z = 0; z < 16; z++) { bsym[z] = -99; bsn[z] = 0; }
        bsym[0] = s0;
#define SYMC(x) ((x).type >= 2 ? 5 : 1)
#define NOTE(ne_, sc_, v_) do { if ((v_) > bev[ne_]) bev[ne_] = (v_); \
        if ((sc_) < 16 && (v_) > bsym[sc_]) { bsym[sc_] = (v_); bsn[sc_] = (ne_); memcpy(bse[sc_], e, sizeof(Edit) * (ne_)); } } while (0)
        if (cap >= 1) for (int a = 0; a < nc; a++) {
            e[0] = cand[a];
            int L = apply_edits(msg[m], n, e, 1, buf); nvar++;
            double v = score_single(buf, L, ord, tk);
            NOTE(1, SYMC(e[0]), v);
            if (v > best) { best = v; bne = 1; be[0] = e[0]; }
            if (cap >= 2) for (int b = a + 1; b < nc; b++) {
                e[1] = cand[b];
                L = apply_edits(msg[m], n, e, 2, buf); nvar++;
                v = score_single(buf, L, ord, tk);
                NOTE(2, SYMC(e[0]) + SYMC(e[1]), v);
                if (v > best) { best = v; bne = 2; be[0] = e[0]; be[1] = e[1]; }
                if (cap >= 3) for (int c = b + 1; c < nc; c++) {
                    e[2] = cand[c];
                    L = apply_edits(msg[m], n, e, 3, buf); nvar++;
                    v = score_single(buf, L, ord, tk);
                    NOTE(3, SYMC(e[0]) + SYMC(e[1]) + SYMC(e[2]), v);
                    if (v > best) { best = v; bne = 3; be[0] = e[0]; be[1] = e[1]; be[2] = e[2]; }
                }
            }
        }
        printf("msg%d_bestev=", m);
        for (int z = 0; z <= cap && z < 4; z++) printf("%.6f%c", bev[z], z < cap && z < 3 ? ',' : '\n');
        printf("msg%d_bestsym=", m);
        for (int z = 0; z < 16; z++) printf("%.6f%c", bsym[z], z < 15 ? ',' : '\n');
        printf("msg%d_bestsymedits=", m);
        for (int z = 0; z < 16; z++) {
            for (int i = 0; i < bsn[z]; i++) printf("%s@%d%s", (const char *[]){"del1", "ins1", "del5", "ins5"}[bse[z][i].type], bse[z][i].pos, i + 1 < bsn[z] ? "," : "");
            putchar(z < 15 ? ';' : '\n');
        }
        printf("msg%d_score0=%.6f\nmsg%d_score=%.6f\nmsg%d_variants=%ld\nmsg%d_edits=", m, s0, m, best, m, nvar, m);
        for (int i = 0; i < bne; i++) printf("%s@%d%c", (const char *[]){"del1", "ins1", "del5", "ins5"}[be[i].type], be[i].pos, i + 1 < bne ? ',' : ' ');
        putchar('\n');
        int L = apply_edits(msg[m], n, be, bne, buf);
        signed char tmp[MAXN];
        untrans(buf, L, ord, tk, tmp);
        printf("msg%d_plain=", m);
        for (int j = 0; j + 1 < L; j += 2) {
            int x = tmp[j], y = tmp[j + 1];
            int c = (x < 6 && y < 6) ? sq[x * 6 + y] : -1;
            putchar(c >= 0 ? ALPH[c] : '-');
        }
        putchar('\n');
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: jattack LMTABLE < job\n"); return 2; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror(argv[1]); return 2; }
    for (int i = 0; i < 46656; i++) if (fscanf(f, "%lf", &LM[i]) != 1) { fprintf(stderr, "bad LM\n"); return 2; }
    fclose(f);
    for (int i = 0; i < 36; i++) freqorder[i] = i;
    char line[8192];
    while (fgets(line, sizeof line, stdin)) {
        char *s = strtok(line, " \t\r\n");
        if (!s) continue;
        if (!strcmp(s, "MODE")) mode = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "WIDTHS")) { char *t; while ((t = strtok(NULL, " \t\r\n"))) widths[nw++] = atoi(t); }
        else if (!strcmp(s, "SQUARE")) { char *t = strtok(NULL, " \t\r\n"); for (int i = 0; i < 36; i++) sq[i] = t[i] == '?' ? -1 : alidx(t[i]); haveSq = 1; }
        else if (!strcmp(s, "TRANS")) { tk = atoi(strtok(NULL, " \t\r\n")); for (int i = 0; i < tk; i++) tperm[i] = atoi(strtok(NULL, " \t\r\n")); }
        else if (!strcmp(s, "CAP")) cap = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "SAITERS")) sa_iters = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "SCREENW")) screenw = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "SCREENR")) screenr = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "SCREENI")) screeni = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "SAT0LM")) sa_t0lm = atof(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "LAMB")) lamb = atof(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "SAT0")) sa_t0 = atof(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "RESTARTS")) restarts = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "TOPW")) topw = atoi(strtok(NULL, " \t\r\n"));
        else if (!strcmp(s, "FREQ")) { char *t = strtok(NULL, " \t\r\n"); for (int i = 0; i < 36; i++) freqorder[i] = alidx(t[i]); }
        else if (!strcmp(s, "SEED")) { rs = strtoull(strtok(NULL, " \t\r\n"), NULL, 10) * 2654435761ULL + 1; for (int i = 0; i < 10; i++) rnd(); }
        else if (!strcmp(s, "MSG")) {
            char *t = strtok(NULL, " \t\r\n");
            if (!t || nmsg >= MAXM) continue;
            int n = 0; for (; t[n] && n < MAXN - 8; n++) msg[nmsg][n] = (signed char)symidx(t[n]);
            mlen[nmsg++] = n;
        }
    }
    if (mode == 4) {   /* diagnostic: known transposition, solve the substitution only */
        int ord[MAXK], map[36];
        for (int i = 0; i < tk; i++) ord[tperm[i] - 1] = i;
        make_cells(ord, tk);
        double sc = solve_sub(map, restarts);
        print_result("best", ord, tk, map, sc, pair_ic(ord, tk));
        return 0;
    }
    if (mode == 1) mode1();
    else if (mode == 2) { if (!haveSq) return 3; mode2(); }
    else { if (!haveSq || !tk) return 3; mode3(); }
    return 0;
}
