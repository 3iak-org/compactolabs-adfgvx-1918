/* fake.c - adversary search engine for ADFGVX false readings.
 *
 * Builds a German quadgram model from a normalised corpus (A-Z0-9, X = stop) and searches for
 * the most German-looking decryption of a ciphertext under one of these freedoms:
 *
 *   free   : transposition (length L) AND 6x6 square both free  (joint simulated annealing)
 *   fsq    : transposition fixed, square free
 *   edit   : key fixed (square may contain '-' cells, which are free), plus up to K edits to the
 *            ciphertext, found by beam search.  Edit ops ("single" set): delete 1, insert 1 (any of
 *            6 symbols), substitute 1.  "block" set adds: delete a block of 2-5, insert a block of
 *            2-5 (content by coordinate ascent from a copy of the preceding symbols = duplication),
 *            swap two adjacent 5-blocks.  Each op counts as one edit.
 *   fedit  : free key AND up to K edits (alternate: one edit step with key fixed, re-anneal key).
 *   rand   : score of decryptions under uniformly random keys (null (a)).
 *
 * Score = mean log10 quadgram probability per quadgram of the plaintext (higher = more German).
 * Transposition convention: perm[i] (1-based) = rank at which column i is read out (Bourdeau's
 * "second" convention; checked here on the solved messages, see adfgvx.md).
 *
 * Build: gcc -O3 -march=native -o fake fake.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define A 36
#define AQ 37  /* 36 letters + unknown (36) */
#define Q4 (AQ*AQ*AQ*AQ)
#define QI(a,b,c,d) ((((a)*AQ+(b))*AQ+(c))*AQ+(d))
static float *QG;
static const char *ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?";
static const char *SYM = "ADFGVX";

/* ---------- rng ---------- */
static uint64_t rs = 88172645463325252ULL;
static inline uint64_t xr(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline int rint_(int n){ return (int)(xr() % (uint64_t)n); }
static inline double runif(void){ return (xr() >> 11) * (1.0/9007199254740992.0); }

static int cidx(int c){ if(c>='A'&&c<='Z') return c-'A'; if(c>='0'&&c<='9') return 26+c-'0'; return -1; }
static int sidx(int c){ if(c=='?') return 6; const char*p=strchr(SYM,c); return (p&&c)?(int)(p-SYM):-1; }

static void load_model(const char *fn){
    FILE *f=fopen(fn,"rb"); if(!f){perror(fn);exit(1);}
    fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET);
    char *t=malloc(n+1); if(fread(t,1,n,f)!=(size_t)n){perror("read");exit(1);} fclose(f);
    double *cnt=calloc(Q4,sizeof(double)); long tot=0;
    int a=-1,b=-1,c=-1;
    for(long i=0;i<n;i++){ int d=cidx(t[i]); if(d<0) continue;
        if(a>=0){ cnt[QI(a,b,c,d)]+=1; tot++; } a=b; b=c; c=d; }
    QG=malloc(Q4*sizeof(float));
    double fl=log10(0.01/tot);
    for(int i=0;i<Q4;i++){ int x=i, unk=0; for(int u=0;u<4;u++){ if(x%AQ==36) unk=1; x/=AQ; } QG[i]= unk?0.0f: cnt[i]>0 ? (float)log10(cnt[i]/tot) : (float)fl; }
    free(cnt); free(t);
}

static inline double qsum(const int *p,int n){ double s=0; for(int i=0;i+3<n;i++) s+=QG[QI(p[i],p[i+1],p[i+2],p[i+3])]; return s; }
static inline int qcount(const int *p,int n){ int c=0; for(int i=0;i+3<n;i++) c+=(p[i]!=36&&p[i+1]!=36&&p[i+2]!=36&&p[i+3]!=36); return c; }
static inline double qmean(const int *p,int n){ int c=qcount(p,n); return c>0? qsum(p,n)/c : -99; }

/* ---------- ADFGVX decryption ---------- */
/* ct: symbols 0..5, length N. perm: 0-based rank of column i. out pairs: 0..35, returns count */
static int untrans(const int *ct,int N,const int *perm,int L,int *pairs){
    static int col_of_rank[64], start[64], len[64]; static int buf[4096];
    for(int i=0;i<L;i++) col_of_rank[perm[i]]=i;
    int base=N/L, ext=N%L;
    for(int i=0;i<L;i++) len[i]=base+(i<ext);
    int pos=0; for(int r=0;r<L;r++){ int c=col_of_rank[r]; start[c]=pos; pos+=len[c]; }
    for(int j=0;j<N;j++){ int c=j%L, r=j/L; buf[j]=ct[start[c]+r]; }
    int n=N/2; for(int k=0;k<n;k++) pairs[k]=(buf[2*k]==6||buf[2*k+1]==6)?36:buf[2*k]*6+buf[2*k+1];
    return n;
}

