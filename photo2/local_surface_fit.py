"""Assisted local surface fitting; manually supplied regions are not detections.

Straight, planar-centerline limit of the calibrated 6.5-bead placement. Original
rounded annular surface, orthographic camera on this small patch, latent neighbors.
This is a local approximation, not a global photo camera or necklace model.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
from pathlib import Path
import argparse,json,time
import numpy as np
from scipy.optimize import least_squares, minimize
from scipy.ndimage import distance_transform_edt
from matplotlib.path import Path as MPath
from bead_placement import Rope

ROOT=Path(__file__).resolve().parents[1]
RADIUS=Rope(676).bead_radius
PITCH=.65*2*RADIUS*1.05/6.5
IDS=['B','C','E','F','G','H','J']
INDICES=np.arange(-26,41)


def frame(p):
    # p: tx,ty,scale,roll_deg,elevation_deg,azimuth_deg,phase_deg
    tx,ty,scale,roll,el,az,phase=p
    el,az,roll=np.radians([el,az,roll])
    eye=np.array([np.cos(el)*np.sin(az),np.cos(el)*np.cos(az),np.sin(el)])
    right=np.array([np.cos(az),-np.sin(az),0.])
    down=np.cross(eye,right)
    r=np.cos(roll)*right-np.sin(roll)*down
    d=np.sin(roll)*right+np.cos(roll)*down
    return r,d,eye


def canonical_view(p, elevation=55.):
    """Choose an equivalent local camera/phase gauge; NOT recovered elevation.

    Rotating a straight circular tube about its axis and rotating the camera
    together preserves every surface projection. Fix this unobservable freedom.
    """
    p=np.array(p,float,copy=True)
    r,d,eye=frame(p)
    el=np.radians(elevation)
    if abs(eye[0])>=np.cos(el):
        raise ValueError('View too axial for this chosen gauge')
    az=np.arcsin(eye[0]/np.cos(el))
    new_alpha=np.arctan2(np.sin(el),np.cos(el)*np.cos(az))
    old_alpha=np.arctan2(eye[2],eye[1])
    projected_axis_angle=np.arctan2(d[0],r[0])
    roll=projected_axis_angle-np.arctan2(np.sin(el)*np.sin(az),np.cos(az))
    p[3:6]=[np.degrees(roll),elevation,np.degrees(az)]
    p[6]-=np.degrees(new_alpha-old_alpha)
    return p


def centers(p,indices,hand):
    phase=np.radians(p[6]+hand*360*np.asarray(indices)/6.5)
    return np.column_stack((np.asarray(indices)*PITCH,4*np.sin(phase),4*np.cos(phase)))


def project(p,xyz):
    r,d,_=frame(p)
    return np.column_stack((xyz@r,xyz@d))*p[2]+p[:2]


def outward(p,indices,hand):
    c=centers(p,indices,hand);c[:,1:]*=(4+RADIUS)/4
    return project(p,c)


def trace(p,xy,hand,indices=INDICES,eps=1e-4):
    """Orthographic first hits on the exact rounded-annulus implicit surface.

    Conservative sphere tracing uses the signed distance in the compressed
    axial coordinate (stretch>1). Rays are first culled by a bounding sphere.
    Returns visible model index, depth and convergence accounting.
    """
    r,d,eye=frame(p)
    base=(xy[:,0,None]-p[0])/p[2]*r+(xy[:,1,None]-p[1])/p[2]*d
    c=centers(p,indices,hand)
    delta=base[:,None,:]-c[None,:,:]
    middle=-np.einsum('ijk,k->ij',delta,eye)
    perp2=np.sum(delta*delta,axis=2)-middle*middle
    bound=RADIUS*np.sqrt(1+.7**2)
    a,b=np.where(perp2<bound**2)
    if not len(a):return np.full(len(xy),-999),np.full(len(xy),-np.inf),0
    half=np.sqrt(np.maximum(0,bound**2-perp2[a,b]))
    depth=middle[a,b]+half
    end=middle[a,b]-half
    localbase=delta[a,b]
    alive=np.ones(len(a),bool);hit=np.zeros(len(a),bool)
    major=.57*RADIUS;minor=.43*RADIUS;rounding=.8*minor;extra=.2*minor;stretch=.7/.43
    for _ in range(400):
        active=np.flatnonzero(alive)
        if not len(active):break
        v=localbase[active]+depth[active,None]*eye
        qrad=np.abs(np.hypot(v[:,1],v[:,2])-major)-extra
        qax=np.abs(v[:,0])/stretch-extra
        sdf=np.hypot(np.maximum(qrad,0),np.maximum(qax,0))+np.minimum(np.maximum(qrad,qax),0)-rounding
        reached=sdf<eps
        hit[active[reached]]=True
        alive[active[reached]]=False
        moving=active[~reached]
        depth[moving]-=np.maximum(sdf[~reached],eps)
        alive[moving[depth[moving]<end[moving]]]=False
    best=np.full(len(xy),-np.inf)
    np.maximum.at(best,a[hit],depth[hit])
    out=np.full(len(xy),-999,dtype=int)
    front=hit&(depth>=best[a]-eps/2)
    out[a[front]]=indices[b[front]]
    return out,best,int(alive.sum())


def polygons(cfg,spacing=1):
    x0,y0,x1,y1=cfg['crop']
    yy,xx=np.mgrid[y0:y1:spacing,x0:x1:spacing]
    xy=np.column_stack((xx.ravel(),yy.ravel()))
    masks={k:MPath(v).contains_points(xy).reshape(xx.shape) for k,v in cfg['observations'].items()}
    return xy,xx.shape,masks


def initial_fit(cfg,mapping,hand):
    """Coarse proposal only: polygon centroids loosely approximate outward points.

    Subsequent ray-region fitting uses visible surfaces. Centroids are never
    recorded as physical centers or measured outward anchors.
    """
    train=[k for k in IDS if k!=cfg['held_out']]
    targets=np.array([np.mean(cfg['observations'][k],axis=0) for k in train])
    indices=np.array([mapping[k] for k in train])
    lo=[1310,240,4,-30,20,-55,-360];hi=[1400,330,15,30,89,55,360]
    fits=[]
    for phase in [-150,-60,30,120]:
      for az in [-25,25]:
        p0=np.array([1350,285,9,-5,55,az,phase],float)
        free=np.array([0,1,2,3,5,6])
        def unpack(v):
            p=p0.copy();p[free]=v;return p
        fit=least_squares(lambda v:(outward(unpack(v),indices,hand)-targets).ravel(),p0[free],
                          bounds=(np.array(lo)[free],np.array(hi)[free]),max_nfev=180)
        fits.append((float(np.mean(fit.fun**2)),unpack(fit.x)))
    return sorted(fits,key=lambda v:v[0])


def evaluate(p,hand,mapping,cfg,spacing=2):
    xy,shape,masks=polygons(cfg,spacing)
    label,depth,unfinished=trace(p,xy,hand)
    label=label.reshape(shape)
    result={}
    for k in IDS:
        pred=label==mapping[k];obs=masks[k]
        intersect=(pred&obs).sum();union=(pred|obs).sum()
        result[k]={'iou':float(intersect/union) if union else 0.,'predicted_area':int(pred.sum()),'observed_area':int(obs.sum())}
    return result,label,unfinished


def refine(p,hand,mapping,cfg,maxiter=30,spacing=3,local=False,maxfev=650):
    xy,shape,masks=polygons(cfg,spacing)
    train=[k for k in IDS if k!=cfg['held_out']]
    # Boundary band represents manual uncertainty; fit positive cores and pixels
    # confidently outside each region. Background is not assigned by pigment.
    band=cfg['boundary_uncertainty_px']/spacing
    data={}
    for k in train:
        obs=masks[k]
        inside=distance_transform_edt(obs);outside=distance_transform_edt(~obs)
        data[k]=(obs,inside,outside)
    count=0
    def loss(v):
        nonlocal count
        count+=1
        labels,_,unconverged=trace(v,xy,hand)
        labels=labels.reshape(shape)
        total=0
        for k,(obs,di,do) in data.items():
            pred=labels==mapping[k]
            miss=np.maximum(di-band,0)*(~pred)
            spill=np.maximum(do-band,0)*pred
            # Normalize each body independently so dark/small ones still count.
            total+=(miss.sum()+spill.sum())/max(obs.sum(),1)
        return total/len(train)
    bounds=[(p[0]-15,p[0]+15),(p[1]-15,p[1]+15),(max(4,p[2]-3),min(15,p[2]+3)),
            (-30,30),(20,89),(-55,55),(p[6]-65,p[6]+65)]
    if local:
        widths=np.array([5,5,1,8,8,8,12])
        bounds=[(max(a,x-w),min(b,x+w)) for x,w,(a,b) in zip(p,widths,bounds)]
    free=np.array([0,1,2,3,5,6])
    def unpack(v):
        value=np.array(p,copy=True);value[free]=v;return value
    fit=minimize(lambda v:loss(unpack(v)),np.array(p)[free],method='Powell',
                 bounds=[bounds[i] for i in free],
                 options={'maxiter':maxiter,'maxfev':maxfev,'xtol':.005,'ftol':.0001})
    return unpack(fit.x),float(fit.fun),count,bool(fit.success)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'photo2/local-fit-r126.json')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/r126')
    parser.add_argument('--coarse-only',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    cfg=json.loads(args.config.read_text());results=[]
    for name,mapping in cfg['hypotheses'].items():
      for hand in [-1,1]:
        coarse=initial_fit(cfg,mapping,hand)
        p=coarse[0][1]
        before,_,u=evaluate(p,hand,mapping,cfg)
        start=time.monotonic()
        if args.coarse_only:loss,count,success=None,0,None
        else:
            p,loss,count,success=refine(p,hand,mapping,cfg)
            if loss<.6:
                p,loss,extra,success=refine(p,hand,mapping,cfg,spacing=1,local=True)
                count+=extra
        after,_,u=evaluate(p,hand,mapping,cfg,1)
        result=dict(hypothesis=name,mapping=mapping,hand=hand,parameters=p.tolist(),
            coarse_parameters=coarse[0][1].tolist(),coarse_centroid_mse=coarse[0][0],before=before,
            after=after,region_loss=loss,evaluations=count,optimizer_success=success,
            unfinished_ray_pairs=u,seconds=time.monotonic()-start)
        results.append(result)
        print(json.dumps(result),flush=True)
        (args.output/'fits.json').write_text(json.dumps(results,indent=2)+'\n')
    from check_placement import sha
    provenance=dict(fitter_sha256=sha(Path(__file__)),config_sha256=sha(args.config),
        image_sha256=sha(ROOT/cfg['image']) if cfg.get('image') else None,
        source_scene_sha256=sha(ROOT/'beads.pov'),
        held_out=cfg['held_out'],parameter_order=['tx','ty','scale','roll','elevation_gauge','azimuth','phase'],
        elevation_gauge_deg=55,scale_units='image pixels per scene unit',
        indices=INDICES.tolist(),radius=RADIUS,pitch=PITCH,
        optimizer='8 deterministic centroid proposal starts per chart/hand; Powell region loss at spacing 3 then spacing 1 for loss<0.6; maxfev 650 per stage',
        uncertainty_band_px=cfg['boundary_uncertainty_px'])
    (args.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')

if __name__=='__main__':main()
