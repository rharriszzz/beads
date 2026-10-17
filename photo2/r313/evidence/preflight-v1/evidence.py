"""Image-only native evidence; no candidate geometry or annotated contours."""
import time
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT, photo, pixels, save, sha, utc
from photo2.r282.common import circular_distance
from photo2.r282.phase1 import image_features
from photo2.r290.detector import fields, shifted
from photo2.r297.geometry import reference

POLICY = dict(arc_halfwidth_px=400, transverse_halfwidth_px=85,
    color_hue_tolerance_deg=18, saturation=.40, luminance=.055,
    background_hue_tolerance_deg=12, background_erosion_px=3,
    transition_uncertainty_px=3, transition_context_px=3,
    comparison_intervals=[[-310,-230],[230,310]], buffer_px=25,
    cohort=list(range(-100,100)), contours_used=False,
    black_material_inferred=False, ownership='Historical supported interior cores; distinct physical identity remains conditional',
    confidence='Conservative uncalibrated engineering thresholds; no calibrated probabilities')

def freeze(out, data):
    began=time.monotonic();native,rgb,meta=photo();f=image_features(rgb)
    ref=reference();signed=((ref.arc-data['arc0'])*data['direction']+ref.length/2)%ref.length-ref.length/2
    pp=ref.points[abs(signed)<=POLICY['arc_halfwidth_px']]
    lo=np.maximum(0,np.floor(pp.min(0)-95).astype(int));hi=np.minimum([rgb.shape[1],rgb.shape[0]],np.ceil(pp.max(0)+96).astype(int))
    x0,y0=lo;x1,y1=hi;cut=np.s_[y0:y1,x0:x1];raw=native[cut];img=rgb[cut]
    yy,xx=np.mgrid[y0:y1,x0:x1];xy=np.c_[xx.ravel(),yy.ravel()]
    # Nearest dense photographic polyline sample, fixed independently of all models.
    dist,ii=cKDTree(ref.points).query(xy);arc=signed[ii].reshape(xx.shape)
    roi=(dist.reshape(xx.shape)<=85)&(abs(arc)<=400)
    split=np.zeros(xx.shape,np.int8)
    for a,b in POLICY['comparison_intervals']:
        split[(arc>=a-25)&(arc<=b+25)]=2
        split[(arc>=a)&(arc<=b)]=1
    hs=f['hsv'][cut];lum=f['lum'][cut];col=np.zeros(xx.shape,np.int8)
    for i,name in enumerate(['red','yellow'],1):
        ok=(circular_distance(hs[:,:,0]*360,f['palette'][name])<18)&(hs[:,:,1]>.40)&(lum>.055)
        col[ok]=i
    # Erosion gives confident paper interiors; dark tinted material is never paper.
    paper=(circular_distance(hs[:,:,0]*360,f['background_hue'])<12)&(hs[:,:,1]>.30)&(lum>.08)
    paper=ndi.binary_erosion(paper,iterations=3)&roi
    material=ndi.binary_erosion(col>0,iterations=1)&roi&~paper
    col[~material]=0
    core=np.zeros(xx.shape,np.int16);regions=[];excluded=[]
    for r in data['rows']:
        if r['kind']!='region' or r['reflection'] or r['color'] not in ['red','yellow']:continue
        pts=pixels(r['pixels'])-lo
        inside=(pts[:,0]>=0)&(pts[:,0]<xx.shape[1])&(pts[:,1]>=0)&(pts[:,1]<xx.shape[0]);pts=pts[inside]
        if not len(pts):continue
        mask=np.zeros(xx.shape,bool);mask[pts[:,1],pts[:,0]]=True
        mask=ndi.binary_erosion(mask,iterations=1)&material
        if mask.sum()<12:
            excluded.append(dict(id=r['id'],point=r['point'],reason='Fewer than 12 independently chromatic eroded pixels; remains unresolved'));continue
        # Never merge fragments or fill holes. Overlap excluded, not reassigned.
        mask&=core==0
        if mask.sum()<12:continue
        k=len(regions)+1;core[mask]=k
        # A core touching split buffer is retained only in diagnostics.
        ss=np.unique(split[mask]);part=int(ss[0]) if len(ss)==1 else 2
        regions.append(dict(id=r['id'],point=r['point'],label=k,pixels=int(mask.sum()),split=part,color=r['color'],historical_pixels=r['pixels']['pixel_count']))
    _,ff=fields(img);edge=[];seam=[];uncertain=[];strength=[]
    for axis,q in enumerate(ff):
        dy,dx=(0,1) if axis==0 else (1,0)
        ca=shifted(col,-3*dy,-3*dx);cb=shifted(col,3*dy,3*dx)
        material_side=(ca>0)|(cb>0)
        # Stronger than R290 local support; no level-set boundary is used.
        dark=(q['drop']>=.35*1.15)&(q['coherence']>=.8)&(q['dark_context']>0)&(np.maximum(q['side_a'],q['side_b'])-q['center']>=.012*1.15)
        chrom=(q['color']>=.25*1.15)&(q['color_coherence']>=.8)&(ca>0)&(cb>0)&(ca!=cb)
        valley=dark&(q['recovery']>=.10*1.15)&(ca>0)&(cb>0)
        background_side=shifted(paper,-4*dy,-4*dx)|shifted(paper,4*dy,4*dx)
        # One-sided darkness can support a colored rim but cannot label a black body.
        supported=material_side&(dark|chrom)&roi
        weak=material_side&((q['drop']>=.35*.85)|(q['color']>=.25*.85))&roi&~supported
        # Persistence across adjacent normal samples; isolated responses are uncertain.
        supported&=ndi.maximum_filter(supported,size=3)&ndi.binary_erosion(roi,iterations=5)
        # Ridge localization avoids counting a broad transition band as many contours.
        z=np.maximum(q['drop']*q['coherence'],q['color']*q['color_coherence'])
        ridge=z>=ndi.maximum_filter1d(z,size=3,axis=1 if axis==0 else 0)-1e-12
        supported&=ridge
        edge.append(supported);seam.append((valley|chrom)&supported);uncertain.append(weak);strength.append(np.clip(z,0,1))
    arrays=dict(xy=xy,origin=lo,shape=np.array(xx.shape),roi=roi,split=split,arc=arc,
        material=material,color=col,paper=paper,core=core,edges=np.array(edge),
        seams=np.array(seam),uncertain_edges=np.array(uncertain),strength=np.array(strength),native=raw)
    out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'maps.npz',**arrays)
    doc=dict(utc=utc(),policy=POLICY,photo=meta,box=[int(x0),int(y0),int(x1),int(y1)],
        palette=f['palette'],background_hue=f['background_hue'],regions=regions,unresolved_regions=excluded,
        counts=dict(material=int(material.sum()),paper=int(paper.sum()),supported_transition_samples=int(np.sum(edge)),supported_seam_samples=int(np.sum(seam)),uncertain_transition_samples=int(np.sum(uncertain)),cores=len(regions),rays=len(xy)),
        sources={p:sha(ROOT/p) for p in ['beads-photo-2.jpg','photo2/r296/evidence/inputs.json.gz','photo2/r282/results/centerline.json','photo2/r290/detector.py','photo2/r313/evidence.py']},
        maps_sha256=sha(out/'maps.npz'),seconds=time.monotonic()-began,
        historical_exposure='Entire photo and all historical supports have been seen in prior work. Comparison regions excluded from R313 fitting, not statistically fresh holdout.',
        dimension_policy='Historical D=36.878 +/-6 px is a remote uncertain reference only; 16 contours retired. Image-traced centerline and conservative 85px transverse region bound selection, never assert a measured rope silhouette.')
    save(out/'freeze.json',doc);return arrays,doc
