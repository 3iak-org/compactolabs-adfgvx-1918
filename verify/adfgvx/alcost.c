/* check-adfgvx: affine-gap alignment COST only (same recurrence as census.py), for the
   E6 search where hundreds of variants per message are scored.  S: 6-bit masks of allowed
   symbols (63 = anything).  P: symbol index 0..5, or 6 = unreadable (matches anything). */
#include <stdlib.h>
#include <string.h>
#define INF 1e9
static double mn(double a,double b){return a<b?a:b;}
double align_cost(const unsigned char*S,int n,const unsigned char*P,int m,double go,double ge,double sub){
  double *Mp=malloc(sizeof(double)*(m+1)),*Dp=malloc(sizeof(double)*(m+1)),*Ip=malloc(sizeof(double)*(m+1));
  double *Mc=malloc(sizeof(double)*(m+1)),*Dc=malloc(sizeof(double)*(m+1)),*Ic=malloc(sizeof(double)*(m+1));
  Mp[0]=0;Dp[0]=INF;Ip[0]=INF;
  for(int j=1;j<=m;j++){Mp[j]=INF;Dp[j]=INF;Ip[j]=go+ge*j;}
  for(int i=1;i<=n;i++){
    Mc[0]=INF;Dc[0]=go+ge*i;Ic[0]=INF;
    for(int j=1;j<=m;j++){
      int okk=(P[j-1]==6)||((S[i-1]>>P[j-1])&1);
      double c=okk?0:sub;
      Mc[j]=mn(Mp[j-1],mn(Dp[j-1],Ip[j-1]))+c;
      Dc[j]=mn(Mp[j]+go+ge,mn(Dp[j]+ge,Ip[j]+go+ge));
      Ic[j]=mn(Mc[j-1]+go+ge,mn(Ic[j-1]+ge,Dc[j-1]+go+ge));
    }
    double*t;t=Mp;Mp=Mc;Mc=t;t=Dp;Dp=Dc;Dc=t;t=Ip;Ip=Ic;Ic=t;
  }
  double r=mn(Mp[m],mn(Dp[m],Ip[m]));
  free(Mp);free(Dp);free(Ip);free(Mc);free(Dc);free(Ic);
  return r;
}
