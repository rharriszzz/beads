"""Two additional compact smooth nodes with independent, narrower support.

Same rigid bead shape; no free bead transforms. Zero fields exactly bypass all
rotations. The only extension is independent support width for these two nodes.
"""
import numpy as np
from photo2.r315.model import bump
from photo2.r295.geometry import AXES
from .experiment import GeneralChain

class Chain(GeneralChain):
    def station(self,k):
        v=super().station(k)
        for c,a in zip(self.p.get('patch_centers',[]),self.p.get('patch_spacing',[])):
            v=v+a*self.extent/self.n*(np.asarray(k)-c)*bump(k,c,self.p.get('patch_halfwidth',10.))
        return v
    def placement(self,k):
        line,g,phase=super().placement(k);cs=self.p.get('patch_centers',[]);w=self.p.get('patch_halfwidth',10.)
        phi=sum(a*bump(k,c,w) for a,c in zip(self.p.get('patch_phase',[]),cs))
        if np.any(phi):
            t=g['axis_tangent'];co=np.cos(phi)[:,None];si=np.sin(phi)[:,None]
            for key in [*AXES,'radial']:
                v=g[key];g[key]=co*v-si*np.cross(t,v)+(1-co)*np.sum(t*v,axis=1)[:,None]*t
            phase=phase+phi
        for field,axis in [('patch_tilt','radial'),('patch_cant',AXES[1])]:
            angle=sum(a*bump(k,c,w) for a,c in zip(self.p.get(field,[]),cs))
            if np.any(angle):
                co=np.cos(np.radians(angle))[:,None];si=np.sin(np.radians(angle))[:,None];t=g[axis].copy()
                for key in AXES:
                    v=g[key];g[key]=co*v+si*np.cross(t,v)+(1-co)*np.sum(t*v,axis=1)[:,None]*t
        return line,g,phase
    def __init__(self,p,data):
        super().__init__(p,data)
        if not p.get('patch_centers'):return
        k=np.linspace(-110,110,1761);cs=p['patch_centers'];w=p.get('patch_halfwidth',10.);eps=.001
        def value(field,x):return sum(a*bump(x,c,w) for c,a in zip(cs,p.get(field,[0]*len(cs))))
        ph=(value('patch_phase',k+eps)-value('patch_phase',k-eps))/(2*eps)
        oldcs=p['compact_centers'];pw=p['phase_halfwidth'];sw=p['spacing_halfwidth'];ow=p.get('orientation_halfwidth',18)
        ph+=sum(a*(bump(k+eps,c,pw)-bump(k-eps,c,pw))/(2*eps) for c,a in zip(oldcs,p['compact_phase']))
        sp=sum(a*((k+eps-c)*bump(k+eps,c,w)-(k-eps-c)*bump(k-eps,c,w))/(2*eps) for c,a in zip(cs,p.get('patch_spacing',[0]*len(cs))))
        sp+=sum(a*((k+eps-c)*bump(k+eps,c,sw)-(k-eps-c)*bump(k-eps,c,sw))/(2*eps) for c,a in zip(oldcs,p['compact_spacing']))
        tilt=value('patch_tilt',k)+sum(a*bump(k,c,ow) for c,a in zip(oldcs,p['compact_tilt']))
        cant=value('patch_cant',k)+p.get('radial_cant',0)+sum(a*bump(k,c,ow) for c,a in zip(oldcs,p['compact_cant']))
        if max(abs(ph))>.05*2*np.pi/6.5 or max(abs(sp))>.02:raise ValueError('combined narrow + inherited compact rate bound')
        if max(abs(tilt))>20 or max(abs(cant))>12:raise ValueError('combined narrow + inherited orientation bound')
        if np.hypot(np.diff(tilt),np.diff(cant)).max()/(k[1]-k[0])>3:raise ValueError('combined narrow orientation slope bound')
