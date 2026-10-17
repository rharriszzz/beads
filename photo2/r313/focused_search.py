"""Separate bounded continuation epoch; original 426 evaluations are immutable."""
import time,signal,argparse
from copy import deepcopy
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from photo2.r297.common import ROOT,read,save,sha,utc,digest
from photo2.r306.evidence import load
from .objective_v2 import SurfaceObjective
from .diagnose_geometry import make
from .geometry_experiment import contacts,paper

KEYS=['phase','s0','elevation','roll','tilt','minor','scale','axial','trajectory_mix','hole','rounding','spacing_wave']
SCALES=np.array([.7,14.,10.,20.,15.,.6,.8,.2,.35,.15,.25,.004])
BOUNDS=dict(elevation=(20,88),roll=(-180,180),yaw=(-90,90),tilt=(-100,100),minor=(2.5,7.),scale=(5.5,12.),axial=(.25,1.5),trajectory_mix=(-1.,1.25),hole=(.02,.60),rounding=(.25,1.))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=float,default=420);args=parser.parse_args();out=ROOT/'photo2/r313/continuation';ev=out.parent/'evidence';data,_,_=load();eng=SurfaceObjective(dict(np.load(ev/'maps.npz')),read(ev/'freeze.json'));old=read(out/'start.json')
 for p,h in old['preserved_trials'].items():assert sha(ROOT/p)==h
 assert sha(ev/'maps.npz')==old['evidence_sha256']
 if (out/'search-selection.json').exists():raise SystemExit('Continuation search sealed; no automatic extra epoch')
 initial=read(out/'initial-incumbents.json')['best'];r312=next(r for r in initial if r['start']=='R312-best')
 starts=[dict(name='shared-profile-R297',**{k:read(out/'diagnostics/070.json.gz')[k] for k in ['parameters','implementation']}),dict(name='initial-R312',parameters=r312['parameters'],implementation=r312['implementation']),dict(name='R309',**{k:read(out/'diagnostics/019.json.gz')[k] for k in ['parameters','implementation']}),dict(name='trajectory-thin',**{k:read(out/'diagnostics/018.json.gz')[k] for k in ['parameters','implementation']})]
 sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r313').glob('*.py'))};sources['photo2/r313/shape_kernel.cpp']=sha(ROOT/'photo2/r313/shape_kernel.cpp')
 save(out/'search-plan.json',dict(utc=utc(),seconds=args.seconds,starts=starts,parameters=KEYS,scales=SCALES.tolist(),bounds=BOUNDS,sources=sources,evidence_sha256=sha(ev/'maps.npz'),policy='Shared rigid glass geometry only. Development selection, historical comparison excluded. Inconclusive envelope is not collision; actual-solid fallback used. No illumination proposals. No adoption from score alone.',objective_limitation='Gross failures rejected; modest dilation may correctly repair material omission or exploit unmeasured boundaries. Final photographic review and individual errors mandatory.'))
 began=time.monotonic();deadline=began+args.seconds;stopped=[False];signal.signal(signal.SIGTERM,lambda *_:stopped.__setitem__(0,True));signal.signal(signal.SIGINT,lambda *_:stopped.__setitem__(0,True));rng=np.random.default_rng(31303);count=0;best=[];cache={}
 class Stop(Exception):pass
 for start in starts:
  end=min(deadline,time.monotonic()+args.seconds/len(starts));base=deepcopy(start['parameters']);base.setdefault('trajectory_mix',0.);base.setdefault('hole',.14);base.setdefault('rounding',.8);base.setdefault('spacing_wave',0.);keys=KEYS.copy()
  if start['implementation'] in ['R297','R313-R297']:keys[3]='yaw'
  incumbent=[float('inf'),None,None];bestv=[np.zeros(len(keys))]
  def parameters(v):
   p=deepcopy(base)
   for k,z,sc in zip(keys,v,SCALES):p[k]=float(base[k]+z*sc)
   p['phase']=float((p['phase']+np.pi)%(2*np.pi)-np.pi)
   p['local_spacing']=(np.array(base['local_spacing'])+p.pop('spacing_wave')*np.cos(2*np.pi*np.arange(len(base['local_spacing']))/len(base['local_spacing']))).tolist()
   return p
  def fun(v):
   nonlocal count
   if stopped[0] or time.monotonic()>=end:raise Stop()
   p=parameters(v);key=digest(p)
   if key in cache:return cache[key]
   tick=time.monotonic();row=dict(id=count,start=start['name'],parameters=p,implementation=start['implementation'],elapsed=tick-began,vector=np.asarray(v).tolist());count+=1
   reason=next((k for k,(a,b) in BOUNDS.items() if k in p and not a<=p[k]<=b),None)
   if max(abs(np.array(p['local_spacing'])))>max(.018,max(abs(np.array(base['local_spacing'])))+.008):reason='coherent_spacing_field_bound'
   if reason:row.update(feasible=False,classification='numerical-bound',reason=reason,score=10000.)
   else:
    try:
     s=make(p,data,start['implementation']);placed=time.monotonic();cert=contacts(s,seconds=.5);checked=time.monotonic();physical={k:v for k,v in cert.items() if k!='witnesses'}
     row.update(feasible=cert['certified'],classification=cert['classification'],physical=physical)
     if cert['classification']!='demonstrated-interpenetration':
      tr=s.trace(eng.xy);rendered=time.monotonic();metric=eng.measure(tr['owner'],tr['unknown'],s.indices,0,False);row['development']=metric;row['photographic_score']=metric['score'];row['score']=metric['score'] if cert['certified'] else 1000+metric['score'];row['profile']=dict(geometry=placed-tick,contact=checked-placed,render=rendered-checked,measure=time.monotonic()-rendered)
     else:row['score']=1000+cert['unresolved_pairs']
    except ValueError as ex:row.update(feasible=False,classification='geometry-bound',reason=str(ex),score=10000.)
   row['seconds']=time.monotonic()-tick;cache[key]=row['score'];save(out/'trials'/f'{row["id"]:05d}.json.gz',row)
   if row['feasible'] and row['score']<incumbent[0]:
    incumbent[:]=[row['score'],p,row['id']];bestv[0]=np.asarray(v).copy();save(out/'current-best.json',dict(start=start['name'],score=row['score'],trial=row['id'],parameters=p,implementation=start['implementation']));print(start['name'],row['id'],round(row['score'],5),'elapsed',round(time.monotonic()-began,1),flush=True)
   return row['score']
  try:
   fun(np.zeros(len(keys)))
   # Shared orientation/proportions are coupled, with meaningful nonlocal probes.
   for j in range(16):
    v=rng.normal(0,.45 if j<8 else 1.,len(keys));fun(v)
   v=bestv[0];simplex=np.tile(v,(len(keys)+1,1));simplex[1:]+=np.eye(len(keys))*.12
   minimize(fun,v,method='Nelder-Mead',options=dict(initial_simplex=simplex,maxiter=100000,xatol=.003,fatol=1e-5))
  except Stop:pass
  if incumbent[1] is not None:best.append(dict(start=start['name'],score=incumbent[0],parameters=incumbent[1],trial=incumbent[2],implementation=start['implementation']))
  save(out/'search-checkpoint.json',dict(utc=utc(),elapsed=time.monotonic()-began,evaluations=count,best=best))
  if stopped[0] or time.monotonic()>=deadline:break
 best.sort(key=lambda r:r['score']);save(out/'search-selection.json',dict(utc=utc(),seconds=time.monotonic()-began,evaluations=count,best=best,selected=best[0],sealed=True,stopped=stopped[0],source_hashes=sources))
 print('SEALED',count,time.monotonic()-began,best[0]['score'],flush=True)
if __name__=='__main__':main()
