"""Connected observed/predicted patches and strict fixed-epoch peak minimax.

No geometric correspondence is inferred by optical proximity. An epoch is supplied
explicitly; ambiguity is retained separately. No production R299 code is changed.
"""
import numpy as np
from scipy import ndimage as ndi
from photo2.r297.common import digest

def components(xy,intensity,step=1.,fraction=.5,floor=1e-4):
    xy=np.asarray(xy,float).reshape(-1,2);v=np.asarray(intensity,float)
    if not len(v) or np.max(v)<floor:return []
    lo=xy.min(0);ij=np.rint((xy-lo)/step).astype(int)
    if not np.allclose(xy,lo+ij*step,atol=1e-7):raise ValueError('Nonuniform sample lattice')
    shape=tuple((ij.max(0)+1)[::-1]);mask=np.zeros(shape,bool);ok=v>=max(floor,float(v.max())*fraction);mask[ij[ok,1],ij[ok,0]]=True
    labels,n=ndi.label(mask,np.ones((3,3),bool));out=[]
    for j in range(1,n+1):
        ix=np.flatnonzero(labels[ij[:,1],ij[:,0]]==j);pts=xy[ix];w=v[ix];peak=float(w.max());ties=pts[w==peak];near=pts[w>=.98*peak]
        out.append(dict(component=j,peak=ties[0].tolist(),peak_ties=ties.tolist(),peak_intensity=peak,centroid=pts.mean(0).tolist(),weighted_centroid=np.average(pts,axis=0,weights=w).tolist(),near_maximum=near.tolist(),pixels=pts.tolist(),intensities=w.tolist(),area_px2=float(len(ix)*step**2),threshold_fraction=fraction,step=step))
    return out

def freeze_epoch(observations,assignments,geometry_hash):
    ids=[o['id'] for o in observations]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate observation id')
    scored=[o for o in observations if o.get('reliable_correspondence') and o.get('reliably_localized') and o.get('specular_status')=='supported']
    for o in scored:
        if o['id'] not in assignments:raise ValueError('Missing predeclared assignment')
    matches=[tuple(assignments[o['id']]) for o in scored]
    if len(matches)!=len(set(matches)):raise ValueError('Distinct patches cannot reuse one predicted lobe')
    return dict(observations=observations,assignments=assignments,cohort=[o['id'] for o in scored],ambiguous=[o['id'] for o in observations if o not in scored],geometry_hash=geometry_hash,measurement_hash=digest(observations),assignment_hash=digest(assignments))

def evaluate(epoch,predictions,assignments=None,geometry_passed=False):
    if assignments is not None and digest(assignments)!=epoch['assignment_hash']:raise ValueError('Correspondence change requires a separate epoch')
    if digest(epoch['observations'])!=epoch['measurement_hash']:raise ValueError('Photographic measurement changed')
    lookup={(p['index'],p['lobe']):p for p in predictions};obs={o['id']:o for o in epoch['observations']};rows=[]
    for ident in epoch['cohort']:
        o=obs[ident];p=lookup.get(tuple(epoch['assignments'][ident]));rows.append(dict(id=ident,assignment=epoch['assignments'][ident],peak_error_px=float(np.linalg.norm(np.array(p['peak'])-o['peak'])) if p else None,centroid_error_px=float(np.linalg.norm(np.array(p['centroid'])-o['centroid'])) if p else None,uncertainty=o.get('uncertainty'),missing=p is None))
    missing=sum(r['missing'] for r in rows);metrics={}
    for kind in ['peak','centroid']:
        d=np.array([r[kind+'_error_px'] for r in rows if not r['missing']])
        metrics[kind]=dict(maximum_px=float(d.max()) if len(d) and not missing else None,maximum_is_infinite=bool(missing),rms_px=float(np.sqrt(np.mean(d*d))) if len(d) and not missing else None,p95_px=float(np.percentile(d,95)) if len(d) and not missing else None)
    return dict(rows=rows,metrics=metrics,missing=missing,cohort=len(rows),ambiguous=epoch['ambiguous'],eligible_for_optimization=bool(geometry_passed and rows),principal='peak-to-peak Euclidean maximum',status='eligible' if geometry_passed and rows else 'not established: geometry or reliable correspondences absent')
