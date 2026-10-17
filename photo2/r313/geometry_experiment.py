"""Shared annular profile and coherent trajectory-related orientation experiments.

Original R312 implementations remain unchanged. h=0.14, rounding=0.8,
trajectory_mix=0 exactly reproduce their shape and orientation law.
"""
import ctypes,subprocess,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from photo2.r312.fast import Chain as Base
from photo2.r295.geometry import AXES,unit
from photo2.r279.geometry import R
from photo2.r297.common import sha
from photo2.r295.contact_fallback import audit_pair
from photo2.r299.forward import Surface

SOURCE=Path(__file__).with_name('shape_kernel.cpp');LIB=Path('/tmp')/('beads-r313-'+sha(SOURCE)[:16]+'.so')
_lib=None

def kernel(q,v,begin,end,dims,direction):
 global _lib
 if _lib is None:
  if not LIB.exists():subprocess.run(['g++','-O3','-std=c++17','-shared','-fPIC',str(SOURCE),'-o',str(LIB)],check=True)
  _lib=ctypes.CDLL(str(LIB));ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');ip=np.ctypeslib.ndpointer(dtype=np.int32,flags='C_CONTIGUOUS');_lib.march.argtypes=[ctypes.c_long,ptr,ptr,ptr,ptr,ptr,ctypes.c_double,ctypes.c_int,ptr,ip]
 n=len(begin);depth=np.empty(n);state=np.empty(n,np.int32);args=[np.ascontiguousarray(x,dtype=float) for x in [q,v,begin,end,dims]];_lib.march(n,*args,R,direction,depth,state);return depth,state

class ShapeMixin:
 def __init__(self,p,data):
  self.hole=p.get('hole',.14);self.rounding=p.get('rounding',.8)
  if not (.02<=self.hole<=.60 and .25<=self.rounding<=1.):raise ValueError('Shared profile exploration bound')
  super().__init__(p,data)
 def placement(self,k):
  line,g,phase=super().placement(k);mix=self.p.get('trajectory_mix',0.)
  if mix:
   eps=.001;cm=[]
   for kk in [np.asarray(k)-eps,np.asarray(k)+eps]:
    l,gg,_=super().placement(kk);y=(self.project(l)[:,1]-1591)/1591
    cm.append(l+self.p['minor']*(1+self.p.get('minor_y',0)*y[:,None])*gg['radial'])
   trajectory=unit(cm[1]-cm[0]);base=g[AXES[0]];dot=np.clip(np.sum(base*trajectory,axis=1),-1,1);angle=np.arccos(dot)
   v=trajectory-dot[:,None]*base;vn=np.linalg.norm(v,axis=1);v=v/np.maximum(vn[:,None],1e-12)
   body=np.cos(mix*angle)[:,None]*base+np.sin(mix*angle)[:,None]*v
   other=unit(np.cross(g['radial'],body));third=np.cross(body,other);g.update(zip(AXES,[body,other,third]))
  return line,g,phase
 def profile(self):
  t=(1-self.hole)/2;c=(1+self.hole)/2;r=t*self.rounding;a=t-r;return c,a,r,.7/t
 def local_sdf(self,q):
  q=np.asarray(q)/self.dims;c,a,r,f=self.profile();u=abs(np.hypot(q[...,1],q[...,2])-c*R)-a*R;v=abs(q[...,0])/f-a*R
  return (np.hypot(np.maximum(u,0),np.maximum(v,0))+np.minimum(np.maximum(u,v),0)-r*R)*min(self.dims)
 def support(self,n,t,gradient=False):
  n=np.asarray(n);t=np.asarray(t);dot=np.sum(n*t,axis=-1);rv=n-dot[...,None]*t;rad=np.linalg.norm(rv,axis=-1);c,a,r,f=self.profile();f*=self.axial;length=np.sqrt(rad*rad+(f*dot)**2)
  value=self.radius*((c+a)*rad+a*f*abs(dot)+r*length)
  if not gradient:return value
  dr=self.radius*((c+a)+r*rad/np.maximum(length,1e-30));da=self.radius*(a*f*np.sign(dot)+r*f*f*dot/np.maximum(length,1e-30));grad=dr[...,None]*rv/np.maximum(rad[...,None],1e-30)+da[...,None]*t
  return value,grad
 def trace(self,xy,normals=False):
  if normals:
   from photo2.r295.geometry import Chain as Python
   return Python.trace(self,xy,True)
  xy=np.asarray(xy,float).reshape(-1,2)
  if len(xy)>20000:
   parts=[self.trace(xy[i:i+20000]) for i in range(0,len(xy),20000)];out={k:np.concatenate([z[k] for z in parts]) for k in ['owner','unknown','points','normal']};out['isolated_counts']=sum(z['isolated_counts'] for z in parts);return out
  base=((xy-self.offset)/self.scale)@np.array([self.right,self.down]);ray=unit(self.eye-base/self.distance) if np.isfinite(self.distance) else np.tile(self.eye,(len(xy),1))
  near=self.tree.query_ball_point(xy,self.query_radius+1e-4);aa=np.repeat(np.arange(len(xy)),[len(z) for z in near]);kk=np.array([j for z in near for j in z],int)
  best=np.full(len(xy),-np.inf);owner=np.full(len(xy),-1,int);unknown=np.zeros(len(xy),bool);counts=np.zeros(self.n,int)
  if len(aa):
   delta=base[aa]-self.centers[kk];mid=-np.sum(delta*ray[aa],axis=1);perp=np.sum(delta*delta,axis=1)-mid*mid;keep=perp<self.bound**2
   aa,kk,delta,mid,perp=[v[keep] for v in [aa,kk,delta,mid,perp]];axes=[self.g[key][kk] for key in AXES];q=np.stack([np.sum(delta*v,axis=1) for v in axes],axis=1);v=np.stack([np.sum(z*ray[aa],axis=1) for z in axes],axis=1);half=np.sqrt(np.maximum(self.bound**2-perp,0))
   dep,state=kernel(q,v,mid+half,mid-half,np.r_[self.dims,self.hole,self.rounding],-1);hit=state==1;active=state==2;np.maximum.at(best,aa[hit],dep[hit]);front=hit&(dep>=best[aa]-1e-6);owner[aa[front]]=kk[front];unknown[aa[active]]=True;owner[unknown]=-1;counts=np.bincount(kk[hit],minlength=self.n)
  points=base+np.where(np.isfinite(best),best,0)[:,None]*ray
  return dict(owner=owner,unknown=unknown,points=points,normal=np.zeros_like(points),isolated_counts=counts)
 def camera(self,xy):
  xy=np.asarray(xy).reshape(-1,2);tr=self.trace(xy);ok=tr['owner']>=0;k=tr['owner'][ok];delta=tr['points'][ok]-self.centers[k];axes=[self.g[key][k] for key in AXES];q=np.stack([np.sum(delta*a,axis=1) for a in axes],axis=1);eps=1e-5
  grad=np.stack([(self.local_sdf(q+np.eye(3)[j]*eps)-self.local_sdf(q-np.eye(3)[j]*eps))/(2*eps) for j in range(3)],axis=1);n=unit(grad);tr['normal'][ok]=sum(n[:,j,None]*a for j,a in enumerate(axes));tr['xy']=xy;tr['viewer']=unit(self.distance*self.eye-tr['points']) if np.isfinite(self.distance) else np.tile(self.eye,(len(xy),1));return tr
 blocked=Surface.blocked

