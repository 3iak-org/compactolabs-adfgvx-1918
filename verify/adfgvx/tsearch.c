/* check-adfgvx: keyless transposition search, stage 1 (own code).
   Objective: index of coincidence of the interim PAIR stream (36 bins), pooled over the given parts, all parts
   transposed under one common key of width w.  Symbols 0..5; 6 = lost (pair skipped).
   Hill-climb (swap + insertion moves, first improvement, random order) from random starts; keeps the TOPK
   distinct local optima.  Used for R1 (pooled parts 5+6) and for its nulls with the same budget. */
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static uint64_t rs;
static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
#define MAXW 32
#define MAXN 600
static int np_, nlen[8]; static const unsigned char*parts[8]; static int W;
static double ic(const int*key){
  int cnt[36]; memset(cnt,0,sizeof cnt); int N=0;
  int order[MAXW];
  for(int i=0;i<W;i++) order[i]=i;
  for(int a=1;a<W;a++){ int v=order[a],b=a-1; while(b>=0&&key[order[b]]>key[v]){order[b+1]=order[b];b--;} order[b+1]=v; }
  for(int p=0;p<np_;p++){
    int n=nlen[p]; unsigned char tmp[MAXN]; int q=n/W, r=n%W; int off=0;
    for(int k=0;k<W;k++){ int pos=order[k]; int L=q+(pos<r?1:0); for(int row=0;row<L;row++) tmp[row*W+pos]=parts[p][off++]; }
    for(int i=0;i+1<n;i+=2){ if(tmp[i]<6&&tmp[i+1]<6){ cnt[tmp[i]*6+tmp[i+1]]++; N++; } }
  }
  if(N<2) return 0; double s=0; for(int i=0;i<36;i++) s+=(double)cnt[i]*(cnt[i]-1);
  return s/((double)N*(N-1));
}
double ic_key(const int*key){ return ic(key); }
int ic_search(const unsigned char*buf,const int*lens,int nparts,int w,int restarts,uint64_t seed,int topk,int*out_keys,double*out_sc){
  rs=seed*2654435761ULL+88172645463325252ULL; for(int i=0;i<10;i++) rnd();
  np_=nparts; W=w; int off=0; for(int p=0;p<nparts;p++){ nlen[p]=lens[p]; parts[p]=buf+off; off+=lens[p]; }
  int ntop=0;
  for(int r=0;r<restarts;r++){
    int key[MAXW]; for(int i=0;i<w;i++) key[i]=i+1;
    for(int i=w-1;i>0;i--){ int j=rnd()%(i+1); int t=key[i];key[i]=key[j];key[j]=t; }
    double s=ic(key); int improved=1;
    while(improved){
      improved=0;
      for(int a=0;a<w;a++) for(int b=a+1;b<w;b++){
        int t=key[a];key[a]=key[b];key[b]=t; double s2=ic(key);
        if(s2>s+1e-12){s=s2;improved=1;} else {t=key[a];key[a]=key[b];key[b]=t;}
      }
      /* insertion moves: remove position a, reinsert at b (shifting) acting on the key vector */
      for(int a=0;a<w;a++) for(int b=0;b<w;b++){
        if(a==b) continue; int save[MAXW]; memcpy(save,key,sizeof(int)*w);
        int v=key[a];
        if(a<b){ for(int k=a;k<b;k++) key[k]=key[k+1]; key[b]=v; } else { for(int k=a;k>b;k--) key[k]=key[k-1]; key[b]=v; }
        double s2=ic(key);
        if(s2>s+1e-12){s=s2;improved=1;} else memcpy(key,save,sizeof(int)*w);
      }
    }
    /* insert into top list if distinct */
    int dup=0; for(int t=0;t<ntop;t++){ if(memcmp(out_keys+t*w,key,sizeof(int)*w)==0){dup=1;break;} }
    if(dup) continue;
    if(ntop<topk){ memcpy(out_keys+ntop*w,key,sizeof(int)*w); out_sc[ntop]=s; ntop++; }
    else { int m=0; for(int t=1;t<ntop;t++) if(out_sc[t]<out_sc[m]) m=t; if(s>out_sc[m]){ memcpy(out_keys+m*w,key,sizeof(int)*w); out_sc[m]=s; } }
  }
  return ntop;
}
