"""Finite curved helix, literal old annulus and one common orthographic camera.

No rendered images are generated. Exact first-hit surface queries reuse R282.
The rope axis remains in one table plane. A finite context guards end occlusion.
"""
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from photo2.r279.geometry import R, PITCH, SURFACE
from photo2.r282.geometry import Scene, unit
from photo2.r293.geometry import Reference
from .common import GUARD

class Chain(Scene):
    def __init__(self,p,inputs,indices=None):
        self.p=p; self.indices=np.arange(GUARD[0],GUARD[1]+1) if indices is None else np.asarray(indices)
        self.n=len(self.indices); self.radius=R;self.bound=R*np.sqrt(1+.7**2)
        ref=Reference(); e=np.radians(p['elevation']); self.scale=p['scale']
        self.right=np.array([1.,0,0]);self.down=np.array([0,np.sin(e),-np.cos(e)])
        self.eye=np.cross(self.right,self.down)
        # Reference is image-only, with no previous fitted pose or global bead count.
        plane=ref.points/[1,np.sin(e)]
        arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))]
        a0=np.interp(inputs['arc0'],ref.arc,arc); self.offset=np.array(inputs['anchor']['measured_photo_location'])
        self.origin_plane=np.c_[*[np.interp([a0],arc,plane[:,j]) for j in range(2)]][0]
        spline=CubicSpline(arc,plane)
        k=self.indices.astype(float)
        # log-rate knots allow smooth axial strain without changing the 6.5 minor turn.
        knots=np.array([-30.,30.,90.,150.,210.])
        strain=np.array(p.get('strain',[0.]*5))
        fine=np.arange(-60.,271.,.25)
        rate=np.exp(np.interp(fine,knots,strain))
        integ=np.r_[0,np.cumsum((rate[1:]+rate[:-1])*.125)]
        integ-=np.interp(0.,fine,integ)
        station=p['s0']+PITCH*p['pitch']*self.scale*np.interp(k,fine,integ)
        aa=a0+inputs['direction']*station
        xy=spline(aa); tt=unit(spline(aa,1))*inputs['direction']
        tangent=np.c_[tt,np.zeros(self.n)];normal=np.c_[-tt[:,1],tt[:,0],np.zeros(self.n)]
        z=np.tile([0.,0.,1.],(self.n,1))
        bend=np.interp(k,knots,p.get('bend',[0.]*5))
        xy+=bend[:,None]*normal[:,:2]
        # Tangents include slow axis correction rather than rotating beads independently.
        if np.any(bend):
            tt=unit(np.gradient(xy,axis=0));tangent=np.c_[tt,np.zeros(self.n)];normal=np.c_[-tt[:,1],tt[:,0],np.zeros(self.n)]
        phase=p['phase']+p['hand']*2*np.pi*k/6.5
        radial=np.sin(phase)[:,None]*normal+np.cos(phase)[:,None]*z
        self.line=np.c_[(xy-self.origin_plane)/self.scale,np.zeros(self.n)]
        self.centers=self.line+4*radial
        self.g=dict(surface_tangent=tangent,surface_normal=normal,surface_binormal=z,radial=radial)
        self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)
        self.station_px=station

    def project(self,xyz):
        xyz=np.asarray(xyz)
        return np.c_[xyz@self.right,xyz@self.down]*self.scale+self.offset

    def surface_points(self):
        return self.centers[:,None,:]+sum(SURFACE[None,:,j,None]*self.g[key][:,None,:]
            for j,key in enumerate(('surface_tangent','surface_normal','surface_binormal')))

    def approximate_visible_centroids(self):
        xyz=self.surface_points();xy=self.project(xyz.reshape(-1,3));depth=xyz.reshape(-1,3)@self.eye
        # Z-buffered analytic surface samples initialize only, never certify a match.
        bins=np.floor(xy/2).astype(int);key=bins[:,0]+bins[:,1]*100000
        order=np.lexsort((-depth,key));unique=np.r_[True,np.diff(key[order])!=0];keep=order[unique]
        owners=keep//xyz.shape[1];counts=np.bincount(owners,minlength=self.n)
        cent=np.c_[np.bincount(owners,weights=xy[keep,0],minlength=self.n),np.bincount(owners,weights=xy[keep,1],minlength=self.n)]/np.maximum(counts[:,None],1)
        return cent,counts

def nominal(hand=1):
    return dict(hand=hand,scale=8.5,pitch=1.30,elevation=80.,phase=0.,s0=0.,strain=[0.]*5,bend=[0.]*5)
