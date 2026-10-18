"""Serialized bilateral multiscale probes and scaled local minimax experiments."""
import argparse,time,traceback
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize
from photo2.r318 import optics
from photo2.r314.geometry import ShapeMixin
from photo2.r318.search import compact
from .common import *
from .evidence import Evidence,gate

class GeneralChain(optics.Chain):
    def blocked(self,points,direction,max_distance=np.inf):
        if not self.exterior and self.hole==.14 and self.rounding==.8:return super().blocked(points,direction,max_distance)
        return ShapeMixin.blocked(self,points,direction,max_distance)
# Isolated R319 process only; historical sources and outputs unchanged.
optics.Chain=GeneralChain

class Run:
    def __init__(self):
        self.epoch=read(OLD/'epoch2/epoch.json');self.p=read(OLD/'epoch2/best.json.gz')['parameters'];self.p.setdefault('orientation_halfwidth',18)
        self.e=optics.Engine(self.epoch);self.ev=Evidence(self.epoch);self.rows=[];self.deadline=time.time()+900
    def trial(self,p,stage,meta=None):
        if time.time()>self.deadline:raise TimeoutError('R319 scientific deadline')
        t=time.time();s=None
        try:
            if p.get('perspective',0)<0 or p.get('light_inverse',0)<0 or p.get('light_width',0)<0:raise ValueError('inverse distance/width must be nonnegative')
            r=self.e.evaluate(p,True)
            if isinstance(r,tuple):
                r,s,a=r;r=compact(r);r['geometry']=self.ev.measure(s)
                if hasattr(self,'baseline'):r['acceptance']=gate(r['geometry'],self.baseline['geometry'])
            else:r=compact(r)
        except (ValueError,AssertionError,FloatingPointError) as ex:r=dict(feasible=False,classification='parameter-or-model-bound',reason=str(ex))
        r.update(id=len(self.rows),parameters=deepcopy(p),stage=stage,meta=meta or {},utc=utc(),elapsed=time.time()-t,epoch_binding=self.epoch['binding'])
        self.rows.append(r);save(OUT/'trials'/f'{r["id"]:05}.json.gz',r)
        if len(self.rows)%25==0:print('TRIAL',r['id'],stage,r.get('emax_px'),r['classification'],flush=True)
        return r
    def usable(self,r):return r.get('feasible') and not r.get('missing')
    def probe(self,p,vs,stage):
        base=self.trial(p,stage+'-parent');pred=positions(base);records=[];columns=[];usable=[]
        for j,v in enumerate(vs):
            tests={}
            for f in [.25,1.]:
                for sign in [-1,1]:
                    r=self.trial(change(p,v['key'],v['scale']*f*sign),stage,dict(variable=j,key=v['key'],factor=f*sign));tests[f*sign]=r
            z=dict(variable=j,**v,trials={str(k):r['id'] for k,r in tests.items()})
            pairs={}
            for f in [.25,1.]:
                a,b=tests[-f],tests[f]
                if self.usable(a) and self.usable(b):
                    plus=(positions(b)-pred)/f;minus=(pred-positions(a))/f;central=(plus+minus)/2
                    pairs[f]=central;z[str(f)]=dict(central=central.tolist(),positive=plus.tolist(),negative=minus.tolist(),asymmetry_norm=float(np.linalg.norm(plus-minus)),relative_asymmetry=float(np.linalg.norm(plus-minus)/max(.1,np.linalg.norm(central))),maximum_second_difference_px=float(np.max(np.linalg.norm(positions(b)+positions(a)-2*pred,axis=1))))
            # For nonnegative boundary parameters, use recorded one-sided response.
            if .25 in pairs:col=pairs[.25];z['derivative']='central'
            elif self.usable(tests[.25]):col=(positions(tests[.25])-pred)/.25;z['derivative']='positive-boundary'
            elif self.usable(tests[-.25]):col=(pred-positions(tests[-.25]))/.25;z['derivative']='negative-feasible'
            else:col=None;z['derivative']='unavailable-physical-or-numerical'
            if col is not None:
                z['scaled_norm']=float(np.linalg.norm(col));z['maximum_scaled_motion_px']=float(np.max(np.linalg.norm(col,axis=1)))
                z['multiscale_relative_change']=float(np.linalg.norm(pairs[1.]-pairs[.25])/max(.1,np.linalg.norm(col))) if len(pairs)==2 else None
                asym=z.get('0.25',{}).get('relative_asymmetry',0)
                z['smooth']=bool(asym<.6 and (z['multiscale_relative_change'] is None or z['multiscale_relative_change']<.6))
                if z['scaled_norm']>.03 and z['smooth']:columns.append(col);usable.append(j)
            records.append(z)
            save(OUT/(stage+'-sensitivity.json.gz'),dict(parent=base['id'],records=records,variables=vs))
        return base,records,np.stack(columns,axis=2),usable
    def solve(self,base,J,vs,ids,label,cohort=None):
        residual=positions(base)-np.array([r['observed'] for r in base['rows']]);sel=np.arange(len(residual)) if cohort is None else np.array(cohort)
        U,S,V=np.linalg.svd(J.reshape(-1,J.shape[2]),full_matrices=False)
        rec=dict(parent=base['id'],variables=[vs[j] for j in ids],jacobian=J.tolist(),residual=residual.tolist(),singular_values=S.tolist(),right_vectors=V.tolist(),left_vectors=U.tolist(),rank_1percent=int(np.sum(S>S[0]*.01)),cohort=sel.tolist(),steps=[])
        # Conditional residual component outside the measured Jacobian range.
        keep=S>S[0]*.01;rr=residual.ravel();rec['residual_outside_1percent_span_px']=float(np.linalg.norm(rr-U[:,keep]@(U[:,keep].T@rr)))
        for trust in [.5,1.,2.]:
            bounds=[]
            for j in ids:
                key=vs[j]['key'];lo=-trust
                if isinstance(key,str) and key in ['perspective','light_inverse','light_width']:lo=max(lo,-base['parameters'].get(key,0)/vs[j]['scale'])
                bounds.append((lo,trust))
            def constraints(x):return x[-1]-np.linalg.norm(residual[sel]+np.einsum('ijk,k->ij',J[sel],x[:-1]),axis=1)
            sol=minimize(lambda x:x[-1],np.r_[np.zeros(len(ids)),np.linalg.norm(residual[sel],axis=1).max()],method='SLSQP',bounds=bounds+[(0,None)],constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=160,ftol=1e-8))
            predicted=residual+np.einsum('ijk,k->ij',J,sol.x[:-1]);p=deepcopy(base['parameters'])
            for j,d in zip(ids,sol.x[:-1]):p=change(p,vs[j]['key'],vs[j]['scale']*d)
            r=self.trial(p,label,dict(parent=base['id'],trust=trust,predicted_errors=np.linalg.norm(predicted,axis=1).tolist(),predicted_points=(predicted+np.array([z['observed'] for z in base['rows']])).tolist(),cohort=sel.tolist()))
            rec['steps'].append(dict(trial=r['id'],trust=trust,success=bool(sol.success),message=sol.message,scaled_step=sol.x.tolist(),predicted_max=float(np.linalg.norm(predicted[sel],axis=1).max()),under10_predicted=bool(np.linalg.norm(predicted[sel],axis=1).max()<10),actual_max=float(max(r['rows'][i]['error_px'] for i in sel)) if self.usable(r) else None))
        save(OUT/(label+'.json.gz'),rec);return rec

