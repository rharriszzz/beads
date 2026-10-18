"""Native whole-scene kernels, fixed photo cohorts, and explicit timer boundaries."""
import time,resource
from copy import deepcopy
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,digest,pixels
from photo2.r306.evidence import load
from photo2.r307.fast import grid
from photo2.r318.optics import make_light,Chain as OldChain
from photo2.r318.detect import principal
from photo2.r299.forward import shade
from photo2.r315.model import refined_trace
import photo2.r319.evidence as old_evidence
from .model import Chain
OUT=ROOT/'photo2/r320/results'
old_evidence.OUT=OUT

class Evidence:
 def __init__(self,data):
  self.epoch=read(ROOT/'photo2/r318/results/epoch2/epoch.json')
  self.local=old_evidence.Evidence(self.epoch)
  self.obs=self.epoch['observations']
  self.auto=read(ROOT/'photo2/r318/results/observations.json.gz')['observations']
  self.data=data
  self.baseline=OldChain(read(ROOT/'photo2/r319/results/best-full.json.gz')['parameters'],data)
  self.regions=[r for r in data['rows'] if r['kind']=='region' and not r['reflection']]
  self.parts=[pixels(r['pixels'])[::max(1,len(pixels(r['pixels']))//128)] for r in self.regions]
  self.region_xy=np.concatenate(self.parts);self.bounds=np.r_[0,np.cumsum(list(map(len,self.parts)))]
  self.cues=dict(np.load(ROOT/'photo2/r296/evidence/cues.npz'))
 def cohort(self,scope):
  obs=[o for o in self.auto if o['eligible']]
  if scope=='all':return obs
  low,high=(0,99) if scope==100 else (-100,99)
  tree=cKDTree(self.baseline.pc[(self.baseline.indices>=low)&(self.baseline.indices<=high)])
  return [o for o in obs if tree.query(o['point'])[0]<=35]
 def assignment(self,s,obs):
  # All bodies are alternatives. Geometry-support overlap, no predicted light.
  costs=np.linalg.norm(np.array([o['point'] for o in obs])[:,None]-s.pc[None],axis=2)*.001+2
  records=[]
  for i,o in enumerate(obs):
   xy=np.asarray(o['component']['pixels']);tr=refined_trace(s,xy)
   js,nn=np.unique(tr['owner'][tr['owner']>=0],return_counts=True)
   costs[i,js]=1-nn/len(xy)+costs[i,js]-2
   records.append(dict(id=o['id'],alternatives=[dict(index=int(s.indices[j]),fraction=float(n/len(xy))) for j,n in zip(js,nn)]))
  ii,jj=linear_sum_assignment(costs)
  mapping={obs[i]['id']:int(s.indices[j]) for i,j in zip(ii,jj)}
  return dict(mapping=mapping,records=records,binding=digest(dict(observations=obs,mapping=mapping)),policy='Frozen one-to-one maximum bright-support overlap, distance tie break. Unsupported assignments retained as low confidence. No reflection prediction used; all identities provisional.')
 def global_geometry(self,s):
  tr=refined_trace(s,self.region_xy);rows=[];claims={}
  for r,a,b in zip(self.regions,self.bounds[:-1],self.bounds[1:]):
   owners=tr['owner'][a:b];js,ns=np.unique(owners[owners>=0],return_counts=True)
   best=float(ns.max()/(b-a)) if len(ns) else 0
   rows.append(dict(id=r['id'],color=r.get('color'),pixels_sampled=int(b-a),modal_fraction=best))
   for j,n in zip(js,ns):
    if n>=20 and n/(b-a)>=.25:claims.setdefault(int(j),[]).append(dict(id=r['id'],color=r.get('color')))
  dual=[dict(index=int(s.indices[j]),regions=rr) for j,rr in claims.items() if len({str(z['color']) for z in rr})>1]
  cu=refined_trace(s,self.cues['xy']);paper=self.cues['paper'].astype(bool)
  return dict(regions=rows,mean_modal_fraction=float(np.mean([r['modal_fraction'] for r in rows])),distinct_color_dual_claims=dual,paper_fraction=float(np.mean(cu['owner'][paper]>=0)),unknown=int(tr['unknown'].sum()+cu['unknown'].sum()),rays=len(self.region_xy)+len(cu['owner']),interpretation='Historical positive pigment supports, sampled up to about 128 each; no complete contours or black silhouettes inferred. Correlated regions may overlap.')

def errors(obs,mapping,pred):
 rows=[]
 for o in obs:
  idx=mapping[o['id']];h=pred.get(idx);pt=h['point'] if h else None
  rows.append(dict(id=o['id'],color=o['color'],index=idx,observed=o['point'],predicted=pt,error_px=float(np.linalg.norm(np.array(pt)-o['point'])) if pt is not None else None))
 vals=[r['error_px'] for r in rows if r['error_px'] is not None];missing=len(rows)-len(vals)
 return dict(rows=rows,observations=len(rows),missing=missing,emax_px=max(vals) if vals and not missing else None,maximum_is_infinite=bool(missing),finite_only_max_px=max(vals) if vals else None,rms_finite_only_px=float(np.sqrt(np.mean(np.square(vals)))) if vals else None)

def evaluate(p,data,evidence,scope,obs,mapping,cached=None,keep=False):
 began=time.perf_counter();times={};t=began
 def tick(name):
  nonlocal t
  now=time.perf_counter();times[name]=now-t;t=now
 if cached is None:
  s=Chain(p,data);tick('positions_orientations_and_initial_acceleration')
  cert=s.certify(iterations=120,witnesses=False);tick('all_body_nonintersection')
  js=np.arange(s.n) if scope=='all' else np.flatnonzero((s.indices>=(0 if scope==100 else -100))&(s.indices<=99))
  if scope=='pilot':js=np.unique(np.r_[js,[int(np.flatnonzero(s.indices==v)[0]) for v in mapping.values()]])
  xy=grid(s,1.,js);tick('native_lattice_construction')
  tr=s.camera(xy);tick('camera_rays_and_normals')
  # Boundaries are obtained from the same first-hit ownership raster. This
  # includes hole/occlusion edges; no unsupported photographic hole scoring.
  ids=xy[:,1].astype(np.int64)*2540+xy[:,0].astype(np.int64);bd=np.zeros(len(ids),bool)
  for delta in [1,2540]:
   pos=np.searchsorted(ids,ids+delta);valid=pos<len(ids);a=np.flatnonzero(valid);b=pos[valid];same=ids[b]==ids[a]+delta
   if delta==1:same &= xy[b,1]==xy[a,1]
   a,b=a[same],b[same]
   hit=(tr['owner'][a]!=tr['owner'][b])&(~tr['unknown'][a])&(~tr['unknown'][b]);bd[a[hit]]=True;bd[b[hit]]=True
  tick('visible_boundary_extraction')
  local=evidence.local.measure(s);glob=evidence.global_geometry(s) if scope=='all' else None;tick('photographic_rays_outlines_ownership')
  cache=dict(s=s,cert=cert,xy=xy,tr=tr,js=js,boundary=bd,local=local,global_geometry=glob)
 else:
  cache=cached;s=cache['s'];s.p=p
  for key in ['positions_orientations_and_initial_acceleration','all_body_nonintersection','native_lattice_construction','camera_rays_and_normals','visible_boundary_extraction','photographic_rays_outlines_ownership']:times[key]=0.
  t=time.perf_counter()
 sh=shade(s,cache['tr'],make_light(p,s));tick('shadows_and_illumination')
 pred={};owner=cache['tr']['owner'];order=np.argsort(owner,kind='stable');cuts=np.r_[0,np.flatnonzero(np.diff(owner[order]))+1,len(order)]
 allowed=set(cache['js'])
 for a,b in zip(cuts[:-1],cuts[1:]):
  ix=order[a:b]
  if not len(ix):continue
  j=int(owner[ix[0]])
  if j<0 or j not in allowed:continue
  h=principal(cache['xy'][ix],sh['intensity'][ix])
  if h:pred[int(s.indices[j])]=h
 tick('reflection_localization')
 result=errors(obs,mapping,pred);tick('objective')
 result.update(times=times,total_seconds=time.perf_counter()-began,scope=scope,bodies=s.n,target_bodies=len(cache['js']),camera_rays=len(cache['xy']),unknown_camera=int(cache['tr']['unknown'].sum()),unknown_shadow_pairs=sh['unknown_shadow_pairs'],physical=cache['cert'],geometry=cache['local'],global_geometry=cache['global_geometry'],peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,cached=cached is not None)
 if keep:result['predictions']={str(k):v for k,v in pred.items()}
 return result,cache,sh
