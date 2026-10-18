"""Minimax with fixed-normal linearized full-chain separating-plane constraints."""
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize
from photo2.r295.geometry import AXES
from .experiment import Run,GeneralChain
from .refine import metric
from .common import *

def gaps(s,pairs,normals):
    a,b=pairs.T
    return np.sum((s.centers[b]-s.centers[a])*normals,axis=1)-s.support(normals,s.g[AXES[0]][a])-s.support(-normals,s.g[AXES[0]][b])

def fit(run,base,vs,J,G,label,cohort=None):
    s=GeneralChain(base['parameters'],run.e.data);cert=s.certify(iterations=220,witnesses=True);assert cert['certified'];pairs=np.array([w['pair'] for w in cert['witnesses']]);normals=np.array([w['normal'] for w in cert['witnesses']]);g0=gaps(s,pairs,normals);cols=[];keep=[];discard=[]
    for i,v in enumerate(vs):
        values=[]
        try:
            for f in [-.25,.25]:
                q=change(base['parameters'],v['key'],v['scale']*f)
                if isinstance(v['key'],str) and v['key'] in ['perspective','light_inverse','light_width'] and q[v['key']]<0:raise ValueError('nonnegative boundary')
                ss=GeneralChain(q,run.e.data);values.append(gaps(ss,pairs,normals))
            col=(values[1]-values[0])/.5
        except ValueError as ex:
            # Positive one-sided geometry derivative at camera/light boundary.
            try:ss=GeneralChain(change(base['parameters'],v['key'],v['scale']*.25),run.e.data);col=(gaps(ss,pairs,normals)-g0)/.25
            except ValueError as ex:discard.append(dict(variable=v,reason=str(ex)));continue
        cols.append(col);keep.append(i)
    vs=[vs[i] for i in keep];J=J[:,:,keep];G=G[:,keep] if G is not None else None;K=np.stack(cols,axis=1);n=len(vs)
    residual=positions(base)-np.array([r['observed'] for r in base['rows']]);sel=np.arange(22) if cohort is None else np.array(cohort);limits=metric(run.baseline)+np.r_[.002,.02,.02,np.full(len(metric(base))-3,.03)];cur=metric(base);steps=[]
    for trust in [1.,2.,4.,8.]:
        # Constraints outside reachable first-order clearance envelope are inactive.
        active=g0-1e-5<=trust*np.abs(K).sum(1)+1e-8;KK=K[active];gg=g0[active];bounds=[]
        for v in vs:
            lo=-trust;k=v['key']
            if isinstance(k,str) and k in ['perspective','light_inverse','light_width']:lo=max(lo,-base['parameters'].get(k,0)/v['scale'])
            bounds.append((lo,trust))
        def cons(x):
            d=residual+np.einsum('ijk,k->ij',J,x[:-1]);out=[x[-1]-np.linalg.norm(d[sel],axis=1),gg+KK@x[:-1]-1e-5]
            if G is not None:out.append(limits-cur-G@x[:-1])
            if cohort is not None:out.append(run.baseline['emax_px']+.05-np.linalg.norm(d,axis=1))
            return np.concatenate(out)
        def dc(x):
            d=residual+np.einsum('ijk,k->ij',J,x[:-1]);norm=np.linalg.norm(d,axis=1);D=-np.einsum('ij,ijk->ik',d/np.maximum(norm[:,None],1e-12),J);out=[np.c_[D[sel],np.ones(len(sel))],np.c_[KK,np.zeros(len(KK))]]
            if G is not None:out.append(np.c_[-G,np.zeros(len(G))])
            if cohort is not None:out.append(np.c_[D,np.zeros(22)])
            return np.concatenate(out)
        sol=minimize(lambda x:x[-1],np.r_[np.zeros(n),np.linalg.norm(residual[sel],axis=1).max()],jac=lambda x:np.r_[np.zeros(n),1.],method='SLSQP',bounds=bounds+[(0,None)],constraints=[dict(type='ineq',fun=cons,jac=dc)],options=dict(maxiter=180,ftol=1e-8))
        pred=residual+np.einsum('ijk,k->ij',J,sol.x[:-1]);p=deepcopy(base['parameters'])
        for v,d in zip(vs,sol.x[:-1]):p=change(p,v['key'],v['scale']*d)
        r=run.trial(p,label,dict(parent=base['id'],trust=trust,predicted_errors=np.linalg.norm(pred,axis=1).tolist(),predicted_points=(pred+np.array([z['observed'] for z in base['rows']])).tolist(),cohort=sel.tolist(),linear_contacts=int(active.sum()),linear_geometry_constrained=G is not None))
        steps.append(dict(trial=r['id'],trust=trust,success=bool(sol.success),message=sol.message,predicted_max=float(np.linalg.norm(pred[sel],axis=1).max()),actual_max=max(r['rows'][i]['error_px'] for i in sel) if run.usable(r) else None,scaled_step=sol.x.tolist(),minimum_predicted_plane_gap=float((g0+K@sol.x[:-1]).min()),active_planes=int(active.sum()),minimum_constraint=float(cons(sol.x).min())))
    np.savez_compressed(OUT/(label+'-planes.npz'),pairs=pairs,normals=normals,gaps=g0,jacobian=K)
    save(OUT/(label+'.json.gz'),dict(parent=base['id'],variables=vs,jacobian=J.tolist(),geometry_jacobian=G.tolist() if G is not None else None,steps=steps,discarded=discard,policy='Positive fixed-normal support margin is sufficient at exact geometry; its FIRST-ORDER extrapolation is only predictive. Full nonlinear all-pair certificate mandatory; new pairs are checked. Not a mechanics solver.'))

def main():
    run=Run();run.rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];run.baseline=read(OUT/'baseline.json.gz');run.deadline=__import__('datetime').datetime(2026,10,18,2,59,7,tzinfo=__import__('datetime').timezone.utc).timestamp()
    x=read(OUT/'geometry-constrained-minimax.json.gz');chosen=read(OUT/'small-selection.json')['chosen'];J=np.array(x['jacobian']);G=np.array(x['geometry_jacobian']);vs=x['variables']
    fit(run,run.baseline,vs,J,G,'contact-constrained-full')
    fit(run,run.baseline,vs,J,G,'contact-constrained-small',chosen['cohort'])
    good=[r for r in run.rows if run.usable(r) and r.get('acceptance',{}).get('passed')];best=min(good,key=lambda r:r['emax_px']);save(OUT/'best-full.json.gz',best)
    goodsmall=[r for r in good if r['emax_px']<=run.baseline['emax_px']+.05];small=min(goodsmall,key=lambda r:max(r['rows'][i]['error_px'] for i in chosen['cohort']));save(OUT/'best-small.json.gz',small)
    save(OUT/'contact-summary.json',dict(utc=utc(),trials=len(run.rows),best_full=best['id'],best_small=small['id']))
    print('CONTACT COMPLETE',len(run.rows),best['emax_px'],max(small['rows'][i]['error_px'] for i in chosen['cohort']),flush=True)
if __name__=='__main__':main()
