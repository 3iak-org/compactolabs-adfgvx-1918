# referee's own ADFGVX: written from the cipher's definition, no code from the branch.
import json
D='/tmp/gp-scratch/ciphers/ref-adfgvx/lead/ciphertexts/'
REC={r['id']:r for r in json.load(open(D+'adfgvx-1918-log.records.json'))}
KEYS={k['id']:k for k in json.load(open(D+'adfgvx-1918-log.keys.json'))}
L='ADFGVX'
def untranspose(ct,key,conv):
    """ct: list of symbols (may include '-' placeholders). Returns intermediate (row-wise) list."""
    k=len(key); n=len(ct); rows,rem=divmod(n,k)
    collen=[rows+(1 if c<rem else 0) for c in range(k)]
    if conv=='rank':   # key[c] = position (1-based) at which column c is read
        order=sorted(range(k),key=lambda c:key[c])
    else:              # key[j] = column (1-based) read j-th
        order=[x-1 for x in key]
    cols=[None]*k; p=0
    for c in order:
        cols[c]=ct[p:p+collen[c]]; p+=collen[c]
    out=[]
    for r in range(rows+1):
        for c in range(k):
            if r<collen[c]: out.append(cols[c][r])
    return out
def sub(inter,sq):
    s=[]
    for i in range(0,len(inter)-1,2):
        a,b=inter[i],inter[i+1]
        if a not in L or b not in L: s.append('-'); continue
        s.append(sq[L.index(a)*6+L.index(b)])
    return ''.join(s)
def dec(ct,key,sq,conv):
    return sub(untranspose(list(ct),key,conv),sq)
