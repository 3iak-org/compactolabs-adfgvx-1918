from r2ref import *
from multiprocessing import Pool
import random,json
def job(a):
    rid,kid=a; k=KEYS[kid]; b=grid(REC[rid]['printed'],k['transposition'],k['square']); return (b[0],rid,kid,b[1])
if __name__=='__main__':
    sol=[r for r in REC.values() if r['plaintext'] and r['key'] in KEYS and r['key']!='nov10' and 200<=len(r['printed'])<=250 and '-' not in r['printed'] and '?' not in r['printed']]
    sol.sort(key=lambda r:r['id']); random.seed(1); random.shuffle(sol); sol=sol[:12]
    tasks=[(r['id'],kid) for r in sol for kid in KEYS if kid!=r['key']]
    with Pool(7) as p: res=p.map(job,tasks)
    ok=[x for x in res if x[0]>-9]; ok.sort(reverse=True)
    json.dump({'entries':[r['id'] for r in sol],'n_tasks':len(tasks),'n_valid':len(ok),'top5':ok[:5]},open('r2null.json','w'),indent=0)
