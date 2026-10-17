"""Actual local-proposal cache reuse on the identical frozen photographic grid."""
import time
from copy import deepcopy
import numpy as np
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from photo2.r314.run import engine
from photo2.r314.geometry import contacts
from photo2.r315.model import refined_trace
from .model import Chain
from .renderer import RayLayers,Hybrid
OUT=ROOT/'photo2/r316/results'

def main():
    data=load()[0];e=engine();p=read(OUT/'narrow-model.json.gz')['parameters'];cache=RayLayers();rows=[]
    for name,change in [('cold',{}),('repeat',{}),('local-phase',{'compact_phase':(np.array(p['compact_phase'])+[0,0,.025]).tolist()}),('local-orientation',{'compact_tilt':[0,0,2.]}),('translation',{'translation':(np.array(p['translation'])+[1,0]).tolist()}),('radius',{'radius':p['radius']*1.01})]:
        q=deepcopy(p);q.update(change);t=time.perf_counter();s=Chain(q,data);geom=time.perf_counter()-t;t=time.perf_counter();cert=contacts(s,seconds=.35);ct=time.perf_counter()-t;t=time.perf_counter();oracle=refined_trace(s,e.xy);rt=time.perf_counter()-t;r=cache.trace(s,e.xy);t=time.perf_counter();metric=e.measure(r['owner'],r['unknown'],s.indices,0,True);score=time.perf_counter()-t
        row=dict(name=name,parameters=q,coordinates=len(e.xy),geometry_seconds=geom,contact_seconds=ct,physical=cert['classification'],r315_seconds=rt,layers=r['stats'],disagreements=int(np.sum(r['owner']!=oracle['owner'])),unknown_disagreements=int(np.sum(r['unknown']!=oracle['unknown'])),scoring_seconds=score,refined_full_seconds=geom+ct+rt+score,layered_full_seconds=geom+ct+r['stats']['total_seconds']+score);rows.append(row);print(name,row,flush=True)
    # Shape polygons reused exactly across image translation, exterior orthographic only.
    p=deepcopy(p);p.update(exterior=True,perspective=0);hy=Hybrid();poly=[]
    for dx in [0.,1.]:
        q=deepcopy(p);q['translation']=(np.array(p['translation'])+[dx,0]).tolist();s=Chain(q,data);r=hy.trace(s,e.xy);o=refined_trace(s,e.xy);poly.append(dict(dx=dx,stats=r['stats'],disagreements=int(np.sum(r['owner']!=o['owner']))))
    save(OUT/'cache-benchmark.json',dict(cases=rows,polygon_translation=poly,passed=all(r['disagreements']==r['unknown_disagreements']==0 for r in rows) and all(r['disagreements']==0 for r in poly),policy='Same frozen coordinates, exactly hashed individual camera/body states; partial local proposals can reuse unchanged isolated layers. Global shape, registration and camera invalidate affected layers.'))
if __name__=='__main__':main()
