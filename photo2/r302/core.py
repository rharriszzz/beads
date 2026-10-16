"""Construction-constrained geometry, native predictions and grouped evidence.

All historical modules are read-only. Radius=1 is a unit gauge. Effective axial
advance is a geometric parameter, not elastic string strain. A bounded smooth
correction describes local stitch reconfiguration; it need not integrate to zero.
"""
import time
from copy import deepcopy
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import binary_erosion
from photo2.r297.common import ROOT, read, save, sha, utc
from photo2.r301.model import Local, NAMES, BOUNDS, AXES, unit
from photo2.r301.objective import assignment, secondary
from photo2.r299.forward import light_params, shade, highlight
from photo2.r298.geometry import bead_extents

BASE = ROOT/'photo2/r302'
# A finite difference unit, not a confidence interval or independent prior.
STEPS = np.array([.04,.06,.03,.12,.015,.008,3.,3.,4.,.65,5.,4.,2.,2.,2.,.004,.08,.008])

def twist_bounds(count):
    if count < 2000: raise ValueError('Conditional total count must be >=2000')
    return 6.5*count/(count+6.5), 6.5*count/(count-6.5)

def bounds(count=2000):
    b=BOUNDS.copy();b[5]=twist_bounds(count);b[17]=[-.02,.02]
    b[15]=[-.02,.02]
    return b

class Scene(Local):
    def __init__(self,v,s,hand,guards=64):
        super().__init__(v,s,hand,guards)
        p=self.p;k=self.indices.astype(float);length=14.
        # ds/dk = pitch*(1+spacing*tanh(k/L)), bounded for ALL guards.
        self.arc=p['pitch']*(k+p['spacing']*length*(np.logaddexp(k/length,-k/length)-np.log(2)))
        self.advance=p['pitch']*(1+p['spacing']*np.tanh(k/length))
        t=np.array(s['tangent']);a=np.radians(p['angle'])
        t=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])@t
        wxy=np.linalg.solve(np.array([self.right[:2],self.down[:2]]),t)
        u=unit(np.r_[wxy,0.]);w=np.array([-u[1],u[0],0.]);z=np.array([0.,0.,1.])
        theta=p['curve']*self.arc
        # Circular arc is arclength parameterized; bending adds no artificial
        # longitudinal stretch as the old quadratic parameterization did.
        along=self.arc*np.sinc(theta/np.pi)
        across=.5*p['curve']*self.arc**2*np.sinc(theta/(2*np.pi))**2
        self.line=along[:,None]*u+across[:,None]*w
        tangent=np.cos(theta)[:,None]*u+np.sin(theta)[:,None]*w
        normal=np.cross(z,tangent)
        radial=np.sin(self.phase)[:,None]*normal+np.cos(self.phase)[:,None]*z
        circum=np.cos(self.phase)[:,None]*normal-np.sin(self.phase)[:,None]*z
        tilt=np.radians(p['tilt']);axis=np.cos(tilt)*tangent+np.sin(tilt)*circum
        other=unit(np.cross(radial,axis));third=np.cross(axis,other)
        self.g=dict(zip(AXES,(axis,other,third)),radial=radial)
        self.centers=self.line+p['minor']*radial;self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)

