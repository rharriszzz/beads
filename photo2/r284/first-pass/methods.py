"""Photo-only candidate methods. No review coordinates, model identities or truth.

Pixels and learned appearance are the only segmentation inputs. Crop boundaries
are experimental bounds, not inferred bead boundaries. All masks are native.
"""
from collections import Counter
import copy
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.graph import MCP_Geometric
from skimage.morphology import disk
from photo2.r282.common import support, pixels, circular_distance
from photo2.r282.phase1 import attempts, component, shape_metrics

PARAMETERS = dict(seed_minimum_mean=.022, seed_merge_distance=4, colored_saddle_merge_distance=11,
                  colored_saddle_ratio=.72, search_radius=24, support_radius=18,
                  competition_margin=1.4, minimum_area=12, high_area=30, area_cap=870,
                  secondary_distance=18, secondary_peak_ratio=.70,
                  semantics='high means engineering gates passed; distinct real bodies uncalibrated')


def cut_features(features, origin, size):
    x,y=origin;w,h=size
    return {k:(v[y:y+h,x:x+w].copy() if isinstance(v,np.ndarray) else copy.deepcopy(v)) for k,v in features.items()}


def seed_color(f, xy):
    x,y=map(int,xy);hs=f['hsv'];lum=f['lum'];yy,xx=np.indices(lum.shape)
    core=((xx-x)**2+(yy-y)**2<=16)&(hs[:,:,1]>.35)&(lum>.025)&~f['paper']
    if core.sum()<10:return 'black'
    hue=np.angle(np.mean(np.exp(2j*np.pi*hs[:,:,0][core])))*180/np.pi%360
    d,c=min((float(circular_distance(hue,h)),c) for c,h in f['palette'].items())
    return c if d<35 else 'unknown'


def route(a,b):
    return np.unique(np.rint(np.linspace(a,b,max(2,int(np.linalg.norm(np.array(a)-b)*2)+1))).astype(int),axis=0)


def cues(f, inherited=()):
    """Shared expanded bank. Every suppressed cue has a retained representative.

    Palette-core maxima supplement luminance peaks in dark colored material.
    Nearby colored peaks collapse only with a high same-material saddle. This
    is a photometric feature consolidation, not a physical same-bead assertion.
    """
    lum=f['lum'];h,w=lum.shape;hs=f['hsv'];mean=f['mean5'];raw=[]
    for n in (3,5):
        signal=ndi.uniform_filter(lum,n)
        maxima=(signal==ndi.maximum_filter(signal,7))&(signal>PARAMETERS['seed_minimum_mean'])&~f['paper']
        labs,count=ndi.label(maxima)
        for sl in ndi.find_objects(labs):
            if sl is None:continue
            yy,xx=np.where(maxima[sl]);j=np.argmax(signal[sl][yy,xx]);x=int(xx[j]+sl[1].start);y=int(yy[j]+sl[0].start)
            raw.append(dict(xy=[x,y],source=f'mean{n}-maximum'))
    for color,hue in f['palette'].items():
        other=next(v for k,v in f['palette'].items() if k!=color)
        own=circular_distance(hs[:,:,0]*360,hue)
        material=(own<22)&(circular_distance(hs[:,:,0]*360,other)-own>3)&(hs[:,:,1]>.35)&(lum>.018)&~f['paper']
        depth=ndi.distance_transform_edt(material)
        maximum=(depth==ndi.maximum_filter(depth,11))&(depth>=3)
        labs,n=ndi.label(maximum)
        for k in range(1,n+1):
            yy,xx=np.where(labs==k);j=np.argmax(mean[yy,xx]);raw.append(dict(xy=[int(xx[j]),int(yy[j])],source='pigment-thickness-maximum'))
    for r in inherited:raw.append(dict(xy=list(map(int,np.rint(r['seed']))),source=r['record_id']))
    raw=[r for r in raw if 24<=r['xy'][0]<w-24 and 24<=r['xy'][1]<h-24]
    for r in raw:
        x,y=r['xy'];r['color']=seed_color(f,r['xy']);r['strength']=float(mean[y,x])
    raw.sort(key=lambda r:(-r['strength'],r['xy'][1],r['xy'][0],r['source']))
    selected=[];ledger=[]
    for r in raw:
        chosen=None;reason=None
        for c in selected:
            d=np.linalg.norm(np.array(r['xy'])-c['xy'])
            if d<=4:chosen=c;reason='same local cue within 4px';break
            if r['color']==c['color'] and r['color'] in f['palette'] and d<=11:
                p=route(r['xy'],c['xy']);v=mean[p[:,1],p[:,0]]
                hue=circular_distance(hs[p[:,1],p[:,0],0]*360,f['palette'][r['color']])
                if v.min()>=.72*min(v[0],v[-1]) and np.all(hue<25) and not f['paper'][p[:,1],p[:,0]].any():
                    chosen=c;reason='nearby colored cue without a dark/material separator';break
        if chosen is None:
            chosen=copy.deepcopy(r);chosen['id']=f"Q-{r['xy'][0]:04}-{r['xy'][1]:04}";chosen['sources']=[];selected.append(chosen)
            reason='retained cue'
        chosen['sources'].append(r['source']);ledger.append(dict(**r,representative=chosen['id'],reason=reason))
    return selected,ledger


