"""R303 parameterization and common native photographic objective.

The independent and calibrated families have the same degrees of freedom.
Only fixed c removes a degree of freedom. No thread path or strain is inferred.
"""
from copy import deepcopy
import time
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import binary_erosion
from photo2.r302 import core as old
from photo2.r297.common import ROOT, read, save, sha, utc
from photo2.r301.objective import assignment, secondary
from photo2.r298.geometry import bead_extents, envelope

BASE=ROOT/'photo2/r303'
NAMES=old.NAMES
MODES=['independent','source','calibrated']

def bounds(mode):
    b=old.bounds()
    if mode!='independent': b[4]=[.975,.975] if mode=='source' else [.1,16.3]
    return b

def steps(mode):
    z=old.STEPS.copy()
    if mode!='independent': z[4]=0 if mode=='source' else .07
    return z

def encode(v,mode):
    z=np.array(v,float).copy()
    if mode!='independent': z[4]=.975 if mode=='source' else z[4]*z[5]/(2*z[0])
    return z

def physical(v,mode):
    z=np.array(v,float).copy()
    if mode!='independent': z[4]=v[4]*2*v[0]/v[5]
    return z

class Scene(old.Scene):
    def __init__(self,v,s,hand,mode,guards=64):
        super().__init__(physical(v,mode),s,hand,guards)
        self.coefficient=self.p['pitch']*self.p['turn']/(2*self.axial)

def structure(scene,s,raster=None,held=False):
    ss=deepcopy(s)
    if held:
        cues=s['cues'];ss['cues']={k:[x for x,h in zip(v,cues['withheld']) if h] for k,v in cues.items() if k!='withheld'}
        ss['bead_dimensions']=[];ss['profiles']=[];ss['separators']=s.get('diagnostic_separators',[])
    sec=secondary(scene,ss,2)
    dims=[] if held else s['bead_dimensions'];profiles=[] if held else s['profiles']
    polygons=scene.polygons();bd=bead_extents(scene,dims,polygons) if dims else np.empty((0,2))
    en=envelope(scene,profiles,polygons) if profiles else np.empty((0,2))
    owners=scene.tree.query(np.array([r['point'] for r in dims]))[1] if dims else []
    boundary=[]
    if raster is not None:
        for r,k in zip(dims,owners):
            mask=(raster['owner']==k).reshape(raster['shape']);edge=mask&~binary_erosion(mask);pts=raster['xy'][edge.ravel()]
            boundary.extend(cKDTree(pts).query(r['polygon'])[0].tolist() if len(pts) else [30.]*len(r['polygon']))
    central=abs((scene.project(scene.line)-s['center'])@s['tangent'])<=s['halfspan']
    sec.update(extents=bd.tolist(),envelope_bounds=en.tolist(),boundary_distances=boundary,
               boundary_mae=float(np.mean(boundary)) if boundary else None,
               contour_owners=scene.indices[owners].tolist() if len(owners) else [],local_positions=int(central.sum()))
    return sec

def flags(ev):
    if not ev['feasible']:return ['uncertified physical geometry']
    z=ev['secondary'];f=[]
    if z['dimensions'] and z['dimension_mae']>3:f.append('bead extent error >3px')
    if z['boundary_mae'] is not None and z['boundary_mae']>4:f.append('visible boundary error >4px')
    if z['profiles'] and z['edge_mae']>4:f.append('envelope boundary error >4px')
    if z['paper']>.10:f.append('paper occupation >10%')
    if z['material_missing']>.23:f.append('colored omission >23%')
    if ev['train']['unmatched']:f.append('unmatched training reflections')
    return f

