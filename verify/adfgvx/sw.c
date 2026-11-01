/* check-adfgvx: Smith-Waterman local alignment score, linear gaps.  Symbols 0..5; 6 = unreadable
   (scores 0 against anything).  match +2, mismatch -2, gap -3. */
#include <stdlib.h>
int sw_score(const unsigned char*a,int n,const unsigned char*b,int m){
  int *prev=calloc(m+1,sizeof(int)),*cur=calloc(m+1,sizeof(int)); int best=0;
  for(int i=1;i<=n;i++){
    cur[0]=0;
    for(int j=1;j<=m;j++){
      int s; if(a[i-1]==6||b[j-1]==6) s=0; else s=(a[i-1]==b[j-1])?2:-2;
      int v=prev[j-1]+s; int u=prev[j]-3; if(u>v)v=u; u=cur[j-1]-3; if(u>v)v=u; if(v<0)v=0;
      cur[j]=v; if(v>best)best=v;
    }
    int*t=prev;prev=cur;cur=t;
  }
  free(prev);free(cur); return best;
}
