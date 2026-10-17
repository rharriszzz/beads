"""Native first hits and exact historical centroids plus unthresholded intensity."""
import numpy as np
from photo2.r307.fast import grid
from photo2.r299.forward import light_params,shade,highlight

def predict(scene,step=1.,observations=None,detail=False,owners=None,threshold=.5):
    if owners is None and observations is not None:
        owners=np.array(sorted({j for row in scene.tree.query_ball_point([r['point'] for r in observations],55.) for j in row}),int)
    if owners is None:owners=np.arange(scene.n)
    xy=grid(scene,step,owners);inv=scene.p.get('light_inverse',0.)
    light=light_params([scene.p['light_az'],scene.p['light_el'],scene.p['roughness']]+([1/inv] if inv else []),'finite' if inv else 'directional',scene.centers.mean(0))
    parts=[];vals=[];unc=[];shadow=0
    for start in range(0,len(xy),20000):
        tr=scene.camera(xy[start:start+20000]);sh=shade(scene,tr,light);parts.append(tr['owner']);vals.append(sh['intensity']);unc.append(tr['unknown']);shadow+=sh['unknown_shadow_pairs']
    owner=np.concatenate(parts);w=np.concatenate(vals);unknown=np.concatenate(unc);order=np.argsort(owner,kind='stable');cuts=np.r_[0,np.flatnonzero(np.diff(owner[order]))+1,len(order)];pred=[];allowed=set(owners);smooth={}
    for a,b in zip(cuts[:-1],cuts[1:]):
        ix=order[a:b];j=int(owner[ix[0]])
        if j<0 or j not in allowed:continue
        mass=float(w[ix].sum());smooth[int(scene.indices[j])]=dict(mass=mass,xy=xy[ix],w=w[ix])
        if threshold==.5:h=highlight(xy[ix],w[ix],step)
        else:
            peak=w[ix].max();mask=w[ix]>=max(peak*threshold,1e-4)
            h=dict(centroid=np.average(xy[ix][mask],weights=w[ix][mask],axis=0).tolist(),peak=xy[ix][w[ix].argmax()].tolist(),peak_intensity=float(peak),area_px2=float(mask.sum()*step**2)) if peak>=1e-4 else None
        if h:pred.append(dict(index=int(scene.indices[j]),point=h['centroid'],peak=h['peak'],strength=h['peak_intensity'],area_px2=h['area_px2']))
    meta=dict(rays=len(xy),unknown_camera=int(unknown.sum()),unknown_shadow=shadow,step=step)
    # Smooth measure is kept internal unless requested; exact centroids unchanged.
    scene._optics=(pred,smooth,meta)
    if detail:meta.update(xy=xy,owner=owner,intensity=w,unknown=unknown)
    return pred,meta
