"""Independent final verification; complete pair certificates and Python native rays."""
import time,subprocess,re
from pathlib import Path
from types import MethodType
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r295.geometry import Chain as Python,AXES
from .diagnose_geometry import make
from .objective_v2 import SurfaceObjective

OUT=ROOT/'photo2/r313/continuation'
def independent_support(s,n,axis):
 dot=np.sum(n*axis,axis=-1);transverse=np.linalg.norm(np.cross(n,axis),axis=-1);rr=(1-s.hole)*s.rounding/2
 return s.radius*((1-rr)*transverse+.7*s.axial*(1-s.rounding)*abs(dot)+np.hypot(rr*transverse,.7*s.axial*s.rounding*dot))

def main():
 began=time.monotonic();start=read(OUT/'start.json');ev=OUT.parent/'evidence';assert sha(ev/'maps.npz')==start['evidence_sha256'];m=dict(np.load(ev/'maps.npz'));eng=SurfaceObjective(m,read(ev/'freeze.json'));data,_,_=load();receipts=[]
 for p,h in start['preserved_trials'].items():assert sha(ROOT/p)==h,p
 for manifest in [read(ev/'fitting-freeze.json')['sources'],read(OUT/'search-plan.json')['sources']]:
  for p,h in manifest.items():assert sha(ROOT/p)==h,p
 # Verify model state and all reported arithmetic, never equate numerical equality with photo accuracy.
 for path in sorted((OUT/'models').glob('*.json.gz')):
  r=read(path);s=make(r['parameters'],data,r['implementation']);a=dict(np.load(path.with_name(r['name']+'.npz')));np.testing.assert_allclose(s.centers,r['positions']['centers'],atol=1e-12,rtol=0);np.testing.assert_allclose(s.pc,r['positions']['projected'],atol=1e-12,rtol=0);np.testing.assert_array_equal(s.indices,r['positions']['indices']);assert r['cohort']==list(range(-100,100));assert int(np.sum((s.indices>=-100)&(s.indices<=99)))==200
  frame=np.stack([s.g[k] for k in AXES],axis=1);np.testing.assert_allclose(frame@frame.transpose(0,2,1),np.broadcast_to(np.eye(3),frame.shape),atol=1e-9)
  pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray');witness={tuple(w['pair']):w for w in r['physical']['witnesses']};assert len(pairs)==len(witness);gaps=[]
  for i,j in pairs:
   w=witness[int(i),int(j)];n=np.array(w['normal']);gap=float((s.centers[j]-s.centers[i])@n-independent_support(s,n,s.g[AXES[0]][i])-independent_support(s,n,s.g[AXES[0]][j]));assert abs(gap-w['gap_units'])<1e-9
   if w['separated']:assert gap>1e-6
   else:
    checks=[z for z in r['physical']['actual_solid_checks'] if z['pair']==w['pair']];assert checks and checks[0]['state']=='certified-nonintersection'
   gaps.append(gap)
  ix=np.unique(np.r_[np.linspace(0,len(eng.xy)-1,1500).astype(int),np.flatnonzero(m['material'].ravel())[::7],np.flatnonzero(m['edges'].any(0).ravel()),np.flatnonzero(m['paper'].ravel())[::25]])
  # Newly selected shared-shape models and old baselines use the same independent Python marcher.
  method=s.trace;s.trace=MethodType(Python.trace,s);tr=s.trace(eng.xy[ix]);s.trace=method;np.testing.assert_array_equal(tr['owner'],a['owner'][ix]);np.testing.assert_array_equal(tr['unknown'],a['unknown'][ix])
  for split,label in [(0,'development'),(1,'comparison'),(2,'buffer')]:assert eng.measure(a['owner'],a['unknown'],s.indices,split,True)==r[label],(r['name'],label)
  receipts.append(dict(name=r['name'],positions=s.n,target=200,pairs=len(pairs),minimum_margin=min(gaps),independent_python_rays=len(ix),exact_positions=True,exact_metrics=True,exact_rays=True));print('verified',r['name'],len(ix),'rays',len(pairs),'pairs',flush=True)
 # Independently evaluate every delivered actual-solid overlap witness at its saved point.
 actual=[]
 for p in sorted((OUT/'diagnostics').glob('*.json.gz')):
  r=read(p);s=make(r['parameters'],data,r['implementation'])
  for q in r['physical']['actual_solid_checks']:
   if q['state']!='demonstrated-interpenetration':continue
   xyz=np.array(q['point']);values=[]
   for k in q['pair']:
    delta=xyz-s.centers[k];local=np.array([delta@s.g[key][k] for key in AXES])/s.dims;h=s.hole;f=s.rounding;t=(1-h)/2;radial=abs(np.hypot(local[1],local[2])-(1+h)/2*s.radius)-(1-f)*t*s.radius
    # local coordinates divide by dims, thus use original source R, not fitted radius.
    from photo2.r279.geometry import R
    radial=abs(np.hypot(local[1],local[2])-(1+h)/2*R)-(1-f)*t*R;ax=abs(local[0])/(.7/t)-(1-f)*t*R;sd=(np.hypot(max(radial,0),max(ax,0))+min(max(radial,ax),0)-f*t*R)*min(s.dims);values.append(float(sd))
   assert max(values)<-1e-7;np.testing.assert_allclose(values,q['implicit_values'],atol=1e-10,rtol=0);actual.append(dict(case=r['id'],pair=q['pair'],values=values))
 trials=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];sel=read(OUT/'search-selection.json');assert sel['sealed'] and len(trials)==sel['evaluations'];feasible=[r for r in trials if r['feasible']];assert abs(min(r['score'] for r in feasible)-sel['selected']['score'])<1e-12;assert sel['seconds']<=read(OUT/'search-plan.json')['seconds']+5
 # No previously tracked source or photograph may be changed; additive handoff allowed.
 parent=read(ev/'start.json')['head'];modified=subprocess.check_output(['git','diff','--diff-filter=MDRT',parent,'--name-only'],cwd=ROOT,text=True).splitlines()
 for p in modified:
  assert p in ['AGENTS.md','SESSION_HANDOFF.md','REQUEST_LOG.md'],p
  assert subprocess.check_output(['git','show',parent+':'+p],cwd=ROOT) in (ROOT/p).read_bytes()
 images=[];links=[]
 for p in (OUT/'review').glob('*.png'):
  with Image.open(p) as im:im.verify()
  images.append(p.name)
 for link in re.findall(r'(?:src|href)="([^"]+)"',(OUT/'index.html').read_text()):
  if link=='verification.json':continue
  assert (OUT/link).exists(),link;links.append(link)
 result=dict(passed=True,utc=utc(),seconds=time.monotonic()-began,models=receipts,total_positions=sum(r['positions'] for r in receipts),independent_contact_pairs=sum(r['pairs'] for r in receipts),independent_python_rays=sum(r['independent_python_rays'] for r in receipts),actual_solid_penetration_witnesses_verified=len(actual),initial_evaluations_preserved=426,new_evaluations=len(trials),maps_unchanged=True,shared_rigid_bead_shape=True,old_tracked_modifications=modified,pngs=len(images),local_links=len(links),limits='Native ray agreement sampled, complete positions/metrics/contact certificates checked. Photographic outline correctness and physical identities are not established by computational verification.')
 save(OUT/'verification.json',result);save(OUT/'penetration-verification.json',actual);print('PASS',result['seconds'],flush=True)
if __name__=='__main__':main()
