/* semi-global Levenshtein: query a (len n) fully aligned to a substring of b (len m), free ends in b.
   Wildcard symbol 6 matches anything.  Returns min edit distance; *best_end = end position in b. */
#include <stdlib.h>
int semiglobal(const unsigned char*a,int n,const unsigned char*b,int m,int*best_end){
  int*prev=malloc(sizeof(int)*(m+1)),*cur=malloc(sizeof(int)*(m+1));
  for(int j=0;j<=m;j++) prev[j]=0;
  for(int i=1;i<=n;i++){ cur[0]=i;
    for(int j=1;j<=m;j++){ int ok=(a[i-1]==6||b[j-1]==6||a[i-1]==b[j-1]);
      int v=prev[j-1]+(ok?0:1); int u=prev[j]+1; if(u<v)v=u; u=cur[j-1]+1; if(u<v)v=u; cur[j]=v; }
    int*t=prev;prev=cur;cur=t; }
  int best=1<<30,be=0; for(int j=0;j<=m;j++) if(prev[j]<best){best=prev[j];be=j;}
  *best_end=be; free(prev);free(cur); return best;
}
/* best ungapped offset: max matches of a against any window of b (both directions overlapping), counting only known pairs */
int best_hamming(const unsigned char*a,int n,const unsigned char*b,int m,int*best_off,int*best_cmp){
  int best=-1; *best_off=0; *best_cmp=0;
  for(int off=-(n-1);off<=m-1;off++){ int match=0,cmp=0;
    for(int i=0;i<n;i++){ int j=i+off; if(j<0||j>=m) continue; if(a[i]==6||b[j]==6) continue; cmp++; if(a[i]==b[j]) match++; }
    if(cmp>=40 && match>best){best=match;*best_off=off;*best_cmp=cmp;} }
  return best;
}
