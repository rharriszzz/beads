"""Actual-glass support-face coincidence at straight reference roots."""
import numpy as np
from photo2.r297.common import ROOT,save
from photo2.r306.evidence import load
from photo2.r320.controls import straight
from photo2.r320.audit import support
from photo2.r295.geometry import AXES
from photo2.r314.geometry import contacts
from .packing import parameters,Chain,straight_reference,straight_gaps
OUT=ROOT/'photo2/r321/results'

def main():
 data=load()[0];rows=[]
 for count in [2401,2402,2600,2800,2801,3200]:
  for axial in [.55,.65,.85,1.05,1.25]:
   p=parameters(count,1.,axial);parent=Chain(p,data);ref=straight_reference(p['turn'],axial);best=ref['best'];R=best['R_over_r'];P=best['P_over_r'];s=straight(parent,P/(1.4*axial),R/(1/np.sin(np.pi/p['turn'])))
   pairs=[]
   for d in [1,6,7]:
    a=20;b=a+d;delta=s.centers[b]-s.centers[a];ta=s.g[AXES[0]][a];tb=s.g[AXES[0]][b]
    # Independent 3D plane optimization, including nonsmooth radial support.
    from scipy.optimize import minimize,lsq_linear
    def f(x):
     n=x/np.linalg.norm(x);return -(delta@n-support(n,ta,1.,axial)-support(n,tb,1.,axial))
    opts=[minimize(f,x,method='Powell',options={'xtol':1e-12,'ftol':1e-13}) for x in [delta,ta,tb,np.cross(ta,tb)]]
    opt=min(opts,key=lambda x:x.fun);n=opt.x/np.linalg.norm(opt.x)
    ha,ga=support(n,ta,1.,axial,True);hb,gb=support(n,tb,1.,axial,True)
    # Radial exposed face is a real axial segment, not the bore: choose
    # subgradients on that segment to minimize explicit endpoint distance.
    vecs=[];signs=[]
    for direction,t,sign in [(n,ta,1),(-n,tb,-1)]:
     if abs(direction@t)<1e-7:vecs.append(sign*t);signs.append(sign)
    pa=ga.copy();pb=-gb.copy()
    if abs(n@ta)<1e-7:pa-=float(pa@ta)*ta
    if abs(n@tb)<1e-7:pb-=float(pb@tb)*tb
    if vecs:
     matrix=np.array(vecs).T;fit=lsq_linear(matrix,delta+pb-pa,bounds=(-.14*axial,.14*axial),tol=1e-13)
     j=0
     if abs(n@ta)<1e-7:pa+=fit.x[j]*ta;j+=1
     if abs(n@tb)<1e-7:pb+=fit.x[j]*tb
    residual=float(np.linalg.norm(delta+pb-pa));sdf=[]
    for q,j in [(pa,a),(pb,b)]:sdf.append(float(s.local_sdf(q@np.stack([s.g[key][j] for key in AXES]).T)))
    pairs.append(dict(offset=d,plane_gap=float(-opt.fun),endpoint_distance=residual,endpoint_sdf=sdf,normal=n.tolist(),actual_contact_within_1e_6=bool(residual<1e-6 and max(abs(np.array(sdf)))<1e-7)))
   # A nearby, strictly separated model verifies all pairs of 41-body toy.
   toy=straight(parent,(P+1e-4)/(1.4*axial),(R+1e-4)/(1/np.sin(np.pi/p['turn'])));c=contacts(toy,seconds=.5);c.pop('witnesses',None)
   rows.append(dict(count=count,axial=axial,reference=ref,pairs=pairs,nearby_finite_scene=c))
 save(OUT/'straight-audit.json',rows);print('STRAIGHT AUDIT',len(rows),sum(all(p['actual_contact_within_1e_6'] for p in r['pairs'][:2]) for r in rows),flush=True)
if __name__=='__main__':main()
