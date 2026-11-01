/* a3.c - adv-adfgvx, 2026-11-01. Adversary for J3 (unknown square + unknown columnar
   transposition, one key shared by a group of messages), scored by the J3 decision statistic:
   pscore = mean over every plaintext trigram position (i >= 2, per message) of ln P, a position
   with an unknown letter (lost symbol) charged ln(1/36). Written from the cipher's definition;
   no code from search/ or verify/.
   Square = free bijection of the 36 cells onto A-Z0-9 (no blanks).
   Usage: a3 LMTABLE < job
     job lines:  MSG text            (one per member; '-' = lost)
                 FREQ 36chars        (plaintext symbols by descending training frequency)
                 SEED s
                 then one of
                 SUB k p1..pk        solve the square for this transposition (p = read-out rank of column i)
                 RANDT w N           N random transpositions of width w, square solved for each
                 JOINT w R I [T0]    R restarts at width w: transposition anneal (T0 on the per-trigram
                                     scale, linear to 0; 0 = hill climb) with the square greedily
                                     re-fitted per move, I iters; then a full square solve
   Output: one line per result:  KIND w score perm(.) square plain(|-joined)                     */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXM 16
#define MAXN 1400
#define PEN (-3.58351893845611)
static double LM[46656];
static const char *AL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
static int nm = 0, len[MAXM]; static signed char ct[MAXM][MAXN];
static int cells[MAXM][MAXN / 2], nc[MAXM], P = 0;   /* P = total trigram positions */
static int freq[36];
static unsigned long long S = 1;
static double ur(void) { S ^= S << 13; S ^= S >> 7; S ^= S << 17; return (S >> 11) * (1.0 / 9007199254740992.0); }
static int ri(int n) { return (int)(ur() * n); }
static int sym(char c) { const char *L = "ADFGVX"; const char *p = strchr(L, c); return (c && p) ? (int)(p - L) : 6; }

