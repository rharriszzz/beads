"""Legacy diagnostic adapter. Deliberately separate from photo-only generation."""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from .generate import ROOT, sha, save
sys.path.insert(0,str(ROOT/'photo2'))
from camera_r254 import Model, rays
from global_fit_r253 import correction, harmonics, NAMES
from tangent_circles import RADIUS
IDS=['N2696_h+1_f0','N2674_h+1_f0','N2681_h-1_f0']
ADAPTER_VERSION='r256-model-adapter-v1'

def triple(k,n):
    signed=k if k<=n//2 else k-n
    b=(signed+3)//7
    return [signed-7*b,0,b]

def load(mid):
    if mid not in IDS: raise ValueError('Unknown model')
    p=ROOT/f'photo2/review/r254/{mid}-camera.json'
    config=json.loads(p.read_text())
    return config,Model(config['n'],config['h'],config['p'],config['focal'],config.get('turn_delta',0))

def model_version(mid):
    sources=[ROOT/f'photo2/review/r254/{mid}-camera.json',ROOT/'photo2/spline-seed-r175.json',
             ROOT/'photo2/camera_r254.py',ROOT/'photo2/global_fit_r253.py',ROOT/'photo2/tangent_circles.py',
             ROOT/'photo2/curved_surface_fit.py',ROOT/'photo2/bead_placement.py',ROOT/'photo2/local_surface_fit.py',ROOT/'photo2/review/r255/pattern-residues.csv',Path(__file__)]
    return hashlib.sha256(''.join(sha(p) for p in sources).encode()).hexdigest(),{str(p.relative_to(ROOT)):sha(p) for p in sources}

