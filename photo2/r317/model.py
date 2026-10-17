"""Shared/coherent radial cant: rigid orientation, with identical unchanged centers.

R306/R316 axis lies in the tangent/circumferential plane. This added angle rotates
that axis toward the radial direction around its transverse body axis. It does not
rotate the placement radial vector or translate any bead. Zero is bit-identical.
"""
import numpy as np
from photo2.r316.model import Chain as Previous
from photo2.r315.model import bump
from photo2.r295.geometry import AXES
class Chain(Previous):
    def placement(self,k):
        line,g,phase=super().placement(k)
        centers=self.p.get('compact_centers',[-13,0,13]);width=self.p.get('orientation_halfwidth',18)
        a=self.p.get('radial_cant',0.)+sum(v*bump(k,c,width) for c,v in zip(centers,self.p.get('compact_cant',[0]*len(centers))))
        if np.max(np.abs(a))>12+1e-10:raise ValueError('radial cant exceeds exploratory 12 degrees')
        kk=np.linspace(-110,110,1761);cc=self.p.get('radial_cant',0.)+sum(v*bump(kk,c,width) for c,v in zip(centers,self.p.get('compact_cant',[0]*len(centers))))
        tt=sum(v*bump(kk,c,width) for c,v in zip(centers,self.p.get('compact_tilt',[0]*len(centers))))
        rate=np.hypot(np.diff(cc),np.diff(tt))/np.diff(kk)
        if rate.max()>3+1e-10:raise ValueError('combined coherent orientation derivative exceeds 3 deg/address')
        if np.any(a):
            axis=g[AXES[1]].copy();a=np.radians(a)[:,None];co=np.cos(a);si=np.sin(a)
            for key in AXES:
                v=g[key];g[key]=co*v+si*np.cross(axis,v)+(1-co)*np.sum(axis*v,axis=1)[:,None]*axis
        return line,g,phase
