"""Explain native derivative noise; compare bilateral, larger-step and half-grid models.

Every minimax proposal is tested by the original native objective and geometric
gates. Predicted feasibility is never substituted for a nonlinear certificate.
"""
import time
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize
from .experiment import Run
from .common import *
from .evidence import gate

def metric(r):
    m=r['geometry'];return np.array([m['paper_fraction'],m['seam_conflict_fraction'],m['core_crossing_fraction'],*[1-z['modal_fraction'] for z in m['cores']]],float)

def minimax(run,base,vs,J,G,label,cohort=None,preserve=False):
    residual=positions(base)-np.array([r['observed'] for r in base['rows']]);n=J.shape[2];sel=np.arange(22) if cohort is None else np.array(cohort);b=metric(run.baseline);cur=metric(base);limits=b+np.r_[.002,.02,.02,np.full(len(b)-3,.03)];steps=[]
    for trust in [.25,.5,1.,2.,4.]:
        bounds=[]
        for v in vs:
            lo=-trust;k=v['key']
            if isinstance(k,str) and k in ['perspective','light_inverse','light_width']:lo=max(lo,-base['parameters'].get(k,0)/v['scale'])
            bounds.append((lo,trust))
        def cons(x):
            d=residual+np.einsum('ijk,k->ij',J,x[:-1]);out=list(x[-1]-np.linalg.norm(d[sel],axis=1))
            if G is not None:out.extend(limits-cur-G@x[:-1])
            if preserve:out.extend(run.baseline['emax_px']+.05-np.linalg.norm(d,axis=1))
            return np.array(out)
        sol=minimize(lambda x:x[-1],np.r_[np.zeros(n),np.linalg.norm(residual[sel],axis=1).max()],method='SLSQP',bounds=bounds+[(0,None)],constraints=[dict(type='ineq',fun=cons)],options=dict(maxiter=250,ftol=1e-8))
        predicted=residual+np.einsum('ijk,k->ij',J,sol.x[:-1]);p=deepcopy(base['parameters'])
        for v,d in zip(vs,sol.x[:-1]):p=change(p,v['key'],v['scale']*d)
        r=run.trial(p,label,dict(parent=base['id'],trust=trust,predicted_errors=np.linalg.norm(predicted,axis=1).tolist(),predicted_points=(predicted+np.array([z['observed'] for z in base['rows']])).tolist(),cohort=sel.tolist(),linear_geometry_constrained=G is not None))
        steps.append(dict(trial=r['id'],trust=trust,success=bool(sol.success),message=sol.message,minimum_constraint=float(cons(sol.x).min()),predicted_max=float(np.linalg.norm(predicted[sel],axis=1).max()),actual_max=max(r['rows'][i]['error_px'] for i in sel) if run.usable(r) else None,scaled_step=sol.x.tolist()))
    U,S,V=np.linalg.svd(J.reshape(-1,n),full_matrices=False)
    save(OUT/(label+'.json.gz'),dict(parent=base['id'],variables=vs,jacobian=J.tolist(),geometry_jacobian=G.tolist() if G is not None else None,metric_limits=limits.tolist(),singular_values=S.tolist(),right_vectors=V.tolist(),left_vectors=U.tolist(),rank_1percent=int(np.sum(S>S[0]*.01)),steps=steps,cohort=sel.tolist()))
    return steps

