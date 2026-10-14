"""Prediction perturbations: geometry only, no truth/color/identity raster access."""
import copy
import numpy as np
from .common import mask_from_runs,runs
from .detector import transform

def perturb(p,shape,shift=(0,0),scale=1.,angle=0.,uncertainty=0.):
 q=copy.deepcopy(p)
 for key in ('visible','silhouette'):q[key]=runs(transform(mask_from_runs(p[key],shape),p['center'],shift,scale,angle))
 q['center']=(np.array(p['center'])+shift).tolist();q['diameter']*=scale;q['uncertainty_px']=uncertainty
 return q

def cases(geometry,other,shape,stage='all'):
 base=geometry['predictions']
 yield 'A1-exact',base,dict(test='A1',kind='correct',level=0.)
 if stage=='A1':return
 for level in (.10,.25,.50):
  ps=[perturb(p,shape,[level*p['diameter'],0],uncertainty=level*p['diameter']) for p in base]
  yield f'A2-position-{level}',ps,dict(test='A2',kind='position',level=level)
 for scale in (.75,1.25):
  ps=[perturb(p,shape,scale=scale) for p in base]
  for p in ps:p['scale_uncertainty']=1/3 if scale<1 else .2
  yield f'A3-scale-{scale}',ps,dict(test='A3',kind='scale',level=scale)
 for angle in (-20.,20.):
  ps=[perturb(p,shape,angle=angle) for p in base]
  for p in ps:p['angle_uncertainty_deg']=20.
  yield f'A3-roll-{angle}',ps,dict(test='A3',kind='roll',level=angle)
 yield 'A3-camera-15',other['camera'],dict(test='A3',kind='camera',level=15.)
 # Correct primary hypotheses plus false rival hypotheses. Expected identity stays
 # attached to original site, never reassigned to the neighbor it lands on.
 for kind in ('paper','neighbor','midpoint','duplicate','phase','wrong-scale','wrong-roll'):
  ps=copy.deepcopy(base)
  for j,p in enumerate(base):
   if kind=='paper':q=perturb(p,shape,[0,-85])
   elif kind=='neighbor':
    # Explicit immediate +1/-1 construction neighbors; no nearest oracle pairs.
    b=base[j+1 if j+1<len(base) else j-1];q=copy.deepcopy(b)
   elif kind=='midpoint':
    b=base[j+1 if j+1<len(base) else j-1];q=perturb(p,shape,(np.array(b['center'])-p['center'])/2)
   elif kind=='duplicate':q=copy.deepcopy(p)
   elif kind=='phase':q=copy.deepcopy(other['phase'][j])
   elif kind=='wrong-scale':q=perturb(p,shape,scale=.60)
   else:q=perturb(p,shape,angle=45.)
   q['id']=p['id']+'-false';q['model_index']=p['model_index'];ps.append(q)
  yield 'A4-'+kind,ps,dict(test='A4',kind=kind,level=1.)

 # Adversarial identity permutation with no unchanged competitor bank. These
 # physically identical image hypotheses expose the limit of image-only identity
 # confirmation when the geometric model provides the wrong identity/address.
 ps=[]
 for j,p in enumerate(base):
  q=copy.deepcopy(base[(j+1)%len(base)]);q['id']=p['id']+'-false';q['model_index']=p['model_index'];ps.append(q)
 yield 'A4-unanchored-neighbor',ps,dict(test='A4',kind='unanchored-neighbor',level=1.)