def prune(mask,seed):
    """Thickness core + one-pixel bounded reconstruction, always a subset."""
    radius=ndi.distance_transform_edt(mask).max()
    opening_radius=int(np.clip(round(radius*.45),2,4))
    core=ndi.binary_opening(mask,structure=disk(opening_radius))
    core=component(core,seed)
    if not core.any():return np.zeros_like(mask)
    # One pixel can recover an inset rim, never a long thin branch.
    return component(ndi.binary_dilation(core)&mask,seed)


def local(f,c):
    x,y=c['xy'];sl=np.s_[y-24:y+25,x-24:x+25]
    hs=f['hsv'][sl];lum=f['lum'][sl];paper=f['paper'][sl]
    yy,xx=np.indices(lum.shape);dist=np.hypot(xx-24,yy-24);peak=float(lum[dist<=4].max())
    return sl,hs,lum,paper,dist,peak


def color_domain(f,c):
    sl,hs,lum,paper,dist,peak=local(f,c)
    own=circular_distance(hs[:,:,0]*360,f['palette'][c['color']])
    other=next(v for k,v in f['palette'].items() if k!=c['color'])
    rival=circular_distance(hs[:,:,0]*360,other)
    pigment=(hs[:,:,1]>.27)&(own<24)&(rival-own>2)&(lum>max(.012,.09*peak))&~paper
    highlight=(hs[:,:,1]<.35)&(lum>max(.06,.45*peak))&(dist<=8)&(ndi.distance_transform_edt(~pigment)<=3)
    return (pigment|highlight)&(dist<=18), (sl,hs,lum,paper,dist,peak)


def radial(domain):
    """All rounded native straight paths stop at first excluded pixel; no reentry."""
    yy,xx=np.indices(domain.shape);dx=xx-24;dy=yy-24
    steps=np.maximum(np.abs(dx),np.abs(dy));alive=domain.copy()
    for j in range(1,25):
        t=np.minimum(j/np.maximum(steps,1),1)
        rx=np.rint(24+dx*t).astype(int);ry=np.rint(24+dy*t).astype(int)
        alive &= domain[ry,rx]
    return component(ndi.binary_opening(alive,structure=disk(2)),[24,24])


def reflection(f,c):
    sl,hs,lum,paper,dist,peak=local(f,c)
    neutral=(hs[:,:,1]<.65)|(hs[:,:,1]*hs[:,:,2]<.12)
    bright=component((lum>=max(.035,.32*peak))&neutral&~paper&(dist<=8),[24,24])
    bright=component(ndi.binary_opening(bright,structure=disk(1)),[24,24])
    dark=(lum<max(.035,.35*peak))&neutral&~paper
    rim=ndi.binary_dilation(bright,iterations=2)&~bright
    enclosure=float(dark[rim].mean()) if rim.any() else 0.
    collar=ndi.binary_dilation(bright)&dark
    mask=component(bright|collar,[24,24])
    return mask,bright,dict(peak=peak,enclosure=enclosure,dark_fraction=float(dark[mask].mean()) if mask.any() else 0.)