class ShapeChain(ShapeMixin,Base):pass

from photo2.r311.model import Legacy
class ShapeLegacy(ShapeMixin,Legacy):pass

def contacts(s,seconds=.5,all_pairs=True):
 """Sufficient envelope first, actual hollow solid fallback; never conflate failure."""
 began=time.monotonic();cert=s.certify(iterations=120,witnesses=True);cert['classification']='certified-separation' if cert['certified'] else 'unresolved';cert['actual_solid_checks']=[]
 if not cert['certified']:
  failed=[w for w in cert['witnesses'] if not w['separated']]
  # Deepest apparent conflicts first: a witnessed true penetration settles rejection.
  failed.sort(key=lambda w:w['gap_units'])
  for w in failed:
   if time.monotonic()-began>seconds:break
   r=audit_pair(s,*w['pair'],max_depth=12,max_nodes=20000);cert['actual_solid_checks'].append(dict(pair=w['pair'],**r))
   if r['state']=='demonstrated-interpenetration':cert['classification']='demonstrated-interpenetration';break
  else:
   if all(r['state']=='certified-nonintersection' for r in cert['actual_solid_checks']):cert['classification']='certified-separation';cert['certified']=True
 cert['contact_seconds']=time.monotonic()-began;return cert

def paper(s):
 n=np.array([0.,0.,1.]);bottom=s.centers[:,2]-s.support(np.tile(n,(s.n,1)),s.g[AXES[0]]);plane=float(bottom.min());clear=bottom-plane
 return dict(plane_z=plane,translation_to_paper_z0=-plane,minimum_clearance=float(clear.min()),maximum_clearance=float(clear.max()),p95_clearance=float(np.percentile(clear,95)),near_contact_count=int(np.sum(clear<=.02*s.radius)),tolerance=.02*s.radius,bodies=s.n,policy='One horizontal supporting plane below every exact convex-support minimum. Rigid vertical translation always possible; sparse contact does not establish mechanical equilibrium or measured paper pose.')