/* several messages under one key: pair streams joined by 3 unknown pairs (no cross-part quadgrams) */
static int NP=0, PN[16]; static int *PCT[16];
static int untrans_all(const int *perm,int L,int *pairs){
    int n=0; for(int q=0;q<NP;q++){ if(q){ for(int u=0;u<3;u++) pairs[n++]=36; } n+=untrans(PCT[q],PN[q],perm,L,pairs+n); } return n; }
/* ---------- free-square solver for a given pair stream (SA with delta scoring) ---------- */
typedef struct { int n; int pairs[2048]; int p[2048]; int sub[A]; int *pos[AQ]; int cnt[AQ]; int posbuf[2048]; } St;
static void st_index(St *s){
    memset(s->cnt,0,sizeof s->cnt);
    for(int k=0;k<s->n;k++) s->cnt[s->pairs[k]]++;
    int o=0; for(int a=0;a<AQ;a++){ s->pos[a]=s->posbuf+o; o+=s->cnt[a]; s->cnt[a]=0; }
    for(int k=0;k<s->n;k++){ int a=s->pairs[k]; s->pos[a][s->cnt[a]++]=k; }
    for(int k=0;k<s->n;k++) s->p[k]=s->pairs[k]==36?36:s->sub[s->pairs[k]];
}
static int stamp[2048], stampv=1;
static double swap_delta(St *s,int a,int b){ /* applies swap of sub[a],sub[b]; returns delta of qsum */
    stampv++; double old=0, nw=0; int idx[512], m=0; int n=s->n;
    for(int t=0;t<2;t++){ int x=t?b:a; for(int u=0;u<s->cnt[x];u++){ int j=s->pos[x][u];
        for(int q=j-3;q<=j;q++){ if(q<0||q+3>=n) continue; if(stamp[q]==stampv) continue; stamp[q]=stampv; if(m<512) idx[m++]=q; } } }
    for(int i=0;i<m;i++){ int q=idx[i]; const int*p=s->p+q; old+=QG[QI(p[0],p[1],p[2],p[3])]; }
    int t_=s->sub[a]; s->sub[a]=s->sub[b]; s->sub[b]=t_;
    for(int u=0;u<s->cnt[a];u++) s->p[s->pos[a][u]]=s->sub[a];
    for(int u=0;u<s->cnt[b];u++) s->p[s->pos[b][u]]=s->sub[b];
    for(int i=0;i<m;i++){ int q=idx[i]; const int*p=s->p+q; nw+=QG[QI(p[0],p[1],p[2],p[3])]; }
    return nw-old;
}
static void freq_init(St *s){ /* most frequent pair -> E, etc. (German order incl X) */
    static const char *ord="ENIRSTADUHXGLOCMBFWKZPV1J2Y03Q456789";
    int cnt[AQ]={0}, idx[A]; for(int k=0;k<s->n;k++) cnt[s->pairs[k]]++;
    for(int i=0;i<A;i++) idx[i]=i;
    for(int i=0;i<A;i++) for(int j=i+1;j<A;j++) if(cnt[idx[j]]>cnt[idx[i]]||(cnt[idx[j]]==cnt[idx[i]]&&runif()<0.5)){int t=idx[i];idx[i]=idx[j];idx[j]=t;}
    for(int i=0;i<A;i++) s->sub[idx[i]]=cidx(ord[i]);
}
static double hc_sub(St *s,double cur){ /* greedy swaps until no improvement */
    int improved=1; while(improved){ improved=0;
        for(int a=0;a<A;a++) for(int b=a+1;b<A;b++){ if(!s->cnt[a]&&!s->cnt[b]) continue;
            double d=swap_delta(s,a,b); if(d>1e-9){ cur+=d; improved=1; } else swap_delta(s,a,b); } }
    return cur;
}

/* stage 1: transposition by hill-climbing the pair index of coincidence (substitution-free).
   IC = sum over the 36 pair values of c(c-1); unknown pairs ignored. */
static int pair_ic(const int *perm,int L){ static int pairs[2048]; int n=untrans_all(perm,L,pairs); int c[AQ]={0};
    for(int k=0;k<n;k++) c[pairs[k]]++; int s=0; for(int a=0;a<A;a++) s+=c[a]*(c[a]-1); return s; }
