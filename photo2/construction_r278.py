"""Explicit intended-radius construction; immutable legacy surface evaluator.

The normalized scene is a change of world units for exact ray evaluation, not
image resizing: centerline length, rope radius and bead radius are set first.
"""
from __future__ import annotations
import copy
from types import SimpleNamespace
import numpy as np
from scipy.spatial import cKDTree
from .reconstruct_r276 import Model as LegacyModel, DEFAULT, initial_base
from .bead_debugger.surface import Scene as LegacyScene, RADIUS, unit
from curved_surface_fit import sdf as legacy_sdf
from bead_placement import Rope


def radius(convention='intended', chain_minor=4.):
    return float(Rope(2600, chain_minor=chain_minor, radius_convention=convention).bead_radius)


def sdf(points, bead_radius):
    factor=bead_radius/RADIUS
    return legacy_sdf(np.asarray(points)/factor)*factor


class Model(LegacyModel):
    def __init__(self, base, p):
        super().__init__(base,p)
        self.bead_radius=base['bead_radius']

    def geometry(self, indices):
        g=super().geometry(indices)
        g['outward']=g['centers']+self.bead_radius*g['radial']
        tilt=np.radians(self.config.get('hole_tilt_deg',0))*self.config['h']
        # One shared tilt toward the circumferential direction; no per-bead DOF.
        circum=unit(np.cross(g['radial'],g['tangent']))
        g['surface_tangent']=np.cos(tilt)*g['tangent']+np.sin(tilt)*circum
        g['surface_normal']=g['radial']
        g['surface_binormal']=unit(np.cross(g['surface_tangent'],g['surface_normal']))
        return g


class Scene:
    def __init__(self, base, p):
        self.config=base; self.model=Model(base,p)
        self.g=self.model.geometry(np.arange(base['n']))
        self.centers=self.g['centers']; self.pc=self.model.view.project(self.centers)
        self.radius=base['bead_radius']; self.factor=self.radius/RADIUS
        self.bound=self.radius*np.sqrt(1+.7**2)
        self.plane_z=-(base['rope_radius']+self.radius)
        self.version='r278-radius-aware-1'; self.mid=base.get('id','R278')
        normalized=LegacyScene.__new__(LegacyScene)
        normalized.g={k:(v/self.factor if k in ('centers','line','outward') else v) for k,v in self.g.items()}
        normalized.centers=normalized.g['centers']; normalized.pc=self.pc
        view=copy.copy(self.model.view); view.scale*=self.factor
        normalized.model=SimpleNamespace(view=view,source=self.model.source)
        normalized.shadow_trees={}; self.normalized=normalized

    def camera(self, xy):
        if self.config.get('hole_tilt_deg',0):
            from .surface_r278 import camera
            return camera(self,xy)
        data=self.normalized.camera(xy)
        data['points']*=self.factor
        return data

    def blocked(self, points, direction, return_owner=False):
        if self.config.get('hole_tilt_deg',0):
            from .surface_r278 import blocked
            return blocked(self,points,direction,return_owner)
        return self.normalized.blocked(np.asarray(points)/self.factor,direction,return_owner)

    def grid(self, box, step=1):
        x0,y0,x1,y1=box
        y,x=np.mgrid[int(np.ceil(y0/step))*step:y1:step,int(np.ceil(x0/step))*step:x1:step]
        return self.camera(np.c_[x.ravel(),y.ravel()])


