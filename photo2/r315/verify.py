"""Independent state/support replay, original Python rays and root-based grazing audit."""
import re,time,subprocess
from pathlib import Path
from types import MethodType
import numpy as np
from scipy.optimize import brentq,minimize_scalar
from scipy.spatial import cKDTree
from PIL import Image
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r295.geometry import Chain as Original,AXES
from photo2.r313.continuation_verify import independent_support
from photo2.r279.geometry import R
from photo2.r314.run import engine
from .model import Chain,refined_trace
from .diagnose import OUT,brackets

def sdf(s,q):
 q=np.asarray(q)/s.dims;t=(1-s.hole)/2;r=t*s.rounding;a=t-r;rho=np.hypot(q[...,1],q[...,2]);u=abs(rho-(1+s.hole)/2*R)-a*R;v=abs(q[...,0])/(.7/t)-a*R
 return (np.hypot(np.maximum(u,0),np.maximum(v,0))+np.minimum(np.maximum(u,v),0)-r*R)*min(s.dims)

def root_owner(s,xy):
 # Root isolation on a uniform depth mesh, independently refine every local minimum.
 base=((xy-s.offset)/s.scale)@np.array([s.right,s.down]);ray=s.eye-base/s.distance;ray/=np.linalg.norm(ray);hits=[]
 for j in s.tree.query_ball_point(xy,s.query_radius+1e-4):
  delta=base-s.centers[j];mid=-delta@ray;perp=delta@delta-mid*mid
  if perp>=s.bound*s.bound:continue
  half=np.sqrt(s.bound*s.bound-perp);q=np.array([delta@s.g[k][j] for k in AXES]);v=np.array([ray@s.g[k][j] for k in AXES]);ts=np.linspace(mid-half,mid+half,2049);values=sdf(s,q+ts[:,None]*v)-1e-5;roots=[]
  for i in np.flatnonzero((values[:-1]<0)&(values[1:]>=0)):
   roots.append(brentq(lambda t:float(sdf(s,q+t*v)-1e-5),ts[i],ts[i+1],xtol=1e-12))
  minima=np.flatnonzero((values[1:-1]<values[:-2])&(values[1:-1]<values[2:]))+1
  for i in minima:
   if values[i]<0:continue
   opt=minimize_scalar(lambda t:float(sdf(s,q+t*v)-1e-5),bounds=(ts[i-1],ts[i+1]),method='bounded',options={'xatol':1e-13})
   if opt.fun<0 and values[i+1]>0:roots.append(brentq(lambda t:float(sdf(s,q+t*v)-1e-5),opt.x,ts[i+1],xtol=1e-12))
  if roots:hits.append((max(roots),j))
 return max(hits)[1] if hits else -1

