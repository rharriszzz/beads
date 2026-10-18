"""Bounded exact-minimax fit with frozen correspondences and all-chain contacts."""
import argparse,time
from copy import deepcopy
from datetime import datetime,timezone
import numpy as np
from scipy.optimize import minimize
from photo2.r297.common import ROOT,read,save,digest,utc
from .detect import OUT
from .optics import Engine,objective

def compact(r):
    r=deepcopy(r)
    for row in r.get('rows',[]):
        if row.get('predicted_lobe'):
            for k in ['pixels','near_maximum']:row['predicted_lobe'].pop(k,None)
    return r

def main():
    global OUT
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=650);ap.add_argument('--resume',action='store_true');ap.add_argument('--folder',default='');ap.add_argument('--seed');args=ap.parse_args()
    if args.folder:OUT=OUT/args.folder
    began=time.time();deadline=min(began+args.seconds,datetime(2026,10,18,2,2,0,tzinfo=timezone.utc).timestamp())
    epoch=read(OUT/'epoch.json');engine=Engine(epoch);rng=np.random.default_rng(318)
    trialdir=OUT/'trials';trialdir.mkdir(exist_ok=True);rows=[read(p) for p in sorted(trialdir.glob('*.gz'))]
    if rows and not args.resume:raise RuntimeError('Existing trials; explicitly resume')
    seen={digest(r['parameters']):r for r in rows};matrices=read(OUT/'jacobians.json.gz') if args.resume and (OUT/'jacobians.json.gz').exists() else []
    def trial(p,stage):
        if time.time()>=deadline:raise TimeoutError
        key=digest(p)
        if key in seen:return seen[key]
        t=time.time()
        try:
            if not (.7<=p['axial']<=1.2 and 3<=p['roughness']<=45 and -10<=p['light_el']<=90 and 45<=p['elevation']<=75 and 3.7<=p['minor']<=4.6 and -20<=p['tilt']<=30 and 0<=p.get('light_inverse',0)<=.01):raise ValueError('declared numerical exploration bounds')
            r=compact(engine.evaluate(p))
        except (ValueError,FloatingPointError) as ex:r=dict(feasible=False,classification='numerical-bound',reason=str(ex))
        r.update(id=len(rows),parameters=p,stage=stage,utc=utc(),seconds=time.time()-t,epoch_binding=epoch['binding'])
        r['objective_px']=objective(r);rows.append(r);seen[key]=r;save(trialdir/f'{r["id"]:05d}.json.gz',r)
        if len(rows)%25==0:print('TRIAL',r['id'],stage,r['classification'],'Emax',round(r['objective_px'],4),'best',round(min(x['objective_px'] for x in rows),4),flush=True)
        return r
    def best():return min(rows,key=lambda r:r['objective_px'])
    def change(p,key,delta):
        q=deepcopy(p)
        if isinstance(key,tuple):q[key[0]][key[1]]+=float(delta)
        else:q[key]=q.get(key,0.)+float(delta)
        return q
    initial=deepcopy(epoch['parameters'])
    # Strip verified ignored zeros and add three shared smooth local basis nodes.
    n=len(initial['compact_centers'])
    for k in ['compact_phase','compact_spacing','compact_tilt','compact_cant']:
        a=initial.get(k,[0.]*n);assert not any(a[n:]);initial[k]=a[:n]
    low,high=epoch['scope'];newcenters=[low,(low+high)/2,high]
    initial['compact_centers']+=newcenters
    for k in ['compact_phase','compact_spacing','compact_tilt','compact_cant']:initial[k]+=[0.,0.,0.]
    globals=[('light_az',10.),('light_el',7.),('roughness',4.),(('translation',0),2.),(('translation',1),2.),('phase',.08),('tilt',3.),('axial',.035),('elevation',1.2),('minor',.05),('roll',2.),('s0',2.),('light_inverse',.001),('radius',.025)]
    locals=[( (field,n+i),step) for field,step in [('compact_phase',.04),('compact_spacing',.002),('compact_tilt',3.),('compact_cant',3.)] for i in range(3)]
    # Additional beta probes are judged solely by the same frozen reflection max.
    try:
        trial(initial,'zero-basis-baseline')
        if args.seed:trial(read(ROOT/args.seed)['parameters'],'transferred-geometry-start')
        # Broad shared illumination only: exact cached camera geometry.
        if not args.resume:
            for az in [90,120,150,180,210,240]:
                for el in [25,45,65,85]:
                    p=deepcopy(initial);p.update(light_az=float(az),light_el=float(el));trial(p,'shared-directional-light')
        cycle=0
        while time.time()<deadline:
            # Coordinate bracket sweeps always evaluate exact primary maximum.
            fields=globals if cycle%2==0 else locals
            for key,scale in fields:
                cur=best();step=scale*[1,.5,.25,.125][cycle%4]
                for sign in [-1,1]:trial(change(cur['parameters'],key,sign*step),'exact-coordinate')
            # Coupled minimax linear trust step, without a mean-error objective.
            cur=best();fields=(globals if cycle%3==0 else (locals if cycle%3==1 else globals[:5]+locals[:3]))
            residual=np.array([np.array(r['predicted'])-r['observed'] for r in cur['rows']]);columns=[];usable=[];probes=[]
            for key,scale in fields:
                rr=trial(change(cur['parameters'],key,scale*.25),'jacobian-positive')
                if not rr.get('feasible') or rr.get('missing'):
                    rr=trial(change(cur['parameters'],key,-scale*.25),'jacobian-negative');sign=-1
                else:sign=1
                if rr.get('feasible') and not rr.get('missing'):
                    dd=np.array([np.array(r['predicted'])-r['observed'] for r in rr['rows']]);columns.append((dd-residual)/(sign*.25));usable.append((key,scale));probes.append(rr['id'])
            if columns:
                jac=np.stack(columns,axis=2);nv=len(columns)
                def constraint(x):return x[-1]-np.linalg.norm(residual+np.einsum('ijk,k->ij',jac,x[:-1]),axis=1)
                sol=minimize(lambda x:x[-1],np.r_[np.zeros(nv),cur['emax_px']],method='SLSQP',bounds=[(-1,1)]*nv+[(0,None)],constraints=[dict(type='ineq',fun=constraint)],options=dict(maxiter=80,ftol=1e-7))
                matrices.append(dict(parent=cur['id'],probes=probes,fields=usable,jacobian=jac.tolist(),residual=residual.tolist(),step=sol.x.tolist(),success=bool(sol.success)))
                for fraction in [.25,.5,1.]:
                    p=deepcopy(cur['parameters'])
                    for (key,scale),v in zip(usable,sol.x[:-1]):p=change(p,key,float(v*scale*fraction))
                    trial(p,'coupled-exact-minimax-trust')
            # Joint perturbations permit escaping discontinuous lobe/visibility basins.
            for _ in range(24):
                cur=best();p=deepcopy(cur['parameters']);fields=globals+locals
                for j in rng.choice(len(fields),size=5,replace=False):
                    key,scale=fields[j];p=change(p,key,rng.normal()*scale*[.5,.2,.1][cycle%3])
                trial(p,'coupled-random')
            cycle+=1
            save(OUT/'checkpoint.json',dict(best=best()['id'],trials=len(rows),epoch_binding=epoch['binding'],utc=utc(),elapsed=time.time()-began))
            save(OUT/'jacobians.json.gz',matrices)
    except TimeoutError:pass
    cur=best();save(OUT/'selection.json',dict(best=cur['id'],trials=len(rows),epoch_binding=epoch['binding'],utc=utc(),elapsed=time.time()-began,maximum_px=cur['emax_px'],expanded=False,reason='Expansion requires separate localization/numerical/visual acceptance, not elapsed time'))
    save(OUT/'jacobians.json.gz',matrices)
    result,s,arrays=engine.evaluate(cur['parameters'],True);save(OUT/'best.json.gz',dict(parameters=cur['parameters'],trial=cur['id'],**result));np.savez_compressed(OUT/'best-optics.npz',**arrays)
    print('SELECTED',cur['id'],'trials',len(rows),'Emax',cur['emax_px'],'missing',cur['missing'],'seconds',time.time()-began,flush=True)

if __name__=='__main__':main()
