"""Shared rounded annuli on a curved local helix; radius=1 fixes the scale gauge.

Generalizes the R299 half-vector model and reuses its exact shadow tracer. Shape
is a rounded rectangle revolved around the hole axis, with an independent axial
stretch. The historical shape is exactly a member of this family.
"""
from functools import lru_cache
import numpy as np
from scipy.spatial import cKDTree
from photo2.r295.geometry import Chain as Kernel, AXES, unit
from photo2.r299.forward import Surface, shade, highlight, light_params

# first 12 parameters shared across sections; remaining 6 are local smooth fields.
NAMES=['axial','round','hole','minor','pitch','turn','tilt','elevation','roll','scale','light_az','light_el','dx','dy','angle','curve','phase','spacing']
BOUNDS=np.array([[.08,.95],[.30,.95],[.05,.36],[1.35,3.5],[.035,.4],[6.489,6.511],[-28,28],[35,88],[-85,85],[10,21],[-180,180],[18,88],[-42,42],[-42,42],[-35,35],[-.045,.045],[-np.pi,np.pi],[-.12,.12]])
DEFAULT=np.array([.22,.80,.14,2.42,.09,6.5,0,62,28,15.5,-45,60,0,0,0,0,.69,0.])

class Local(Kernel):
    blocked=Surface.blocked
    def __init__(self,v,section,hand,guards=32):
        p=self.p=dict(zip(NAMES,map(float,v)));self.hand=hand;self.radius=1.;self.axial=p['axial'];self.scale=p['scale'];self.closed=False
        self.indices=np.arange(-12-guards,13+guards);self.n=len(self.indices)
        self.hole=p['hole'];self.round=p['round']*(1-self.hole)/2
        self.radial_mid=(1+self.hole)/2;self.radial_core=(1-self.hole)/2-self.round
        self.axial_core=(1-self.hole)/2-self.round;self.stretch=self.axial/((1-self.hole)/2)
        self.bound=np.hypot(1,self.axial);self.distance=np.inf
        el,roll=np.radians([p['elevation'],p['roll']]);right=np.array([1.,0,0]);down=np.array([0,np.sin(el),-np.cos(el)])
        self.right=np.cos(roll)*right+np.sin(roll)*down;self.down=-np.sin(roll)*right+np.cos(roll)*down;self.eye=np.cross(self.right,self.down)
        self.offset=np.array(section['center'])+[p['dx'],p['dy']]
        # Deproject geographic direction only. Camera and local orientation remain variable.
        t=np.array(section['tangent']);ang=np.radians(p['angle']);t=np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]])@t
        world=np.linalg.solve(np.array([self.right[:2],self.down[:2]]),t);a=np.arctan2(world[1],world[0]);u=np.array([np.cos(a),np.sin(a),0]);w=np.array([-np.sin(a),np.cos(a),0]);z=np.array([0.,0.,1.])
        k=self.indices.astype(float);s=p['pitch']*(k+p['spacing']*k*k/56)
        # Quadratic centerline with tangent-consistent frames, curvature in radius^-1.
        self.line=s[:,None]*u+.5*p['curve']*s[:,None]**2*w
        tangent=unit(u+p['curve']*s[:,None]*w);normal=np.cross(z,tangent)
        self.phase=p['phase']+hand*2*np.pi*k/p['turn']
        radial=np.sin(self.phase)[:,None]*normal+np.cos(self.phase)[:,None]*z
        circum=np.cos(self.phase)[:,None]*normal-np.sin(self.phase)[:,None]*z
        tilt=np.radians(p['tilt']);axis=np.cos(tilt)*tangent+np.sin(tilt)*circum
        other=unit(np.cross(radial,axis));third=np.cross(axis,other)
        self.g=dict(zip(AXES,(axis,other,third)),radial=radial)
        self.centers=self.line+p['minor']*radial;self.pc=self.project(self.centers);self.tree=cKDTree(self.pc);self.query_radius=self.bound*self.scale

    def local_sdf(self,q):
        q=np.asarray(q);a=abs(np.hypot(q[...,1],q[...,2])-self.radial_mid)-self.radial_core;b=abs(q[...,0])/self.stretch-self.axial_core
        return (np.hypot(np.maximum(a,0),np.maximum(b,0))+np.minimum(np.maximum(a,b),0)-self.round)*min(1,self.stretch)

    def normal(self,q):
        rho=np.linalg.norm(q[...,1:],axis=-1);a=abs(rho-self.radial_mid)-self.radial_core;b=abs(q[...,0])/self.stretch-self.axial_core
        ga=np.maximum(a,0);gb=np.maximum(b,0);inside=ga+gb==0;ga=np.where(inside&(a>=b),1,ga);gb=np.where(inside&(b>a),1,gb)
        rr=ga*np.sign(rho-self.radial_mid)/np.maximum(rho,1e-20)
        return unit(np.stack([gb*np.sign(q[...,0])/self.stretch,rr*q[...,1],rr*q[...,2]],axis=-1))

    def camera(self,xy):
        tr=self.trace(xy,normals=False);ok=tr['owner']>=0;k=tr['owner'][ok];axes=[self.g[key][k] for key in AXES];delta=tr['points'][ok]-self.centers[k];q=np.stack([np.sum(delta*a,axis=1) for a in axes],axis=1);n=self.normal(q)
        tr['normal'][ok]=sum(n[:,j,None]*a for j,a in enumerate(axes));tr['xy']=np.asarray(xy);tr['viewer']=np.tile(self.eye,(len(xy),1));return tr

    def support(self,v,t,gradient=False):
        a=np.sum(v*t,axis=-1);perp=v-a[...,None]*t;rr=np.linalg.norm(perp,axis=-1);norm=np.sqrt(rr*rr+(self.stretch*a)**2)
        h=(1-self.round)*rr+self.axial_core*self.stretch*abs(a)+self.round*norm
        if not gradient:return h
        g=(1-self.round)*perp/np.maximum(rr[...,None],1e-20)+self.axial_core*self.stretch*np.sign(a)[...,None]*t+self.round*(perp+self.stretch**2*a[...,None]*t)/np.maximum(norm[...,None],1e-20)
        return h,g

    def samples(self,resolution=0):
        # 4 rounded corners plus flat faces in the meridian, revolved about axis.
        nr,nt=(4,24) if resolution==0 else (8,64)
        aa=[];rr=[]
        for side_a,side_r,lo in [(1,1,0),(-1,1,np.pi/2),(-1,-1,np.pi),(1,-1,3*np.pi/2)]:
            angle=np.linspace(lo,lo+np.pi/2,nr,endpoint=True)
            aa.extend(side_a*self.axial_core+self.round*np.cos(angle));rr.extend(self.radial_mid+side_r*self.radial_core+self.round*np.sin(angle))
        # corners above have mismatched quadrants for radial signs: explicit rectangle parametrization
        aa=[];rr=[]
        for sa,sr,lo in [(1,1,0),(-1,1,np.pi/2),(-1,-1,np.pi),(1,-1,3*np.pi/2)]:
            angle=np.linspace(lo,lo+np.pi/2,nr)
            aa.extend(sa*self.axial_core+self.round*np.cos(angle));rr.extend(self.radial_mid+sr*self.radial_core+self.round*np.sin(angle))
        theta=np.arange(nt)*2*np.pi/nt;a=np.repeat(aa,nt)*self.stretch;r=np.repeat(rr,nt);th=np.tile(theta,len(aa));q=np.c_[a,r*np.cos(th),r*np.sin(th)]
        normals=self.normal(q);axes=np.stack([self.g[key] for key in AXES],axis=1)
        xyz=self.centers[:,None]+np.einsum('sj,bjk->bsk',q,axes);norm=np.einsum('sj,bjk->bsk',normals,axes)
        return xyz,norm

    def polygons(self):
        ang=np.arange(48)*2*np.pi/48;v=np.cos(ang)[:,None]*self.right+np.sin(ang)[:,None]*self.down
        _,g=self.support(v[None],self.g[AXES[0]][:,None],True)
        return self.project((self.centers[:,None]+g).reshape(-1,3)).reshape(self.n,48,2)