def prepare(mid, inventory, generation_id, out):
    out=Path(out); version,sources=model_version(mid); target=out/f'{mid}.json'
    if target.exists():
        cached=json.loads(target.read_text())
        if cached['version']==version and cached['generation_id']==generation_id: return cached
    config,m=load(mid);n=config['n'];g=m.geometry(np.arange(n)); pc=m.view.project(g['centers']);po=m.view.project(g['outward'])
    # Exact rounded-annulus ray ownership, sampled on a documented 4px image grid.
    step=4;bound=RADIUS*np.sqrt(1+.7**2)*m.view.scale+2
    mask=np.zeros((int(3200/step)+1,int(2600/step)+1),bool)
    for x,y in pc:
        a=np.floor((np.array([x,y])-bound)/step).astype(int);b=np.ceil((np.array([x,y])+bound)/step).astype(int)
        mask[max(0,a[1]):b[1]+1,max(0,a[0]):b[0]+1]=True
    yy,xx=np.where(mask); xy=np.c_[xx,yy]*step
    own,_,unknown=rays(m,xy,g);ok=(own>=0)&(unknown==0)
    counts=np.bincount(own[ok],minlength=n); sums=np.c_[[np.bincount(own[ok],weights=xy[ok,j],minlength=n) for j in [0,1]]].T
    centroid=sums/np.maximum(counts[:,None],1)
    footprints=[[] for _ in range(n)]
    for pt,k in zip(xy[ok],own[ok]): footprints[k].append(pt.tolist())
    obs=inventory['observations']; points=np.array([[r['x'],r['y']] for r in obs]);owner,_,un=rays(m,points,g)
    distances,near=cKDTree(pc).query(points,k=6)
    corr={}; associated=[[] for _ in range(n)]
    patch_points=[];patch_obs=[]
    for j,r in enumerate(obs):
        pp=r.get('patch',[]); pp=pp[::max(1,len(pp)//32)]
        patch_points.extend(pp);patch_obs.extend([j]*len(pp))
    patch_owner,_,patch_unknown=rays(m,np.array(patch_points),g) if patch_points else ([],[],[])
    patch_results=[[] for _ in obs]
    for j,k,u in zip(patch_obs,patch_owner,patch_unknown): patch_results[j].append((int(k),int(u)))
    for j,r in enumerate(obs):
        k=int(owner[j]); alt=[dict(generator_index=int(gi),legacy_k=int((gi-config['origin'])%n),center_distance_px=float(d)) for gi,d in zip(near[j],distances[j])]
        votes=patch_results[j]; support=sum(gi==k and u==0 for gi,u in votes)/len(votes) if votes and k>=0 else None
        corr[r['id']]=dict(owner_generator_index=k if k>=0 else None,owner_legacy_k=int((k-config['origin'])%n) if k>=0 else None,
                          ray_unfinished=int(un[j]),patch_support=support,patch_samples=len(votes),alternatives=alt,
                          status='conditional surface ownership' if k>=0 and un[j]==0 else 'unresolved / no completed surface hit',
                          center_residual_px=float(np.linalg.norm(points[j]-pc[k])) if k>=0 else None)
        if k>=0 and un[j]==0: associated[k].append(r['id'])
    t=np.arange(n)/n;ds,tw=correction(t,config['p']);stretch=harmonics(t)@np.array(config['p'][6:10])
    beads=[]
    for i in range(n):
        beads.append(dict(generator_index=i,legacy_k=int((i-config['origin'])%n),center=pc[i].tolist(),outward=po[i].tolist(),
                          visible_centroid=centroid[i].tolist() if counts[i] else None,area_px2=int(counts[i]*step**2),
                          visibility='sampled visible surface' if counts[i] else 'no sampled surface: occluded or smaller than 4px grid',
                          footprint=footprints[i],observations=associated[i],stretch=float(stretch[i]),twist_deg=float(np.degrees(tw[i])),
                          longitudinal_shift_px=float(ds[i]*m.unscaled_length)))
    patterns=[r for r in csv.DictReader((ROOT/'photo2/review/r255/pattern-residues.csv').open()) if r['model']==mid]
    doc=dict(id=mid,version=version,generation_id=generation_id,provenance='LEGACY-ASSISTED diagnostic geometry: historical bead/adjacency constraints used in fitting',
             n=n,h=config['h'],origin=config['origin'],origin_label='Legacy C252-A948 / maker20; arbitrary reference, not manufacturing seam',
             fitted_camera=dict(elevation_deg=config['p'][4],roll_deg=config['p'][5],focal_px=config['focal'],scale=m.view.scale,tx=m.view.tx,ty=m.view.ty),
             parameters=dict(zip(NAMES,config['p'])),turns=m.source.nrows,turn_delta=config.get('turn_delta',0),sources=sources,
             centerline=m.view.project(g['line'])[::3].tolist(),beads=beads,correspondences=corr,
             visibility_grid_px=step,unfinished_rays=int((unknown>0).sum()),patterns=patterns,
             pattern_status='Rejected legacy templates; unproven colors are never observations',
             independent_fit='STAGED: see README; no independent count/camera/phase fit is claimed')
    save(target,doc);return doc

def legacy():
    rows=list(csv.DictReader((ROOT/'photo2/review/r252/accepted.csv').open()))
    for r in rows: r['x']=float(r['x']);r['y']=float(r['y']);r['id']=r['observation_id'];r['source']='R252 legacy-assisted'
    maker=json.loads((ROOT/'photo2/review/r200/centers.json').read_text())['points']
    rows += [dict(**r,source='R200 maker mark (legacy)',observation_id='M'+str(r['number']),color='unknown',evidence_level='maker-marked') for r in maker]
    inv=json.loads((ROOT/'photo2/review/r252/inventory.json').read_text())
    for r in inv['sources']:
        if r['disposition'] not in ['ambiguous','provisional','rejected']: continue
        xy=r.get('original_xy')
        if not xy: continue
        rows.append(dict(id='legacy-source:'+r['key'],observation_id=r['key'],x=xy[0],y=xy[1],color=r.get('color','unknown'),
                         evidence_level=r['disposition'],source='R252 withheld legacy-assisted source',withheld=True,reason=r.get('decision_reason')))
    return rows

def fft_data():
    # Preserve all candidates. Only drawing density is reduced by the browser.
    rows=[]
    for r in csv.DictReader((ROOT/'photo2/review/r250/candidates.csv').open()):
        for key in ['x','y','s','angle','relative_angle','tangent_deg','frequency','wavelength','relative_brightness','prominence','angle_uncertainty']:
            r[key]=float(r[key])
        r['index']=int(r['index']);rows.append(r)
    return dict(source='R250 saved image FFT on inherited centerline; not independent observed adjacency',candidates=rows,
                protocol=json.loads((ROOT/'photo2/review/r250/protocol.json').read_text()))
