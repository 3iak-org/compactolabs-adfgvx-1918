/* check-adfgvx numerical kernels (own code).
   hc_square : iterated-local-search over the 36 cells of a Polybius square, maximising the
               summed log10 quadgram probability of the decrypted pair stream.
   vit_fill  : exact Viterbi over per-letter candidate sets (quadgram state), returns the best
               total log10 score and the arg-max letters. */
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#define V 27
#define V3 (V*V*V)
static uint64_t rs;
static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static double score_sq(const int8_t*codes,int n,const int*sq,const float*lp){
  double t=0; 
  for(int i=3;i<n;i++){
    int a=codes[i-3],b=codes[i-2],c=codes[i-1],d=codes[i];
    if((a|b|c|d)<0) continue;
    t+=lp[((sq[a]*V+sq[b])*V+sq[c])*V+sq[d]];
  }
  return t;
}
/* sq[36] in/out initial ignored; restarts = number of random starts; kicks = ILS kicks per start */
double hc_square(const int8_t*codes,int n,const float*lp,int restarts,int kicks,uint64_t seed,int*best_sq){
  rs=seed*2654435761ULL+88172645463325252ULL; for(int i=0;i<10;i++) rnd();
  int base[36]; for(int i=0;i<26;i++) base[i]=i; for(int i=26;i<36;i++) base[i]=26;
  double best=-1e300;
  int cur[36],loc[36];
  for(int r=0;r<restarts;r++){
    memcpy(cur,base,sizeof cur);
    for(int i=35;i>0;i--){ int j=rnd()%(i+1); int t=cur[i];cur[i]=cur[j];cur[j]=t; }
    double s=score_sq(codes,n,cur,lp);
    for(int k=0;k<=kicks;k++){
      int improved=1;
      while(improved){
        improved=0;
        for(int a=0;a<35;a++) for(int b=a+1;b<36;b++){
          if(cur[a]==cur[b]) continue;
          int t=cur[a];cur[a]=cur[b];cur[b]=t;
          double s2=score_sq(codes,n,cur,lp);
          if(s2>s+1e-12){ s=s2; improved=1; } else { t=cur[a];cur[a]=cur[b];cur[b]=t; }
        }
      }
      if(s>best){ best=s; memcpy(best_sq,cur,sizeof cur); }
      if(k==kicks) break;
      /* kick from best-of-this-start: 3 random swaps of the best-so-far of this start */
      memcpy(loc,cur,sizeof cur);
      for(int m=0;m<3;m++){ int a=rnd()%36,b=rnd()%36; int t=cur[a];cur[a]=cur[b];cur[b]=t; }
      double s3=score_sq(codes,n,cur,lp);
      /* accept kicked state as new current (random walk of local optima) */
      s=s3; (void)loc;
    }
  }
  return best;
}

/* masks[i]: bit k set = class k allowed at letter i.  Returns best total, fills out[i]. */
double vit_fill(const uint32_t*masks,int n,const float*lp,int*out){
  if(n<4){ for(int i=0;i<n;i++) out[i]=__builtin_ctz(masks[i]); return 0; }
  int *ls[3]; 
  /* candidate lists */
  int *cl=malloc(sizeof(int)*n*V), *cn=malloc(sizeof(int)*n);
  for(int i=0;i<n;i++){ cn[i]=0; for(int k=0;k<V;k++) if(masks[i]>>k&1) cl[i*V+cn[i]++]=k; if(cn[i]==0){ cl[i*V]=0; cn[i]=1; } }
  (void)ls;
  float *dp=malloc(sizeof(float)*V3), *nd=malloc(sizeof(float)*V3);
  /* back[i] : for state (b,c,d) at letter i (i>=3) the best predecessor a ; stored as uint8 */
  uint8_t *back=malloc((size_t)n*V3);
  const float NEG=-1e30f;
  for(int s=0;s<V3;s++) dp[s]=NEG;
  for(int x=0;x<cn[0];x++) for(int y=0;y<cn[1];y++) for(int z=0;z<cn[2];z++){
    int a=cl[x],b=cl[V+y],c=cl[2*V+z]; dp[(a*V+b)*V+c]=0; }
  /* dp index (a,b,c) = last three letters i-2,i-1,i with i=2 initially */
  for(int i=3;i<n;i++){
    for(int s=0;s<V3;s++) nd[s]=NEG;
    for(int xa=0;xa<cn[i-3];xa++){ int a=cl[(i-3)*V+xa];
     for(int xb=0;xb<cn[i-2];xb++){ int b=cl[(i-2)*V+xb];
      for(int xc=0;xc<cn[i-1];xc++){ int c=cl[(i-1)*V+xc];
        float base=dp[(a*V+b)*V+c]; if(base<=NEG/2) continue;
        for(int xd=0;xd<cn[i];xd++){ int d=cl[i*V+xd];
          float v=base+lp[((a*V+b)*V+c)*V+d]; int ni=(b*V+c)*V+d;
          if(v>nd[ni]){ nd[ni]=v; back[(size_t)i*V3+ni]=(uint8_t)a; }
        }}}}
    float*t=dp;dp=nd;nd=t;
  }
  float best=NEG; int bb=0,bc=0,bd=0;
  for(int xb=0;xb<cn[n-3];xb++){ int b=cl[(n-3)*V+xb];
   for(int xc=0;xc<cn[n-2];xc++){ int c=cl[(n-2)*V+xc];
    for(int xd=0;xd<cn[n-1];xd++){ int d=cl[(n-1)*V+xd];
      float v=dp[(b*V+c)*V+d]; if(v>best){best=v;bb=b;bc=c;bd=d;} }}}
  out[n-1]=bd; out[n-2]=bc; out[n-3]=bb;
  int b=bb,c=bc,d=bd;
  for(int i=n-1;i>=3;i--){ int a=back[(size_t)i*V3+(b*V+c)*V+d]; out[i-3]=a; d=c; c=b; b=a; }
  free(cl);free(cn);free(dp);free(nd);free(back);
  return best;
}