def infer(f,seed_bank,method):
    h,w=f['lum'].shape;rows=[];masks=[];costs=[]
    for c in seed_bank:
        alt=attempts(f,c['xy']);a=next(a for a in alt if a['method']=='C')
        x,y=c['xy'];sl=np.s_[y-24:y+25,x-24:x+25];p=pixels(a['region'])-[x-24,y-24]
        base=np.zeros((49,49),bool)
        if len(p):base[p[:,1],p[:,0]]=True
        reflection_mask=None;black={};seed=c['xy'];notes=[]
        if method=='A':mask=prune(base,[24,24]);black=dict(enclosure=a['enclosure'],peak=a['peak_luminance'])
        elif c['color'] in f['palette']:
            domain,data=color_domain(f,c)
            if method=='C':mask=radial(domain)
            else:
                _,hs,lum,paper,dist,peak=data
                gy,gx=np.gradient(lum)
                native_cost=1+4*np.hypot(gx,gy)/max(peak,.05)+.6*(1-np.minimum(lum/max(peak,.05),1))
                native_cost[~domain]=np.inf
                nearest=np.argwhere(domain)
                if len(nearest):
                    start=nearest[np.argmin(np.sum((nearest-[24,24])**2,axis=1))]
                    if np.linalg.norm(start-[24,24])<=4:
                        cost,_=MCP_Geometric(native_cost,fully_connected=False).find_costs([tuple(start)])
                    else:cost=np.full((49,49),np.inf)
                else:cost=np.full((49,49),np.inf)
                mask=np.isfinite(cost)&(cost<=25)
        else:
            if method=='C':mask,reflection_mask,black=reflection(f,c)
            else:mask=base;black=dict(enclosure=a['enclosure'],peak=a['peak_luminance'])
        full=np.zeros((h,w),bool);full[sl]=mask;masks.append(full)
        if method=='B':
            fullcost=np.full((h,w),np.inf)
            if c['color'] in f['palette']:fullcost[sl]=np.where(mask,cost,np.inf)
            else:
                yy,xx=np.indices((49,49));fullcost[sl]=np.where(mask,np.hypot(xx-24,yy-24),np.inf)
            costs.append(fullcost)
        rows.append(dict(record_id=c['id'],seed=list(seed),cue_sources=c['sources'],color=c['color'],
            measured_support=None,measured_photo_location=None,status='unresolved',notes=notes,
            black_evidence=black,secondary_of=None,
            reflection_support=support(np.c_[np.where(reflection_mask)[1],np.where(reflection_mask)[0]]+[x-24,y-24]) if reflection_mask is not None else None))
    if method=='B' and costs:
        costs=np.array(costs);best=np.argmin(costs,axis=0);sorted_cost=np.sort(costs,axis=0)
        with np.errstate(invalid='ignore'):margin=sorted_cost[1]-sorted_cost[0] if len(costs)>1 else np.full((h,w),np.inf)
        for j,r in enumerate(rows):
            owned=masks[j]&(best==j)&(margin>=PARAMETERS['competition_margin'])
            masks[j]=component(ndi.binary_opening(owned,structure=disk(1)),r['seed'])
            r['competition_abstained_pixels']=int((owned!= (masks[j] if masks[j].any() else owned)).sum())
            r['competition_lost_pixels']=int((np.isfinite(costs[j])&~masks[j]).sum())
    for r,mask in zip(rows,masks):
        yy,xx=np.where(mask);r['measured_support']=support(np.c_[xx,yy]);r['measured_photo_location']=[float(xx.mean()),float(yy.mean())] if len(xx) else None
        metrics=shape_metrics(mask);metrics['thin_fraction']=float((mask&~ndi.binary_opening(mask,structure=disk(2))).sum()/max(1,len(xx)))
        r['metrics']=metrics
        reasons=[]
        if not 12<=len(xx)<=870:reasons.append('area-outside-12..870')
        if len(xx)<30:reasons.append('small-support')
        if metrics['solidity']<.80:reasons.append('concave-support')
        if metrics['neck_retention']<.70:reasons.append('thin-or-necked')
        if metrics['components']!=1:reasons.append('disconnected-or-empty')
        if r['color']=='unknown':reasons.append('unknown-material')
        if r['color']=='black':
            if (r['black_evidence'].get('enclosure') or 0)<.65:reasons.append('incomplete-dark-collar')
            if r['black_evidence']['peak']<.12:reasons.append('weak-reflection')
        elif len(xx) and f['lum'][yy,xx].mean()<.025:reasons.append('dim-color-support')
        r['notes']=reasons;r['status']='high' if not reasons else 'rejected' if not 12<=len(xx)<=870 else 'unresolved'
    pairs=[]
    for i,a in enumerate(rows):
        for j in range(i+1,len(rows)):
            b=rows[j];d=float(np.linalg.norm(np.array(a['seed'])-b['seed']))
            if d>48:continue
            shared=int((masks[i]&masks[j]).sum());den=min(masks[i].sum(),masks[j].sum())
            if shared>=5 and shared/max(1,den)>=.12:
                pairs.append(dict(ids=[a['record_id'],b['record_id']],kind='overlapping-support',shared=shared))
                for r in (a,b):
                    if r['status']=='high':r['status']='unresolved'
                    r['notes'].append('shared-support-owner-unresolved')
            if method=='C' and a['color']==b['color']=='black' and d<=18:
                strong,weak=sorted((a,b),key=lambda r:-r['black_evidence']['peak'])
                ratio=weak['black_evidence']['peak']/max(strong['black_evidence']['peak'],1e-8)
                p=route(a['seed'],b['seed']);v=f['lum'][p[:,1],p[:,0]];hs=f['hsv'][p[:,1],p[:,0]]
                neutral=((hs[:,1]<.65)|(hs[:,1]*hs[:,2]<.12)).mean()
                no_paper=not f['paper'][p[:,1],p[:,0]].any()
                if ratio<.70 and neutral>=.8 and no_paper and np.median(v)<.45*strong['black_evidence']['peak']:
                    weak['secondary_of']=strong['record_id'];weak['status']='secondary';weak['notes'].append('weaker-feature-in-shared-neutral-envelope; same body unverified')
                    pairs.append(dict(ids=[strong['record_id'],weak['record_id']],kind='possible-secondary',peak_ratio=ratio,distance=d,neutral_fraction=float(neutral)))
    return rows,pairs
