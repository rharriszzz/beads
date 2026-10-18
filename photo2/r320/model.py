"""Closed helicoidal staircase. Only count, radius, axial are physical inputs.

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
             axis_harmonics=[0.]*4,axis_nodes=[0.]*32,local_phase=[0.]*32,local_spacing=[0.]*32,
             tilt=0.,tilt_y=0.,tilt_y2=0.,minor_y=0.,radial_cant=0.,trajectory_mix=0.,
             hole=.14,rounding=.8,exterior=False,compact_centers=[],
             compact_phase=[],compact_spacing=[],compact_tilt=[],compact_cant=[])
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
        if p.get('hole',.14)!=.14 or p.get('rounding',.8)!=.8 or p.get('exterior',False):raise ValueError('R320 fixed shared legacy profile')
        if abs(p['s0'])>.1*D+1e-9 or np.any(p.get('translation',[0,0])):raise ValueError('R320 registration budget')
        if any(np.any(p.get(k,0)) for k in ['local_phase','local_spacing','compact_phase','compact_spacing','compact_tilt','compact_cant','tilt','radial_cant','tilt_y','tilt_y2','minor_y','trajectory_mix']):raise ValueError('R320 pilot has zero placement correction fields and derived orientation')
        coeff=np.asarray(p.get('axis_harmonics',[0.]*4));u=np.arange(32)/32
        expected=sum(v*f(2*np.pi*m*u) for v,f,m in zip(coeff,[np.cos,np.sin,np.cos,np.sin],[1,1,2,2]))
        if not np.allclose(p['axis_nodes'],expected,atol=1e-12):raise ValueError('Centerline coefficients must be two harmonics')
        from photo2.r297.geometry import periodic_field
        if np.max(abs(periodic_field(p['axis_nodes'],np.linspace(0,1,4097))))>.1*D+1e-10:raise ValueError('Centerline correction exceeds 0.1 fixed photo diameter')
        super().__init__(p,data)
        self.offset=self.offset+np.asarray(p.get('translation',[0,0]))
        self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)
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
        return dict(count=self.n,winding=p['winding'],turn=T,radius=self.radius,axial=self.axial,hand=p['hand'],
            H=H,diameter_photo_px=2*self.radius*self.scale,length=self.length,rise=self.length/p['winding'],
            circumference_ratio=self.length/(p['winding']*H),minor=p['minor'],ideal_minor=R0,
            minor_ratio=p['minor']/R0,ideal_tilt_deg=-p['hand']*float(np.degrees(np.arctan(H/(2*np.pi*R0)))),
            rise_tilt_deg=-p['hand']*float(np.degrees(np.arctan(self.length/p['winding']/(2*np.pi*p['minor'])))),
            actual_tilt_min_deg=float(angle.min()),actual_tilt_max_deg=float(angle.max()),closure=cl,
            axis_correction_px=float(np.max(abs(__import__('photo2.r297.geometry',fromlist=['periodic_field']).periodic_field(p['axis_nodes'],np.linspace(0,1,4097))))),phase_correction_deg=0.,spacing_correction_percent=0.)

def derive(p,data,refine=True):
    """First certified R in ascending 1..1.16 R0 grid, then 8 bisections.

    Conservative full-chain support separation is the construction rule. Failed
    convex certificates are unresolved until actual-solid fallback; never called
    collision merely because the sufficient test fails. No empirical .96 input.
    The 16% ceiling and circumference band are explicit experimental budgets.
    """
    began=time.perf_counter();p=deepcopy(p);R0=p['radius']/np.sin(np.pi/(p['count']/p['winding']));history=[]
    def test(f):
        q=deepcopy(p);q['minor']=float(R0*f);s=Chain(q,data);c=s.certify(iterations=100,witnesses=False)
        history.append(dict(factor=float(f),**c));return s,c
    s,c=test(1.)
    if refine and not c['certified']:
        lo=1.;hi=None
        for f in [1.02,1.04,1.08,1.12,1.16]:
            ss,cc=test(f)
            if cc['certified']:hi=f;s,c=ss,cc;break
            lo=f;s,c=ss,cc
        if hi is not None:
            for _ in range(8):
                mid=(lo+hi)/2;ss,cc=test(mid)
                if cc['certified']:hi=mid;s,c=ss,cc
                else:lo=mid
            # positive clearance avoids accepting exact numerical tangency
            s,c=test(hi+2e-5)
    sm=s.summary();ratio_ok=.90<=sm['circumference_ratio']<=1.15
    return s,dict(certified=c['certified'],ratio_accepted=ratio_ok,eligible=bool(c['certified'] and ratio_ok),
        classification='certified-separation' if c['certified'] else 'unresolved-support',history=history,
        summary=sm,seconds=time.perf_counter()-began)


def corrected(p,coefficients):
    q=deepcopy(p);q['axis_harmonics']=list(map(float,coefficients));u=np.arange(32)/32
    q['axis_nodes']=sum(v*f(2*np.pi*m*u) for v,f,m in zip(coefficients,[np.cos,np.sin,np.cos,np.sin],[1,1,2,2])).tolist()
    return q
