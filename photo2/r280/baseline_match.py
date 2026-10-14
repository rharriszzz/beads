"""Frozen image-only Phase1 outputs queried with the same search aperture as A.
No surface/occlusion/color inputs; no threshold changes or new detections.
"""
import numpy as np
from .common import mask_from_runs
from .detector import _record

def match(state,predictions,inventory):
 by={b['id']:b for b in inventory['beads']};out=[]
 for p in predictions:
  near=sorted(inventory['locations'],key=lambda o:np.linalg.norm(np.array([o['point']['x'],o['point']['y']])-p['center']))
  support=np.zeros(state['lum'].shape,bool);oid=None
  if near:
   o=near[0];dist=np.linalg.norm(np.array([o['point']['x'],o['point']['y']])-p['center'])
   if dist<=.6*p['diameter']+p.get('uncertainty_px',0.) and o['id'] in by:
    oid=o['id'];support=mask_from_runs(by[oid]['region']['runs'],support.shape)
  r=_record(p,state,support,1. if oid else 0.,dict(boundary=1.,foreground=1.,paper=0.),dict(phase1_id=oid),[])
  r.update(method='P',status='strong' if oid else 'insufficient',color=by[oid]['color'] if oid else 'unknown');out.append(r)
 return out
