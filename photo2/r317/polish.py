"""Small measured Jacobian/trust-region experiment with simultaneous preservation.

Numerical finite differences use feasible states only. Unavailable columns are
reported, not silently zeroed. No derivative gate rejects a discrete hypothesis.
"""
import time
from copy import deepcopy
import numpy as np
from scipy.optimize import linprog
from photo2.r297.common import read,save,digest,utc
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r316.renderer import RayLayers
from . import search
from .search import OUT,vals,merit,vector
from .model import Chain
from .refine import rank,admissible

def score(r):
    if not r['feasible']:return (1e6,1e6)
    a=vals(r,'A');z=np.maximum(0,np.array([.87,.85,.80,.79,.80,.79])-a)/np.array([.05,.025,.10,.04,.10,.025])
    old=rank(r);return (max(float(z.max()),old[0]),float(np.square(z).mean())+old[1])
def output(r):
    return np.r_[vals(r,'A'),*[r[k]['vector'][q] for k in ['development','comparison'] for q in ['paper','omission','seam','worst']],*[r['brackets'][k]['p95'] for k in ['development','comparison']]]
def main():
    start=time.monotonic();end=time.time()+180;data=load()[0];e=engine();search.Chain=Chain;rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];n0=len(rows);seen={digest(r['parameters']):r for r in rows};cache=RayLayers();matrices=[]
    fields=[(key,i,step) for key,step in [('compact_phase',.025),('compact_spacing',.002),('compact_tilt',2.),('compact_cant',2.)] for i in range(3)]
    def trial(p,stage):
        if time.time()>end:raise TimeoutError
        h=digest(p)
        if h in seen:return seen[h]
        t=time.monotonic()
        try:r,s,tr=search.evaluate(p,data,e,cache)
        except ValueError as ex:r=dict(parameters=p,feasible=False,classification='exploration-bound',reason=str(ex))
        r.update(id=len(rows),stage=stage,hypothesis='A',seconds=time.monotonic()-t)
        if 'physical' in r:r['physical'].pop('witnesses',None)
        save(OUT/'trials'/f'{r["id"]:05d}.json.gz',r);rows.append(r);seen[h]=r
        if len(rows)%10==0:print(r['id'],stage,r['classification'],score(r),flush=True)
        return r
    def perturb(p,col,amount):
        p=deepcopy(p);key,i,step=fields[col];p[key]=list(p.get(key,[0]*len(p['compact_centers'])));p[key][i]+=amount*step;return p
    f=[r for r in rows if r['feasible']];adm=[r for r in f if admissible(r)];seeds=[min(adm or f,key=score),rows[3],min(f,key=score)]
    try:
        for seed in seeds:
            cur=seed
            for iteration in range(4):
                y=output(cur);cols=[];avail=[];probeids=[];candidates=[cur]
                for col in range(len(fields)):
                    neg=trial(perturb(cur['parameters'],col,-1),'E-jacobian');pos=trial(perturb(cur['parameters'],col,1),'E-jacobian');probeids.append([neg['id'],pos['id']]);candidates.extend([neg,pos])
                    if neg['feasible'] and pos['feasible']:d=(output(pos)-output(neg))/2
                    elif pos['feasible']:d=output(pos)-y
                    elif neg['feasible']:d=y-output(neg)
                    else:continue
                    if np.linalg.norm(d)<1e-10:continue
                    cols.append(d);avail.append(col)
                if not cols:break
                J=np.array(cols).T;nc=len(avail)
                # Shared slack t measures normalized target deficits; preservation rows have
                # tighter scales than the two unresolved cores. Full physical check remains exact.
                target=np.r_[[.87,.85,.80,.79,.80,.79],[.30,9.26,33.34,13.42],[.97,9.38,26.87,10.77],[9.,14.3]]
                scales=np.r_[[.05,.025,.10,.04,.10,.025],[.3,2,12,1.5],[.3,2,12,1.5],[2,2]]
                signs=np.r_[-np.ones(6),np.ones(10)];A=signs[:,None]*J/scales[:,None];b=signs*(target-y)/scales
                opt=linprog(np.r_[np.zeros(nc),1.],A_ub=np.c_[A,-np.ones(len(y))],b_ub=b,bounds=[(-1.5,1.5)]*nc+[(0,None)],method='highs')
                record=dict(seed=seed['id'],current=cur['id'],iteration=iteration,fields=fields,available_columns=avail,probe_ids=probeids,jacobian=J.tolist(),singular_values=np.linalg.svd(J,compute_uv=False).tolist(),success=bool(opt.success),predicted_max_violation=float(opt.x[-1]) if opt.success else None)
                if opt.success:
                    record['step']=opt.x[:-1].tolist()
                    for alpha in [.25,.5,1.]:
                        p=deepcopy(cur['parameters'])
                        for col,x in zip(avail,opt.x[:-1]):p=perturb(p,col,alpha*x)
                        candidates.append(trial(p,'E-joint-trust-step'))
                matrices.append(record);save(OUT/'jacobians.json',matrices)
                winner=min(candidates,key=score)
                if winner['id']==cur['id']:break
                cur=winner
    except TimeoutError:print('POLISH CUTOFF',flush=True)
    f=[r for r in rows if r['feasible']];adm=[r for r in f if admissible(r)];old=read(OUT/'refinement.json');selected=dict(old['selected']);selected['A']=min(adm or f,key=score)['id'];selected['C']=min(f,key=merit)['id'];vv=np.array([vector(r) for r in f]);pareto=[r['id'] for i,r in enumerate(f) if not np.any(np.all(vv<=vv[i]+1e-12,axis=1)&np.any(vv<vv[i]-1e-12,axis=1))]
    save(OUT/'polish.json',dict(seconds=time.monotonic()-start,new_trials=len(rows)-n0,total_trials=len(rows),selected=selected,admissible=[r['id'] for r in adm],pareto=pareto,jacobians=len(matrices),finished=utc(),policy='Measured local feasible finite differences, normalized minimax linear trust steps with simultaneous preservation, and exact full-scene/contact re-evaluation. No physical rank or parameter identification inferred. A constrained retained candidate; B explicit -15 branch; C unrestricted tradeoff.'))
    print('DONE',len(rows),selected,'admissible',len(adm),flush=True)
if __name__=='__main__':main()
