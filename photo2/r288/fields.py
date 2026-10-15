"""Original M measurement fields with explicit conditional perturbations.

This is the M branch of R287's frozen adapter, factored for repeated construction.
No reviewed coordinates or identities. HSV/paper/palette stay fixed under Y changes.
"""
import numpy as np
from scipy import ndimage as ndi
from photo2.r285.methods import measurements

def field(lum,hsv,paper,palette,bgh,color,*,gain=1.,contrast=1.,sigma=.65,bg_shift=0.,offset=(0,0),jradius=24,mradius=48):
    n=len(lum)//2;cx,cy=np.array([n,n])+offset;raw=np.maximum(0,(lum-float(np.median(lum)))*contrast+float(np.median(lum)))*gain
    mr=min(mradius,n-2) if offset[0] or offset[1] else min(mradius,n);sl=np.s_[cy-mr:cy+mr+1,cx-mr:cx+mr+1];ml,mh,mp=raw[sl],hsv[sl],paper[sl]
    sm,pg,dm,seed,meta=measurements(ml,mh,mp,palette,bgh,color)
    if sigma!=.65 or bg_shift:
        sm=ndi.gaussian_filter(ml,sigma);yy,xx=np.indices(ml.shape);ds=np.hypot(xx-mr,yy-mr);core=pg&(ds<=8);diffuse=float(np.quantile(sm[core],.60)) if core.any() else 0.;samples=sm[(ds>=10)&(ds<=24)];background=float(np.quantile(samples,.10)) if len(samples) else meta['noise_floor'];background=max(0,background+bg_shift*diffuse);lev=max(meta['noise_floor'],background+.20*max(0,diffuse-background));hi=(mh[:,:,1]<.40)&(ml>diffuse)&(ndi.distance_transform_edt(~pg)<=2)&~mp;dm=(pg|hi)&(sm>=lev);pool=pg&(ds<=4)&(sm>=lev);seed=None
        if pool.any():py,px=np.unravel_index(np.argmax(np.where(pool,sm,-1)),ml.shape);seed=[int(px),int(py)]
        meta.update(diffuse_Y=diffuse,background_Y=background,level=lev,refined_seed=seed)
    return dict(lum=ml,hsv=mh,paper=mp,smooth=sm,pigment=pg,domain=dm,seed=seed,meta=meta,origin=np.array([cx-mr,cy-mr]),slice=sl,fullshape=lum.shape)

def expand(mask,f):
    full=np.zeros(f['fullshape'],bool);full[f['slice']]=mask;return full
