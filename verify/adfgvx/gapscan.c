/* check-adfgvx: R2 gap scan with MASKING (prereg C3).  For a ciphertext ct (symbols 0..5), a key (ranks, width w) and a
   square (cls[36]: letter class 0..26 or -1 for an unknown cell), insert L unknown symbols at position g of the log,
   decrypt, MASK every letter that has an unknown symbol or an unknown cell, and score the quadgrams that lie entirely
   in unmasked letters.  Output for each (L,g): total log10 and number of quadgrams. */
#include <stdlib.h>
#include <string.h>
#define V 27
int gap_eval(const unsigned char*ct,int n0,int L,int g,const int*trans,int w,const int*cls,const float*lp,double*tot,int*nq,int*nmasked){
  int n=n0+L; unsigned char s[1024];
  for(int i=0;i<g;i++) s[i]=ct[i]; for(int i=0;i<L;i++) s[g+i]=6; for(int i=g;i<n0;i++) s[L+i]=ct[i];
  int order[64]; for(int i=0;i<w;i++) order[i]=i;
  for(int a=1;a<w;a++){ int v=order[a],b=a-1; while(b>=0&&trans[order[b]]>trans[v]){order[b+1]=order[b];b--;} order[b+1]=v; }
  unsigned char tmp[1024]; int q=n/w,r=n%w,off=0;
  for(int k=0;k<w;k++){ int pos=order[k]; int Lc=q+(pos<r?1:0); for(int row=0;row<Lc;row++) tmp[row*w+pos]=s[off++]; }
  int let[512]; int nl=n/2; int masked=0;
  for(int i=0;i<nl;i++){ int a=tmp[2*i],b=tmp[2*i+1]; if(a>5||b>5){let[i]=-1;masked++;} else { int c=cls[a*6+b]; let[i]=c; if(c<0) masked++; } }
  double t=0; int c4=0;
  for(int i=3;i<nl;i++){ int a=let[i-3],b=let[i-2],c=let[i-1],d=let[i]; if((a|b|c|d)<0) continue; t+=lp[((a*V+b)*V+c)*V+d]; c4++; }
  *tot=t; *nq=c4; *nmasked=masked; return nl;
}
/* scan: for L in 0..Lmax, g in 0..n0: out[(L*(n0+1)+g)*3+{0,1,2}] = total, nq, nmasked */
void gap_scan(const unsigned char*ct,int n0,int Lmax,const int*trans,int w,const int*cls,const float*lp,double*out){
  for(int L=0;L<=Lmax;L++) for(int g=0;g<=n0;g++){
    double t; int nq,nm; gap_eval(ct,n0,L,g,trans,w,cls,lp,&t,&nq,&nm);
    double*o=out+((size_t)L*(n0+1)+g)*3; o[0]=t; o[1]=nq; o[2]=nm; }
}