static void untrans(const int *rank, int k) {
    int order[64]; for (int i = 0; i < k; i++) order[rank[i] - 1] = i;
    P = 0;
    for (int m = 0; m < nm; m++) {
        static signed char g[MAXN]; int n = len[m], q = n / k, r = n % k, pos = 0;
        for (int t = 0; t < k; t++) { int c = order[t], L = q + (c < r); for (int row = 0; row < L; row++) g[row * k + c] = ct[m][pos++]; }
        nc[m] = n / 2;
        for (int j = 0; j < nc[m]; j++) { int a = g[2 * j], b = g[2 * j + 1]; cells[m][j] = (a < 6 && b < 6) ? a * 6 + b : -1; }
        if (nc[m] > 2) P += nc[m] - 2;
    }
}
static double total(const int *map) {   /* sum, not mean */
    double s = 0;
    for (int m = 0; m < nm; m++) {
        int a = -1, b = -1;
        for (int j = 0; j < nc[m]; j++) {
            int c = cells[m][j] >= 0 ? map[cells[m][j]] : -1;
            if (j >= 2) s += (a >= 0 && b >= 0 && c >= 0) ? LM[a * 1296 + b * 36 + c] : PEN;
            a = b; b = c;
        }
    }
    return s;
}
/* square: start from frequency ranks, then anneal on swaps of two cells' plaintexts */
static double solve_sub(int *best, int restarts, int iters) {
    double gb = -1e18; int map[36];
    for (int r = 0; r < restarts; r++) {
        int cnt[36] = {0}, idx[36];
        for (int m = 0; m < nm; m++) for (int j = 0; j < nc[m]; j++) if (cells[m][j] >= 0) cnt[cells[m][j]]++;
        for (int i = 0; i < 36; i++) idx[i] = i;
        for (int i = 0; i < 36; i++) for (int j = i + 1; j < 36; j++) if (cnt[idx[j]] > cnt[idx[i]]) { int t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
        for (int i = 0; i < 36; i++) map[idx[i]] = freq[i];
        if (r > 0) for (int z = 0; z < 6 * r; z++) { int a = ri(36), b = ri(36), t = map[a]; map[a] = map[b]; map[b] = t; }
        double cur = total(map), T0 = 0.6 * (P > 0 ? 1 : 0);
        double bl = cur; int bm[36]; memcpy(bm, map, sizeof map);
        for (int it = 0; it < iters; it++) {
            double T = T0 * (1.0 - (double)it / iters) + 1e-9;
            int a = ri(36), b = ri(36); if (a == b) continue;
            int t = map[a]; map[a] = map[b]; map[b] = t;
            double v = total(map);
            if (v >= cur || ur() < exp((v - cur) / T)) { cur = v; if (v > bl) { bl = v; memcpy(bm, map, sizeof map); } }
            else { t = map[a]; map[a] = map[b]; map[b] = t; }
        }
        /* greedy finish */
        memcpy(map, bm, sizeof map); cur = bl; int imp = 1;
        while (imp) { imp = 0; for (int a = 0; a < 36; a++) for (int b = a + 1; b < 36; b++) {
            int t = map[a]; map[a] = map[b]; map[b] = t; double v = total(map);
            if (v > cur + 1e-12) { cur = v; imp = 1; } else { t = map[a]; map[a] = map[b]; map[b] = t; } } }
        if (cur > gb) { gb = cur; memcpy(best, map, sizeof map); }
    }
    return P ? gb / P : -99;
}
static void out(const char *kind, const int *rank, int k, const int *map, double sc) {
    printf("%s %d %.6f ", kind, k, sc);
    for (int i = 0; i < k; i++) printf("%d%s", rank[i], i + 1 < k ? "." : " ");
    char sq[37]; for (int c = 0; c < 36; c++) sq[c] = AL[map[c]]; sq[36] = 0; printf("%s ", sq);
    for (int m = 0; m < nm; m++) { for (int j = 0; j < nc[m]; j++) putchar(cells[m][j] >= 0 ? AL[map[cells[m][j]]] : '-'); putchar(m + 1 < nm ? '|' : '\n'); }
    fflush(stdout);
}
static void rperm(int *rank, int k) { for (int i = 0; i < k; i++) rank[i] = i + 1; for (int i = k - 1; i > 0; i--) { int j = ri(i + 1), t = rank[i]; rank[i] = rank[j]; rank[j] = t; } }

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); for (int i = 0; i < 46656; i++) if (fscanf(f, "%lf", &LM[i]) != 1) return 2; fclose(f);
    static char line[16384];
    while (fgets(line, sizeof line, stdin)) {
        char *s = strtok(line, " \t\n"); if (!s) continue;
        if (!strcmp(s, "MSG")) { char *t = strtok(NULL, " \t\n"); len[nm] = strlen(t); for (int i = 0; i < len[nm]; i++) ct[nm][i] = sym(t[i]); nm++; }
        else if (!strcmp(s, "FREQ")) { char *t = strtok(NULL, " \t\n"); for (int i = 0; i < 36; i++) freq[i] = (int)(strchr(AL, t[i]) - AL); }
        else if (!strcmp(s, "SEED")) { S = strtoull(strtok(NULL, " \t\n"), NULL, 10) * 0x9E3779B97F4A7C15ULL + 7; for (int i = 0; i < 20; i++) ur(); }
        else if (!strcmp(s, "SUB")) {
            int k = atoi(strtok(NULL, " \t\n")), rank[64], map[36];
            for (int i = 0; i < k; i++) rank[i] = atoi(strtok(NULL, " \t\n"));
            untrans(rank, k); double sc = solve_sub(map, 4, 60000); out("SUB", rank, k, map, sc);
        } else if (!strcmp(s, "RANDT")) {
            int k = atoi(strtok(NULL, " \t\n")), N = atoi(strtok(NULL, " \t\n")), rank[64], map[36];
            for (int n = 0; n < N; n++) { rperm(rank, k); untrans(rank, k); double sc = solve_sub(map, 2, 40000); out("RANDT", rank, k, map, sc); }
        } else if (!strcmp(s, "JOINT")) {
            /* transposition hill-climb (swap two ranks / move one column) with the square re-solved
               cheaply for each candidate; then a full square solve. */
            int k = atoi(strtok(NULL, " \t\n")), R = atoi(strtok(NULL, " \t\n")), I = atoi(strtok(NULL, " \t\n"));
            char *t0s = strtok(NULL, " \t\n"); double T0 = t0s ? atof(t0s) : 0.0;
            int rank[64], map[36], bestr[64], bestm[36]; double gb = -99;
            for (int r = 0; r < R; r++) {
                rperm(rank, k); untrans(rank, k); double cur = solve_sub(map, 1, 8000);
                int brk[64], bmp[36]; double bcur = cur; memcpy(brk, rank, sizeof(int) * k); memcpy(bmp, map, sizeof map);
                for (int it = 0; it < I; it++) {
                    double T = T0 * (1.0 - (double)it / I) + 1e-12;
                    int tr[64]; memcpy(tr, rank, sizeof(int) * k);
                    int a = ri(k), b = ri(k); if (a == b) continue;
                    if (ur() < 0.5) { int t = rank[a]; rank[a] = rank[b]; rank[b] = t; }
                    else { /* move column a's rank position: rotate ranks between a and b */
                        int lo = a < b ? a : b, hi = a < b ? b : a, t = rank[lo];
                        for (int x = lo; x < hi; x++) rank[x] = rank[x + 1]; rank[hi] = t; }
                    untrans(rank, k); int m2[36]; memcpy(m2, map, sizeof map);
                    /* quick re-fit: greedy swaps from the current square */
                    double v = total(m2); int imp = 1, pass = 0;
                    while (imp && pass++ < 2) { imp = 0; for (int x = 0; x < 36; x++) for (int y = x + 1; y < 36; y++) {
                        int t = m2[x]; m2[x] = m2[y]; m2[y] = t; double w = total(m2);
                        if (w > v + 1e-12) { v = w; imp = 1; } else { t = m2[x]; m2[x] = m2[y]; m2[y] = t; } } }
                    v = P ? v / P : -99;
                    if (v > cur || ur() < exp((v - cur) / T)) { cur = v; memcpy(map, m2, sizeof map);
                        if (cur > bcur) { bcur = cur; memcpy(brk, rank, sizeof(int) * k); memcpy(bmp, map, sizeof map); } }
                    else memcpy(rank, tr, sizeof(int) * k);
                }
                memcpy(rank, brk, sizeof(int) * k); memcpy(map, bmp, sizeof map);
                untrans(rank, k); cur = solve_sub(map, 3, 60000);
                if (cur > gb) { gb = cur; memcpy(bestr, rank, sizeof(int) * k); memcpy(bestm, map, sizeof map); }
            }
            untrans(bestr, k); out("JOINT", bestr, k, bestm, gb);
        }
    }
    return 0;
}