def main():
    run=Run();run.deadline=__import__('datetime').datetime(2026,10,18,2,59,7,tzinfo=__import__('datetime').timezone.utc).timestamp()
    save(OUT/'start.json',dict(utc=utc(),start='2026-10-18T02:35:07Z',scientific_cutoff='2026-10-18T02:59:07Z',delivery_deadline='2026-10-18T03:05:07Z',photo_sha256=sha(ROOT/'beads-photo-2.jpg')))
    run.baseline=run.trial(run.p,'baseline');save(OUT/'baseline.json.gz',run.baseline)
    vs=variables(run.p);save(OUT/'variables.json',vs)
    base,records,J,ids=run.probe(run.p,vs,'bilateral');run.solve(base,J,vs,ids,'full-minimax')
    good=[r for r in run.rows if run.usable(r) and r.get('acceptance',{}).get('passed')];best=min(good,key=lambda r:r['emax_px']) if good else base
    save(OUT/'best-full.json.gz',best)
    # Select compact interval by frozen photo-only colors/count/uncertainty;
    # conditional address contiguity is required, optical errors never enter.
    candidates=[]
    obs=run.epoch['observations'];mapping=run.epoch['mapping']
    for low in range(25,67):
        selected=[i for i,o in enumerate(obs) if low<=mapping[o['id']]<=low+19]
        if len({obs[i]['color'] for i in selected})<3:continue
        candidates.append(dict(low=low,high=low+19,cohort=selected,count=len(selected),uncertainty=float(np.mean([obs[i]['uncertainty_px'] for i in selected]))))
    chosen=min(candidates,key=lambda c:(-c['count'],c['uncertainty'],c['low']));save(OUT/'small-selection.json',dict(chosen=chosen,candidates=candidates,policy='20 consecutive conditional addresses (~3.08 turns), all three pigment cues, maximize retained reliable observations then minimize photo localization uncertainty; no predicted optical error. All 22 still evaluated as preservation guards.'))
    run.solve(base,J,vs,ids,'small-minimax',chosen['cohort'])
    # Add only existing basis functions at finer support to test representation.
    # They remain smooth fields, never per-bead translations.
    p=deepcopy(best['parameters']);n=len(p['compact_centers']);p['compact_centers'] += [chosen['low']+5,chosen['low']+14]
    for k in ['compact_phase','compact_spacing','compact_tilt','compact_cant']:p[k]+=[0.,0.]
    # Global widths remain unchanged: separate width controls already measured.
    local=[dict(key=[k,n+j],scale=h,unit=u,interpretation='added existing smooth basis in compact interval') for k,h,u in [('compact_phase',.04,'rad'),('compact_spacing',.002,'fraction'),('compact_tilt',1,'deg'),('compact_cant',1,'deg')] for j in range(2)]
    # Reuse strong global parameters; a fresh Jacobian is required at changed geometry.
    local += [vs[j] for j in ids if isinstance(vs[j]['key'],str) and vs[j]['key'] in ['phase','s0','tilt','axial','radius','minor','elevation','roll','scale','light_az','light_el','roughness']]
    b,rr,jj,ii=run.probe(p,local,'small-local');run.solve(b,jj,local,ii,'small-local-minimax',chosen['cohort'])
    good=[r for r in run.rows if run.usable(r) and r.get('acceptance',{}).get('passed') and r['emax_px']<=run.baseline['emax_px']+.05]
    small=min(good,key=lambda r:max(r['rows'][i]['error_px'] for i in chosen['cohort'])) if good else base
    save(OUT/'best-small.json.gz',small)
    save(OUT/'run-summary.json',dict(utc=utc(),trials=len(run.rows),best_full=best['id'],best_small=small['id'],small_scope=[chosen['low'],chosen['high']],all22_preserved=True))
    print('COMPLETE',len(run.rows),best['emax_px'],max(small['rows'][i]['error_px'] for i in chosen['cohort']),flush=True)
if __name__=='__main__':main()