static void perm_move(int *perm,int L){ int i=rint_(L), j=rint_(L); while(j==i) j=rint_(L);
    double u=runif();
    if(u<0.5){ int t=perm[i];perm[i]=perm[j];perm[j]=t; }
    else { int ri=perm[i], rj=perm[j];   /* move column i to read-out rank rj, shifting the others */
        for(int c=0;c<L;c++){ if(ri<rj){ if(perm[c]>ri&&perm[c]<=rj) perm[c]--; } else { if(perm[c]>=rj&&perm[c]<ri) perm[c]++; } }
        perm[i]=rj; } }
static double IC_T0=8.0;
static int ic_search(int L,int *perm,int steps){
    for(int i=0;i<L;i++) perm[i]=i; for(int i=L-1;i>0;i--){int j=rint_(i+1);int t=perm[i];perm[i]=perm[j];perm[j]=t;}
    int cur=pair_ic(perm,L), best=cur, bp[64]; memcpy(bp,perm,L*sizeof(int)); int op[64];
    for(int it=0;it<steps;it++){ memcpy(op,perm,L*sizeof(int)); perm_move(perm,L);
        double T=IC_T0*(1.0-(double)it/steps)+0.05;
        int v=pair_ic(perm,L); if(v>=cur || runif()<exp((v-cur)/T)){ cur=v; if(v>best){best=v; memcpy(bp,perm,L*sizeof(int));} } else memcpy(perm,op,L*sizeof(int)); }
    memcpy(perm,bp,L*sizeof(int)); return best; }

/* stage 2: substitution by simulated annealing with delta scoring, perm fixed */
static double sa_sub(St *s,int iters,int warm,double T0){
    if(!warm) freq_init(s); st_index(s); double cur=qsum(s->p,s->n), best=cur; int bsub[A]; memcpy(bsub,s->sub,sizeof bsub);
    for(int it=0;it<iters;it++){ double T=T0*(1.0-(double)it/iters)+1e-3;
        int a=rint_(A), b=rint_(A); if(a==b||(!s->cnt[a]&&!s->cnt[b])) continue;
        double d=swap_delta(s,a,b);
        if(d>=0 || runif()<exp(d/T)){ cur+=d; if(cur>best+1e-9){ best=cur; memcpy(bsub,s->sub,sizeof bsub);} } else swap_delta(s,a,b); }
    memcpy(s->sub,bsub,sizeof bsub); st_index(s); return hc_sub(s,qsum(s->p,s->n)); }

/* phase 2: with the square fixed, hill-climb the column order on the German score
   (rank swaps, rank moves, and swaps of adjacent-column pairs, which leave the pair IC unchanged) */
static double perm_hc_fixedsub(St *s,int *perm,int L){
    s->n=untrans_all(perm,L,s->pairs); st_index(s); double cur=qsum(s->p,s->n); int op[64];
    int improved=1; while(improved){ improved=0;
        for(int mv=0;mv<3;mv++) for(int i=0;i<L;i++) for(int j=0;j<L;j++){ if(i==j) continue;
            memcpy(op,perm,L*sizeof(int));
            if(mv==0){ if(j<i) continue; int t=perm[i];perm[i]=perm[j];perm[j]=t; }
            else if(mv==1){ int ri=perm[i], rj=perm[j];
                for(int c=0;c<L;c++){ if(ri<rj){ if(perm[c]>ri&&perm[c]<=rj) perm[c]--; } else { if(perm[c]>=rj&&perm[c]<ri) perm[c]++; } }
                perm[i]=rj; }
            else { if((i&1)||(j&1)||j<i||i+1>=L||j+1>=L) continue; int t=perm[i];perm[i]=perm[j];perm[j]=t; t=perm[i+1];perm[i+1]=perm[j+1];perm[j+1]=t; }
            s->n=untrans_all(perm,L,s->pairs); for(int k=0;k<s->n;k++) s->p[k]=s->pairs[k]==36?36:s->sub[s->pairs[k]];
            double v=qsum(s->p,s->n); if(v>cur+1e-9){ cur=v; improved=1; } else memcpy(perm,op,L*sizeof(int)); } }
    s->n=untrans_all(perm,L,s->pairs); st_index(s); return cur; }

