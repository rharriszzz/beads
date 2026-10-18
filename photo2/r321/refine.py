"""Small joint physical/centerline/photo probes under frozen family maps."""
from copy import deepcopy
import itertools
import numpy as np
from photo2.r297.common import save,read
from .continue_campaign import resumed
from .campaign import OUT
from .model import corrected

def key(r):
 o=r.get('optical',{});g=o.get('geometry',{});e=o.get('emax_px')
 # Do not hide ownership regressions behind a low reflection maximum.
 return (e is None,g.get('dual_count',999),g.get('seam_conflict_fraction',1),e or 1e6)

def main():
 c=resumed()
 for parent_id in [99,108]:
  parent=c.rows[parent_id];p=parent['parameters'];local=[parent]
  for dr,da in itertools.product([-.035,0,.035],[-.025,0,.025]):
   if dr==da==0:continue
   q=deepcopy(p);q['radius']+=dr;q['axial']+=da
   existing=[r for r in c.rows if r['kind']=='joint-radius-thickness' and r['meta'].get('parent')==parent_id and abs(r['parameters']['radius']-q['radius'])<1e-10 and abs(r['parameters']['axial']-q['axial'])<1e-10]
   local.append(existing[0] if existing else c.trial(q,'joint-radius-thickness',dict(parent=parent_id)))
  good=[r for r in local if r.get('optical',{}).get('emax_px') is not None]
  best=min(good or [r for r in local if r.get('contact',{}).get('certified')],key=key)
  for dp,ds in itertools.product([-.10,0,.10],[-3.,0.,3.]):
   if dp==ds==0:continue
   q=deepcopy(best['parameters']);q['phase']+=dp;q['s0']+=ds
   local.append(c.trial(q,'registration',dict(parent=best['id'])))
  best=min([r for r in local if r.get('contact',{}).get('certified')],key=key)
  # Basis around the photographed anchor and actual inner-side collision.
  for knot,sign in itertools.product([0,14],[-1,1]):
   co=np.zeros(32);co[knot]=sign*3.;q=corrected(best['parameters'],co)
   c.trial(q,'photo-centerline',dict(parent=best['id'],knot=knot))
 # Preserve and evaluate the independently solved uniform-spacing interventions.
 for label in ['fixed-h-1','thickness-h-1','fixed-h1','thickness-h1']:
  r=read(OUT/f'centerline-{label}.json.gz');c.trial(r['parameters'],'contact-centerline',dict(source=label))
 # Literal R320 harmonic basis, expressed in the new cubic coefficient storage.
 p=deepcopy(c.rows[98]['parameters']);p['packing_spacing']='uniform';u=np.arange(32)/32
 A=np.eye(32)*4+np.roll(np.eye(32),1,axis=1)+np.roll(np.eye(32),-1,axis=1)
 for j,sign in itertools.product(range(4),[-1,1]):
  v=sign*3.*([np.cos,np.sin,np.cos,np.sin][j])(2*np.pi*[1,1,2,2][j]*u)
  c.trial(corrected(p,np.linalg.solve(A,6*v)),'harmonic-curvature-control',dict(coordinate=j,sign=sign),optical=False)
 save(OUT/'campaign-summary.json',dict(trials=len(c.rows),certified=sum(r['contact']['certified'] for r in c.rows),optical=sum('optical' in r for r in c.rows)))
if __name__=='__main__':main()
