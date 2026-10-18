"""Independent literal supports, original Python rays, and raw optical centroids."""
from .coupled import *
from photo2.r295.geometry import AXES,Chain as PythonChain
from photo2.r299.forward import Surface
from PIL import Image

def literal_support(n,t,r,a):
 d=np.sum(n*t,axis=-1);q=np.sqrt(np.maximum(0,1-d*d));f=1.4/.86*a
 return r*(.656*q+.086*f*abs(d)+.344*np.sqrt(q*q+f*f*d*d))

def main():
 start=time.perf_counter();data=load()[0];counts=Counter();minimum=1e9;models=[];scene_cache={};rays=[]
 # Verify every saved feasible fitting setting, including superseded exploratory
 # bridge epoch, using independent support arithmetic and no optical re-ranking.
 roots=[OUT,ROOT/'photo2/r324/development/bridge-conditional-fit']
 for root in roots:
  for folder in ['fit-trials','expand-trials']:
   for f in sorted((root/folder).glob('*.gz')):
    r=read(f);counts['saved_trials']+=1
    if not r.get('parameters'):continue
    key=digest(r['parameters'])
    if key not in scene_cache:
     s=R321(r['parameters'],data);cert=s.certify(iterations=120,witnesses=True)
     if cert['certified']:
      ws=cert['witnesses'];a=np.array([w['pair'][0] for w in ws]);b=np.array([w['pair'][1] for w in ws]);n=np.array([w['normal'] for w in ws]);gaps=np.sum((s.centers[b]-s.centers[a])*n,axis=1)-literal_support(n,s.g[AXES[0]][a],s.radius,s.axial)-literal_support(n,s.g[AXES[0]][b],s.radius,s.axial);assert gaps.min()>1e-6;assert np.max(abs(gaps-np.array([w['gap_units'] for w in ws])))<1e-9;minimum=min(minimum,float(gaps.min()));counts['independent_support_witnesses']+=len(ws)
     scene_cache[key]=cert['certified'];counts['unique_geometries']+=1
    if r.get('feasible'):assert scene_cache[key]
    elif r.get('contact',{}).get('classification')=='demonstrated-interpenetration':
     s=R321(r['parameters'],data)
     for a in r['contact']['actual_solid_checks']:
      if a['state']!='demonstrated-interpenetration':continue
      for j in a['pair']:
       delta=np.array(a['point'])-s.centers[j];q=np.array([delta@s.g[k][j] for k in AXES]);assert s.local_sdf(q)<0
      counts['actual_penetration_witnesses']+=1
    if r.get('native',{}).get('feasible'):
     rr=r['native']['rows'];errors=[float(np.linalg.norm(np.array(v['predicted'])-v['observed'])) for v in rr if v['predicted'] is not None];missing=sum(v['predicted'] is None for v in rr);assert missing==r['native']['missing'];assert r['native']['maximum_is_infinite']==bool(missing)
     for v in rr:
      if v['predicted'] is not None:assert abs(np.linalg.norm(np.array(v['predicted'])-v['observed'])-v['error_px'])<1e-10
     if not missing:assert abs(max(errors)-r['native']['emax_px'])<1e-10
     assert len(r['native']['target_addresses'])==r['native']['scope'];assert np.array_equal(np.diff(r['native']['target_addresses']),np.ones(r['native']['scope']-1));counts['optical_cohorts_checked']+=1
 # Original Python camera/shadow paths on all frozen and selected final models.
 for label,s,saved in frozen_models(data):models.append((label,s))
 fs=read(OUT/'fit-summary.json');es=read(OUT/'expand-summary.json')
 for key in ['baseline100','final100','reflection_tradeoff']:
  r=read(OUT/f'fit-trials/{fs[key]:04}.json.gz');models.append((key,R321(r['parameters'],data)))
 if es['best'] is not None:
  r=read(OUT/f'expand-trials/{es["best"]:04}.json.gz');models.append(('best200',R321(r['parameters'],data)))
 rng=np.random.default_rng(1324)
 for label,s in models:
  sel=rng.choice(s.n,120,replace=False);xy=s.pc[sel]+rng.uniform(-s.radius*s.scale,s.radius*s.scale,(120,2));fast=s.camera(xy);slow=PythonChain.trace(s,xy,True);known=~fast['unknown']&~slow['unknown'];assert np.array_equal(fast['owner'][known],slow['owner'][known]);hit=known&(fast['owner']>=0);err=float(np.max(np.linalg.norm(fast['points'][hit]-slow['points'][hit],axis=1))) if hit.any() else 0;assert err<1e-8
  light=make_light(s.p,s);a=shade(s,fast,light);old=s.blocked;s.blocked=lambda points,d,max_distance=np.inf:Surface.blocked(s,points,d,max_distance);b=shade(s,fast,light);s.blocked=old;delta=float(abs(a['intensity']-b['intensity']).max());assert delta<1e-10;rays.append(dict(label=label,rays=len(xy),python_unknown=int(slow['unknown'].sum()),point_difference=err,shadow_difference=delta))
 # Measured reflection locations reconstructed from native original pixels,
 # independently of the detector and without treating them as bead centers.
 rgb=np.array(Image.open(ROOT/'beads-photo-2.jpg').convert('RGB'));refl=read(OUT/'fit-evidence.json')['reflections']
 for o in refl:
  xy=np.array(o['pixels'],int);v=rgb[xy[:,1],xy[:,0]]/255;lin=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);point=np.average(xy,axis=0,weights=lin.min(1));assert np.max(abs(point-o['point']))<1e-9
 save(OUT/'physical-verification.json',dict(passed=True,counts=dict(counts),minimum_independent_gap=minimum,original_python_checks=rays,raw_reflection_centroids=len(refl),seconds=time.perf_counter()-start,warning='Sampled Python rays and full support witnesses; not every camera ray independently rerun. No full-circuit photographic accuracy validation.'))
 print('PHYSICAL VERIFY',dict(counts),len(refl),time.perf_counter()-start,flush=True)
if __name__=='__main__':main()