static int IC_STEPS=200000; static int last_ic=0; static int ROUNDS=3;
/* restarts x (IC transposition search, unless fixperm) x (substitution SA). returns best mean score */
static double solve_free(int L,int *perm,int *sub,int iters,int restarts,int fixperm,const int *perm0){
    St *s=malloc(sizeof(St)); double best=-1e9; int bperm[64], bsub[A];
    for(int r=0;r<restarts;r++){
        int ic;
        if(fixperm){ memcpy(perm,perm0,L*sizeof(int)); ic=pair_ic(perm,L); } else ic=ic_search(L,perm,IC_STEPS);
        s->n=untrans_all(perm,L,s->pairs);
        double tot=sa_sub(s,iters,0,0.6);
        for(int rd=0;rd<ROUNDS && !fixperm;rd++){ perm_hc_fixedsub(s,perm,L); tot=sa_sub(s,iters/4,1,0.25); }
        int kc=qcount(s->p,s->n); double m=kc>0?tot/kc:-99;
        if(m>best){ best=m; last_ic=ic; memcpy(bperm,perm,L*sizeof(int)); memcpy(bsub,s->sub,sizeof bsub); }
    }
    memcpy(perm,bperm,L*sizeof(int)); memcpy(sub,bsub,A*sizeof(int)); free(s); return best;
}

/* ---------- fixed key decrypt+score ---------- */
static int decrypt_fixed(const int *ct,int N,const int *perm,int L,const int *sub,int *p){
    static int pairs[2048]; int n=untrans(ct,N,perm,L,pairs); for(int k=0;k<n;k++) p[k]=pairs[k]==36?36:sub[pairs[k]]; return n; }
static double score_fixed(const int *ct,int N,const int *perm,int L,const int *sub){
    static int p[2048]; int n=decrypt_fixed(ct,N,perm,L,sub,p); return qmean(p,n); }

/* fill free square cells ('-') by hill climbing among themselves */
static int nfree, freecell[A];
static double fill_free(const int *ct,int N,const int *perm,int L,int *sub,int passes){
    double cur=score_fixed(ct,N,perm,L,sub);
    for(int ps=0;ps<passes;ps++){ int imp=0;
        for(int i=0;i<nfree;i++) for(int j=i+1;j<nfree;j++){ int a=freecell[i], b=freecell[j];
            int t=sub[a];sub[a]=sub[b];sub[b]=t; double s=score_fixed(ct,N,perm,L,sub);
            if(s>cur+1e-12){cur=s;imp=1;} else {t=sub[a];sub[a]=sub[b];sub[b]=t;} }
        if(!imp) break; }
    return cur;
}

/* ---------- edit beam search ---------- */
typedef struct { int N; unsigned char ct[2100]; double sc; char log[600]; int sub[A]; } ES;
static void es_get(const ES*e,int*o){ for(int i=0;i<e->N;i++) o[i]=e->ct[i]; }
static void es_put(ES*e,const int*c,int N){ e->N=N; for(int i=0;i<N;i++) e->ct[i]=(unsigned char)c[i]; }
static int cmp_es(const void*a,const void*b){ double x=((ES*)a)->sc, y=((ES*)b)->sc; return x<y?1:x>y?-1:0; }
static ES *cand; static int ncand, capcand;
static void push_cand(const ES *base,const int *ct,int N,double sc,const char *op){
    if(ncand>=capcand){ /* keep the best half */ qsort(cand,ncand,sizeof(ES),cmp_es); ncand=capcand/2; }
    ES *e=&cand[ncand++]; es_put(e,ct,N); e->sc=sc; memcpy(e->sub,base->sub,sizeof e->sub);
    snprintf(e->log,sizeof e->log,"%s%s%s",base->log,base->log[0]?" ":"",op);
}
static void expand(const ES *b,const int *perm,int L,int block){
    static int t[2100], bc[2100]; int N=b->N; char op[64]; const int *sub=b->sub; es_get(b,bc);
    for(int i=0;i<N;i++){ /* substitute */
        memcpy(t,bc,N*sizeof(int));
        for(int s=0;s<6;s++){ if(s==bc[i]) continue; t[i]=s; snprintf(op,64,"S%d:%c",i,SYM[s]); push_cand(b,t,N,score_fixed(t,N,perm,L,sub),op); }
    }
    int mmax=block?5:1;
    for(int m=1;m<=mmax;m++) for(int i=0;i+m<=N;i++){ /* delete m at i */
        memcpy(t,bc,i*sizeof(int)); memcpy(t+i,bc+i+m,(N-i-m)*sizeof(int));
        snprintf(op,64,"D%d:%d",i,m); push_cand(b,t,N-m,score_fixed(t,N-m,perm,L,sub),op); }
    for(int m=1;m<=mmax;m++) for(int i=0;i<=N;i++){ /* insert m at i */
        memcpy(t,bc,i*sizeof(int)); memcpy(t+i+m,bc+i,(N-i)*sizeof(int)); int M=N+m;
        for(int u=0;u<m;u++) t[i+u]= (i-m+u>=0)? bc[i-m+u] : 0; /* duplicate preceding */
        double cur=score_fixed(t,M,perm,L,sub);
        for(int ps=0;ps<(m==1?1:2);ps++) for(int u=0;u<m;u++){ int keep=t[i+u];
            for(int s=0;s<6;s++){ if(s==keep) continue; int o=t[i+u]; t[i+u]=s; double sc=score_fixed(t,M,perm,L,sub);
                if(sc>cur){cur=sc; keep=s;} else t[i+u]=o; } t[i+u]=keep; }
        char c[8]; for(int u=0;u<m;u++) c[u]=SYM[t[i+u]]; c[m]=0;
        snprintf(op,64,"I%d:%s",i,c); push_cand(b,t,M,cur,op); }
    if(block) for(int i=0;i+10<=N;i++){ memcpy(t,bc,N*sizeof(int));
        for(int u=0;u<5;u++){ int x=t[i+u]; t[i+u]=t[i+5+u]; t[i+5+u]=x; }
        snprintf(op,64,"W%d",i); push_cand(b,t,N,score_fixed(t,N,perm,L,sub),op); }
}
static void print_plain(const int *ct,int N,const int *perm,int L,const int *sub){
    static int p[2048]; int n=decrypt_fixed(ct,N,perm,L,sub,p); for(int k=0;k<n;k++) putchar(ALPH[p[k]]); }
