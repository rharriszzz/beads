"""Full-length placement; R295 surfaces, camera rays and support are inherited.

Closed families have integer minor winding and a periodic right-handed frame.
Open families leave an explicit seam gap and retain free (noninteger) winding.
The image reference is a conditional planar axis, never measured bead centers.
"""
from copy import deepcopy
from functools import lru_cache
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from photo2.r295.geometry import Chain as LocalChain, AXES, KNOTS, R, PITCH, unit, extend
from photo2.r295.contact_fallback import audit_pair
from photo2.r295.physical_audit import independent_support
from photo2.r293.geometry import Reference
from .common import *

FIELD_SIZE = 32

@lru_cache(maxsize=1)
def reference():
    return Reference()

@lru_cache(maxsize=32)
def plane_reference(scale, elevation, yaw, perspective, arc0):
    ref=reference();e,y=np.radians([elevation,yaw])
    right=np.array([np.cos(y),np.sin(y),0.])
    down=np.array([-np.sin(y)*np.sin(e),np.cos(y)*np.sin(e),-np.cos(e)])
    eye=np.cross(right,down)
    anchor=np.array([np.interp(arc0,ref.arc,ref.points[:,j]) for j in range(2)])
    image=(ref.points-anchor)/scale; base=image@np.array([right,down])
    if perspective:
        distance=1/perspective
        denominator=distance*eye[2]-base[:,2]
        if np.min(np.abs(denominator))<.1*distance*abs(eye[2]):
            raise ValueError('Camera plane approaches a projection singularity')
        t=distance*eye[2]/denominator
        plane=(t[:,None]*base+(1-t[:,None])*distance*eye)[:,:2]*scale
    else:
        plane=(base-base[:,2,None]/eye[2]*eye)[:,:2]*scale
    plane[-1]=plane[0]
    arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))]
    a0=float(np.interp(arc0,ref.arc,arc))
    spline=CubicSpline(arc,plane,bc_type='periodic')
    origin=spline(a0)
    return right,down,eye,spline,a0,origin,float(arc[-1])

def periodic_field(values, f, derivative=0):
    values=np.asarray(values)
    spline=CubicSpline(np.linspace(-.5,.5,len(values)+1),np.r_[values,values[0]],bc_type='periodic')
    return spline((np.asarray(f)+.5)%1-.5,derivative)

def legacy_field(p,key,k):
    """Keep historic knots near bead zero; smoothly taper extrapolation elsewhere."""
    k=np.asarray(k)
    taper=np.ones_like(k,dtype=float)
    left=np.clip((-30-k)/120,0,1);right=np.clip((k-210)/190,0,1)
    smooth=lambda x:x*x*(3-2*x)
    taper=(1-smooth(left))*(1-smooth(right))
    return np.interp(k,KNOTS,p[key])*taper

def full_parameters(base,count,topology='closed'):
    p=extend(deepcopy(base));p.update(count=int(count),topology=topology,
        winding=int(round(count/p['turn'])),gap_steps=1.,
        local_phase=[0.]*FIELD_SIZE,local_spacing=[0.]*FIELD_SIZE,local_bend=[0.]*FIELD_SIZE)
    return p

