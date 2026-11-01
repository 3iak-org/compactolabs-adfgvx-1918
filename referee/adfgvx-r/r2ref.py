from adf import *
import math,collections,sys
def norm(p): return ''.join('#' if c.isdigit() else c for c in p if c.isalnum())
train=[norm(r['plaintext']) for r in REC.values() if r['plaintext'] and r['key']!='nov10']
C=collections.Counter(); N=0
for t in train:
    for i in range(len(t)-3): C[t[i:i+4]]+=1; N+=1
V=27**4; base=math.log10(0.5/(N+0.5*V))
def score(p):
    p=norm2(p); s=0;n=0
    for i in range(len(p)-3):
        q=p[i:i+4]
        if '-' in q or '?' in q: continue
        c=C.get(q); s+= math.log10((c+0.5)/(N+0.5*V)) if c else base; n+=1
    return (s/n if n>=40 else None), n
def norm2(p): return ''.join('#' if c.isdigit() else c for c in p)
def grid(ct,key,sq):
    best=(-9,None)
    for Lg in range(21):
        for g in range(len(ct)+1):
            c2=ct[:g]+'-'*Lg+ct[g:]
            if Lg==0 and g>0: break
            sc,n=score(dec(c2,key,sq,'rank'))
            if sc is not None and sc>best[0]: best=(sc,(Lg,g,n))
    return best
if __name__=='__main__':
    ct=REC['p179B1']['printed']; nk=KEYS['nov10']
    print('claim', score(dec(ct[:160]+'-'*20+ct[160:],nk['transposition'],nk['square'],'rank')))
    print('nov10 grid', grid(ct,nk['transposition'],nk['square']))
    res=[]
    for kid,k in KEYS.items():
        if kid=='nov10': continue
        b=grid(ct,k['transposition'],k['square']); res.append((b[0],kid,b[1]))
    res.sort(reverse=True); print('wrong keys top3',res[:3])
    sys.stdout.flush()
    sol=[r for r in REC.values() if r['plaintext'] and r['key'] in KEYS and r['key']!='nov10' and 200<=len(r['printed'])<=250 and '-' not in r['printed'] and '?' not in r['printed']]
    import random; random.seed(1); random.shuffle(sol); sol=sol[:25]
    mx=(-9,)
    for r in sol:
        for kid,k in KEYS.items():
            if kid==r['key']: continue
            b=grid(r['printed'],k['transposition'],k['square'])
            if b[0]>mx[0]: mx=(b[0],r['id'],kid,b[1])
    print('solved-entry wrong-key null over',len(sol),'entries x21: max',mx)
