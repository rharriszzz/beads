"""Independent support, dense density integration and original Python rays."""
import numpy as np
from scipy.integrate import cumulative_simpson
from scipy.interpolate import PchipInterpolator
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r295.geometry import AXES,Chain as PythonChain
from photo2.r320.audit import support
from .gaps import neighbor_gaps
from photo2.r318.optics import make_light
from photo2.r299.forward import shade,Surface
from .model import Chain
from .packing import curvature
OUT=ROOT/'photo2/r321/results'

def verify(p,data,label):
 s=Chain(p,data);cert=s.certify(iterations=220,witnesses=True);assert cert['certified'];diff=0.;gaps=[]
 for w in cert['witnesses']:
  a,b=w['pair'];n=np.array(w['normal']);g=float((s.centers[b]-s.centers[a])@n-support(n,s.g[AXES[0]][a],s.radius,s.axial)-support(n,s.g[AXES[0]][b],s.radius,s.axial));gaps.append(g);diff=max(diff,abs(g-w['gap_units']))
 assert min(gaps)>1e-6 and diff<1e-10
 # Separately integrate on twice the resolution, using independent interpolants.
 drift=0.;M=None
 if p.get('packing_spacing')=='curvature-density':
  ar=np.linspace(0,s.length,32769);u=s.inverse(ar);v=s.spline(u,1);w=s.spline(u,2);kap=abs(v[:,0]*w[:,1]-v[:,1]*w[:,0])/np.linalg.norm(v,axis=1)**3
  mass=cumulative_simpson(1-p['minor']*kap,x=ar,initial=0);inv=PchipInterpolator(mass,ar);origin=(s.a0+s.direction*p['s0']/s.scale)%s.length;target=float(PchipInterpolator(ar,mass)(origin))+s.direction*s.indices*mass[-1]/s.n
  cyc=np.floor(target/mass[-1]);ind=p['s0']/s.scale+s.direction*(inv(target-cyc*mass[-1])+cyc*s.length-origin);drift=float(abs(ind-s.station(s.indices)).max());M=float(mass[-1]);assert drift<5e-4,drift
 # Exact differential staircase formula; ds/dk comes from the production map's
 # derivative, while frame differentiation is independent of finite differences.
 k=s.indices;kap=curvature(s);v=(s.station(k+.002)-s.station(k-.002))/.004
 circ=np.cross(s.g['radial'],s.g['axis_tangent']);tangent=s.g['axis_tangent']
 trajectory=v[:,None]*(1-p['minor']*kap*np.sin(s.phase))[:,None]*tangent+p['minor']*(p['hand']*2*np.pi*p['winding']/s.n)*circ
 normal=np.cross(s.g['radial'],trajectory);normal/=np.linalg.norm(normal,axis=1)[:,None];normal*=np.where(np.sum(normal*tangent,axis=1)<0,-1,1)[:,None]
 orientation=float(np.linalg.norm(normal-s.g[AXES[0]],axis=1).max());assert orientation<2e-5,orientation
 rng=np.random.default_rng(321);js=rng.choice(s.n,180,replace=False);xy=s.pc[js]+rng.uniform(-s.radius*s.scale,s.radius*s.scale,(180,2))
 fast=s.camera(xy);slow=PythonChain.trace(s,xy,True);known=~slow['unknown']&~fast['unknown'];assert np.array_equal(fast['owner'][known],slow['owner'][known]);ok=known&(fast['owner']>=0)
 point=float(np.linalg.norm(fast['points'][ok]-slow['points'][ok],axis=1).max()) if ok.any() else 0.;assert point<1e-8
 light=make_light(p,s);a=shade(s,fast,light);original=s.blocked;s.blocked=lambda pts,d,max_distance=np.inf:Surface.blocked(s,pts,d,max_distance);b=shade(s,fast,light);s.blocked=original
 intensity=float(abs(a['intensity']-b['intensity']).max());assert intensity<1e-10
 neighbors=neighbor_gaps(s)
 for row in neighbors:
  assert row['endpoint_sdf_max']<1e-8
  assert sum(v['seam'] for v in row['pairs'])==row['offset']
  assert row['lower_min']>0
 save(OUT/f'{label}-neighbor-gaps.json.gz',neighbors);save(OUT/f'{label}-contact-witnesses.json.gz',cert)
 result=dict(label=label,summary=s.summary(),witnesses=len(gaps),minimum_independent_gap=min(gaps),support_max_difference=diff,doubled_density_station_difference_units=drift,independent_density_integral=M,analytic_orientation_max_difference=orientation,python_camera_rays=len(xy),python_unknown=int(slow['unknown'].sum()),camera_point_max_difference=point,shadow_intensity_max_difference=intensity,neighbors=[{k:v for k,v in row.items() if k!='pairs'} for row in neighbors])
 save(OUT/f'{label}-verification.json',result);print('VERIFY',label,len(gaps),drift,orientation,flush=True);return result

if __name__=='__main__':
 data=load()[0]
 for f in OUT.glob('*-model.json.gz'):verify(read(f)['parameters'],data,f.name.removesuffix('-model.json.gz'))