def native(scene,s,step=1.):
    """Complete selected body bounding boxes on ONE native image lattice.

    Same first-hit/shadow kernel and half-height centroid as R301 full_predict,
    without repeatedly tracing overlapping per-body boxes. Never a surface proxy.
    """
    c=np.array(s['center']);t=np.array(s['tangent']);n=np.array([-t[1],t[0]])
    d=scene.pc-c
    owners=np.flatnonzero((abs(d@t)<s['halfspan']+16+scene.query_radius)&(abs(d@n)<80+scene.query_radius))
    size=scene.query_radius+2
    lo=np.maximum([0,0],np.floor((scene.pc[owners].min(0)-size)/step)*step)
    hi=np.minimum([2539,3181],scene.pc[owners].max(0)+size)
    yy,xx=np.mgrid[lo[1]:hi[1]+step/2:step,lo[0]:hi[0]+step/2:step];xy=np.c_[xx.ravel(),yy.ravel()]
    tr=scene.camera(xy)
    light=light_params([scene.p['light_az'],scene.p['light_el'],10.],'directional',scene.centers.mean(0))
    # Shade only selected bodies; complete chain still occludes all rays.
    keep=np.isin(tr['owner'],owners)
    sub={k:tr[k][keep] for k in ['xy','owner','points','normal','viewer','unknown']}
    sh=shade(scene,sub,light);pred=[]
    for owner in owners:
        mask=sub['owner']==owner;h=highlight(sub['xy'][mask],sh['intensity'][mask],step)
        if h:pred.append(dict(owner=int(owner),index=int(scene.indices[owner]),point=h['centroid'],peak=h['peak'],strength=h['peak_intensity']))
    return pred,dict(xy=xy,owner=tr['owner'],shape=xx.shape,unknown=int(tr['unknown'].sum()),rays=len(xy),shadow={k:v for k,v in sh.items() if k!='intensity'})

def structure(scene,s,raster=None,held=False):
    ss=deepcopy(s)
    if held:
        cues=s['cues'];ss['cues']={k:[x for x,h in zip(v,cues['withheld']) if h] for k,v in cues.items() if k!='withheld'}
        ss['bead_dimensions']=[];ss['separators']=s.get('diagnostic_separators',[])
    sec=secondary(scene,ss,2)
    bd=bead_extents(scene,s['bead_dimensions'],scene.polygons())
    # Nearest projected body is an explicit uncertain contour assignment, as in
    # R301. Visible-boundary distance tests it independently of its convex extent.
    _,owners=scene.tree.query([r['point'] for r in s['bead_dimensions']])
    boundary=[]
    if raster is not None:
        for r,k in zip(s['bead_dimensions'],owners):
            mask=(raster['owner']==k).reshape(raster['shape'])
            edge=mask&~binary_erosion(mask)
            pts=raster['xy'][edge.ravel()]
            boundary.extend(cKDTree(pts).query(r['polygon'])[0].tolist() if len(pts) else [30.]*len(r['polygon']))
    t=np.array(s['tangent']);n=np.array([-t[1],t[0]])
    central=np.flatnonzero(abs((scene.project(scene.line)-s['center'])@t)<=s['halfspan'])
    poly=scene.polygons();pts=poly[central].reshape(-1,2)
    transverse=float(np.ptp(pts@n)) if len(pts) else 0.
    neighbors={}
    for lag in [1,6,7]:
        a=central[central+lag<scene.n];b=a+lag;v=scene.pc[b]-scene.pc[a]
        neighbors[str(lag)]=dict(distance=np.linalg.norm(v,axis=1).tolist(),tangent=(v@t).tolist(),normal=(v@n).tolist(),angle=np.degrees(np.arctan2(v@n,v@t)).tolist(),indices=scene.indices[a].tolist(),world_distance=np.linalg.norm(scene.centers[b]-scene.centers[a],axis=1).tolist())
    sec.update(extents=bd.tolist(),boundary_distances=boundary,boundary_mae=float(np.mean(boundary)) if boundary else None,contour_owners=scene.indices[owners].tolist(),transverse_extent=transverse,neighbors=neighbors,local_positions=len(central))
    return sec

def flags(result):
    if not result['feasible']:return ['uncertified physical geometry']
    z=result['secondary'];f=[]
    if not 15<=z['local_positions']<=30:f.append('excess or insufficient local positions')
    if z['dimension_mae']>3:f.append('bead extent error >3px')
    if z['boundary_mae'] is not None and z['boundary_mae']>4:f.append('visible boundary error >4px')
    if z['paper']>.10:f.append('paper occupation >10%')
    if z['material_missing']>.23:f.append('colored omission >23%')
    if result['train']['unmatched']:f.append('unmatched training reflections')
    return f