def evaluate(v,s,hand,mode,detail=False):
    started=time.perf_counter();q=physical(v,mode)
    if not .035<=q[4]<=.4:return dict(feasible=False,loss=2e5,reason='common physical pitch search bounds',seconds=time.perf_counter()-started)
    c=Scene(v,s,hand,mode);cert=c.certify(iterations=100,witnesses=detail)
    if not cert['certified']:return dict(feasible=False,loss=1e5+max(0,-cert['minimum_gap_units'])*1e3,contact=cert,seconds=time.perf_counter()-started)
    # No position-count gate. 153 addresses and complete close-pair certification.
    pred,raster=old.native(c,s);train=assignment(pred,[r for r in s['observations'] if r['split']=='train'],s)
    sec=structure(c,s,raster)
    d=np.array(sec['extents'])-np.array([r['extent_px'] for r in s['bead_dimensions']]) if s['bead_dimensions'] else np.array([])
    e=np.array(sec['envelope_bounds'])-np.array([r['bounds'] for r in s['profiles']]) if s['profiles'] else np.array([])
    dim=float(np.mean(d*d)) if d.size else 0.
    edge=float(np.mean(e*e)) if e.size else 0.
    boundary=float(np.mean(np.minimum(sec['boundary_distances'],20.)**2)) if sec['boundary_distances'] else 0.
    penalty=dim+.5*boundary+edge+100*(sec['paper']+sec['material_missing'])
    barrier=4000*(max(0,sec['paper']-.10)**2+max(0,sec['material_missing']-.23)**2)+4*max(0,sec['dimension_mae']-3)**2+4*max(0,sec['edge_mae']-4)**2
    out=dict(feasible=True,loss=train['loss']+penalty+barrier,reflection_loss=train['loss'],structural_loss=penalty+barrier,secondary=sec,contact=cert,train=train,predictions=pred,local_positions=sec['local_positions'],seconds=time.perf_counter()-started,
             diagnostic={k:v for k,v in raster.items() if k not in ['xy','owner','shape']})
    out['flags']=flags(out)
    if detail:out.update(parameters=dict(c.p),hand=hand,polygons=c.polygons().tolist(),indices=c.indices.tolist(),centers=c.centers.tolist(),projected_centers=c.pc.tolist())
    return out

def features(v,s,hand,mode,anchors=None):
    c=Scene(v,s,hand,mode);cert=c.certify(iterations=100,witnesses=False)
    pp,rr=old.native(c,s);match=assignment(pp,[r for r in s['observations'] if r['split']=='train'],s)
    if anchors is None:anchors=[r['index'] for r in match['records'] if r['index'] is not None]
    lookup={p['index']:p['point'] for p in pp};z=structure(c,s,rr)
    y=[];groups=[]
    def add(a,scale,g):
        a=np.ravel(a);y.extend((a/scale).tolist());groups.extend([g]*len(a))
    add([lookup.get(i,[np.nan,np.nan]) for i in anchors],3.,'reflection')
    add(z['extents'],3*np.sqrt(max(1,len(np.ravel(z['extents'])))),'dimension')
    add(z['boundary_distances'],3*np.sqrt(max(1,len(z['boundary_distances']))),'boundary')
    add(z['envelope_bounds'],4*np.sqrt(max(1,len(np.ravel(z['envelope_bounds'])))),'envelope')
    add([z['paper'],z['material_missing']],.1*np.sqrt(2),'material')
    return np.array(y),anchors,groups,cert,z['contour_owners']

def sensitivity(v,s,hand,mode):
    began=time.monotonic();y,anchors,groups,cert,owners=features(v,s,hand,mode);cols=[];records=[]
    active=np.flatnonzero(steps(mode)>0)
    for j in active:
        sides=[]
        for sign in [-1,1]:
            q=np.array(v).copy();q[j]=np.clip(q[j]+sign*steps(mode)[j],*bounds(mode)[j])
            yy,_,_,cc,oo=features(q,s,hand,mode,anchors);sides.append((q[j]-v[j],yy,cc['certified']))
            records.append(dict(parameter=int(j),sign=sign,parameters=q.tolist(),values=yy.tolist(),physical=cc,contour_owners=oo))
        a,b=sides
        if a[2] and b[2]:d=(b[1]-a[1])/(b[0]-a[0])*steps(mode)[j]
        elif b[2] and b[0]:d=(b[1]-y)/b[0]*steps(mode)[j]
        elif a[2] and a[0]:d=(a[1]-y)/a[0]*steps(mode)[j]
        else:d=np.full_like(y,np.nan)
        cols.append(d)
    J=np.array(cols).T;finite=np.all(np.isfinite(J),axis=1);A=np.nan_to_num(J[finite]);_,sv,vt=np.linalg.svd(A,full_matrices=False)
    norms=np.zeros(18);norms[active]=np.linalg.norm(A,axis=0)
    vectors=np.zeros((len(vt),18));vectors[:,active]=vt
    return dict(seconds=time.monotonic()-began,parameters=list(v),active=active.tolist(),anchors=anchors,groups=groups,jacobian=J.tolist(),finite_rows=int(finite.sum()),singular_values=sv.tolist(),resolved_scale_directions=int(sum(sv>=1)),column_norms=norms.tolist(),right_vectors=vectors.tolist(),perturbations=records,base_physical=cert,contour_owners=owners)
