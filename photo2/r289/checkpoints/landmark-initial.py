"""RGB-only native photographic measurements. No masks, models or reference IDs."""
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import local_maxima
from photo2.bead_detection.brightness_r270 import linearize
from photo2.r282.phase1 import image_features
from photo2.bead_debugger.surface import moments
from .common import runs
PARAMETERS=dict(radius=16,patch_fraction=.85,peak_Y=.08,min_contrast=.025,min_relative_contrast=.2,patch_area=[3,100],dark_radius=20,dark_parallel=5,dark_fraction=.25,dark_consecutive=3)

def patch(lum,seed,fraction=.85,radius=16):
    x,y=map(int,seed);h,w=lum.shape
    if min(x,y,w-1-x,h-1-y)<radius:return None
    a=lum[y-radius:y+radius+1,x-radius:x+radius+1];yy,xx=np.indices(a.shape);rad=np.hypot(xx-radius,yy-radius)
    floor=float(np.percentile(a[(rad>=12)&(rad<=radius)],30));peak=float(lum[y,x]);threshold=peak*fraction
    labels,_=ndi.label(a>=threshold,np.ones((3,3)));k=labels[radius,radius]
    if not k:return None  # never borrow a component
    mask=labels==k;py,px=np.where(mask);xy=np.c_[px+x-radius,py+y-radius];weights=np.maximum(a[mask]-floor,1e-10)
    m=moments(xy,weights)
    return dict(point=[x,y],centroid=xy.mean(0).tolist(),weighted=m['centroid'],shape=m,area=len(xy),runs=runs(xy),background=floor,peak=peak,contrast=peak-floor,touches=bool(np.any(mask[[0,-1],:]) or np.any(mask[:,[0,-1]])),contains_brighter=bool(a[mask].max()>peak+1e-12))

def darkness(lum,seed):
    x,y=map(int,seed);radius=20;h,w=lum.shape
    if min(x,y,w-1-x,h-1-y)<radius+2:return dict(offset=[0.,0.],axes=0,profiles=[])
    offset=[];profiles=[];axes=0
    for axis in (0,1):
        ends=[];sides=[]
        for sign in (-1,1):
            vals=np.array([[lum[y+b,x+sign*t] if axis==0 else lum[y+sign*t,x+b] for b in range(-2,3)] for t in range(radius+1)])
            central=float(np.median(vals[0]));low=np.sum(vals<.25*central,axis=1)>=4;edge=None
            for t in range(2,radius-1):
                if np.all(low[t:t+3]):edge=t;break
            ends.append(None if edge is None else sign*edge)
            sides.append(dict(sign=sign,median=np.median(vals,axis=1).tolist(),low_votes=np.sum(vals<.25*central,axis=1).tolist(),edge=edge))
        valid=all(v is not None for v in ends);offset.append(float(sum(ends)/2) if valid else 0.);axes+=int(valid)
        profiles.append(dict(axis=axis,sides=sides,paired=valid))
    return dict(offset=offset,axes=axes,profiles=profiles)

def detect(rgb,with_dark=True):
    # Raw ICC linear Y, no smoothing of maxima or spatial relocation.
    f=image_features(rgb);lum=linearize(rgb/255.)@np.array([.2126,.7152,.0722]);h,w=lum.shape
    maxima=local_maxima(lum,connectivity=2,allow_borders=False)&(lum>=.08)
    labels,n=ndi.label(maxima,np.ones((3,3)));rows=[]
    for k,sl in enumerate(ndi.find_objects(labels),1):
        yy,xx=np.where(labels[sl]==k);yy+=sl[0].start;xx+=sl[1].start
        x,y=int(xx[0]),int(yy[0]);q=patch(lum,[x,y]);reasons=[]
        if q is None:continue
        q['id']=f'H-{x:04}-{y:04}';q['plateau_pixels']=np.c_[xx,yy].tolist()
        if q['peak']-q['background']<.025 or q['contrast']/q['peak']<.2:reasons.append('weak local contrast')
        if not 3<=q['area']<=100:reasons.append('patch area outside 3..100')
        if q['touches']:reasons.append('patch touches computational window')
        if q['contains_brighter']:reasons.append('secondary maximum in brighter connected patch')
        # Paper is excluded only with affirmative local hue evidence. Neutral peaks remain.
        if f['paper'][y-1:y+2,x-1:x+2].mean()>=.8:reasons.append('paper-colored neighborhood')
        hs=f['hsv'][y-5:y+6,x-5:x+6];paper=f['paper'][y-5:y+6,x-5:x+6]
        pigment=(hs[:,:,1]>.35)&~paper&(hs[:,:,2]>.2)
        hues=hs[:,:,0][pigment]*360
        counts={c:int(np.sum(abs((hues-v+180)%360-180)<15)) for c,v in f['palette'].items()}
        col=max(counts,key=counts.get) if max(counts.values(),default=0)>=6 else 'unknown'
        q.update(color=col,color_evidence=counts,peak_saturation=float(f['hsv'][y,x,1]),specularity='unresolved: diffuse or specular',accepted=not reasons,reasons=reasons)
        if not reasons:
            variants=[patch(lum,[x,y],v) for v in (.80,.90)]
            shift=[np.linalg.norm(np.array(v['weighted'])-q['weighted']) for v in variants if v]
            q['threshold_sensitivity_px']=float(max(shift,default=0));q['dark']=darkness(lum,[x,y]) if with_dark else None
        rows.append(q)
    good=[r for r in rows if r['accepted']];tree=cKDTree([r['point'] for r in good]) if good else None
    for r in good:
        r['nearby_alternatives']=[good[j]['id'] for j in tree.query_ball_point(r['point'],12) if good[j]['id']!=r['id']]
    return rows,dict(shape=[h,w],palette=f['palette'],background_hue=f['background_hue'],parameters=PARAMETERS,scope='All-image local maxima; no historic masks/locations or geometry enter inference')
