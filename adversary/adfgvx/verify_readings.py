"""Independent re-check of every reading fake.c prints (shares no code with fake.c).

For each result line it: rebuilds the starting ciphertext (msgs.txt, or the shuffled ct the line
printed), re-applies the edit list in order, decrypts with the stated key using its own ADFGVX
implementation, checks the plaintext is identical, and re-scores it with its own quadgram counter
and a German word-coverage measure (fraction of plaintext letters covered by non-overlapping
corpus words of length >= 4, longest-cover DP).

Usage: verify_readings.py CORPUS_NORMALISED RAW_DIR results/X.txt [...]  -> results/verified_<X>.tsv
"""
import collections, math, os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SYM = 'ADFGVX'
ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def build_quad(text):
    c = collections.Counter(text[i:i + 4] for i in range(len(text) - 3))
    tot = len(text) - 3
    return {k: math.log10(v / tot) for k, v in c.items()}, math.log10(0.01 / tot)

def build_words(raw_dir):
    cnt = collections.Counter()
    for fn in glob.glob(os.path.join(raw_dir, '*.txt')):
        t = open(fn, encoding='utf-8', errors='replace').read().upper()
        for a, b in (('Ä', 'AE'), ('Ö', 'OE'), ('Ü', 'UE'), ('ß', 'SS')):
            t = t.replace(a, b)
        cnt.update(w for w in re.findall(r'[A-Z]+', t) if len(w) >= 4)
    return {w for w, v in cnt.items() if v >= 3}

def coverage(p, words, maxlen=24):
    n = len(p); best = [0] * (n + 1)
    for i in range(1, n + 1):
        b = best[i - 1]
        for l in range(4, min(maxlen, i) + 1):
            if p[i - l:i] in words and best[i - l] + l > b: b = best[i - l] + l
        best[i] = b
    return best[n] / max(n, 1)

def decrypt(ct, ranks, square):
    """ranks[i] = 1-based read-out rank of column i. Incomplete columnar, rows filled left to right."""
    N, L = len(ct), len(ranks)
    heights = [N // L + (1 if c < N % L else 0) for c in range(L)]
    columns, k = {}, 0
    for c in sorted(range(L), key=lambda c: ranks[c]):
        columns[c] = ct[k:k + heights[c]]; k += heights[c]
    stream = ''.join(columns[j % L][j // L] for j in range(N))
    return ''.join('?' if '?' in stream[2 * i:2 * i + 2] else square[SYM.index(stream[2 * i]) * 6 + SYM.index(stream[2 * i + 1])]
                   for i in range(N // 2))

def apply_edits(ct, edits):
    s = list(ct)
    for e in edits:
        op, rest = e[0], e[1:]
        if op == 'S': i, c = rest.split(':'); s[int(i)] = c
        elif op == 'D': i, m = rest.split(':'); del s[int(i):int(i) + int(m)]
        elif op == 'I': i, c = rest.split(':'); s[int(i):int(i)] = list(c)
        elif op == 'W': i = int(rest); s[i:i + 5], s[i + 5:i + 10] = s[i + 5:i + 10], s[i:i + 5]
        else: raise ValueError(e)
    return ''.join(s)

def main():
    corpus, raw = sys.argv[1], sys.argv[2]
    Q, floor = build_quad(open(corpus).read())
    W = build_words(raw)
    def score(text):  # mean over quadgrams with no unknown letter; parts separated by '|'
        qs = [p[i:i + 4] for p in text.split('|') for i in range(len(p) - 3) if '?' not in p[i:i + 4]]
        return sum(Q.get(q, floor) for q in qs) / max(len(qs), 1)
    msgs = dict(l.split() for l in open(os.path.join(HERE, 'msgs.txt')))
    for fn in sys.argv[3:]:
        out = open(os.path.join(os.path.dirname(fn), 'verified_' + os.path.basename(fn).replace('.txt', '.tsv')), 'w')
        out.write('tag\tk\tclaimed\tpy_score\tcoverage\tmatch\tplain\n')
        shuf = {}; bad = 0; n = 0
        for ln in open(fn):
            f = ln.split()
            if len(f) == 2 and f[1].startswith('ct='): shuf[f[0]] = f[1][3:]; continue
            if 'plain=' not in ln: continue
            d = dict(x.split('=', 1) for x in f[1:] if '=' in x)
            tag = f[0]
            ct = d.get('ct') or shuf.get(tag) or msgs[tag.split(':')[0]]
            if 'ct' not in d and (':shuf' in tag) and tag not in shuf:
                continue  # shuffled run whose ct was not printed; cannot verify
            ed = [] if d.get('edits', '-') == '-' else d['edits'].split()
            # edits field may contain spaces: recover it from the raw line
            m = re.search(r'edits=(.*?) perm=', ln)
            if m and m.group(1) != '-': ed = m.group(1).split()
            ranks = list(map(int, d['perm'].split(',')))
            p = '|'.join(decrypt(apply_edits(c, ed), ranks, d['square']) for c in ct.split(','))
            ok = p == d['plain']; bad += not ok; n += 1
            out.write('%s\t%s\t%s\t%.4f\t%.3f\t%s\t%s\n' % (tag, d.get('k', '0'), d['score'], score(p), coverage(p.replace('|', '?'), W), ok, p))
        print(fn, 'lines', n, 'mismatches', bad)

if __name__ == '__main__':
    main()