def main():
    run=Run();run.rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];run.baseline=read(OUT/'baseline.json.gz');run.deadline=__import__('datetime').datetime(2026,10,18,2,59,7,tzinfo=__import__('datetime').timezone.utc).timestamp();base=run.baseline
    audit=read(OUT/'bilateral-sensitivity.json.gz');vs=[];cols=[];gcols=[];selected=[]
    for r in audit['records']:
        # Full-sized symmetric secants reduce threshold quantization. They are
        # approximation models with measured disagreement, NOT exact derivatives.
        if '1.0' not in r:continue
        j=np.array(r['1.0']['central']);norm=np.linalg.norm(j)
        if norm<.15:continue
        a,b=[run.rows[r['trials'][str(f)]] for f in [-1.,1.]]
        vs.append({k:r[k] for k in ['key','scale','unit','interpretation']});cols.append(j);gcols.append((metric(b)-metric(a))/2);selected.append(r)
    J=np.stack(cols,axis=2);G=np.stack(gcols,axis=1)
    minimax(run,base,vs,J,None,'wide-secant-minimax')
    minimax(run,base,vs,J,G,'geometry-constrained-minimax')
    chosen=read(OUT/'small-selection.json')['chosen'];minimax(run,base,vs,J,G,'small-constrained-minimax',chosen['cohort'],True)
    # Half-pixel lattice uses the same connected threshold rule in doubled coords.
    from photo2.r318 import optics
    from photo2.r307.fast import grid as original_grid
    from photo2.r318.detect import principal as original_principal
    original_optics_grid=optics.grid;original_optics_principal=optics.principal
    def principal_half(xy,v):
        h=original_principal(xy*2,v)
        if h:
            for k in ['point','centroid','peak','ties','near_maximum','pixels']:h[k]=(np.array(h[k])/2).tolist()
        return h
    optics.grid=lambda s,step,js:original_grid(s,.5,js);optics.principal=principal_half
    engine=optics.Engine(run.epoch);hb=engine.evaluate(base['parameters']);hp=positions(hb);hcols=[];hvs=[];records=[]
    # Independent coefficients with substantial measured optical effect;
    # cap 40 ranked by scale response, not by favorable error sign.
    order=np.argsort([-np.linalg.norm(c) for c in cols])[:40]
    for ii in order:
        v=vs[ii];results={}
        for f in [-.5,.5]:
            p=change(base['parameters'],v['key'],v['scale']*f)
            try:r=engine.evaluate(p)
            except (ValueError,AssertionError) as ex:r=dict(feasible=False,reason=str(ex))
            results[str(f)]=r
        a,b=results['-0.5'],results['0.5'];rec=dict(variable=v,results=results)
        if run.usable(a) and run.usable(b):
            col=positions(b)-positions(a);hcols.append(col);hvs.append(v);rec.update(central=col.tolist(),relative_asymmetry=float(np.linalg.norm(positions(b)+positions(a)-2*hp)/max(.1,.5*np.linalg.norm(col))),native_secant_difference=float(np.linalg.norm(col-J[:,:,ii])))
        records.append(rec)
        save(OUT/'half-grid-sensitivity.json.gz',dict(baseline=hb,records=records,policy='Half-pixel connected principal centroid; same frozen observations. Central step ±0.5 diagnostic scale. Top40 native motion directions; no error-sign selection.'))
    optics.grid=original_optics_grid;optics.principal=original_optics_principal
    if hcols:minimax(run,base,hvs,np.stack(hcols,axis=2),None,'half-grid-minimax')
    # Final selections remain explicit baseline-relative screens.
    good=[r for r in run.rows if run.usable(r) and r.get('acceptance',{}).get('passed')]
    best=min(good,key=lambda r:r['emax_px']);save(OUT/'best-full.json.gz',best)
    goodsmall=[r for r in good if r['emax_px']<=base['emax_px']+.05];bestsmall=min(goodsmall,key=lambda r:max(r['rows'][i]['error_px'] for i in chosen['cohort']))
    save(OUT/'best-small.json.gz',bestsmall)
    save(OUT/'refine-summary.json',dict(utc=utc(),trials=len(run.rows),best_full=best['id'],best_small=bestsmall['id']))
    print('REFINE COMPLETE',len(run.rows),best['emax_px'],max(bestsmall['rows'][i]['error_px'] for i in chosen['cohort']),flush=True)
if __name__=='__main__':main()
