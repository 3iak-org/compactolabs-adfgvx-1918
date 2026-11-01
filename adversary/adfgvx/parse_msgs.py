"""Parse the triage ciphertext file into one message per line: NAME SYMBOLS.
Gap marks (- – —) are dropped; lowercase v is read as V; bracketed groups (VVFGD) {VVDAD}
on p.158 are dropped (they look like an operator's repeat) - variant flag --keep-brackets keeps them."""
import sys, re
keep = '--keep-brackets' in sys.argv
lines = open(sys.argv[1], encoding='utf-8').read().split('\n')
msgs, cur, name = [], [], None
seen = {}
pend = None
for ln in lines:
    if ln.startswith('#') or not ln.strip(): continue
    m = re.match(r'^Page\s+(\S+)', ln)
    if m:
        if name: msgs.append((name, ''.join(cur)))
        base = m.group(1)
        seen[base] = seen.get(base, 0) + 1
        name, cur = None, []
        pend = base
        continue
    if pend is None and name is None: continue
    t = ln.strip()
    if not keep: t = re.sub(r'[\(\{][A-Za-z]+[\)\}]', '', t)
    t = re.sub(r'[^ADFGVXadfgvx]', '', t).upper()
    if name is None:
        name = 'p' + pend.replace('?', 'Q') + '_' + t[:5]
        pend = None
    cur.append(t)
if name: msgs.append((name, ''.join(cur)))
for n, s in msgs: print(n, s)
