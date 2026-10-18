"""Closed helicoidal staircase. Count, radius, axial are the physical inputs.

The photograph fixes the centerline and scale in this experiment. R is selected
by a deterministic contact construction, never a photographic fitting variable.
"""
from copy import deepcopy
import time
import numpy as np
from scipy.spatial import cKDTree
from photo2.r306.geometry import Chain as Placement
from photo2.r314.geometry import ShapeChain, contacts
from photo2.r318.optics import Chain as Optical
from photo2.r312.fast import Chain as Shadow
from photo2.r295.geometry import AXES, unit
from photo2.r297.common import ROOT, read

D=33.468

def parameters(count,radius,axial,hand=-1,phase=None):
    old=read(ROOT/'photo2/r319/results/best-full.json.gz')['parameters']
    p=deepcopy(old)
    if int(count)!=count or count<2 or radius<=0 or axial<=0:raise ValueError('Positive radius/thickness and integer count required')
    p.update(count=int(count),radius=float(radius),axial=float(axial),hand=int(hand),
             topology='closed',winding=int(np.floor(count/6.5+.5)),seam_fraction=-.5,
             gap_steps=0.,s0=0.,translation=[0.,0.],perspective=0.,
             axis_harmonics=[0.]*4,axis_bspline=[0.]*32,axis_nodes=[0.]*32,local_phase=[0.]*32,local_spacing=[0.]*32,
             tilt=0.,tilt_y=0.,tilt_y2=0.,minor_y=0.,radial_cant=0.,trajectory_mix=0.,
             hole=.14,rounding=.8,exterior=False,compact_centers=[],
             compact_phase=[],compact_spacing=[],compact_tilt=[],compact_cant=[])
    p['packing_spacing']='curvature-density'
    p['turn']=p['count']/p['winding']
    p['minor']=p['radius']/np.sin(np.pi/p['turn'])
    if phase is not None:p['phase']=float(phase)
    return p

class Chain(ShapeChain):
    # Exact legacy shadow kernel is valid for fixed .14/.8 annulus only.
    blocked=Shadow.blocked
    camera=Optical.camera
    def __init__(self,p,data):
        if p['topology']!='closed' or p['gap_steps']!=0 or p['seam_fraction']!=-.5:raise ValueError('Closed indexing contract')
        if p['winding']!=int(np.floor(p['count']/6.5+.5)):raise ValueError('Winding must be derived')
        if abs(p['turn']-p['count']/p['winding'])>1e-12:raise ValueError('Turn must equal count/winding')
        if p.get('hole',.14)!=.14 or p.get('rounding',.8)!=.8 or p.get('exterior',False):raise ValueError('R321 fixed shared legacy profile')
        if abs(p['s0'])>.1*D+1e-9 or np.any(p.get('translation',[0,0])):raise ValueError('R321 registration budget')
        if any(np.any(p.get(k,0)) for k in ['local_phase','local_spacing','compact_phase','compact_spacing','compact_tilt','compact_cant','tilt','radial_cant','tilt_y','tilt_y2','minor_y','trajectory_mix']):raise ValueError('R321 pilot has zero placement correction fields and derived orientation')
        coefficients=np.asarray(p.get('axis_bspline',[0.]*32))
        expected=(np.roll(coefficients,1)+4*coefficients+np.roll(coefficients,-1))/6
        if len(coefficients)!=32 or not np.allclose(p['axis_nodes'],expected,atol=1e-12):raise ValueError('Centerline must be a periodic cubic B-spline with 32 fixed knots')
        from photo2.r297.geometry import periodic_field
        if np.max(abs(periodic_field(p['axis_nodes'],np.linspace(0,1,4097))))>.1*D+1e-10:raise ValueError('Centerline correction exceeds 0.1 fixed photo diameter')
        super().__init__(p,data)
        self.offset=self.offset+np.asarray(p.get('translation',[0,0]))
        self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)
    def station(self,k):
        if self.p.get('packing_spacing','uniform')=='curvature-density':
            from .spacing import station
            return station(self,k)
        return super().station(k)
    def placement(self,k):
        # Base placement provides closed arclength and phase; its zero tilt is
        # replaced by the normal of the radial/trajectory staircase surface.
        line,g,phase=Placement.placement(self,k)
        eps=1e-3;ends=[]
        for q in [np.asarray(k)-eps,np.asarray(k)+eps]:
            l,gg,_=Placement.placement(self,q);ends.append(l+self.p['minor']*gg['radial'])
        trajectory=(ends[1]-ends[0])/(2*eps)
        body=unit(np.cross(g['radial'],trajectory))
        body*=np.where(np.sum(body*g['axis_tangent'],axis=1)<0,-1,1)[:,None]
        other=unit(np.cross(g['radial'],body));third=np.cross(body,other)
        g.update(zip(AXES,(body,other,third)))
        return line,g,phase
    def summary(self):
        p=self.p;H=1.4*self.radius*self.axial;T=self.n/p['winding'];R0=self.radius/np.sin(np.pi/T)
        t=self.g['axis_tangent'];rad=self.g['radial'];circ=np.cross(t,rad)*-1
        # radial x tangent equals circumferential in the inherited convention.
        circ=np.cross(rad,t)
        angle=np.degrees(np.arctan2(np.sum(self.g[AXES[0]]*circ,axis=1),np.sum(self.g[AXES[0]]*t,axis=1)))
        cl=self.closure();l,g,ph=self.placement([self.start,self.start+self.n]);c=l+p['minor']*g['radial']
        cl.update(center_endpoint_gap=float(np.linalg.norm(c[1]-c[0])),orientation_endpoint_gap=max(float(np.linalg.norm(g[a][1]-g[a][0])) for a in AXES))
        kk=np.linspace(self.start,self.start+self.n,4*self.n+1);ss=self.station(kk);rate=np.gradient(ss,kk)/(self.length/self.n)
        return dict(spacing_law=p.get('packing_spacing','uniform'),local_pitch_min=float(rate.min()*self.length/p['winding']),local_pitch_max=float(rate.max()*self.length/p['winding']),station_departure_max_px=float(np.max(abs(ss-(p['s0']/self.scale+kk*self.length/self.n)))*self.scale),density=getattr(self,'_density_map',(None,None,None,{}))[3],count=self.n,winding=p['winding'],turn=T,radius=self.radius,axial=self.axial,hand=p['hand'],
            H=H,diameter_photo_px=2*self.radius*self.scale,length=self.length,rise=self.length/p['winding'],
            circumference_ratio=self.length/(p['winding']*H),minor=p['minor'],ideal_minor=R0,
            minor_ratio=p['minor']/R0,ideal_tilt_deg=-p['hand']*float(np.degrees(np.arctan(H/(2*np.pi*R0)))),
            rise_tilt_deg=-p['hand']*float(np.degrees(np.arctan(self.length/p['winding']/(2*np.pi*p['minor'])))),
            actual_tilt_min_deg=float(angle.min()),actual_tilt_max_deg=float(angle.max()),closure=cl,
            axis_correction_px=float(np.max(abs(__import__('photo2.r297.geometry',fromlist=['periodic_field']).periodic_field(p['axis_nodes'],np.linspace(0,1,4097))))),phase_correction_deg=0.,spacing_correction_percent=float(abs(rate-1).max()*100))


def corrected(p,coefficients):
    q=deepcopy(p);c=np.asarray(coefficients,float)
    if c.shape!=(32,):raise ValueError('32 cubic B-spline coefficients required')
    q['axis_bspline']=c.tolist();q['axis_nodes']=((np.roll(c,1)+4*c+np.roll(c,-1))/6).tolist()
    return q
