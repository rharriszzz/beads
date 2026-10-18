"""Bounded photo-sized physical families; every proposal saved before selection."""
import time,itertools
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,save,read,utc,sha
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r320.audit import neighbor_gaps
from .packing import parameters,derive,curvature
from .evaluate import Evidence,evaluate
OUT=ROOT/'photo2/r321/results'

class Campaign:
 def __init__(self):
  self.data=load()[0];self.ev=Evidence(self.data);self.rows=[];self.maps={}
 def trial(self,p,kind,meta=None,optical=True):
  began=time.perf_counter();s,z=derive(p,self.data);r=dict(id=len(self.rows),kind=kind,meta=meta or {},parameters=s.p if s else p,construction=z)
  if s:
   t=time.perf_counter();c=contacts(s,seconds=.3);c.pop('witnesses',None);r['contact_seconds']=time.perf_counter()-t;r['contact']=c
   k=curvature(s);r['curvature']=dict(minimum=float(k.min()),maximum=float(k.max()),absolute_max=float(abs(k).max()))
   t=time.perf_counter();gaps=neighbor_gaps(s);r['gap_measurement_seconds']=time.perf_counter()-t;r['neighbors']=[{k:v for k,v in g.items() if k!='pairs'} for g in gaps]
   if c['certified'] and optical:
    family=(p['count'],p['hand'])
    if family not in self.maps:
     self.maps[family]=self.ev.assignment(s,self.ev.obs);save(OUT/f'epoch-N{family[0]}-h{family[1]}.json.gz',dict(parameters=s.p,observations=self.ev.obs,**self.maps[family]))
    o,_,_=evaluate(s.p,self.data,self.ev,'pilot',self.ev.obs,self.maps[family]['mapping']);r['optical']=o
  r['seconds']=time.perf_counter()-began;r['utc']=utc();self.rows.append(r);save(OUT/'trials'/f'{r["id"]:04}.json.gz',r)
  print('TRIAL',r['id'],kind,p['count'],p['hand'],round(p['radius'],5),round(p['axial'],5),r.get('contact',{}).get('classification'),r.get('optical',{}).get('emax_px'),round(r['seconds'],3),flush=True)
  return r

def main():
 c=Campaign();save(OUT/'start.json',dict(start='2026-10-18T04:58:00Z',scientific_cutoff='2026-10-18T05:22:00Z',deadline='2026-10-18T05:28:00Z',photo_sha256=sha(ROOT/'beads-photo-2.jpg'),beads_pov_sha256=sha(ROOT/'beads.pov')))
 for n,r,a,h in itertools.product([2200,2400,2600,2800,2801,3000,3200],[1.85,1.95,2.05],[.65,.85],[-1,1]):c.trial(parameters(n,r,a,h),'physical-family')
 save(OUT/'campaign-summary.json',dict(trials=len(c.rows),certified=sum(r['contact']['certified'] for r in c.rows),optical=sum('optical' in r for r in c.rows)))
if __name__=='__main__':main()
