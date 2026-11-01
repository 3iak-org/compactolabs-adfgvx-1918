"""Tabulate results/*.txt into results/summary.md. Usage: summarize.py MODEL_TXT (only for true-text scores)."""
import collections, json, os, re, statistics as st, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'results')
FAKE = os.environ.get('FAKE', os.path.join(os.environ.get('TMPDIR', '/tmp'), 'fake')); MODEL = sys.argv[1]
MSGS = dict(l.split() for l in open(os.path.join(HERE, 'msgs.txt')))
OPEN = ['p73_DFXGD', 'p152_FXVAD', 'p153_VFVAX', 'p153_AXVAA', 'p158_GDDFV', 'p170_AAGVG',
        'p176_GGDAA', 'p189_DVGAG', 'p198_DFVXV']
out = []
def P(*a): out.append(' '.join(str(x) for x in a))
def fl(ln, key):
    m = re.search(r'\b' + key + r'=(\S+)', ln); return m.group(1) if m else None
def lines(name):
    fn = os.path.join(R, name)
    return [l for l in open(fn) if 'score=' in l] if os.path.exists(fn) else []
def score(text):
    return float(subprocess.run([FAKE, MODEL, 'score', text], capture_output=True, text=True).stdout)

src = open(os.path.join(HERE, 'planted_source.txt')).read().strip()
P('## Reference: genuine 1918 telegram German under this scorer\n')
P('| text | letters | score |\n|---|---|---|')
P('| all nine solved readings joined | %d | %.3f |' % (len(src), score(src)))
for n in (42, 52, 66, 88, 120):
    vals = [score(src[a:a + n]) for a in range(0, len(src) - n, 7)]
    P('| windows of %d letters (step 7), min / median / max | %d | %.2f / %.2f / %.2f |' % (n, n, min(vals), st.median(vals), max(vals)))

A = lines('A_random_keys.txt')
if A:
    P('\n## (a) Random keys (200,000 per message, L uniform 10-25)\n')
    P('| message | symbols | mean | sd | max |\n|---|---|---|---|---|')
    for l in sorted(A, key=lambda l: OPEN.index(l.split()[0]) if l.split()[0] in OPEN else 99):
        m = l.split(); P('| %s | %d | %s | %s | %s |' % (m[0], len(MSGS[m[0]]), fl(l, 'mean'), fl(l, 'sd'), fl(l, 'max')))