static void print_key(const int *perm,int L,const int *sub){
    printf("perm="); for(int i=0;i<L;i++) printf("%d%s",perm[i]+1,i<L-1?",":"");
    printf(" square="); for(int a=0;a<A;a++) putchar(ALPH[sub[a]]); }

static void edit_search(const int *ct0,int N0,const int *perm,int L,const int *sub0,int K,int beam,int block,const char *tag){
    capcand=120000; cand=malloc(sizeof(ES)*capcand);
    ES *bm=malloc(sizeof(ES)*beam); int nb=1;
    es_put(&bm[0],ct0,N0); memcpy(bm[0].sub,sub0,sizeof bm[0].sub); bm[0].log[0]=0;
    bm[0].sc= nfree? fill_free(ct0,N0,perm,L,bm[0].sub,4) : score_fixed(ct0,N0,perm,L,sub0);
    double bestsofar=bm[0].sc;
    printf("%s k=0 score=%.4f N=%d edits=- ",tag,bm[0].sc,N0); print_key(perm,L,bm[0].sub); printf(" plain="); print_plain(ct0,N0,perm,L,bm[0].sub); printf("\n"); fflush(stdout);
    for(int k=1;k<=K;k++){
        ncand=0; for(int b=0;b<nb;b++) expand(&bm[b],perm,L,block);
        qsort(cand,ncand,sizeof(ES),cmp_es);
        nb=0; for(int c=0;c<ncand&&nb<beam;c++){ int dup=0; for(int b=0;b<nb;b++) if(bm[b].N==cand[c].N&&!memcmp(bm[b].ct,cand[c].ct,cand[c].N)){dup=1;break;} if(!dup) bm[nb++]=cand[c]; }
        if(nfree) for(int b=0;b<nb;b++){ int tc[2100]; es_get(&bm[b],tc); bm[b].sc=fill_free(tc,bm[b].N,perm,L,bm[b].sub,3); }
        qsort(bm,nb,sizeof(ES),cmp_es);
        if(bm[0].sc>bestsofar) bestsofar=bm[0].sc;
        printf("%s k=%d score=%.4f N=%d edits=%s ",tag,k,bm[0].sc,bm[0].N,bm[0].log); print_key(perm,L,bm[0].sub); printf(" plain="); { int tc[2100]; es_get(&bm[0],tc); print_plain(tc,bm[0].N,perm,L,bm[0].sub); } printf("\n"); fflush(stdout);
    }
    free(cand); free(bm);
}

