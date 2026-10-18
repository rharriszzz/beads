"""Batch the same affine hypotheses; no parallel execution or proposal pruning.

Normal equations solve tiny full-rank weighted 3-column affine systems. Singular
systems fall back to the original least-squares formulation. A measured control
compares every retained assignment and numeric prediction to R323's reference.
"""
import numpy as np
from photo2.r323.tracker import STEPS,CONFIG


def valid(B,B0):
    det=B[:,0,0]*B[:,1,1]-B[:,0,1]*B[:,1,0];d0=np.linalg.det(B0)
    norm=np.linalg.norm(B,axis=1);n0=np.linalg.norm(B0,axis=0)
    stretch=norm/n0
    return (det*d0>0)&np.all((stretch>.62)&(stretch<1.5),axis=1)&(abs(det/d0)>.55)&(abs(det/d0)<1.65)&np.all(np.sum(B*B0,axis=1)/(np.maximum(norm*n0,1e-300))>.68,axis=1)


def unique_good(ab,err):
    good=err<2
    same=np.all(ab[:,:,None,:]==ab[:,None,:,:],axis=-1)
    n=ab.shape[1];ii=np.arange(n)
    better=(err[:,None,:]<err[:,:,None])|((err[:,None,:]==err[:,:,None])&(ii[None,None,:]<ii[None,:,None]))
    return good&~np.any(same&better&good[:,None,:],axis=2)


def fit_hypotheses(xy,sigma,weight,B0,ids,rng):
    n=len(xy);diff=xy[None,:,:]-xy[:,None,:];seeds=[]
    for i in range(n):
        near0=np.flatnonzero(np.linalg.norm(diff[i]-B0[:,0],axis=1)<19)
        near1=np.flatnonzero(np.linalg.norm(diff[i]-B0[:,1],axis=1)<19)
        for j in near0:
            for k in near1:
                if len({i,int(j),int(k)})==3:seeds.append((i,np.column_stack([diff[i,j],diff[i,k]])))
    seeds += [(i,B0.copy()) for i in range(n)]
    if len(seeds)>1500:seeds=[seeds[i] for i in rng.choice(len(seeds),1500,replace=False)]
    count=len(seeds)
    if not seeds:return [],0,0
    B=np.array([s[1] for s in seeds]);offset=np.array([xy[s[0]] for s in seeds]);keep=valid(B,B0);B=B[keep];offset=offset[keep]
    if not len(B):return [],count,0
    active=np.ones(len(B),bool);ab=np.zeros((len(B),n,2),int)
    for iteration in range(5):
        ix=np.flatnonzero(active)
        if not len(ix):break
        bi=B[ix];of=offset[ix];det=np.linalg.det(bi)
        inv=np.stack([bi[:,1,1],-bi[:,0,1],-bi[:,1,0],bi[:,0,0]],axis=1).reshape(-1,2,2)/det[:,None,None]
        aa=np.rint(np.einsum('sni,sji->snj',xy[None,:,:]-of[:,None,:],inv)).astype(int);ab[ix]=aa
        pred=np.einsum('sni,sji->snj',aa,bi)+of[:,None,:];err=np.linalg.norm(pred-xy,axis=2)/sigma
        good=unique_good(aa,err);enough=good.sum(1)>=6;active[ix[~enough]]=False
        if not enough.any():continue
        use=ix[enough];aa=aa[enough];err=err[enough];good=good[enough]
        X=np.concatenate([aa,np.ones((*aa.shape[:2],1))],axis=2)
        w=weight*np.exp(-.5*err**2)/sigma**2;w[~good]=0
        A=np.einsum('sni,sn,snj->sij',X,w,X);rhs=np.einsum('sni,sn,nj->sij',X,w,xy)
        full=np.abs(np.linalg.det(A))>1e-14;coef=np.zeros((len(A),3,2))
        coef[full]=np.linalg.solve(A[full],rhs[full])
        for j in np.flatnonzero(~full):coef[j]=np.linalg.lstsq(X[j]*np.sqrt(w[j,:,None]),xy*np.sqrt(w[j,:,None]),rcond=None)[0]
        nb=coef[:,:2,:].transpose(0,2,1);ok=valid(nb,B0);active[use[~ok]]=False
        B[use[ok]]=nb[ok];offset[use[ok]]=coef[ok,2]
    pred=np.einsum('sni,sji->snj',ab,B)+offset[:,None,:];res=np.linalg.norm(pred-xy,axis=2);err=res/sigma;goods=unique_good(ab,err)
    hypotheses={}
    for si in np.flatnonzero(goods.sum(1)>=6):
        good=goods[si];a=ab[si];lookup={tuple(a[i]):i for i in np.flatnonzero(good)};triangles=0;edges=[]
        for i in np.flatnonzero(good):
            for d,f in STEPS.items():
                j=lookup.get((a[i,0]+d[0],a[i,1]+d[1]))
                if j is not None:edges.append((ids[i],ids[j],f))
            triangles+=int((a[i,0]+1,a[i,1]) in lookup and (a[i,0],a[i,1]+1) in lookup)
        if triangles<2:continue
        score=float(np.sum(weight[good]*(1-.25*err[si,good]**2))+.18*triangles)
        accepted=np.flatnonzero(good);norm=a-a[accepted[0]];signature=tuple((ids[i],*norm[i]) for i in accepted)
        h=dict(score=score,basis=B[si].tolist(),offset=offset[si].tolist(),triangles=triangles,
            assignments={ids[i]:dict(ab=a[i].tolist(),predicted_xy=pred[si,i].tolist(),residual_px=float(res[si,i])) for i in accepted},edges=edges)
        if signature not in hypotheses or score>hypotheses[signature]['score']:hypotheses[signature]=h
    return sorted(hypotheses.values(),key=lambda h:-h['score'])[:CONFIG['candidate_limit']],count,len(hypotheses)
