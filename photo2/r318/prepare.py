"""Freeze geometry-based assignments before any optical fitting."""
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial.distance import pdist
from skimage.segmentation import watershed
from PIL import Image
from photo2.r297.common import ROOT,read,save,digest,sha,utc
from photo2.r306.evidence import load
from photo2.r315.model import refined_trace
from .detect import OUT,linear
from .optics import Chain,Engine

def main():
    doc=read(OUT/'observations.json.gz');allobs=doc['observations'];obs=[deepcopy(r) for r in allobs if r['selected_photo_candidate']]
    p=read(ROOT/'photo2/r317/results/joint-preserved-model.json.gz')['parameters'];s=Chain(p,load()[0])
    kept=[];excluded=[];groups={}
    for o in obs:
        xy=np.array(o['component']['pixels']);tr=refined_trace(s,xy)
        js,ns=np.unique(tr['owner'][tr['owner']>=0],return_counts=True);order=np.argsort(-ns)
        alternatives=[dict(index=int(s.indices[js[i]]),fraction=float(ns[i]/len(xy))) for i in order]
        if alternatives:idx=alternatives[0]['index'];fraction=alternatives[0]['fraction']
        else:
            d,j=s.tree.query(o['point'],k=4);idx=int(s.indices[j[0]]);fraction=0.
            alternatives=[dict(index=int(s.indices[k]),projected_center_distance_px=float(v),fraction=0.) for k,v in zip(j,d)]
        o.update(index=idx,geometry_alternatives=alternatives,correspondence_confidence='provisional-moderate' if fraction>=.8 else 'provisional-low',
                 correspondence_basis='baseline visible-body overlap of observed bright support; nearest projected center only if no overlap',physical_identity_verified=False)
        groups.setdefault(idx,[]).append(o)
    # More than one lobe on a modeled bead: choose by observed brightness only.
    for idx,items in groups.items():
        items.sort(key=lambda o:(-o['component']['peak_intensity'],o['id']));kept.append(items[0])
        for o in items[1:]:o['exclusion_reasons']=['secondary_observed_lobe_same_provisional_body'];excluded.append(o)
    assert 15<=len(kept)<=25,len(kept)
    kept.sort(key=lambda o:o['index']);mapping={o['id']:o['index'] for o in kept}
    assert len(set(mapping.values()))==len(mapping)
    # Automatic image-only apparent bead basins, not manually traced contours.
    im=np.array(Image.open(ROOT/'beads-photo-2.jpg'));mask=np.load(OUT/'photo-mask.npz')['mask']
    markers=np.zeros(mask.shape,np.int32)
    for i,o in enumerate(allobs):
        x,y=o['detected_peak'];markers[y,x]=i+1
    lum=linear(im)@np.array([.2126,.7152,.0722]);regions=watershed(-ndi.gaussian_filter(lum,1.2),markers,mask=mask)
    ds=[]
    for o in kept:
        i=next(i for i,r in enumerate(allobs) if r['id']==o['id']);ys,xs=np.where(regions==i+1)
        d=2*np.sqrt(len(xs)/np.pi);ds.append(d)
        o['photo_apparent_diameter_px']=float(d);o['photo_basin_area_px']=len(xs)
    dirs=np.linspace(0,np.pi,181);nn=np.cos(dirs)[:,None]*s.right+np.sin(dirs)[:,None]*s.down
    dm=[]
    for o in kept:
        j=int(np.flatnonzero(s.indices==o['index'])[0]);width=2*s.scale*s.support(nn,np.tile(s.g['surface_tangent'][j],(len(nn),1)))
        o['baseline_model_diameter_px']=float(width.max());o['baseline_model_minor_width_px']=float(width.min());dm.append(width.max())
    diameter=dict(photo_method='Equivalent-area diameter of automatic luminance watershed basin within photo-only rope mask; partial/merged basins are uncertain visible supports, not complete contours',
                  photo_median_px=float(np.median(ds)),photo_q25_px=float(np.percentile(ds,25)),photo_q75_px=float(np.percentile(ds,75)),
                  baseline_model_median_px=float(np.median(dm)),baseline_model_min_px=float(min(dm)),
                  fixed_conservative_reference_px=float(min(np.percentile(ds,25),min(dm))))
    epoch=dict(id='stage1-epoch1',utc=utc(),method=doc['localization'],observations=kept,mapping=mapping,
               photo_sha256=doc['photo_sha256'],observation_file_sha256=sha(OUT/'observations.json.gz'),
               parameters=p,excluded_secondary_lobes=excluded,diameter=diameter,
               scope=[min(mapping.values()),max(mapping.values())],
               policy='Provisional one-to-one, geometry-support assignment frozen before optical predictions. No physical identity proof required; no reassignment during fit.')
    epoch['binding']=digest(dict(observations=kept,mapping=mapping,method=epoch['method']))
    save(OUT/'epoch.json',epoch)
    engine=Engine(epoch);result,scene,arrays=engine.evaluate(p,True);save(OUT/'baseline.json.gz',dict(parameters=p,**result));np.savez_compressed(OUT/'baseline-optics.npz',**arrays)
    print('FROZEN',len(kept),'secondary',len(excluded),'scope',epoch['scope'],'D',diameter,'Emax',result['emax_px'],'seconds',result['seconds'],flush=True)
    print([(o['id'],o['index'],o['correspondence_confidence']) for o in kept],flush=True)

if __name__=='__main__':main()