class Chain(LocalChain):
    def __init__(self,p,inputs):
        self.p=p;self.radius=p['radius'];self.axial=p['axial'];self.scale=p['scale']
        n=int(p['count']);self.n=n;self.start=n*p.get('seam_fraction',-.5)
        self.indices=np.arange(int(np.ceil(self.start)),int(np.ceil(self.start))+n)
        self.dims=np.array([self.axial,1.,1.])*self.radius/R
        self.bound=self.radius*np.sqrt(1+(.7*self.axial)**2)
        self.distance=1/p['perspective'] if p['perspective'] else np.inf
        self.offset=np.asarray(inputs['anchor']['measured_photo_location'])
        self.right,self.down,self.eye,self.spline,self.a0,self.origin,self.length=plane_reference(
            p['scale'],p['elevation'],p['yaw'],p['perspective'],inputs['arc0'])
        self.direction=inputs['direction'];self.closed=p['topology']=='closed'
        fine=np.linspace(self.start,self.start+n,max(4097,4*n+1))
        rate=np.exp(legacy_field(p,'strain',fine)+periodic_field(p['local_spacing'],fine/n))
        gap=0 if self.closed else p['gap_steps']*self.length/n
        integ=np.r_[0,np.cumsum((rate[1:]+rate[:-1])*np.diff(fine)/2)]
        integ-=np.interp(0.,fine,integ)
        gap=0 if self.closed else p['gap_steps']*self.length/n
        self.integral_grid=fine;self.integral=integ*(self.length-gap)/(integ[-1]-integ[0])
        self.base_integral=self.integral.copy()
        blend=p.get('local_metric',0.)
        if blend:
            # A compact station correction preserves the exterior fit exactly.
            # Integrate the original local physical rate; do not renormalize it.
            weight=legacy_field(dict(strain=[1.]*5),'strain',fine)*blend
            local_rate=np.exp(np.interp(fine,KNOTS,p['strain']))
            target=np.r_[0,np.cumsum((local_rate[1:]+local_rate[:-1])*np.diff(fine)/2)]
            target-=np.interp(0.,fine,target)
            target*=PITCH*p['pitch']*self.scale
            self.integral+=weight*(target-self.integral)
            if np.min(np.diff(self.integral))<=0:raise ValueError('Compact station correction reverses local order')
        self.station_px=p['s0']+np.interp(self.indices,fine,self.integral)
        self.effective_pitch=(self.length-gap)/n/PITCH/self.scale
        self.line,self.g,self.phase=self.placement(self.indices)
        self.centers=self.line+p['minor']*self.g['radial']
        self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)
        self.query_radius=self.bound*self.scale
        if np.isfinite(self.distance):
            depth=self.centers@self.eye
            if np.max(depth+self.bound)>.85*self.distance:
                raise ValueError('Geometry too close to camera for conservative projection bound')
            self.query_radius*=np.max((1+np.linalg.norm(self.centers,axis=1)/self.distance)/(1-(depth+self.bound)/self.distance)**2)

    def placement(self,k):
        k=np.asarray(k,dtype=float);p=self.p;n=p['count']
        # At the seam test k +/- N explicitly; preserve unwrapped station progress.
        cycle=np.floor((k-self.start)/n);wrapped=k-cycle*n
        integrated=np.interp(wrapped,self.integral_grid,self.integral)
        extent=self.integral[-1]-self.integral[0]
        aa=self.a0+self.direction*(p['s0']+integrated+cycle*extent)
        base=self.spline(aa%self.length);t=unit(self.spline(aa%self.length,1))*self.direction
        normal=np.c_[-t[:,1],t[:,0]]
        bend=legacy_field(p,'bend',wrapped)+periodic_field(p['local_bend'],k/n)
        xy=base+bend[:,None]*normal
        # Finite differences include the same shared smooth bend on both sides.
        eps=.01
        def bent(q):
            cyc=np.floor((q-self.start)/n);w=q-cyc*n
            a=self.a0+self.direction*(p['s0']+np.interp(w,self.integral_grid,self.integral)+cyc*extent)
            tt=unit(self.spline(a%self.length,1))*self.direction
            b=legacy_field(p,'bend',w)+periodic_field(p['local_bend'],q/n)
            return self.spline(a%self.length)+b[:,None]*np.c_[-tt[:,1],tt[:,0]]
        t=unit(bent(k+eps)-bent(k-eps))
        tangent=np.c_[t,np.zeros(len(k))];normal=np.c_[-t[:,1],t[:,0],np.zeros(len(k))];z=np.tile([0.,0.,1.],(len(k),1))
        turns=p['winding']/n if self.closed else 1/p['turn']
        phase=p['phase']+p['hand']*2*np.pi*k*turns+legacy_field(p,'phase_knots',wrapped)+periodic_field(p['local_phase'],k/n)
        phase+=p.get('local_phase_bias',0.)*legacy_field(dict(strain=[1.]*5),'strain',wrapped)
        phase+=p.get('local_turn',0.)*legacy_field(dict(strain=[1.]*5),'strain',wrapped)*p['hand']*2*np.pi*wrapped*(1/p['turn']-turns)
        if p.get('phase_transport',0.):
            # Partial phase transport through a compact station correction.
            # Zero in the restored core; unchanged at the exterior and seam.
            # Aggressive transport can collide and must pass the usual contact gate.
            original_index=np.interp(integrated,self.base_integral,self.integral_grid)
            transport=(1-legacy_field(dict(strain=[1.]*5),'strain',wrapped))*(original_index-wrapped)
            phase+=p['phase_transport']*p['hand']*2*np.pi*turns*transport
        radial=np.sin(phase)[:,None]*normal+np.cos(phase)[:,None]*z
        line=np.c_[(xy-self.origin)/self.scale,np.zeros(len(k))]
        return line,dict(zip(AXES,(tangent,normal,z)),radial=radial),phase

    def closure(self):
        k=np.array([self.start,self.start+self.n]);line,g,phase=self.placement(k)
        return dict(topology=self.p['topology'],axis_endpoint_gap=float(np.linalg.norm(line[1]-line[0])),
            radial_endpoint_gap=float(np.linalg.norm(g['radial'][1]-g['radial'][0])),
            tangent_endpoint_gap=float(np.linalg.norm(g[AXES[0]][1]-g[AXES[0]][0])),
            phase_turns=float((phase[1]-phase[0])/(2*np.pi)),integer_winding=self.p['winding'] if self.closed else None,
            seam_indices=[int(self.indices[-1]),int(self.indices[0])],
            seam_center_distance=float(np.linalg.norm(self.centers[-1]-self.centers[0])),
            effective_pitch=self.effective_pitch,
            inference='Conditional topology. Periodic reference alone does not prove a physical joint.')

