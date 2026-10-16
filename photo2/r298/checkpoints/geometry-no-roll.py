"""R297 physical kernel with a newly parameterized planar photographic axis.

World radius fixes the unit gauge. Image-normal spline nodes have no small-deviation
prior; their range is ±45 native pixels, and both frame and arc integration change.
"""
from copy import deepcopy
from functools import lru_cache
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree
from photo2.r297.geometry import Chain as Baseline, reference, legacy_field, periodic_field, PITCH, R, unit, contact
from photo2.r295.geometry import AXES

@lru_cache(maxsize=128)
def calibrated_reference(scale,elevation,yaw,perspective,arc0,nodes):
    ref=reference(); e,y=np.radians([elevation,yaw])
    right=np.array([np.cos(y),np.sin(y),0.]);down=np.array([-np.sin(y)*np.sin(e),np.cos(y)*np.sin(e),-np.cos(e)]);eye=np.cross(right,down)
    tangent=unit(np.gradient(ref.points,axis=0));normal=np.c_[-tangent[:,1],tangent[:,0]]
    f=ref.arc/ref.length
    correction=CubicSpline(np.linspace(0,1,len(nodes)+1),np.r_[nodes,nodes[0]],bc_type='periodic')(f)
    pts=ref.points+correction[:,None]*normal;pts[-1]=pts[0]
    anchor=np.array([np.interp(arc0,ref.arc,ref.points[:,j]) for j in range(2)])
    image=(pts-anchor)/scale;base=image@np.array([right,down])
    if perspective:
        d=1/perspective;den=d*eye[2]-base[:,2]
        if np.min(abs(den))<.1*d*abs(eye[2]):raise ValueError('Camera plane singularity')
        tt=d*eye[2]/den;plane=(tt[:,None]*base+(1-tt[:,None])*d*eye)[:,:2]*scale
    else:plane=(base-base[:,2,None]/eye[2]*eye)[:,:2]*scale
    plane[-1]=plane[0];arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(plane,axis=0),axis=1))]
    a0=float(np.interp(arc0,ref.arc,arc));spline=CubicSpline(arc,plane,bc_type='periodic')
    # Fixed original camera-plane anchor: moving the curve must not cancel its
    # displacement at bead zero by silently translating the image.
    from photo2.r297.geometry import plane_reference
    origin=plane_reference(scale,elevation,yaw,perspective,arc0)[5]
    return right,down,eye,spline,a0,origin,float(arc[-1])

class Chain(Baseline):
    def __init__(self,p,inputs):
        self.p=p;self.radius=p['radius'];self.axial=p['axial'];self.scale=p['scale'];n=int(p['count']);self.n=n;self.start=n*p.get('seam_fraction',-.5)
        self.indices=np.arange(int(np.ceil(self.start)),int(np.ceil(self.start))+n)
        self.dims=np.array([self.axial,1.,1.])*self.radius/R;self.bound=self.radius*np.sqrt(1+(.7*self.axial)**2)
        self.distance=1/p['perspective'] if p['perspective'] else np.inf;self.offset=np.asarray(inputs['anchor']['measured_photo_location'])
        self.right,self.down,self.eye,self.spline,self.a0,self.origin,self.length=calibrated_reference(p['scale'],p['elevation'],p['yaw'],p['perspective'],inputs['arc0'],tuple(p.get('axis_nodes',[0.]*16)))
        self.direction=inputs['direction'];self.closed=p['topology']=='closed'
        fine=np.linspace(self.start,self.start+n,max(4097,4*n+1));rate=np.exp(legacy_field(p,'strain',fine)+periodic_field(p['local_spacing'],fine/n))
        gap=0 if self.closed else p['gap_steps']*self.length/n
        integ=np.r_[0,np.cumsum((rate[1:]+rate[:-1])*np.diff(fine)/2)];integ-=np.interp(0.,fine,integ)
        self.integral_grid=fine;self.integral=integ*(self.length-gap)/(integ[-1]-integ[0]);self.base_integral=self.integral.copy()
        blend=p.get('local_metric',0.)
        if blend:
            weight=legacy_field(dict(strain=[1.]*5),'strain',fine)*blend;lr=np.exp(np.interp(fine,[-30,30,90,150,210],p['strain']))
            target=np.r_[0,np.cumsum((lr[1:]+lr[:-1])*np.diff(fine)/2)];target-=np.interp(0.,fine,target);target*=PITCH*p['pitch']*self.scale
            self.integral+=weight*(target-self.integral)
            if np.min(np.diff(self.integral))<=0:raise ValueError('Reversed station order')
        self.station_px=p['s0']+np.interp(self.indices,fine,self.integral);self.effective_pitch=(self.length-gap)/n/PITCH/self.scale
        self.line,self.g,self.phase=self.placement(self.indices);self.centers=self.line+p['minor']*self.g['radial'];self.pc=self.project(self.centers);self.tree=cKDTree(self.pc)
        self.query_radius=self.bound*self.scale
        if np.isfinite(self.distance):
            depth=self.centers@self.eye
            if max(depth+self.bound)>.85*self.distance:raise ValueError('Camera bound')
            self.query_radius*=np.max((1+np.linalg.norm(self.centers,axis=1)/self.distance)/(1-(depth+self.bound)/self.distance)**2)

def outlines(scene, samples=48):
    """Outer convex silhouette support; holes do not alter the external envelope.

    Orthographic support is analytic. Perspective vertices are a controlled polygon
    approximation and must be checked against exact first-hit rays at export.
    """
    angle=np.arange(samples)*2*np.pi/samples;directions=np.cos(angle)[:,None]*scene.right+np.sin(angle)[:,None]*scene.down
    t=scene.g[AXES[0]][:,None,:];v=np.broadcast_to(directions,(scene.n,samples,3))
    _,g=scene.support(v,t,True)
    xyz=scene.centers[:,None,:]+g
    return scene.project(xyz.reshape(-1,3)).reshape(scene.n,samples,2)

def envelope(scene,rows,polygons=None,lanes=(-12,-6,0,6,12)):
    """Intersect projected annular outer silhouette polygons with native transects."""
    polygons=outlines(scene) if polygons is None else polygons
    result=[]
    for row in rows:
        c=np.array(row['point']);t=np.array(row['tangent']);n=np.array(row['normal'])
        near=scene.tree.query_ball_point(c,110)
        if not near:result.append([0.,0.]);continue
        q=polygons[near]-c;x=q@t;y=q@n;x1=np.roll(x,-1,axis=1);y1=np.roll(y,-1,axis=1);bounds=[]
        for lane in lanes:
            hit=((x<=lane)&(x1>lane))|((x1<=lane)&(x>lane))
            yy=y+(lane-x)*(y1-y)/np.where(abs(x1-x)>1e-12,x1-x,1.)
            vals=yy[hit];bounds.append([float(vals.min()),float(vals.max())] if len(vals) else [0.,0.])
        result.append(np.median(bounds,axis=0))
    return np.array(result)

def bead_extents(scene,rows,polygons=None):
    polygons=outlines(scene) if polygons is None else polygons
    # Conditional orientation, no observation representative becomes a center.
    _,ids=scene.tree.query([r['point'] for r in rows])
    return np.array([np.ptp(polygons[i]@np.array([r['tangent'],r['normal']]).T,axis=0) for r,i in zip(rows,ids)])
