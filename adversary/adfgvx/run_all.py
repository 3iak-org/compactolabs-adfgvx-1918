"""Driver for the ADFGVX false-reading baseline. Runs ./fake (C) across 8 cores; raw lines go to
results/<experiment>.txt. Re-run:  python run_all.py MODEL_TXT [experiment ...]
Experiments: A (random keys), B (free key, real + shuffled), P (planted positive controls, free key),
E (published keys + edits, real / shuffled / random keys / true-key controls), FE (free key + edits),
T (TRUPPENVERSCHIEBUNG transposition, free square)."""
import json, os, random, subprocess, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
FAKE = os.environ.get('FAKE', os.path.join(os.environ.get('TMPDIR', '/tmp'), 'fake'))
MODEL = sys.argv[1]
WANT = set(sys.argv[2:]) or {'A', 'B', 'P', 'E', 'FE', 'T'}
OUT = os.path.join(HERE, 'results'); os.makedirs(OUT, exist_ok=True)

MSGS = dict(l.split() for l in open(os.path.join(HERE, 'msgs.txt')))
KEYS = json.load(open(os.path.join(HERE, 'keys_bourdeau.json')))
OPEN = ['p73_DFXGD', 'p152_FXVAD', 'p153_VFVAX', 'p153_AXVAA', 'p158_GDDFV', 'p170_AAGVG',
        'p176_GGDAA', 'p189_DVGAG', 'p198_DFVXV']
SOLVED = {'p100_VDDAD': 3, 'p105_GAGVA': 3, 'p109_XGDFG': 3, 'p132_AAXAX': 4, 'p146_FVFAF': 4,
          'p171_AAVGF': 5, 'p176_VVAVD': 6, 'p187_FFVXV': 14, 'pQQQ_AFAFF': 14}
SYM = 'ADFGVX'
ALPH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def keyword_perm(w):
    order = sorted(range(len(w)), key=lambda i: (w[i], i))
    r = [0] * len(w)
    for rank, i in enumerate(order): r[i] = rank + 1
    return r

def run(args):
    tag, cmd = args
    o = subprocess.run([FAKE, MODEL] + [str(c) for c in cmd], capture_output=True, text=True)
    return tag, o.stdout + (('#ERR ' + o.stderr) if o.returncode else '')

def pool_run(name, jobs):
    with Pool(8) as p, open(os.path.join(OUT, name + '.txt'), 'w') as f:
        for tag, out in p.imap_unordered(run, jobs):
            f.write(out); f.flush()
    print('done', name, len(jobs), flush=True)

def kp(i): return ','.join(map(str, KEYS[i]['perm'])), KEYS[i]['square']

# ---- planted plaintexts: 1918 telegram German (the solved readings, X as stop) ----
READ = open(os.path.join(HERE, 'planted_source.txt')).read().strip()

def encrypt(plain, perm, square):
    """Independent Python encryption (perm = 1-based rank of each column)."""
    pos = {c: i for i, c in enumerate(square)}
    s = ''.join(SYM[pos[c] // 6] + SYM[pos[c] % 6] for c in plain)
    L = len(perm); cols = [s[i::L] for i in range(L)]
    return ''.join(cols[i] for i in sorted(range(L), key=lambda i: perm[i]))

if __name__ == '__main__':
    R = random.Random(20261031)
    if 'A' in WANT:
        pool_run('A_random_keys', [(m, ['rand', m, MSGS[m], 200000, 7]) for m in OPEN + ['p217_DXXXG']])
    if 'B' in WANT:
        jobs = []
        for m in OPEN:
            for L in range(10, 26):
                jobs.append((m, ['free', m + ':real', MSGS[m], L, 1000000, 8, 1000 + L, 0]))
                for s in range(3):
                    jobs.append((m, ['free', m + ':shuf%d' % s, MSGS[m], L, 1000000, 8, 2000 + 100 * s + L, 1]))
        pool_run('B_free_key', jobs)
    if 'P' in WANT:
        jobs, meta = [], []
        for m in OPEN:
            n = len(MSGS[m]) // 2
            for t in range(4):
                a = R.randrange(0, len(READ) - n); plain = READ[a:a + n]
                L = R.randrange(16, 21); perm = list(range(1, L + 1)); R.shuffle(perm)
                sq = list(ALPH); R.shuffle(sq); sq = ''.join(sq)
                ct = encrypt(plain, perm, sq)
                tag = '%s:planted%d' % (m, t)
                meta.append({'tag': tag, 'plain': plain, 'L': L, 'perm': perm, 'square': sq, 'ct': ct})
                jobs.append((tag, ['free', tag, ct, L, 1000000, 8, 3000 + t, 0]))
        json.dump(meta, open(os.path.join(OUT, 'P_planted_meta.json'), 'w'), indent=0)
        pool_run('P_planted', jobs)
    if 'E' in WANT:
        jobs = []
        for m in OPEN:
            for i in range(len(KEYS)):
                p, s = kp(i)
                jobs.append((m, ['edit', '%s:key%d:block:real' % (m, i), MSGS[m], p, s, 10, 16, 1, 1, 0]))
                jobs.append((m, ['edit', '%s:key%d:single:real' % (m, i), MSGS[m], p, s, 10, 16, 0, 1, 0]))
                jobs.append((m, ['edit', '%s:key%d:block:shuf' % (m, i), MSGS[m], p, s, 10, 16, 1, 50 + i, 1]))
            for r in range(10):
                L = R.randrange(10, 26)
                jobs.append((m, ['rkedit', '%s:rand%d:L%d:block' % (m, r, L), MSGS[m], L, 10, 16, 1, 70 + r]))
        for m, i in SOLVED.items():
            p, s = kp(i)
            jobs.append((m, ['edit', '%s:key%d:block:truekey' % (m, i), MSGS[m], p, s, 10, 16, 1, 1, 0]))
            jobs.append((m, ['edit', '%s:key%d:single:truekey' % (m, i), MSGS[m], p, s, 10, 16, 0, 1, 0]))
        pool_run('E_edits', jobs)
    if 'FE' in WANT:
        jobs = []
        for m in OPEN:
            for L in (16, 19):
                jobs.append((m, ['fedit', '%s:L%d:real' % (m, L), MSGS[m], L, 10, 300000, 4, 1, 400 + L, 0]))
                jobs.append((m, ['fedit', '%s:L%d:shuf' % (m, L), MSGS[m], L, 10, 300000, 4, 1, 500 + L, 1]))
        pool_run('FE_free_edits', jobs)
    if 'T' in WANT:
        tp = ','.join(map(str, keyword_perm('TRUPPENVERSCHIEBUNG')))
        jobs = []
        for m in OPEN:
            jobs.append((m, ['fsq', m + ':TRUPPEN:real', MSGS[m], tp, 1000000, 8, 600, 0]))
            for s in range(3):
                jobs.append((m, ['fsq', m + ':TRUPPEN:shuf%d' % s, MSGS[m], tp, 1000000, 8, 700 + s, 1]))
        pool_run('T_truppen_free_square', jobs)