def evaluate(v,s,hand,detail=False,gate=True):
    started=time.perf_counter();scene=Scene(v,s,hand)
    cert=scene.certify(iterations=100,witnesses=detail)
    if not cert['certified']:
        return dict(feasible=False,loss=1e5+max(0,-cert['minimum_gap_units'])*1e3,contact=cert,seconds=time.perf_counter()-started)
    central=int(np.sum(abs((scene.project(scene.line)-s['center'])@s['tangent'])<=s['halfspan']))
    if gate and not 15<=central<=30:
        return dict(feasible=False,loss=1e4+100*abs(central-25),reason='position-density guard',local_positions=central,contact=cert,seconds=time.perf_counter()-started)
    pred,raster=native(scene,s);train=assignment(pred,[r for r in s['observations'] if r['split']=='train'],s)
    sec=structure(scene,s,raster)
    # Reflections retain squared native-pixel scale and bounded robust influence.
    # Structural blocks are normalized by FEATURE GROUP, never by pixel count.
    d=np.array(sec['extents'])-np.array([r['extent_px'] for r in s['bead_dimensions']])
    dim=float(np.mean(d*d));boundary=float(np.mean(np.minimum(sec['boundary_distances'],20.)**2))
    penalty=dim+.5*boundary+100*sec['paper']+100*sec['material_missing']
    # Strong contradiction barriers permit transient exploration but disallow a
    # reflection-only winner being called geometrically accepted.
    barrier=4000*(max(0,sec['paper']-.10)**2+max(0,sec['material_missing']-.23)**2)+4*max(0,sec['dimension_mae']-3)**2
    out=dict(feasible=True,loss=train['loss']+penalty+barrier,reflection_loss=train['loss'],structural_loss=penalty+barrier,secondary=sec,contact=cert,train=train,predictions=pred,local_positions=central,seconds=time.perf_counter()-started,diagnostic={k:v for k,v in raster.items() if k not in ['xy','owner','shape']})
    out['flags']=flags(out)
    if detail:
        out.update(parameters=dict(scene.p),hand=hand,polygons=scene.polygons().tolist(),indices=scene.indices.tolist(),centers=scene.centers.tolist(),projected_centers=scene.pc.tolist())
    return out

def feature_vector(scene,s,pred,raster,anchors):
    """Finite-difference outputs; fixed identities ONLY within each perturbation.

    Neighbor predictions have no observed physical labels and are NOT part of
    data rank. Dark valleys stay withheld. No sensitivity call uses withheld data.
    """
    lookup={p['index']:p for p in pred};values=[];labels=[];groups=[];sigma=[]
    def add(vals,tag,group,noise):
        for j,x in enumerate(np.ravel(vals)):values.append(float(x));labels.append(f'{tag}:{j}');groups.append(group);sigma.append(noise)
    for r,idx in anchors['reflection']:
        q=lookup.get(idx);add(q['point'] if q else [np.nan,np.nan],r,'reflection',3.)
    sec=structure(scene,s,raster)
    add(sec['extents'],'B15','dimension',3.*np.sqrt(2))
    add(sec['boundary_distances'],'B15-edge','boundary',3.*np.sqrt(8))
    add([sec['paper'],sec['material_missing']],'material','material',.1*np.sqrt(2))
    add([sec['transverse_extent']],'transverse-model-only','prediction_only',4.)
    for lag in [1,6,7]:
        ix=np.array(anchors['neighbors']);a=np.searchsorted(scene.indices,ix);b=a+lag
        vec=scene.pc[b]-scene.pc[a]
        add(vec,f'neighbor-{lag}-vector','prediction_only',3.*np.sqrt(len(ix)))
        add(np.linalg.norm(scene.centers[b]-scene.centers[a],axis=1),f'neighbor-{lag}-world-distance','prediction_only',.1*np.sqrt(len(ix)))
    return np.array(values),labels,groups,np.array(sigma),sec
