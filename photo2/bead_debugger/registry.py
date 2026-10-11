"""Additive R258 registry. Original adapter/version hashes stay immutable."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from . import models as legacy_models
from .models import ROOT,RADIUS,rays,legacy,fft_data
from .generate import save,sha
from .refit import BeadCurve,OUT,ROW

def new_ids():
    p=OUT/'model-index.json';return json.loads(p.read_text()) if p.exists() else []
IDS=legacy_models.IDS+new_ids()
def load(mid):
    if mid in legacy_models.IDS:return legacy_models.load(mid)
    if mid not in new_ids():raise ValueError('Unknown model')
    c=json.loads((OUT/(mid+'.json')).read_text());return c,BeadCurve(c)
def model_version(mid):
    if mid in legacy_models.IDS:return legacy_models.model_version(mid)
    sources={str(p.relative_to(ROOT)):sha(p) for p in [OUT/(mid+'.json'),ROOT/'photo2/bead_debugger/refit.py',ROOT/'photo2/camera_r254.py',ROOT/'photo2/curved_surface_fit.py',ROOT/'photo2/bead_placement.py',ROOT/'photo2/tangent_circles.py',ROOT/'photo2/local_surface_fit.py',ROOT/'beads.pov',Path(__file__)]}
    return hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest(),sources

def prepare(mid,inventory,generation_id,out):
    if mid in legacy_models.IDS:return legacy_models.prepare(mid,inventory,generation_id,out)
    version,sources=model_version(mid);target=Path(out)/(mid+'.json')
    if target.exists():
        doc=json.loads(target.read_text())
        if doc['version']==version and doc['generation_id']==generation_id:return doc
    c,m=load(mid);n=c['n'];g=m.geometry(np.arange(n));pc=m.view.project(g['centers']);po=m.view.project(g['outward']);step=4
    mask=np.zeros((797,637),bool);bound=RADIUS*np.sqrt(1+.7**2)*m.view.scale+3
    for x,y in pc:
        a=np.floor((np.array([x,y])-bound)/step).astype(int);b=np.ceil((np.array([x,y])+bound)/step).astype(int)
        mask[max(0,a[1]):min(797,b[1]+1),max(0,a[0]):min(637,b[0]+1)]=True
    yy,xx=np.where(mask);xy=np.c_[xx,yy]*step;own,_,un=rays(m,xy,g);own[un>0]=-1
    footprints=[[] for _ in range(n)]
    for pt,j in zip(xy,own):
        if j>=0:footprints[j].append(pt.tolist())
    obs=inventory['observations'];pts=np.array([[r['x'],r['y']] for r in obs]);owners,_,uu=rays(m,pts,g);dd,near=cKDTree(pc).query(pts,k=6);corr={};associated=[[] for _ in range(n)]
    for r,i,u,ds,nn in zip(obs,owners,uu,dd,near):
        i=int(i);pp=np.array(r.get('patch',[]));support=None
        if len(pp):
            oo,_,pu=rays(m,pp,g);support=float(np.mean((oo==i)&(pu==0))) if i>=0 else 0.
        corr[r['id']]=dict(owner_generator_index=i if i>=0 and not u else None,owner_legacy_k=(i-c['origin'])%n if i>=0 else None,ray_unfinished=int(u),patch_support=support,patch_samples=len(pp),
             alternatives=[dict(generator_index=int(j),legacy_k=int((j-c['origin'])%n),center_distance_px=float(d)) for j,d in zip(nn,ds)],status='R258 conditional ray owner; not an established identity',center_residual_px=float(np.linalg.norm(np.array([r['x'],r['y']])-pc[i])) if i>=0 else None)
        if i>=0 and not u:associated[i].append(r['id'])
    beads=[];t=np.arange(n)/n;der=m.curve(t,1);speed=np.linalg.norm(der,axis=1)
    a=2*np.pi*t;tw=np.array([np.sin(a),np.cos(a),np.sin(2*a),np.cos(2*a)]).T@np.array(c.get('phase_harmonics',[0]*4))
    for b in c.get('local',[]):
        u=((t-b['t']+.5)%1-.5)/b['width'];w=np.where(abs(u)<1,(1-u*u)**3,0);tw+=w*(b.get('phase',0)+b.get('winding',0)*u)
    for i,fp in enumerate(footprints):
        beads.append(dict(generator_index=i,legacy_k=(i-c['origin'])%n,center=pc[i].tolist(),outward=po[i].tolist(),visible_centroid=np.mean(fp,axis=0).tolist() if fp else None,
                          area_px2=len(fp)*16,visibility='sampled visible surface' if fp else 'occluded / below 4px grid',footprint=fp,observations=associated[i],stretch=float(speed[i]/(m.source.nrows*ROW)-1),twist_deg=float(np.degrees(tw[i])),longitudinal_shift_px=0.))
    audit=None
    for name in ['results.json','alternatives.json','compact-controls.json']:
        path=OUT/name
        if path.exists():audit=next((r for r in json.loads(path.read_text()) if r['id']==mid),audit)
    failures=[];unsupported=[]
    if c.get('section') and (OUT/(c['section']+'-evidence.json')).exists():
        ev=json.loads((OUT/(c['section']+'-evidence.json')).read_text())
        audit_map={r['id']:r for r in (audit or {}).get('observations',[])}
        positive=np.array([p for r in ev['observations'] for p in r['patch']]);tree=cKDTree(positive)
        inside=(xy[:,0]>=ev['box'][0])&(xy[:,0]<ev['box'][2])&(xy[:,1]>=ev['box'][1])&(xy[:,1]<ev['box'][3])&(own>=0)
        check=xy[inside];unsupported=check[tree.query(check)[0]>2].tolist()
        for r in ev['observations']:
            pp=np.asarray(r['patch']);oo,_,pu=rays(m,pp,g);assigned=audit_map.get(r['id'],{}).get('owner',-1)
            for p,o,u in zip(pp,oo,pu):failures.append([*map(int,p),int(o),int(assigned),int(o==assigned and o>=0 and u==0)])
    doc=dict(id=mid,version=version,generation_id=generation_id,provenance='R258 bead-surface fit: initialized from old geometry; no curve/edge resemblance objective. Correspondences conditional.',
        n=n,h=c['h'],origin=c['origin'],origin_label='Historical review address retained; R258 identities separate and conditional',fitted_camera=c['camera'],parameters=dict(dx_px=c['camera']['tx']-1269.5,dy_px=c['camera']['ty']-1590.5),turns=c['turns'],turn_delta=0,sources=sources,
        centerline=m.view.project(g['line'])[::3].tolist(),beads=beads,correspondences=corr,visibility_grid_px=4,unfinished_rays=int(un.sum()),patterns=[],pattern_status='No fitted color pattern',independent_fit=c['independence'],model_parameters=c,fit_audit=audit,ownership_evidence=failures,unsupported_footprint=unsupported)
    save(target,doc);return doc
