"""Per-body visible boundaries/occlusion on every feasible primary perturbation.

Distances compare modeled visible boundaries with baseline modeled boundaries;
photographic segments remain separately supported, never inferred complete rims.
"""
import time
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r318 import optics
from photo2.r315.model import refined_trace,subset
from photo2.r306.evidence import load
from .common import *
from .evidence import Evidence,gate
from .local_model import Chain
optics.Chain=Chain

def boundary(mask):return mask&~ndi.binary_erosion(mask)

def main():
    t=time.time();epoch=read(OLD/'epoch2/epoch.json');ev=Evidence(epoch);data=load()[0];baseline=read(OUT/'baseline.json.gz');s=Chain(baseline['parameters'],data);b,arrays=ev.measure(s,True);baseowner=arrays['owner'];basebound={};basetree={}
    for idx in epoch['mapping'].values():
        j=int(np.flatnonzero(s.indices==idx)[0]);pts=ev.xy[boundary(baseowner==j).ravel()];basebound[idx]=pts;basetree[idx]=cKDTree(pts) if len(pts) else None
    rows=[]
    for path in sorted((OUT/'trials').glob('*.gz')):
        r=read(path)
        if not r.get('feasible') or r.get('missing'):continue
        s=Chain(r['parameters'],data);tr=refined_trace(s,ev.xy);own=tr['owner'].reshape(ev.shape);unknown=tr['unknown'].reshape(ev.shape);out=[]
        for idx in epoch['mapping'].values():
            j=int(np.flatnonzero(s.indices==idx)[0]);mask=(own==j)&~unknown;pts=ev.xy[boundary(mask).ravel()];old=basebound[idx];tree=basetree[idx]
            distances=np.r_[tree.query(pts)[0],cKDTree(pts).query(old)[0]] if len(pts) and tree is not None else np.array([])
            # Exact isolated projection restricted only to the same fixed evidence crop.
            near=np.linalg.norm(ev.xy-s.pc[j],axis=1)<=s.query_radius+1e-4
            iso=refined_trace(subset(s,[j]),ev.xy[near]);isolated=int(np.sum((iso['owner']>=0)&~iso['unknown']));visible=int(mask.sum());fullown=tr['owner'][near];hidden=(iso['owner']>=0)&~iso['unknown']&(fullown!=j)&(fullown>=0);oc,nn=np.unique(fullown[hidden],return_counts=True)
            out.append(dict(index=idx,visible_pixels=visible,isolated_pixels=isolated,occluded_pixels=int(hidden.sum()),occluders=[dict(index=int(s.indices[k]),pixels=int(n)) for k,n in zip(oc,nn)],visible_boundary_pixels=len(pts),symmetric_boundary_mean_px=float(distances.mean()) if len(distances) else None,symmetric_boundary_p95_px=float(np.percentile(distances,95)) if len(distances) else None,maximum_boundary_change_px=float(distances.max()) if len(distances) else None,visible_pixel_changes=int(np.sum(mask!=(baseowner==j)))))
        rows.append(dict(trial=r['id'],bodies=out,changed_owner_pixels=int(np.sum(own!=baseowner)),unknown=int(unknown.sum())))
        if len(rows)%50==0:save(OUT/'per-body-outline-response.json.gz',dict(rows=rows,policy='Fixed crop, native rays; isolated counts are occlusion diagnostics only, never photographic contour penalties. Boundary distances are model-to-baseline, not model-to-photo.'));print('OUTLINES',len(rows),time.time()-t,flush=True)
    save(OUT/'per-body-outline-response.json.gz',dict(rows=rows,seconds=time.time()-t,policy='Fixed crop, native rays; isolated counts are occlusion diagnostics only, never photographic contour penalties. Boundary distances are model-to-baseline, not model-to-photo.'))
    # Stress tests ensure visible owner merging cannot earn acceptance.
    controls=[]
    for name,oo in [('identity',baseowner.copy()),('all-visible-owners-merged',np.where(baseowner>=0,0,-1)),('shift12px',ndi.shift(baseowner,(0,12),order=0,cval=-1))]:
        m=ev.measure(s,owner=oo,unknown=np.zeros(ev.shape,bool));controls.append(dict(name=name,geometry=m,acceptance=gate(m,b)))
    assert controls[0]['acceptance']['passed'];assert all(not c['acceptance']['passed'] for c in controls[1:]);assert controls[1]['geometry']['dual_count']>0
    save(OUT/'geometry-stress-controls.json',controls)
    print('OUTLINES COMPLETE',len(rows),time.time()-t,flush=True)
if __name__=='__main__':main()
