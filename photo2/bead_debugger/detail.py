"""Cached local native-pixel measurements; geometry and lighting caches separate."""
from __future__ import annotations
import json, hashlib, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from .generate import ROOT,sha,save
from .surface import Scene,cache_key,shade,highlight,moments,EPS
from .lighting import plane_points

ARTIFACTS=ROOT/'photo2/review/r257'

def summary(data,gi,weight=None):
    take=data['owner']==gi;w=np.ones(take.sum()) if weight is None else weight[take]
    m=moments(data['xy'][take],w)
    return dict(centroid=m['centroid'] if m else None,area_px2=float(w.sum()),samples=int(take.sum()))


def local_geometry(scene,gi):
    indices=sorted(set((gi+d)%scene.config['n'] for d in [0,-1,1,-6,6,-7,7]));box=scene.box(indices,pad=18)
    native=scene.grid(box);coarse={s:scene.grid(box,s) for s in [2,4]}
    h=box[3]-box[1];w=box[2]-box[0];owner=native['owner'].reshape(h,w)
    boundary=np.zeros((h,w),bool)
    boundary[1:] |= owner[1:]!=owner[:-1];boundary[:-1] |= owner[:-1]!=owner[1:]
    boundary[:,1:] |= owner[:,1:]!=owner[:,:-1];boundary[:,:-1] |= owner[:,:-1]!=owner[:,1:]
    # Four subpixel rays in each ownership-boundary pixel, centered ±.25px.
    edge=native['xy'][boundary.ravel()];subxy=(edge[:,None,:]+np.array([[-.25,-.25],[.25,-.25],[-.25,.25],[.25,.25]])).reshape(-1,2)
    sub=scene.camera(subxy)
    adaptive={k:np.concatenate([v[~boundary.ravel()],sub[k]]) for k,v in native.items()};weight=np.r_[np.ones((~boundary).sum()),np.full(len(subxy),.25)]
    beads=[]
    for j in indices:
        convergence={str(s):summary(coarse[s],j) for s in [4,2]};convergence['1']=summary(native,j);convergence['adaptive']=summary(adaptive,j,weight)
        for s in ['4','2']:convergence[s]['area_px2']*=int(s)**2
        ref=convergence['adaptive']['centroid']
        for row in convergence.values():row['distance_to_adaptive_px']=float(np.linalg.norm(np.array(row['centroid'])-ref)) if row['centroid'] is not None and ref is not None else None
        own=scene.outward(j);take=native['owner']==j
        beads.append(dict(generator_index=j,legacy_k=(j-scene.config['origin'])%scene.config['n'],center_xyz=scene.centers[j].tolist(),center_xy=scene.pc[j].tolist(),
                          outward=own,centroid=convergence['adaptive']['centroid'],convergence=convergence,
                          visible=bool(ref is not None),visibility='visible sampled area' if ref is not None else 'no reliable visible area at native + boundary sampling; subpixel exposure not excluded',
                          surface_mean_xyz=np.mean(native['points'][take],axis=0).tolist() if take.any() else None))
    metadata=dict(box=box,indices=indices,beads=beads,ray_resolution_px=1,adaptive_grid_px=.5,adaptive_pixels=int(boundary.sum()),
                  native_rays=len(native['xy']),adaptive_rays=len(subxy),unfinished_camera_pairs=int(native['unknown'].sum()+sub['unknown'].sum()),
                  camera_epsilon_units=EPS,plane_z=scene.plane_z,geometry_version=scene.version)
    return metadata,native