def contact(scene, exact=False):
    cert=scene.certify(iterations=180 if exact else 65,witnesses=True)
    cert['state']='certified-nonintersection' if cert['certified'] else 'unresolved'
    cert['fallback']=[]
    failed=[w for w in cert['witnesses'] if not w['separated']]
    if failed:
        # A demonstrated volume overlap is sufficient to reject. Budget exhaustion
        # remains unresolved; no absence-of-samples certificate is permitted.
        for w in failed[:(12 if exact else 3)]:
            result=audit_pair(scene,*w['pair'],max_depth=13 if exact else 9,max_nodes=100000 if exact else 16000)
            cert['fallback'].append(dict(pair=w['pair'],**result))
            if result['state']=='demonstrated-interpenetration':
                cert['state']=result['state'];break
        if len(cert['fallback'])==len(failed) and all(r['state']=='certified-nonintersection' for r in cert['fallback']):
            cert.update(certified=True,state='certified-nonintersection')
    if exact:
        gaps=[]
        for w in cert['witnesses']:
            a,b=w['pair'];v=np.asarray(w['normal'])
            gap=float((scene.centers[b]-scene.centers[a])@v-independent_support(v,scene.g[AXES[0]][a],scene.radius,scene.axial)-independent_support(v,scene.g[AXES[0]][b],scene.radius,scene.axial))
            if abs(gap-w['gap_units'])>1e-9:
                raise ArithmeticError('Independent support witness disagrees')
            gaps.append(gap)
        cert['independent_minimum_gap']=min(gaps,default=None)
        cert['index_pairs']=[[int(scene.indices[a]),int(scene.indices[b])] for a,b in [w['pair'] for w in cert['witnesses']]]
    return cert

def valid(p,count_range):
    scalars=dict(scale=(6.6,10.5),elevation=(48,88),yaw=(-22,22),perspective=(0,.0015),radius=(1.60,2.12),
        axial=(.70,1.18),minor=(3.7,4.5),turn=(6.30,6.75),s0=(-18,18),phase=(-np.pi,np.pi),gap_steps=(.25,12.))
    if not np.isfinite(p.get('local_phase_bias',0.)) or abs(p.get('local_phase_bias',0.))>1.2:return False
    if not 0<=p.get('phase_transport',0.)<=1:return False
    if not (-.85<=p.get('seam_fraction',-.5)<=-.15 and 0<=p.get('local_metric',0.)<=1 and 0<=p.get('local_turn',0.)<=1):return False
    if not all(np.isfinite(p[k]) and lo<=p[k]<=hi for k,(lo,hi) in scalars.items()):return False
    if not (count_range[0]<=p['count']<=count_range[1] and isinstance(p['count'],int)):return False
    if p['topology'] not in ('closed','open') or p['hand'] not in (-1,1):return False
    if not 6.30<=p['count']/p['winding']<=6.75:return False
    for key,limit in [('local_phase',1.2),('local_spacing',.15),('local_bend',10.)]:
        if len(p[key])!=FIELD_SIZE or not np.isfinite(p[key]).all() or max(abs(np.asarray(p[key])))>limit:return False
    return True