static int parse_ct(const char *s,int *ct){ int N=0; for(;*s;s++){ int v=sidx(*s); if(v>=0) ct[N++]=v; } return N; }
static int parse_perm(const char *s,int *perm){ int L=0; const char*p=s; while(*p){ perm[L++]=atoi(p)-1; while(*p&&*p!=',') p++; if(*p) p++; } return L; }
static void parse_square(const char *s,int *sub){ /* '-' cells free: fill with unused symbols */
    int used[A]={0}; nfree=0;
    for(int a=0;a<A;a++){ int c=cidx(s[a]); if(c>=0&&!used[c]){ sub[a]=c; used[c]=1; } else { sub[a]=-1; freecell[nfree++]=a; } }
    int u=0; for(int a=0;a<A;a++) if(sub[a]<0){ while(used[u]) u++; sub[a]=u; used[u]=1; }
}
static void shuffle_ct(int *ct,int N){ for(int i=N-1;i>0;i--){int j=rint_(i+1);int t=ct[i];ct[i]=ct[j];ct[j]=t;} }

int main(int argc,char**argv){
    if(argc<4){ fprintf(stderr,"usage: fake MODEL MODE ...\n"); return 1; }
    load_model(argv[1]); const char *mode=argv[2]; if(getenv("IC_STEPS")) IC_STEPS=atoi(getenv("IC_STEPS"));
    static int ct[2100], perm[64], sub[A];
    if(!strcmp(mode,"score")){ /* score PLAINTEXT */
        int p[4096], n=0; for(const char*s=argv[3];*s;s++){int c=cidx(*s); if(c>=0) p[n++]=c;} printf("%.4f\n",qmean(p,n)); return 0; }
    if(!strcmp(mode,"dec")){ /* dec CT PERM SQUARE */
        int N=parse_ct(argv[3],ct), L=parse_perm(argv[4],perm); parse_square(argv[5],sub);
        printf("score=%.4f plain=",score_fixed(ct,N,perm,L,sub)); print_plain(ct,N,perm,L,sub); printf("\n"); return 0; }
    if(!strcmp(mode,"free")||!strcmp(mode,"fsq")){
        /* free TAG CT L ITERS RESTARTS SEED SHUFFLE   |  fsq TAG CT PERM ITERS RESTARTS SEED SHUFFLE */
        const char *tag=argv[3]; int N=parse_ct(argv[4],ct); int fix=!strcmp(mode,"fsq"); int L; int perm0[64];
        if(fix) L=parse_perm(argv[5],perm0); else L=atoi(argv[5]);
        int iters=atoi(argv[6]), R=atoi(argv[7]); rs^=strtoull(argv[8],0,10)*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++) xr();
        if(atoi(argv[9])) shuffle_ct(ct,N);
        NP=1; PCT[0]=ct; PN[0]=N; double sc=solve_free(L,perm,sub,iters,R,fix,perm0);
        printf("%s L=%d score=%.4f ic=%d ",tag,L,sc,last_ic); print_key(perm,L,sub); printf(" plain="); print_plain(ct,N,perm,L,sub);
        printf(" ct="); for(int i=0;i<N;i++) putchar(SYM[ct[i]]); printf("\n"); return 0; }
    if(!strcmp(mode,"edit")){
        /* edit TAG CT PERM SQUARE K BEAM BLOCK SEED SHUFFLE */
        const char *tag=argv[3]; int N=parse_ct(argv[4],ct), L=parse_perm(argv[5],perm); parse_square(argv[6],sub);
        int K=atoi(argv[7]), B=atoi(argv[8]), blk=atoi(argv[9]); rs^=strtoull(argv[10],0,10)*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++) xr();
        if(atoi(argv[11])) shuffle_ct(ct,N);
        if(atoi(argv[11])){ printf("%s ct=",tag); for(int i=0;i<N;i++) putchar(SYM[ct[i]]); printf("\n"); }
        edit_search(ct,N,perm,L,sub,K,B,blk,tag); return 0; }
    if(!strcmp(mode,"rkedit")){
        /* rkedit TAG CT L K BEAM BLOCK SEED : random key (random perm of length L, random square) + edits */
        const char *tag=argv[3]; int N=parse_ct(argv[4],ct), L=atoi(argv[5]); int K=atoi(argv[6]), B=atoi(argv[7]), blk=atoi(argv[8]);
        rs^=strtoull(argv[9],0,10)*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++) xr();
        for(int i=0;i<L;i++) perm[i]=i; for(int i=L-1;i>0;i--){int j=rint_(i+1);int t=perm[i];perm[i]=perm[j];perm[j]=t;}
        for(int i=0;i<A;i++) sub[i]=i; for(int i=A-1;i>0;i--){int j=rint_(i+1);int t=sub[i];sub[i]=sub[j];sub[j]=t;}
        nfree=0; edit_search(ct,N,perm,L,sub,K,B,blk,tag); return 0; }
    if(!strcmp(mode,"fedit")){
        /* fedit TAG CT L K ITERS RESTARTS BLOCK SEED SHUFFLE : free key + edits, alternating */
        const char *tag=argv[3]; int N=parse_ct(argv[4],ct), L=atoi(argv[5]); int K=atoi(argv[6]), it=atoi(argv[7]), R=atoi(argv[8]), blk=atoi(argv[9]);
        rs^=strtoull(argv[10],0,10)*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++) xr();
        if(atoi(argv[11])){ shuffle_ct(ct,N); printf("%s ct=",tag); for(int i=0;i<N;i++) putchar(SYM[ct[i]]); printf("\n"); }
        NP=1; PCT[0]=ct; PN[0]=N; double sc=solve_free(L,perm,sub,it,R,0,NULL);
        char log[1200]=""; nfree=0;
        printf("%s k=0 L=%d score=%.4f edits=- ",tag,L,sc); print_key(perm,L,sub); printf(" plain="); print_plain(ct,N,perm,L,sub); printf("\n"); fflush(stdout);
        for(int k=1;k<=K;k++){
            capcand=200000; cand=malloc(sizeof(ES)*capcand); ncand=0;
            ES *b=malloc(sizeof(ES)); es_put(b,ct,N); memcpy(b->sub,sub,sizeof b->sub); strcpy(b->log,log);
            expand(b,perm,L,blk); qsort(cand,ncand,sizeof(ES),cmp_es);
            N=cand[0].N; es_get(&cand[0],ct); strcpy(log,cand[0].log); free(cand); free(b);
            /* re-anneal from current key: fsq with current perm then a short free run seeded at it */
            int p0[64]; memcpy(p0,perm,L*sizeof(int)); int s0[A]; memcpy(s0,sub,sizeof s0);
            double s_keep=score_fixed(ct,N,perm,L,sub);
            PN[0]=N; double s1=solve_free(L,perm,sub,it,R,0,NULL);
            if(s1<s_keep){ memcpy(perm,p0,L*sizeof(int)); memcpy(sub,s0,sizeof s0); s1=s_keep; }
            printf("%s k=%d L=%d score=%.4f edits=%s ",tag,k,L,s1,log); print_key(perm,L,sub); printf(" plain="); print_plain(ct,N,perm,L,sub); printf("\n"); fflush(stdout);
        }
        return 0; }
    if(!strcmp(mode,"jfree")){
        /* jfree TAG CT1,CT2,... L ITERS RESTARTS SEED SHUFFLE : one key for all parts ('?' = unknown symbol) */
        const char *tag=argv[3]; static int store[16][2100]; char *cts=strdup(argv[4]); NP=0;
        for(char *tok=strtok(cts,",");tok;tok=strtok(NULL,",")){ PN[NP]=parse_ct(tok,store[NP]); PCT[NP]=store[NP]; NP++; }
        int L=atoi(argv[5]), iters=atoi(argv[6]), R=atoi(argv[7]); rs^=strtoull(argv[8],0,10)*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++) xr();
        if(atoi(argv[9])) for(int q=0;q<NP;q++) shuffle_ct(PCT[q],PN[q]);
        int fp[64], fix=0; if(argc>10){ fix=1; L=parse_perm(argv[10],fp); }   /* optional fixed transposition */
        double sc=solve_free(L,perm,sub,iters,R,fix,fp);
        printf("%s L=%d score=%.4f ic=%d ",tag,L,sc,last_ic); print_key(perm,L,sub); printf(" plain=");
        for(int q=0;q<NP;q++){ if(q) putchar('|'); print_plain(PCT[q],PN[q],perm,L,sub); }
        printf(" ct="); for(int q=0;q<NP;q++){ if(q) putchar(','); for(int i=0;i<PN[q];i++) putchar(PCT[q][i]==6?'?':SYM[PCT[q][i]]); }
        printf("\n"); return 0; }
    if(!strcmp(mode,"gap")){
        /* gap TAG CT PERM SQUARE M SEED SHUFFLE POS : insert M free symbols at every position (or only POS>=0) */
        const char *tag=argv[3]; int N=parse_ct(argv[4],ct), L=parse_perm(argv[5],perm); parse_square(argv[6],sub);
        int M=atoi(argv[7]); rs^=strtoull(argv[8],0,10)*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++) xr();
        if(atoi(argv[9])) shuffle_ct(ct,N); int only=atoi(argv[10]);
        static int t[2200], bt[2200]; int bsub[A]; double best=-1e9; int bi=-1;
        for(int i=(only>=0?only:0); i<=(only>=0?only:N); i++){
            for(int init=0;init<2;init++){ int s2[A]; memcpy(s2,sub,sizeof s2);
                memcpy(t,ct,i*sizeof(int)); memcpy(t+i+M,ct+i,(N-i)*sizeof(int));
                for(int u=0;u<M;u++) t[i+u]= init? rint_(6) : ((i-M+u>=0)? ct[i-M+u] : 0);
                double cur= nfree? fill_free(t,N+M,perm,L,s2,2) : score_fixed(t,N+M,perm,L,s2);
                for(int ps=0;ps<3;ps++){ for(int u=0;u<M;u++){ int keep=t[i+u];
                    for(int v=0;v<6;v++){ if(v==keep) continue; int o=t[i+u]; t[i+u]=v; double sc=score_fixed(t,N+M,perm,L,s2); if(sc>cur){cur=sc;keep=v;} else t[i+u]=o; } t[i+u]=keep; }
                    if(nfree) cur=fill_free(t,N+M,perm,L,s2,2); }
                if(cur>best){ best=cur; bi=i; memcpy(bt,t,(N+M)*sizeof(int)); memcpy(bsub,s2,sizeof bsub); } } }
        char c[64]; for(int u=0;u<M&&u<63;u++) c[u]=SYM[bt[bi+u]]; c[M<63?M:63]=0;
        printf("%s M=%d score=%.4f N=%d edits=I%d:%s ",tag,M,best,N+M,bi,c); print_key(perm,L,bsub); printf(" plain="); print_plain(bt,N+M,perm,L,bsub);
        printf(" ct="); for(int i=0;i<N;i++) putchar(SYM[ct[i]]); printf("\n"); return 0; }
    if(!strcmp(mode,"ic")){
        /* ic TAG CT1,CT2,... L RESTARTS STEPS SEED SHUFFLE : best pair-IC transposition (substitution-free null) */
        const char *tag=argv[3]; static int store[16][2100]; char *cts=strdup(argv[4]); NP=0;
        for(char *tok=strtok(cts,",");tok;tok=strtok(NULL,",")){ PN[NP]=parse_ct(tok,store[NP]); PCT[NP]=store[NP]; NP++; }
        int L=atoi(argv[5]), R=atoi(argv[6]), steps=atoi(argv[7]); rs^=strtoull(argv[8],0,10)*0x9E3779B97F4A7C15ULL; for(int i=0;i<10;i++) xr();
        if(atoi(argv[9])) for(int q=0;q<NP;q++) shuffle_ct(PCT[q],PN[q]);
        int best=-1, bp[64]; for(int r=0;r<R;r++){ int v=ic_search(L,perm,steps); if(v>best){best=v; memcpy(bp,perm,L*sizeof(int));} }
        printf("%s L=%d ic=%d perm=",tag,L,best); for(int i=0;i<L;i++) printf("%d%s",bp[i]+1,i<L-1?",":""); printf("\n"); return 0; }
    if(!strcmp(mode,"icof")){ /* icof CT1,CT2 PERM : pair IC of a given transposition */
        static int store[16][2100]; char *cts=strdup(argv[3]); NP=0;
        for(char *tok=strtok(cts,",");tok;tok=strtok(NULL,",")){ PN[NP]=parse_ct(tok,store[NP]); PCT[NP]=store[NP]; NP++; }
        int L=parse_perm(argv[4],perm); printf("ic=%d\n",pair_ic(perm,L)); return 0; }
    if(!strcmp(mode,"rand")){
        /* rand TAG CT SAMPLES SEED : random key, L uniform 10..25 */
        const char *tag=argv[3]; int N=parse_ct(argv[4],ct); int S=atoi(argv[5]); rs^=strtoull(argv[6],0,10)*0x9E3779B97F4A7C15ULL;
        double mx=-99, sum=0, ss=0;
        for(int t=0;t<S;t++){ int L=10+rint_(16);
            for(int i=0;i<L;i++) perm[i]=i; for(int i=L-1;i>0;i--){int j=rint_(i+1);int x=perm[i];perm[i]=perm[j];perm[j]=x;}
            for(int i=0;i<A;i++) sub[i]=i; for(int i=A-1;i>0;i--){int j=rint_(i+1);int x=sub[i];sub[i]=sub[j];sub[j]=x;}
            double s=score_fixed(ct,N,perm,L,sub); sum+=s; ss+=s*s; if(s>mx) mx=s; }
        printf("%s rand samples=%d mean=%.4f sd=%.4f max=%.4f\n",tag,S,sum/S,sqrt(ss/S-(sum/S)*(sum/S)),mx); return 0; }
    fprintf(stderr,"bad mode\n"); return 1;
}
