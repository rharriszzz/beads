"""Replay-compatible J/M/B adapters and explicit conditional perturbations.

No decisions, color preference, review coordinates or physical inputs. Original
initial photographic support is used only for J's inherited background ring.
"""
import numpy as np
from scipy import ndimage as ndi
from photo2.r282.common import circular_distance
from photo2.r284b.methods import nearest_peak,connected
from photo2.r285.methods import measurements
from photo2.r286.methods import watershed_support

PERTURBATIONS=[dict(name='gain0.9',gain=.9),dict(name='gain1.1',gain=1.1),
 dict(name='contrast0.9',contrast=.9),dict(name='contrast1.1',contrast=1.1),
 dict(name='sigma0.5',sigma=.5),dict(name='sigma0.8',sigma=.8),
 dict(name='background-low',bg_shift=-.02),dict(name='background-high',bg_shift=.02),
 dict(name='seed-left',offset=[-2,0]),dict(name='seed-right',offset=[2,0]),
 dict(name='seed-up',offset=[0,-2]),dict(name='seed-down',offset=[0,2]),
 dict(name='domain-small',jradius=20,mradius=32),dict(name='domain-large',jradius=32,mradius=48)]

def produce(lum,hsv,paper,palette,bgh,color,initial,*,gain=1.,contrast=1.,sigma=.65,bg_shift=0.,offset=(0,0),jradius=24,mradius=48):
    n=lum.shape[0]//2;cx,cy=np.array([n,n])+offset;yy,xx=np.indices(lum.shape);dist=np.hypot(xx-cx,yy-cy);raw=np.maximum(0,(lum-float(np.median(lum)))*contrast+float(np.median(lum)))*gain
    # Use original49-pixel convolution window at the J baseline, larger for domain test.
    r=max(24,jradius);sl=np.s_[cy-r:cy+r+1,cx-r:cx+r+1];ls=raw[sl];hs=hsv[sl];ps=paper[sl];ini=initial[sl];y,x=np.indices(ls.shape);dd=np.hypot(x-r,y-r)
    peak=float(ls[dd<=4].max());own=circular_distance(hs[:,:,0]*360,palette[color]);other=next(v for k,v in palette.items() if k!=color);rival=circular_distance(hs[:,:,0]*360,other)
    pigment=(hs[:,:,1]>.27)&(own<24)&(rival-own>2)&(ls>max(.012,.09*peak))&~ps
    highlight=(hs[:,:,1]<.35)&(ls>max(.06,.45*peak))&(dd<=8)&(ndi.distance_transform_edt(~pigment)<=3)
    domain=(pigment&(dd<=jradius))|(highlight&(dd<=18));sm=ndi.gaussian_filter(ls,sigma);pk=nearest_peak(sm,[r,r]);p=float(sm[pk[1],pk[0]]);ring=ndi.binary_dilation(ini,iterations=3)&~ini;bg=float(np.quantile(sm[ring],.20)) if ring.any() else 0.;bg=max(0,bg+bg_shift*p);level=max(.012,bg+.18*max(0,p-bg));jm=connected(domain&(sm>=level),pk);j=np.zeros_like(paper);j[sl]=jm
    infoj=dict(level=level,background_Y=bg,peak_Y=p,peak=[int(pk[0]+cx-r),int(pk[1]+cy-r)],radius_contact=int((jm&(dd>=jradius-.5)).sum()),seed_connected=bool(j[cy,cx]),component_substitution=not bool((domain&(sm>=level))[pk[1],pk[0]]))
    # Symmetric center crop keeps M's original local cue/refinement semantics.
    mr=min(mradius,n-2) if offset[0] or offset[1] else min(mradius,n);slm=np.s_[cy-mr:cy+mr+1,cx-mr:cx+mr+1];ml=raw[slm];mh=hsv[slm];mp=paper[slm]
    smooth,pg,dm,seed,meta=measurements(ml,mh,mp,palette,bgh,color)
    if sigma!=.65 or bg_shift:
        smooth=ndi.gaussian_filter(ml,sigma);ym,xm=np.indices(ml.shape);ds=np.hypot(xm-mr,ym-mr);core=pg&(ds<=8);diffuse=float(np.quantile(smooth[core],.60)) if core.any() else 0.;samples=smooth[(ds>=10)&(ds<=24)];background=float(np.quantile(samples,.10)) if len(samples) else meta['noise_floor'];background=max(0,background+bg_shift*diffuse);lev=max(meta['noise_floor'],background+.20*max(0,diffuse-background));hi=(mh[:,:,1]<.40)&(ml>diffuse)&(ndi.distance_transform_edt(~pg)<=2)&~mp;dm=(pg|hi)&(smooth>=lev);pool=pg&(ds<=4)&(smooth>=lev)
        seed=None
        if pool.any():py,px=np.unravel_index(np.argmax(np.where(pool,smooth,-1)),ml.shape);seed=[int(px),int(py)]
        meta.update(diffuse_Y=diffuse,background_Y=background,level=lev,refined_seed=seed)
    out={'J':(j,infoj)}
    for method in ('M','B'):
        mask,detail,barrier=watershed_support(smooth,pg,dm,mp,seed,method=='B') if seed is not None else (np.zeros_like(dm),{},np.zeros_like(dm));full=np.zeros_like(paper);full[slm]=mask;meta2=dict(meta,**detail,window_contact=int(mask[0].sum()+mask[-1].sum()+mask[:,0].sum()+mask[:,-1].sum()),local_origin=[int(cx-mr),int(cy-mr)])
        out[method]=(full,meta2)
    return out