def main():
 began=time.monotonic();e=engine();data=load()[0];receipts=[];names=['baseline','translation','compact']+(['narrow'] if (OUT/'narrow-model.json.gz').exists() else [])
 for name in names:
  r=read(OUT/f'{name}-model.json.gz');s=Chain(r['parameters'],data);a=np.load(OUT/f'{name}-raster.npz');np.testing.assert_array_equal(s.centers,r['positions']['centers']);np.testing.assert_array_equal(s.pc,r['positions']['projected']);assert list(s.indices[(s.indices>=-100)&(s.indices<=99)])==list(range(-100,100))
  pairs=cKDTree(s.centers).query_pairs(2*s.bound+1e-8,output_type='ndarray');ws={tuple(w['pair']):w for w in r['physical']['witnesses']};assert len(pairs)==len(ws)
  for i,j in pairs:
   w=ws[int(i),int(j)];n=np.array(w['normal']);gap=(s.centers[j]-s.centers[i])@n-independent_support(s,n,s.g[AXES[0]][i])-independent_support(s,n,s.g[AXES[0]][j]);assert abs(gap-w['gap_units'])<1e-9;assert gap>1e-6
  ix=np.unique(np.r_[np.arange(0,len(e.xy),97),np.flatnonzero(e.m['core'].ravel())[::5],np.flatnonzero(e.m['edges'].any(0).ravel())]);tr=Original.trace(s,e.xy[ix]);known=~tr['unknown'];np.testing.assert_array_equal(tr['owner'][known],a['owner'][ix][known]);assert not a['unknown'].any()
  for part,key in enumerate(['development','comparison','buffer']):
   measured=e.measure(a['owner'],a['unknown'],s.indices,part,True)
   for k in measured:assert measured[k]==r[key][k],(name,key,k)
  assert brackets(e,dict(owner=a['owner'],unknown=a['unknown']))==read(OUT/f'{name}-brackets.json.gz')
  tt=np.load(OUT/f'{name}-target.npz');j=np.arange(0,len(tt['xy']),31);tr=Original.trace(s,tt['xy'][j]);known=~tr['unknown'];np.testing.assert_array_equal(tr['owner'][known],tt['owner'][j][known]);receipts.append(dict(name=name,positions=s.n,contact_witnesses=len(pairs),original_python_rays=len(ix)+len(j),grazing_original_unknown=int((~known).sum()),all_metrics_exact=True));print('VERIFIED',name,flush=True)
 # Independently resolve every originally unknown baseline ray with 1D roots.
 s=Chain(read(OUT/'baseline-model.json.gz')['parameters'],data);old=np.load(ROOT/'photo2/r314/results/models/R306-2405.npz');ix=np.flatnonzero(old['unknown']);a=np.load(OUT/'baseline-raster.npz');owners=np.array([root_owner(s,xy) for xy in e.xy[ix]]);np.testing.assert_array_equal(owners,a['owner'][ix]);print('ROOT VERIFIED',len(ix),flush=True)
 ledger=read(OUT/'ledger.json.gz');counter=0
 for r in ledger:
  for c in r['candidates']:
   assert c['isolated_fraction']+1e-10>=c['visible_fraction']
   for o in c['occluders']:assert o['depth_difference_min']>=-1e-6;assert o['removed_candidate_visible_fraction']+1e-10>=c['visible_fraction'];counter+=1
 c=read(OUT/'contacts.json.gz');refined=[r for r in c['pairs'] if r['refined']]
 for r in refined:assert r['actual_surface_residual']<1e-7;assert r['solid_surface_upper']>=r['support_lower']-1e-8
 assert sha(ROOT/'photo2/r314/evidence/maps.npz')==read(OUT/'diagnosis-receipt.json')['evidence_sha']
 images=[]
 manifest=read(OUT/'review-manifest.json');by={(r['model'],r['id']):r for r in ledger}
 for item in manifest:
  r=by[item['model'],item['id']];x,y=np.rint(r['point']).astype(int);x-=e.m['origin'][0];y-=e.m['origin'][1]
  raw=e.m['native'][y-40:y+41,x-40:x+41];panel=np.array(Image.open(OUT/item['image']))
  np.testing.assert_array_equal(panel[38:281:3,0:243:3],raw)
 assert read(OUT/'bright-placement.json.gz')['all_inherited']==read(ROOT/'photo2/r314/results/observation-catalog.json.gz')['all_inherited_observations']
 for p in (OUT/'review').glob('*.png'):
  with Image.open(p) as im:im.verify()
  images.append(p.name)
 links=re.findall(r'(?:src|href)="([^"]+)"',(OUT/'index.html').read_text())
 for link in links:assert (OUT/link).exists(),link
 parent=read(OUT/'start.json')['head'];modified=subprocess.check_output(['git','diff','--diff-filter=MDRT',parent,'--name-only'],cwd=ROOT,text=True).splitlines()
 for p in modified:
  assert p in ['AGENTS.md','SESSION_HANDOFF.md','REQUEST_LOG.md'],p
  assert subprocess.check_output(['git','show',parent+':'+p],cwd=ROOT) in (ROOT/p).read_bytes()
 save(OUT/'verification.json',dict(passed=True,utc=utc(),seconds=time.monotonic()-began,models=receipts,independent_root_grazing_rays=len(ix),counterfactual_records=counter,refined_actual_solid_bounds=len(refined),images=len(images),raw_photo_crops_exact=len(manifest),all_811_observations_unchanged=True,local_links=len(links),historical_changes=modified,evidence_hash_unchanged=True,limitations='Independent Python rays stratified; all positions and complete contact witnesses verified. Numerical agreement is not photographic correctness.'))
if __name__=='__main__':main()
