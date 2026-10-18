"""Cyclic finite-state inference, with no finalized geographic charts.

The objective contains unary photo-fit scores, first/second-neighbor overlap
factors, and triple translation-cocycle factors. The first two states are
conditioned exhaustively. Forward/backward DP yields exact max marginals of
this finite objective. No maker or model imports. Integer translations are
relative; the sum around the ring is not constrained to zero.
"""
from collections import Counter
import time
import numpy as np


def overlap(h,k):
    a,b=h['assignments'],k['assignments']; common=sorted(a.keys()&b.keys())
    if len(common)<4:return (0.,None,len(common),0)
    shifts=[(a[o]['ab'][0]-b[o]['ab'][0],a[o]['ab'][1]-b[o]['ab'][1]) for o in common]
    shift,count=Counter(shifts).most_common(1)[0]
    return (.35*count-2.5*(len(common)-count),shift,len(common),count)


def build_factors(windows,cyclic=True):
    hs=[w['hypotheses'] or [dict(score=0.,assignments={})] for w in windows]
    n=len(hs); unary=[np.array([h['score'] for h in hh]) for hh in hs]
    unary=[u-u.max() for u in unary]; pair={}; info={}
    for i in range(n):
        for d in (1,2):
            if not cyclic and i+d>=n:continue
            j=(i+d)%n
            v=[[overlap(h,k) for k in hs[j]] for h in hs[i]]
            pair[i,j]=np.array([[x[0] for x in row] for row in v]);info[i,j]=v
    triple={}
    for i in range(n if cyclic else n-2):
        j,k=(i+1)%n,(i+2)%n
        v=np.zeros((len(hs[i]),len(hs[j]),len(hs[k])))
        for a in range(len(hs[i])):
            for b in range(len(hs[j])):
                x=info[i,j][a][b]
                for c in range(len(hs[k])):
                    y,z=info[j,k][b][c],info[i,k][a][c]
                    if all(t[1] is not None for t in (x,y,z)):
                        residual=sum(abs(x[1][q]+y[1][q]-z[1][q]) for q in (0,1))
                        v[a,b,c]=-2.5*min(residual,4)
        triple[i,j,k]=v
    return hs,unary,pair,triple,info


def solve(windows,cyclic=True,allowance=3.):
    start=time.perf_counter();hs,u,p,t,info=build_factors(windows,cyclic);n=len(hs)
    assert n>=5
    transitions=[None,None]+[u[i][None,None,:]+p[i-1,i][None,:,:]+p[i-2,i][:,None,:]+t[i-2,i-1,i] for i in range(2,n)]
    marg=[np.full(len(x),-np.inf) for x in hs];paths=[];best=-np.inf;chosen=None
    for a in range(len(hs[0])):
        for b in range(len(hs[1])):
            f=[None,np.full((len(hs[0]),len(hs[1])),-np.inf)];f[1][a,b]=u[0][a]+u[1][b]+p[0,1][a,b]
            back=[None,None]
            for i in range(2,n):
                v=f[-1][:,:,None]+transitions[i]
                back.append(np.argmax(v,axis=0));f.append(v.max(axis=0))
            end=np.zeros_like(f[-1])
            if cyclic:
                end+=p[n-1,0][:,a][None,:]+p[n-2,0][:,a][:,None]+p[n-1,1][:,b][None,:]
                end+=t[n-2,n-1,0][:,:,a]+t[n-1,0,1][:,a,b][None,:]
            final=f[-1]+end;v=float(final.max());s,z=np.unravel_index(np.argmax(final),final.shape)
            path=[0]*n;path[-2:]=[int(s),int(z)]
            for i in range(n-1,1,-1):path[i-2]=int(back[i][path[i-1],path[i]])
            if v>best:best=v;chosen=path
            paths.append(dict(score=v,choices=path))
            marg[0][a]=max(marg[0][a],v);marg[1][b]=max(marg[1][b],v)
            future=end
            for i in range(n-1,1,-1):
                marg[i]=np.maximum(marg[i],(f[i]+future).max(axis=0))
                future=(transitions[i]+future[None,:,:]).max(axis=2)
    selected=[np.flatnonzero(m>=best-allowance-1e-9).tolist() if w['hypotheses'] else [] for w,m in zip(windows,marg)]
    bestchoices=[h if w['hypotheses'] else None for w,h in zip(windows,chosen)]
    paths.sort(key=lambda x:-x['score'])
    return dict(method='exact cyclic second-order max-sum DP with translation cocycles' if cyclic else 'exact open second-order max-sum DP',
        score=best,choices=bestchoices,selected=selected,
        max_marginal_gaps=[(best-m).tolist() for m in marg],
        anchor_conditioned_paths=paths[:6],cyclic=cyclic,allowance=allowance,
        states=[len(h) for h in hs],pair_factors=len(p),triple_factors=len(t),
        seconds=time.perf_counter()-start,
        limitation='Exact on retained candidate bank and stated factors; finite proposal pruning and correlated photographic evidence remain.')


def objective(windows,choices,cyclic=True):
    hs,u,p,t,_=build_factors(windows,cyclic)
    return float(sum(x[c] for x,c in zip(u,choices))+sum(v[choices[i],choices[j]] for (i,j),v in p.items())+sum(v[choices[i],choices[j],choices[k]] for (i,j,k),v in t.items()))
