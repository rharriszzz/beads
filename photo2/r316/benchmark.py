"""Same-coordinate owner equivalence and separated cold/warm timings."""
import time,resource
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import contacts
from photo2.r295.geometry import Chain as Python,AXES
from photo2.r315.model import refined_trace,subset
from photo2.r307.fast import grid
from .model import Chain
from .renderer import Hybrid,RayLayers,sandwich
OUT=ROOT/'photo2/r316/results'

def contour_delta(a,b,xy):
    # Native owner disagreement is stronger than contour proximity; coordinates fixed.
    bad=np.flatnonzero(a!=b)
    return dict(disagreements=len(bad),pixels=xy[bad].tolist(),oracle_owner=b[bad].tolist(),candidate_owner=a[bad].tolist(),maximum_px=0. if not len(bad) else None,p95_px=0. if not len(bad) else None)

def main():
    data=load()[0];e=engine();rows=[];models=[]
    for name,path in [('R306','photo2/r315/results/baseline-model.json.gz'),('focused3','photo2/r314/results/models/R313-focused-3.json.gz'),('narrow','photo2/r315/results/narrow-model.json.gz'),('opposite','photo2/r314/results/models/R312-local.json.gz')]:
        models.append((name,read(ROOT/path)['parameters']))
    base=deepcopy(models[0][1])
    for name,updates in [('convex-ortho',dict(perspective=0,exterior=True,edge=.344,face=.8)),('legacy-ortho',dict(perspective=0)),('convex-finite',dict(perspective=.0004,exterior=True,edge=.344,face=.8)),('convex-tilt',dict(perspective=0,exterior=True,edge=.5,face=.55,tilt=18))]:
        p=deepcopy(base);p.update(updates);models.append((name,p))
    for name,p in models:
        t=time.perf_counter();s=Chain(p,data);geometry=time.perf_counter()-t
        ix=np.flatnonzero((s.indices>=-100)&(s.indices<=99));xy=grid(s,1.,ix);assert len(ix)==200
        t=time.perf_counter();original=s.trace(xy);oldtime=time.perf_counter()-t
        t=time.perf_counter();oracle=refined_trace(s,xy);refinet=time.perf_counter()-t
        hy=Hybrid();r=hy.trace(s,xy);hw=hy.trace(s,xy)
        ly=RayLayers();l=ly.trace(s,xy);lw=ly.trace(s,xy)
        sample=np.unique(np.r_[np.arange(0,len(xy),41),np.flatnonzero(r['owner']!=oracle['owner'])]);t=time.perf_counter();ind=Python.trace(s,xy[sample]);python_seconds=time.perf_counter()-t;known=~ind['unknown']
        eq=contour_delta(r['owner'],oracle['owner'],xy);leq=contour_delta(l['owner'],oracle['owner'],xy)
        pybad=int(np.sum(ind['owner'][known]!=oracle['owner'][sample][known]))
        t=time.perf_counter();cert=contacts(s,seconds=.4);ct=time.perf_counter()-t
        t=time.perf_counter();ev=refined_trace(s,e.xy);evtime=time.perf_counter()-t;t=time.perf_counter();score=e.measure(ev['owner'],ev['unknown'],s.indices,0,True);scoretime=time.perf_counter()-t
        row=dict(name=name,parameters=p,rays=len(xy),target_bodies=200,full_bodies=s.n,geometry_seconds=geometry,r314_seconds=oldtime,r315_seconds=refinet,r314_unknown=int(original['unknown'].sum()),r314_known_disagreements=int(np.sum((original['owner']!=oracle['owner'])&~original['unknown'])),oracle_unknown=int(oracle['unknown'].sum()),hybrid=r['stats'],hybrid_warm=hw['stats'],ray_layers=l['stats'],ray_layers_warm=lw['stats'],hybrid_equivalence=eq,layer_equivalence=leq,python_rays=len(sample),python_unknown=int(ind['unknown'].sum()),python_known_disagreements=pybad,python_seconds=python_seconds,contact_seconds=ct,physical=cert['classification'],frozen_scoring_coordinates=len(e.xy),evidence_render_seconds=evtime,scoring_seconds=scoretime,full_refined_evaluation_seconds=geometry+ct+evtime+scoretime,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        rows.append(row);save(OUT/'benchmarks.json',rows);np.savez_compressed(OUT/f'benchmark-{name}.npz',xy=xy,oracle=oracle['owner'],hybrid=r['owner'],layers=l['owner'],unknown=oracle['unknown']);save(OUT/f'orders-{name}.json.gz',r.get('orders',[]));print(name,'rays',len(xy),'refined',round(refinet,3),'hybrid',round(r['stats']['total_seconds'],3),'layer',round(l['stats']['total_seconds'],3),'warm',round(lw['stats']['total_seconds'],3),'bad',eq['disagreements'],leq['disagreements'],pybad,flush=True)
    save(OUT/'benchmark-summary.json',dict(passed=all(not r['hybrid_equivalence']['disagreements'] and not r['layer_equivalence']['disagreements'] and not r['python_known_disagreements'] for r in rows),models=len(rows),rays=sum(r['rays'] for r in rows),python_rays=sum(r['python_rays'] for r in rows),policy='Warm cache is identical geometry and coordinates only, never a proposal speedup. Orthographic controls are distinct from saved finite-camera models. Peak RSS is cumulative process high water.'))
if __name__=='__main__':main()