B = lines('B_free_key.txt')
if B:
    P('\n## (b) Free key (transposition L=10..25 and square both free), real vs shuffled ciphertext\n')
    P('Best over L of 8 restarts each (pair-IC transposition search, 200k steps; substitution SA, 1M steps; 3 rounds of column reordering). "shuf" = symbols of the message randomly permuted (3 independent shuffles, each searched at every L).\n')
    P('| message | letters | real: best | shuffled: best of each shuffle | shuffled max |\n|---|---|---|---|---|')
    best = collections.defaultdict(lambda: (-99, ''))
    for l in B:
        tag = l.split()[0]; s = float(fl(l, 'score'))
        if s > best[tag][0]: best[tag] = (s, l)
    for m in OPEN:
        sh = [best['%s:shuf%d' % (m, i)][0] for i in range(3) if '%s:shuf%d' % (m, i) in best]
        if m + ':real' not in best: continue
        P('| %s | %d | %.3f | %s | %.3f |' % (m, len(MSGS[m]) // 2, best[m + ':real'][0], ' '.join('%.3f' % x for x in sh), max(sh) if sh else -99))
    P('\nPer-L view (best over restarts; real / max over 3 shuffles):\n')
    byL = collections.defaultdict(dict)
    for l in B:
        tag = l.split()[0]; L = int(fl(l, 'L')); s = float(fl(l, 'score')); kind = 'real' if tag.endswith('real') else 'shuf'
        k = (tag.split(':')[0], L, kind); byL[k] = max(byL.get(k, -99), s) if isinstance(byL.get(k), float) else s
    Ls = sorted({k[1] for k in byL})
    P('| message | ' + ' | '.join('L%d' % L for L in Ls) + ' |'); P('|---' * (len(Ls) + 1) + '|')
    for m in OPEN:
        row = []
        for L in Ls:
            r = byL.get((m, L, 'real')); s = byL.get((m, L, 'shuf'))
            row.append('%s/%s' % ('%.2f' % r if isinstance(r, float) else '-', '%.2f' % s if isinstance(s, float) else '-'))
        P('| %s | %s |' % (m, ' | '.join(row)))
    P('\nBest false readings from SHUFFLED ciphertext (free key):\n')
    for m in OPEN:
        cand = [(best['%s:shuf%d' % (m, i)]) for i in range(3) if '%s:shuf%d' % (m, i) in best]
        if not cand: continue
        s, l = max(cand)
        P('- %s (%.3f, L=%s): `%s`' % (m, s, fl(l, 'L'), fl(l, 'plain')))

Pm = os.path.join(R, 'P_planted_meta.json')
PL = lines('P_planted.txt')
if PL and os.path.exists(Pm):
    meta = {d['tag']: d for d in json.load(open(Pm))}
    P('\n## Positive control: planted 1918 telegram text, same lengths, free-key solver at the true L\n')
    P('| tag | letters | L | true-text score | solver best | letters correct |\n|---|---|---|---|---|---|')
    for l in sorted(PL):
        tag = l.split()[0]; d = meta[tag]; p = fl(l, 'plain')
        ok = sum(a == b for a, b in zip(p, d['plain'])) / len(d['plain'])
        P('| %s | %d | %d | %.3f | %s | %.0f%% |' % (tag, len(d['plain']), d['L'], score(d['plain']), fl(l, 'score'), 100 * ok))

E = lines('E_edits.txt')
if E:
    P('\n## (c) Published period keys + k free edits (beam 16)\n')
    P('Max over the 15 published keys of the best score after k edits. block = ops: substitute 1, delete 1-5, insert 1-5, swap adjacent 5-blocks; single = substitute/delete/insert one symbol. shuf = same keys on shuffled ciphertext; rand = 10 random keys (random L 10-25, random square).\n')
    tab = collections.defaultdict(lambda: -99.0); txt = {}
    for l in E:
        tag = l.split()[0]; k = int(fl(l, 'k')); s = float(fl(l, 'score'))
        parts = tag.split(':'); m = parts[0]
        if parts[1].startswith('rand'): cls = 'rand'
        else: cls = parts[2] + ':' + parts[3]
        key = (m, cls, k)
        if s > tab[key]: tab[key] = s; txt[key] = l
    Ks = range(0, 11)
    for cls in ('block:real', 'single:real', 'block:shuf', 'rand'):
        P('\n**%s**\n' % cls); P('| message | ' + ' | '.join('k=%d' % k for k in Ks) + ' |'); P('|---' * 12 + '|')
        for m in OPEN:
            P('| %s | %s |' % (m, ' | '.join('%.2f' % tab[(m, cls, k)] if (m, cls, k) in tab else '-' for k in Ks)))
    P('\n**true key on the solved messages (what a real fit looks like)**\n')
    P('| message | mode | ' + ' | '.join('k=%d' % k for k in Ks) + ' |'); P('|---' * 13 + '|')
    for m in sorted({k[0] for k in tab if k[1].endswith('truekey')}):
        for mode in ('block', 'single'):
            P('| %s | %s | %s |' % (m, mode, ' | '.join('%.2f' % tab[(m, mode + ':truekey', k)] if (m, mode + ':truekey', k) in tab else '-' for k in Ks)))
    P('\nBest false readings, published keys on the REAL open messages, k=10 block edits:\n')
    for m in OPEN:
        if (m, 'block:real', 10) in txt:
            l = txt[(m, 'block:real', 10)]
            P('- %s %s (%.3f) edits `%s`: `%s`' % (m, l.split()[0].split(':')[1], tab[(m, 'block:real', 10)], re.search(r'edits=(.*?) perm=', l).group(1), fl(l, 'plain')))

FE = lines('FE_free_edits.txt')
if FE:
    P('\n## (c\') Free key + k block edits (alternating), L = 16 and 19\n')
    tab = collections.defaultdict(lambda: -99.0)
    for l in FE:
        tag = l.split()[0]; m, L, kind = tag.split(':'); k = int(fl(l, 'k')); s = float(fl(l, 'score'))
        tab[(m, kind, k)] = max(tab[(m, kind, k)], s)
    P('| message | kind | ' + ' | '.join('k=%d' % k for k in range(11)) + ' |'); P('|---' * 13 + '|')
    for m in OPEN:
        for kind in ('real', 'shuf'):
            P('| %s | %s | %s |' % (m, kind, ' | '.join('%.2f' % tab[(m, kind, k)] if (m, kind, k) in tab else '-' for k in range(11))))

T = lines('T_truppen_free_square.txt')
if T:
    P('\n## TRUPPENVERSCHIEBUNG transposition (L=19), square free\n')
    P('| message | real | shuffled (3) |\n|---|---|---|')
    d = collections.defaultdict(list)
    for l in T:
        tag = l.split()[0]; m = tag.split(':')[0]; d[(m, 'real' if tag.endswith('real') else 'shuf')].append(float(fl(l, 'score')))
    for m in OPEN:
        P('| %s | %s | %s |' % (m, ' '.join('%.3f' % x for x in d[(m, 'real')]), ' '.join('%.3f' % x for x in sorted(d[(m, 'shuf')], reverse=True))))

C = lines('C_creilly.txt')
if C:
    P('\n## Calibration on creilly11235/adfgvx-1918 claims\n')
    for l in sorted(C):
        P('- `%s` score %s L/M=%s plain `%s`' % (l.split()[0], fl(l, 'score'), fl(l, 'L') or fl(l, 'M'), (fl(l, 'plain') or '')[:140]))

open(os.path.join(R, 'summary.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
