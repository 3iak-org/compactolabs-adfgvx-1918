from adf import *
def best_ungapped(a,b,minc=40):
    best=(0,0,0)
    for off in range(-len(a)+1,len(b)):
        m=c=0
        for i,x in enumerate(a):
            j=i+off
            if 0<=j<len(b) and x in L and b[j] in L:
                c+=1; m+=(x==b[j])
        if c>=minc and m>best[0]: best=(m,c,off)
    return best
for op,tw in (('p155E','p139B'),('p192A','p188_.2')):
    a=REC[op]['printed']; t=best_ungapped(a,REC[tw]['printed'])
    null=sorted((best_ungapped(a,r['printed'])[0],r['id']) for r in REC.values() if r['id'] not in (op,tw) and r['plaintext'])
    print(op,tw,'twin',t,'null n',len(null),'top',null[-3:])