def predict(scene,section,resolution=0,roughness=10.):
    light=light_params([scene.p['light_az'],scene.p['light_el'],roughness],'directional',scene.centers.mean(0))
    if resolution==0:
        xyz,n=scene.samples();h=unit(scene.eye+np.array(light['direction']));nl=np.maximum(n@np.array(light['direction']),0);nv=np.maximum(n@scene.eye,0)
        intensity=np.maximum(n@h,0)**(2/np.radians(roughness)**2-2)*nl*(nv>0)
        # Fast surface quadrature with conservative approximate front-depth raster.
        xy=scene.project(xyz.reshape(-1,3)).reshape(scene.n,-1,2);grid=np.rint(xy/2).astype(int);flat=grid.reshape(-1,2);_,inv=np.unique(flat,axis=0,return_inverse=True)
        depth=xyz.reshape(-1,3)@scene.eye;front=np.full(inv.max()+1,-np.inf);np.maximum.at(front,inv,depth)
        intensity*=((front[inv]-depth).reshape(intensity.shape)<.18)
        pred=[]
        for k,w in enumerate(intensity):
            hh=highlight(xy[k],w,2)
            if hh:pred.append(dict(owner=k,index=int(scene.indices[k]),point=hh['centroid'],peak=hh['peak'],strength=hh['peak_intensity']))
        return pred,dict(rays=0,unknown=0,approximate=True)
    center=np.array(section['center']);t=np.array(section['tangent']);n=np.array([-t[1],t[0]])
    # Frozen geographic window plus buffer; all guard beads cast shadows/occlude.
    extent=section.get('halfspan',52)+24
    corners=center+np.array([a*t+b*n for a in [-extent,extent] for b in [-91,91]])
    step=2. if resolution==1 else 1.;lo=np.floor(corners.min(0));hi=np.ceil(corners.max(0));yy,xx=np.mgrid[lo[1]:hi[1]+1:step,lo[0]:hi[0]+1:step];xy=np.c_[xx.ravel(),yy.ravel()]
    data=scene.camera(xy);sh=shade(scene,data,light);pred=[]
    for k in np.unique(data['owner']):
        if k<0:continue
        mask=data['owner']==k;hh=highlight(xy[mask],sh['intensity'][mask],step)
        if hh:pred.append(dict(owner=int(k),index=int(scene.indices[k]),point=hh['centroid'],peak=hh['peak'],strength=hh['peak_intensity']))
    return pred,dict(rays=len(xy),unknown=int(data['unknown'].sum()),shadow={k:v for k,v in sh.items() if k!='intensity'},approximate=False)
