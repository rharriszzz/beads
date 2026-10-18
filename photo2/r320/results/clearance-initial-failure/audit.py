"""Independent formula, seam, original-ray and neighbor-clearance audit."""
import numpy as np
from scipy.spatial import cKDTree
from photo2.r295.geometry import AXES,Chain as PythonChain
from photo2.r297.common import ROOT,save,read
from photo2.r318.optics import make_light
from photo2.r299.forward import shade,Surface
from .model import Chain
OUT=ROOT/'photo2/r320/results'
def support(n,t,r,a,gradient=False):
 # Independently expanded literal POV rounded rectangle: c=.57, half-flat=.086,
 # rounded radius=.344, axial scaling .7/.43 * a.
 d=np.sum(n*t,axis=-1);v=n-d[...,None]*t;q=np.linalg.norm(v,axis=-1);f=.7/.43*a;z=np.sqrt(q*q+(f*d)**2)
 h=r*(.656*q+.086*f*abs(d)+.344*z)
 if not gradient:return h
 g=r*(.656+.344*q/np.maximum(z,1e-30))[...,None]*v/np.maximum(q[...,None],1e-30)+r*(.086*f*np.sign(d)+.344*f*f*d/np.maximum(z,1e-30))[...,None]*t
 return h,g

def neighbor_gaps(s):
 rows=[]
 for offset in [1,6,7]:
  a=np.arange(s.n);b=(a+offset)%s.n;delta=s.centers[b]-s.centers[a];ta=s.g[AXES[0]][a];tb=s.g[AXES[0]][b]
  n=delta/np.linalg.norm(delta,axis=1)[:,None];step=np.full(s.n,.2)
  for _ in range(220):
   ha,ga=support(n,ta,s.radius,s.axial,True);hb,gb=support(n,tb,s.radius,s.axial,True);gap=np.sum(delta*n,axis=1)-ha-hb
   grad=delta-ga-gb;grad-=np.sum(grad*n,axis=1)[:,None]*n;c=n+step[:,None]*grad;c/=np.linalg.norm(c,axis=1)[:,None]
   ng=np.sum(delta*c,axis=1)-support(c,ta,s.radius,s.axial)-support(c,tb,s.radius,s.axial);good=ng>gap
   n[good]=c[good];step[~good]*=.5;step[good]=np.minimum(.5,step[good]*1.1)
  ha,ga=support(n,ta,s.radius,s.axial,True);hb,gb=support(n,tb,s.radius,s.axial,True)
  lo=np.sum(delta*n,axis=1)-ha-hb;hi=np.linalg.norm(delta-ga-gb,axis=1)
  # Gradient witnesses are actual external glass points unless radial norm=0.
  # Save SDF residuals to check the upper-bound endpoints explicitly.
  residual=[]
  for pts,js in [(ga,a),(-gb,b)]:
   q=np.stack([np.sum(pts*s.g[k][js],axis=1) for k in AXES],axis=1);residual.append(abs(s.local_sdf(q)))
  rows.append(dict(offset=offset,lower_min=float(lo.min()),lower_median=float(np.median(lo)),upper_median=float(np.median(hi)),upper_max=float(hi.max()),max_interval_width=float((hi-np.maximum(lo,0)).max()),near_contacts_upper_le_002r=int(np.sum(hi<=.02*s.radius)),small_gaps_upper_le_01r=int(np.sum(hi<=.1*s.radius)),unresolved_envelope=int(np.sum(lo<0)),endpoint_sdf_max=float(np.max(residual)),pairs=[dict(indices=[int(s.indices[i]),int(s.indices[j])],lower=float(l),upper=float(u),normal=nn.tolist(),seam=bool(j<i)) for i,j,l,u,nn in zip(a,b,lo,hi,n)]))
 return rows

def verify_scene(p,data,label):
 s=Chain(p,data);cert=s.certify(iterations=180,witnesses=True);checks=[];err=0.
 for w in cert['witnesses']:
  a,b=w['pair'];n=np.array(w['normal']);g=float((s.centers[b]-s.centers[a])@n-support(n,s.g[AXES[0]][a],s.radius,s.axial)-support(n,s.g[AXES[0]][b],s.radius,s.axial))
  err=max(err,abs(g-w['gap_units']));checks.append(g)
 assert cert['certified'] and min(checks)>0 and err<1e-10
 # Analytical differentiation of planar spline and phase, independent of the
 # finite difference used to orient the production body.
 k=s.indices.astype(float);a=(s.a0+s.direction*(p['s0']/s.scale+k*s.length/s.n))%s.length;u=s.inverse(a);v=s.spline(u,1);vv=s.spline(u,2);norm=np.linalg.norm(v,axis=1);t=v/norm[:,None];du=s.inverse(a,1)*s.direction*s.length/s.n
 dt=(vv-t*np.sum(vv*t,axis=1)[:,None])/norm[:,None]*du[:,None]*s.direction
 dn=np.c_[-dt[:,1],dt[:,0],np.zeros(s.n)];phi=p['phase']+p['hand']*2*np.pi*k*p['winding']/s.n
 circ=np.cross(s.g['radial'],s.g['axis_tangent']);derivative=np.c_[v*du[:,None],np.zeros(s.n)]+p['minor']*(np.sin(phi)[:,None]*dn+p['hand']*2*np.pi*p['winding']/s.n*circ)
 normal=np.cross(s.g['radial'],derivative);normal/=np.linalg.norm(normal,axis=1)[:,None];normal*=np.where(np.sum(normal*s.g['axis_tangent'],axis=1)<0,-1,1)[:,None]
 orientation=float(np.max(np.linalg.norm(normal-s.g[AXES[0]],axis=1)));assert orientation<2e-6,orientation
 rng=np.random.default_rng(320);js=rng.choice(s.n,100,replace=False);xy=s.pc[js]+rng.uniform(-s.radius*s.scale,s.radius*s.scale,(100,2))
 fast=s.camera(xy);slow=PythonChain.trace(s,xy,True);known=~slow['unknown']&~fast['unknown'];assert np.array_equal(fast['owner'][known],slow['owner'][known])
 ok=known&(fast['owner']>=0);point=float(np.max(np.linalg.norm(fast['points'][ok]-slow['points'][ok],axis=1))) if ok.any() else 0.;assert point<1e-8
 light=make_light(p,s);a=shade(s,fast,light);original=s.blocked;s.blocked=lambda pts,d,max_distance=np.inf:Surface.blocked(s,pts,d,max_distance);b=shade(s,fast,light);s.blocked=original
 intensity=float(np.max(abs(a['intensity']-b['intensity'])));assert intensity<1e-10
 gaps=neighbor_gaps(s);save(OUT/f'{label}-neighbor-gaps.json.gz',gaps)
 save(OUT/f'{label}-contact-witnesses.json.gz',cert)
 result=dict(label=label,summary=s.summary(),witnesses=len(checks),support_max_difference=err,analytic_orientation_max_difference=orientation,python_rays=len(xy),known_python_rays=int(known.sum()),python_unknown=int(slow['unknown'].sum()),point_max_difference=point,shadow_intensity_max_difference=intensity,neighbors=[{k:v for k,v in row.items() if k!='pairs'} for row in gaps])
 save(OUT/f'{label}-verification.json',result);return result