def calculate(scene,gi,light,observations,geometry=None):
    meta,data=geometry or local_geometry(scene,gi)
    # Copy metadata because light switches share the geometric calculation.
    meta=json.loads(json.dumps(meta));sh=shade(scene,data,light);box=meta['box']
    nearby=[o for o in observations if box[0]<=o['xy'][0]<box[2] and box[1]<=o['xy'][1]<box[3]]
    hit=scene.camera(np.array([o['xy'] for o in nearby])) if nearby else None
    for i,o in enumerate(nearby):o=dict(o);nearby[i]=o;o['local_owner']=int(hit['owner'][i])
    for b in meta['beads']:
        j=b['generator_index'];mask=data['owner']==j;h=highlight(data['xy'][mask],sh['specular'][mask]);b['highlight']=h
        if h:
            ix=np.flatnonzero(mask)[np.argmax(sh['specular'][mask])];h['peak_xyz']=data['points'][ix].tolist();h['peak_normal']=data['normal'][ix].tolist()
        found=[o for o in nearby if o['local_owner']==j];b['observed_reflections']=found
        reliable=[o for o in found if o['reliable_candidate']]
        b['reflection_error_px']=float(np.linalg.norm(np.array(h['centroid'])-reliable[0]['xy'])) if h and len(reliable)==1 else None
        b['match_status']='one reliable photo candidate conditionally owned' if len(reliable)==1 else 'ambiguous or no reliable photo reflection; no forced nearest match'
    points=[]
    for i in np.flatnonzero(np.isin(data['owner'],meta['indices'])):
        points.append([int(data['xy'][i,0]),int(data['xy'][i,1]),int(data['owner'][i]),round(float(sh['specular'][i]),6),round(float(sh['cast_shadow'][i]),4),round(float(sh['back_facing'][i]),4),round(float(sh['self_cast'][i]),4),round(float(sh['neighbor_cast'][i]),4)])
    # Background diagnostics use all-scene rays, and retain observations separately.
    yy,xx=np.mgrid[box[1]:box[3]:3,box[0]:box[2]:3];xy=np.c_[xx.ravel(),yy.ravel()];camera=scene.camera(xy);bg=camera['owner']<0;xy=xy[bg];p=plane_points(scene,xy)
    from .surface import directions
    blocked=np.zeros(len(xy));un=0
    for d,w in directions(light,9):
        q,u=scene.blocked(p+[0,0,.001],d);blocked+=w*q;un+=u
    shadows=json.loads((ARTIFACTS/'observations.json').read_text())['shadows'];observed_shadow=[]
    for p,v in zip(shadows['xy'],shadows['deficit']):
        if box[0]<=p[0]<box[2] and box[1]<=p[1]<box[3]:observed_shadow.append([*p,v])
    meta.update(schema=1,selected_generator_index=gi,model_id=scene.mid,lighting=light,observed_reflections=nearby,
                footprint=points,footprint_columns=['x','y','owner_generator_index','specular_relative','cast_shadow_fraction','back_facing_fraction','self_cast_fraction','neighbor_cast_fraction'],
                background_shadows=np.c_[xy,blocked].tolist(),observed_background_deficit=observed_shadow,background_grid_px=3,
                unfinished_shadow_pairs=int(sh['unfinished_shadow_pairs']+un),
                uncertainty=dict(lighting='Competing globally fitted configurations; conditional on inherited geometry. See heldout metrics.',
                                 numerical='4/2/1px versus boundary-adaptive 2x2 estimates; not an error bound. Highlights evaluated at 1px; extended source uses 9x9 angular quadrature.',
                                 shadows='Back-facing surfaces are separate from ray-blocked surfaces. Self and neighbor shadow blockers are recorded separately; gaps remain unassigned.',
                                 geometry=('R258 bead-driven partial fit; unobserved spans and correspondences remain conditional.' if scene.mid.startswith('R258') else 'Frozen legacy-assisted model; uncertainty dominates precision. No new index certification.')))
    return meta


class DetailService:
    def __init__(self,work):
        self.work=Path(work)/'surface-r257';self.work.mkdir(parents=True,exist_ok=True)
        self.scenes={};self.geometry={};self.jobs={};self.pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix='surface');self.lock=threading.RLock()
    def lighting(self):return json.loads((ARTIFACTS/'lighting.json').read_text())
    def scene(self,mid):
        if mid not in self.scenes:self.scenes[mid]=Scene(mid)
        return self.scenes[mid]
    def submit(self,mid,gi,lid):
        with self.lock:
            scene=self.scene(mid)
            if not 0<=gi<scene.config['n']:raise ValueError('Surface index out of range')
            light=next((x for x in self.lighting()['lights'] if x['id']==lid),None)
            if light is None:raise ValueError('Unknown lighting model')
            key=hashlib.sha256((cache_key(scene,light,[gi])+sha(Path(__file__))+sha(ARTIFACTS/'observations.json')).encode()).hexdigest();path=self.work/f'{key}.json'
            if key not in self.jobs:
                # Drop obsolete queued calculations, but never interrupt an active one.
                for old,f in list(self.jobs.items()):
                    if f.cancel():del self.jobs[old]
                self.jobs[key]=self.pool.submit(self.compute,scene,gi,light,key,path)
            return key,self.jobs[key]
    def compute(self,scene,gi,light,key,path):
        if path.exists():return json.loads(path.read_text())
        gkey=(scene.mid,gi)
        if gkey not in self.geometry:
            if len(self.geometry)>12:self.geometry.pop(next(iter(self.geometry)))
            self.geometry[gkey]=local_geometry(scene,gi)
        obs=json.loads((ARTIFACTS/'observations.json').read_text())['observations']
        result=calculate(scene,gi,light,obs,self.geometry[gkey]);result['cache_key']=key;result['image_sha256']=sha(ROOT/'beads-photo-2.jpg')
        save(path,result);return result
    def result(self,mid,gi,lid):return self.submit(mid,gi,lid)[1].result()