def base_model(n, h, convention='intended', pitch_factor=1., focal=0., elevation=None):
    """Preserve warm-start projected spline, reset handed phase/deformation.

    Set L=turns*(1.05*.65*2*r)*pitch_factor. The inverse camera scale preserves
    the image centerline but changes projected rope width and bead dimensions.
    """
    b=initial_base(n,h)
    # Retain geometry/camera only. Historical review origins and unused frozen
    # identity metadata must not masquerade as R278 correspondence constraints.
    b={k:b[k] for k in ('id','n','h','turns','phase','phase_harmonics','knots','local','focal','camera') if k in b}
    b['schema']='r278-physical-construction-1'
    b['independence']='Historical spline/camera warm start; current identity assignments use frozen image-only interiors'
    original=LegacyModel(b,DEFAULT)
    image_knots=original.view.project(np.asarray(b['knots']))
    b.update(bead_radius=radius(convention),radius_convention=convention,
             rope_radius=4.,uniform_material=True,phase=0.,phase_harmonics=[0.]*4,
             local=[],focal=focal,pitch_factor=pitch_factor)
    if elevation is not None:b['camera']['elevation']=elevation
    if focal or elevation is not None:
        from camera_r254 import Camera
        view=Camera(**b['camera']);view.focal=focal
        r,d,eye=view.basis();P=(image_knots-[view.tx,view.ty])/view.scale
        matrix=np.broadcast_to(np.array([r[:2],d[:2]]),(len(P),2,2)).copy()
        if focal:matrix+=P[:,:,None]*eye[None,None,:2]*view.scale/focal
        plane=np.linalg.solve(matrix,P[...,None])[...,0]
        b['knots']=np.c_[plane,np.zeros(len(plane))].tolist()
    old=LegacyModel(b,DEFAULT)
    target=b['turns']*.65*2*b['bead_radius']*1.05*pitch_factor
    factor=target/old.length
    b['knots']=(np.asarray(b['knots'])*factor).tolist()
    b['camera']['scale']/=factor
    b['id']=f'{convention}_N{n}_h{h:+d}_p{pitch_factor:.3f}_f{focal:g}'
    b['initialization']='R258 spline warm start; reset phase/harmonics/local fields; physical source row pitch; no legacy identities'
    return b


def surface_samples(r, profile=32, azimuth=32):
    """Complete rounded annulus profile including all flat faces and inner hole."""
    a=np.linspace(0,2*np.pi,profile,endpoint=False)
    extra=.2*.43*r; rounding=.8*.43*r; stretch=.7/.43
    rho=.57*r+extra*np.sign(np.cos(a))+rounding*np.cos(a)
    z=(extra*np.sign(np.sin(a))+rounding*np.sin(a))*stretch
    flat=np.linspace(-extra,extra,max(3,profile//4))
    rho=np.r_[rho,.57*r+flat,.57*r+flat,np.full(len(flat),r),np.full(len(flat),.14*r)]
    z=np.r_[z,np.full(len(flat),.7*r),np.full(len(flat),-.7*r),flat*stretch,flat*stretch]
    az=np.linspace(0,2*np.pi,azimuth,endpoint=False)
    zz,aa=np.meshgrid(np.arange(len(rho)),az,indexing='ij')
    return np.c_[z[zz.ravel()],rho[zz.ravel()]*np.cos(aa.ravel()),rho[zz.ravel()]*np.sin(aa.ravel())]


def contact_audit(s, profile=16, azimuth=16, all_pairs=True):
    """Both directions, all bounding-sphere candidates; no neighbor-only blind spot."""
    n=len(s.centers); local=surface_samples(s.radius,profile,azimuth)
    pairs=cKDTree(s.centers).query_pairs(2*s.bound,output_type='ndarray') if all_pairs else np.array([(i,(i+d)%n) for i in range(n) for d in (1,6,7)])
    minima=np.full(len(pairs),np.inf)
    for reverse in (False,True):
        for start in range(0,len(pairs),32):
            ab=pairs[start:start+32]; a,b=ab[:,int(reverse)],ab[:,int(not reverse)]
            p=s.centers[a,None,:]+local[None,:,0,None]*s.g['surface_tangent'][a,None,:]+local[None,:,1,None]*s.g['surface_normal'][a,None,:]+local[None,:,2,None]*s.g['surface_binormal'][a,None,:]
            q=p-s.centers[b,None,:]
            loc=np.stack([np.sum(q*s.g[k][b,None,:],axis=2) for k in ('surface_tangent','surface_normal','surface_binormal')],axis=-1)
            minima[start:start+len(ab)]=np.minimum(minima[start:start+len(ab)],sdf(loc,s.radius).min(1))
    delta=np.minimum(abs(pairs[:,1]-pairs[:,0]),n-abs(pairs[:,1]-pairs[:,0])) if len(pairs) else np.array([],int)
    return dict(samples_per_bead=len(local),both_directions=True,all_bounding_pairs=all_pairs,
        pair_count=len(pairs),penetrating_pairs=int(np.sum(minima<-.001)),
        minimum_sdf_units=float(minima.min()) if len(minima) else None,
        families={str(d):dict(pairs=int(np.sum(delta==d)),penetrations=int(np.sum((delta==d)&(minima<-.001)))) for d in np.unique(delta)},
        pairs=pairs.tolist(),minimum_sdf_by_pair=minima.tolist(),
        limitation='Negative samples establish overlap. Zero detected penetrations is sampled evidence, not exact nonintersection certification.')
