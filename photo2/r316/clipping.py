"""Continuous convex clipping versus Boolean operations on the same inner polygons."""
import time
from copy import deepcopy
import numpy as np
from matplotlib.path import Path
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save
from photo2.r306.evidence import load
from .model import Chain
from .renderer import sandwich
OUT=ROOT/'photo2/r316/results'

def clip(p,q):
    out=p.copy()
    for a,b in zip(q,np.roll(q,-1,axis=0)):
        if not len(out):break
        edge=b-a;v=out-a;side=edge[0]*v[:,1]-edge[1]*v[:,0];nxt=[]
        for i in range(len(out)):
            j=(i+1)%len(out);inside=side[i]>=0;other=side[j]>=0
            if inside:nxt.append(out[i])
            if inside!=other:nxt.append(out[i]+side[i]/(side[i]-side[j])*(out[j]-out[i]))
        out=np.asarray(nxt).reshape(-1,2)
    return out

def main():
    p=deepcopy(read(ROOT/'photo2/r315/results/baseline-model.json.gz')['parameters']);p.update(perspective=0,exterior=True);s=Chain(p,load()[0]);ids=np.flatnonzero((s.indices>=-20)&(s.indices<=25));pairs=sorted(cKDTree(s.pc[ids]).query_pairs(2*s.query_radius));rows=[]
    for aa,bb in pairs[:40]:
        a,b=ids[aa],ids[bb];pa=sandwich(s,a)['inner'];pb=sandwich(s,b)['inner'];lo=np.floor(np.minimum(pa.min(0),pb.min(0))).astype(int)-1;hi=np.ceil(np.maximum(pa.max(0),pb.max(0))).astype(int)+1;yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xy=np.c_[xx.ravel(),yy.ravel()];ma=Path(pa).contains_points(xy);mb=Path(pb).contains_points(xy)
        t=time.perf_counter();poly=clip(pa,pb);clipping=time.perf_counter()-t;t=time.perf_counter();mask=Path(poly).contains_points(xy) if len(poly)>=3 else np.zeros(len(xy),bool);raster=time.perf_counter()-t;t=time.perf_counter();boolean=ma&mb;booltime=time.perf_counter()-t;rows.append(dict(pair=s.indices[[a,b]].tolist(),pixels=len(xy),overlap_pixels=int(boolean.sum()),clipping_seconds=clipping,clipped_raster_seconds=raster,boolean_seconds=booltime,disagreements=int(np.sum(mask!=boolean)),vertices=len(poly)))
    save(OUT/'clipping.json',dict(cases=rows,passed=all(r['disagreements']==0 for r in rows),policy='Same inner convex polygons only; timing Boolean intersection assumes cached footprint masks. Continuous clipping also must rasterize for native-grid scoring. Neither operation fills a bore or resolves unknown depth.'))
if __name__=='__main__':main()
