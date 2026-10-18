"""Causal R320 collision controls and literal witness locations."""
import time
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.geometry import contacts
from photo2.r320.controls import straight
from photo2.r295.geometry import AXES
from .packing import parameters,derive,curvature,planes,Chain,straight_gaps
OUT=ROOT/'photo2/r321/results'

def details(s,c):
 k=curvature(s);g,n,aa,bb=planes(s,iterations=150);rows=[]
 for d in [1,6,7]:
  section=slice([1,6,7].index(d)*s.n,([1,6,7].index(d)+1)*s.n);gg=g[section];nn=n[section];a=aa[section];b=bb[section];j=int(np.argmin(gg))
  rows.append(dict(offset=d,minimum_plane=float(gg[j]),median_plane=float(np.median(gg)),negative_planes=int(sum(gg<0)),array_pair=[int(a[j]),int(b[j])],indices=[int(s.indices[a[j]]),int(s.indices[b[j]])],normal=nn[j].tolist(),curvature=[float(k[a[j]]),float(k[b[j]])],phase=[float(s.phase[a[j]]),float(s.phase[b[j]])],inner_metric=[float(1-k[x]*s.p['minor']*np.sin(s.phase[x])) for x in [a[j],b[j]]],center_projected=s.pc[a[j]].tolist(),reference_u_fraction=float(s.inverse((s.a0+s.direction*s.station([s.indices[a[j]]])[0])%s.length)/s.inverse(s.length))))
 solids=[]
 for v in c['actual_solid_checks']:
  v=deepcopy(v);a,b=v['pair'];v['physical_indices']=[int(s.indices[a]),int(s.indices[b])]
  if 'point' in v:
   local=[(np.array(v['point'])-s.centers[j])@np.stack([s.g[key][j] for key in AXES]).T for j in [a,b]]
   v['local_points']=np.array(local).tolist();v['normalized_axial_and_radial']=[[float(q[0]/(.7*s.radius*s.axial)),float(np.hypot(q[1],q[2])/s.radius)] for q in local]
  solids.append(v)
 return dict(neighbors=rows,actual_solid_checks=solids,curvature_min=float(k.min()),curvature_max=float(k.max()))

def main():
 data=load()[0];rows=[]
 for hand in [-1,1]:
  for factor in [1.,1.16]:
   p=parameters(2800,1.95,.85,hand);p['minor']*=factor;s=Chain(p,data);c=contacts(s,seconds=1.)
   z=dict(kind='R320-radius-control',factor=factor,parameters=p,classification=c['classification'],summary=s.summary(),**details(s,c));rows.append(z)
   # Same rise and R, major bend removed, then old non-staircase orientation.
   ss=straight(s,s.length/(p['winding']*1.4*s.radius*s.axial),factor);cc=contacts(ss,seconds=1.)
   rows.append(dict(kind='straight-same-pitch',hand=hand,factor=factor,classification=cc['classification'],certificate=cc,exact_support_gaps=straight_gaps(p['turn'],p['axial'],p['minor'],s.length/p['winding'],p['radius'],True)))
  s,z=derive(parameters(2800,1.95,.85,hand),data);c=contacts(s,seconds=1.);rows.append(dict(kind='new-law',parameters=s.p,construction=z,classification=c['classification'],**details(s,c)))
 save(OUT/'failure-diagnosis.json',rows)
 for z in rows:
  print(z['kind'],z.get('parameters',{}).get('hand',z.get('hand')),z.get('factor'),z['classification'],z.get('neighbors'),flush=True)
if __name__=='__main__':main()
