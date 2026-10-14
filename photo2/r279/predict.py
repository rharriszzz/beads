"""AB-only geometry search. Functions accept only the fitted observations.

No filesystem reads, ground truth, or hidden observations inside predict_pair.
"""
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from .geometry import R,PITCH,centers,project,frame,visible,trace,contact

PHASES=np.linspace(-np.pi,np.pi,12,endpoint=False)
INCLINATIONS=(-40.,-20.,0.,20.,40.)

def align(p,a,b,delta):
    xyz=centers([0,delta],p['hand'],p['phase'],p['pitch']);base=project({**p,'roll':0.,'scale':1.,'translation':[0,0]},xyz)
    u=base[1]-base[0];v=np.array(b['centroid'])-a['centroid'];scale=np.linalg.norm(v)/max(np.linalg.norm(u),1e-6)
    roll=np.degrees(np.arctan2(v[1],v[0])-np.arctan2(u[1],u[0]));p={**p,'roll':float(roll),'scale':float(scale),'translation':[0.,0.]}
    p['translation']=(np.array(a['centroid'])-project(p,xyz)[0]).tolist();return p

def predict_pair(a,b,tangent=None):
    """Freeze nominal geometric predictions; collision failures are never promoted."""
    results=[];evaluations=0
    extent=np.sqrt((a['area']+b['area'])/(2*np.pi))/R
    for hand in (-1,1):
        for delta in (-7,-6,-1,1,6,7):
            trials=[]
            for inc in INCLINATIONS:
                for phase in PHASES:
                    p=align(dict(hand=hand,phase=float(phase),inclination=inc,pitch=1.),a,b,delta);evaluations+=1
                    if not .5*extent<=p['scale']<=4*extent:continue
                    # Positive interior pixels only, with occlusion from the whole local patch.
                    pix=np.array(a['pixels'])[::max(1,len(a['pixels'])//12)]
                    pixb=np.array(b['pixels'])[::max(1,len(b['pixels'])//12)]
                    owner,_,unk=trace(p,np.r_[pix,pixb]);ownership=(np.mean(owner[:len(pix)]==0)+np.mean(owner[len(pix):]==delta))/2
                    axis=project(p,np.array([[0.,0,0],[1.,0,0]]));ang=np.arctan2(*(axis[1]-axis[0])[::-1]);axis_cost=0 if tangent is None else .08*(1-np.cos(2*(ang-tangent)))
                    loss=1-ownership+axis_cost+.025*abs(np.log(p['scale']/max(extent,1e-6)))
                    trials.append((float(loss),p,float(ownership),int(unk.sum())))
            trials.sort(key=lambda z:z[0])
            for rank,(loss,p,own,unknown) in enumerate(trials[:2]):
                sign=1 if delta>0 else -1;k=sign*(1 if abs(delta)==7 else 7)
                xy,u=visible(p,k);cen=xy.mean(0).tolist() if len(xy) else None
                results.append(dict(hand=hand,delta=delta,target=k,rank=rank,parameters=p,AB_loss=loss,AB_positive_ownership=own,unknown_rays=unknown+u,C_visible_pixels=xy.tolist(),C_centroid=cen,C_projected_center=project(p,centers([k],hand,p['phase']))[0].tolist(),uncertainty_px=float(a['uncertainty']+b['uncertainty']),triangle=[0,delta,k],physical_valid=False,physical_reason='source-pitch sampled interpenetration',fit_uses=[a['id'],b['id']]))
    return dict(A=a['id'],B=b['id'],frozen_before_C=True,evaluations_per_hand=evaluations//2,hypotheses=results,non_neighbor_alternative=dict(status='retained',reason='AB can be unrelated in construction; image proximity does not identify index difference'),pitch_sensitivity={str(x):contact(x) for x in (.95,1.,1.05,1.10)})

def score_prediction(h,obs,excluded,state,key='C'):
    xy=np.array(h.get(key+'_visible_pixels',[])).reshape(-1,2);cen=h.get(key+'_centroid');candidates=[]
    if not len(xy) or cen is None:return dict(status='occluded or unsupported',candidates=[],match=None)
    tree=cKDTree(xy)
    for o in obs:
        if o['id'] in excluded:continue
        dist=float(np.linalg.norm(np.array(o['centroid'])-cen));support=float(np.mean(tree.query(o['pixels'])[0]<=2.5))
        if dist<=R*h['parameters']['scale']*3:
            candidates.append(dict(id=o['id'],distance_px=dist,positive_overlap=support,score=dist/max(o['uncertainty'],2)+3*(1-support)))
    candidates.sort(key=lambda o:o['score']);ij=np.rint(xy).astype(int);H,W=state['known_background'].shape;ok=(ij[:,0]>=0)&(ij[:,0]<W)&(ij[:,1]>=0)&(ij[:,1]<H);ij=ij[ok]
    bg=float(state['known_background'][ij[:,1],ij[:,0]].mean()) if len(ij) else None
    best=candidates[0] if candidates else None
    accepted=bool(best and best['positive_overlap']>=.5 and best['distance_px']<=h['uncertainty_px'])
    return dict(status='conditional match' if accepted else 'unmatched/ambiguous',match=best['id'] if accepted else None,candidates=candidates[:4],known_background_fraction=bg,uncertain_fraction=None if bg is None else 1-bg,physical_valid=h['physical_valid'])

def refit_ABC(h,a,b,c):
    """Diagnostic shared transform+phase only; C now fitted, D stays withheld."""
    p=h['parameters'];ks=[0,h['delta'],h['target']];target=np.array([o['centroid'] for o in (a,b,c)])
    start=np.array([*p['translation'],p['roll'],np.log(p['scale']),p['phase']])
    def unpack(x):return {**p,'translation':x[:2].tolist(),'roll':float(x[2]),'scale':float(np.exp(x[3])),'phase':float(x[4])}
    def residual(x):return (project(unpack(x),centers(ks,p['hand'],x[4],p['pitch']))-target).ravel()
    lo=start-np.array([10,10,15,.15,.3]);hi=start+np.array([10,10,15,.15,.3]);fit=least_squares(residual,start,bounds=(lo,hi),max_nfev=30)
    p2=unpack(fit.x);sign=1 if h['delta']>0 else -1;k=sign*8
    xy,u=visible(p2,k);singular=np.linalg.svd(fit.jac,compute_uv=False)
    return dict(parameters=p2,D_target=k,D_visible_pixels=xy.tolist(),D_centroid=xy.mean(0).tolist() if len(xy) else None,uncertainty_px=h['uncertainty_px'],physical_valid=False,frozen_before_D=True,fit_uses=[a['id'],b['id'],c['id']],ABC_RMS_px=float(np.sqrt(np.mean(fit.fun**2))),jacobian_singular_values=singular.tolist(),unknown_rays=u,bounds_hit=bool(np.any(abs(fit.x-lo)<1e-4)|np.any(abs(fit.x-hi)<1e-4)))
