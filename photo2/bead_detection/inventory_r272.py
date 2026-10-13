"""R272 image-derived conservative inventory; no review coordinates or identities."""
from dataclasses import dataclass,asdict
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from skimage.measure import find_contours
from .brightness_r270 import linearize
from .annular_detect import straight_pixels

CROSS=ndi.generate_binary_structure(2,1)
@dataclass(frozen=True)
class Parameters:
    context_radius:int=20
    hue_tolerance:float=10.
    strict_hue_tolerance:float=8.
    colored_floor_fraction:float=.40
    black_floor_fraction:float=.55
    minimum_luminance:float=.08
    minimum_region_pixels:int=20
    minimum_black_pixels:int=9
    maximum_pixels:int=870
    minimum_patch_pixels:int=5
    maximum_patch_distance:float=4.
    minimum_strict_retention:float=.60
    maximum_centroid_shift:float=1.5

REASONS={
'color-uncertain':'The bright patch and its surroundings do not establish a clear color.',
'color-outside-palette':'The observed color does not confidently match black, yellow or red.',
'brightest-color-uncertain':'The local brightest pixel has incompatible color evidence; a dimmer substitute is not used.',
'brightest-patch-too-small':'The reliable brightest patch is too small.',
'brightest-patch-displaced':'The brightest patch is too far from the stable location.',
'interior-too-small':'Too little connected interior survives the conservative checks.',
'interior-open':'The region reaches the analysis limit before finding a safe stop.',
'interior-too-large':'The proposal exceeds the established 870-pixel safety ceiling.',
'peak-not-interior':'The brightest point does not survive the interior retreat.',
'interior-holes':'The interior contains uncertain holes.',
'interior-unstable':'Small threshold changes alter the region too much.',
'competing-location-inside':'The region contains another substantial location maximum.',
'ownership-overlap':'Two proposed regions overlap; both are withheld.'}

def hue_distance(a,b):return np.abs((np.asarray(a)-b+180)%360-180)
def circular_mean(degrees):return float(np.angle(np.mean(np.exp(1j*np.deg2rad(degrees))))*180/np.pi%360)
def component(mask,xy):
    lab,_=ndi.label(mask,CROSS);x,y=xy
    return (lab==lab[y,x]) if lab[y,x] else np.zeros_like(mask)
def rle(mask,origin=(0,0)):
    out=[];ox,oy=origin
    for y,row in enumerate(mask):
        edges=np.diff(np.r_[False,row,False].astype(np.int8));out.extend([[int(y+oy),int(a+ox),int(b+ox-1)] for a,b in zip(np.where(edges==1)[0],np.where(edges==-1)[0])])
    return out

def features(hsv,lum,paper,x,y):
    a=hsv[y-5:y+6,x-5:x+6];l=lum[y-5:y+6,x-5:x+6];p=paper[y-5:y+6,x-5:x+6]
    core=a[3:8,3:8];good=(a[:,:,1]>=.35)&(a[:,:,2]>=.25)&(l>=.08)&(p==0)
    angles=a[:,:,0][good]*360
    yy,xx=np.mgrid[-5:6,-5:6];disk=(xx*xx+yy*yy<=25)
    good &= disk;angles=a[:,:,0][good]*360
    h=circular_mean(angles) if len(angles) else None
    # Dark-body evidence is outside the bright core, not inferred from neutrality alone.
    b=hsv[y-10:y+11,x-10:x+11];bp=paper[y-10:y+11,x-10:x+11];yy,xx=np.mgrid[-10:11,-10:11];ring=(xx*xx+yy*yy>=49)&(xx*xx+yy*yy<=100)
    dark=(b[:,:,2]<=.35)&(b[:,:,1]<=.30)&(bp==0)
    return dict(color_samples=int(len(angles)),hue=h,hue_deviation90=float(np.percentile(hue_distance(angles,h),90)) if len(angles) else None,
        colored_core_fraction=float(np.mean(core[:,:,1]>=.35)),neutral_core_fraction=float(np.mean(core[:,:,1]<=.25)),dark_neutral_ring_fraction=float(np.mean(dark[ring])))

def learn_palette(feature_rows):
    angles=np.array([f['hue'] for f in feature_rows if f['color_samples']>=25 and f['colored_core_fraction']>=.65 and f['hue_deviation90']<=12])
    if not len(angles):return []
    vectors=np.c_[np.cos(np.deg2rad(angles)),np.sin(np.deg2rad(angles))];first=int(np.argmin(angles));second=int(np.argmax(np.sum((vectors-vectors[first])**2,axis=1)));centers=vectors[[first,second]].copy()
    for _ in range(40):
        labels=np.argmin(((vectors[:,None]-centers)**2).sum(axis=2),axis=1);updated=centers.copy()
        for k in range(2):
            if np.any(labels==k):updated[k]=vectors[labels==k].mean(axis=0);updated[k]/=np.linalg.norm(updated[k])
        if np.allclose(updated,centers,atol=1e-12):break
        centers=updated
    hues=(np.rad2deg(np.arctan2(centers[:,1],centers[:,0]))%360).tolist()
    if hue_distance(hues[0],hues[1])<20:hues=[circular_mean(angles)]
    out=[]
    for h in hues:
        ds={'red':float(hue_distance(h,0)),'yellow':float(hue_distance(h,60))};name=min(ds,key=ds.get);other=max(ds,key=ds.get)
        out.append(dict(hue=h,name=name if ds[name]<=25 and ds[other]-ds[name]>=10 else None,semantic_distances=ds))
    return sorted(out,key=lambda z:z['hue'])

def classify(f,palette):
    if f['neutral_core_fraction']>=.80 and f['dark_neutral_ring_fraction']>=.75:
        return 'black',dict(rule='neutral reflection plus dark neutral surround',**f)
    if f['colored_core_fraction']<.65 or f['color_samples']<25 or f['hue_deviation90'] is None or f['hue_deviation90']>12:
        return None,dict(reason='color-uncertain',**f)
    if not palette:return None,dict(reason='color-outside-palette',**f)
    distances=sorted((float(hue_distance(f['hue'],c['hue'])),i) for i,c in enumerate(palette));d,i=distances[0];margin=distances[1][0]-d if len(distances)>1 else 180.
    color=palette[i]['name'] if d<=12 and margin>=10 else None
    return color,dict(reason=None if color else 'color-outside-palette',prototype_distance=d,prototype_margin=margin,prototype=palette[i],**f)

def measure(mask,origin):
    yy,xx=np.where(mask);ox,oy=origin
    if not len(xx):return dict(pixel_count=0,centroid=None,runs=[])
    return dict(pixel_count=int(len(xx)),centroid=[float(xx.mean()+ox),float(yy.mean()+oy)],bbox=[int(xx.min()+ox),int(yy.min()+oy),int(xx.max()+ox+1),int(yy.max()+oy+1)],runs=rle(mask,origin))

def outline(mask,origin):
    curves=find_contours(np.pad(mask,1).astype(float),.5,fully_connected='low');raw=max(curves,key=len)[:-1,::-1]-1+np.array(origin)
    smooth=raw.copy()
    for _ in range(2):smooth=(np.roll(smooth,1,axis=0)+2*smooth+np.roll(smooth,-1,axis=0))/4
    return dict(raw=np.vstack([raw,raw[0]]).tolist(),smooth=np.vstack([smooth,smooth[0]]).tolist(),maximum_vertex_displacement=float(np.linalg.norm(smooth-raw,axis=1).max()),method='two cyclic 1:2:1 vertex averages; display only, no splines or mask alteration')

def build_region(row,native,srgb,hsv,lum,paper,palette,feature,all_locations,params=Parameters()):
    x,y=row['x'],row['y'];r=params.context_radius;o=(x-r,y-r);cut=np.s_[y-r:y+r+1,x-r:x+r+1];l=lum[cut];hs=hsv[cut];pp=paper[cut];color,cf=classify(feature,palette)
    rec=dict(candidate_id=row['id'],anchor=[x,y],color=color,color_evidence=cf,location_confidence={k:v for k,v in row.items() if k not in ('plateau_pixels','explanations')},reasons=[],accepted=False)
    if color is None:rec['reasons']=[cf['reason']];return rec
    yy,xx=np.mgrid[-r:r+1,-r:r+1];local9=(abs(xx)<=4)&(abs(yy)<=4)
    hue=hsv[y,x,0]*360 if feature['hue'] is None else feature['hue']
    if color=='black':color_ok=hs[:,:,1]<=.30
    else:color_ok=(hue_distance(hs[:,:,0]*360,hue)<=params.hue_tolerance)&(hs[:,:,1]>=.30)
    possible=local9&(pp==0)
    if not np.any(possible):rec['reasons']=['color-uncertain'];return rec
    peak=float(l[possible].max());py,px=min(zip(*np.where(possible&(l==peak))),key=lambda z:((z[1]-r)**2+(z[0]-r)**2,z[0],z[1]));seed=(int(px),int(py));rec['initial_peak']=[int(px+o[0]),int(py+o[1])]
    # The absolute local brightest sample is mandatory. Neutral specular pixels
    # may join a colored patch only in this bright 9x9 core with strong body color.
    neutral_highlight=local9&(hs[:,:,1]<.30)&(l>=.85*peak) if color!='black' else np.zeros_like(local9)
    if not (color_ok[py,px] or neutral_highlight[py,px]):rec['reasons']=['brightest-color-uncertain'];return rec
    rec['local9_peak_luminance']=peak
    frac=params.black_floor_fraction if color=='black' else params.colored_floor_fraction
    def proposal(strict=False):
        co=(hs[:,:,1]<=.25 if strict else hs[:,:,1]<=.30) if color=='black' else ((hue_distance(hs[:,:,0]*360,hue)<=(params.strict_hue_tolerance if strict else params.hue_tolerance))&(hs[:,:,1]>=.30))
        co |= neutral_highlight
        allowed=co&(pp==0)&(l>=max(params.minimum_luminance,peak*(frac+(.05 if strict else 0))))
        pathmask=np.zeros_like(allowed);stops=Counter()
        for ty,tx in zip(*np.where(allowed)):
            running=peak;reason=None
            for ax,ay in straight_pixels(seed,(int(tx),int(ty))):
                if not allowed[ay,ax]:reason='color-background-or-brightness-floor';break
                if l[ay,ax]>running+1e-12:reason='first-native-brightness-rise';break
                running=min(running,float(l[ay,ax]))
            if reason is None:pathmask[ty,tx]=True
            else:stops[reason]+=1
        before=component(pathmask,seed)
        # Exact native retreat is part of measurement; display smoothing is separate.
        mask=component(ndi.binary_erosion(before,CROSS),seed)
        return mask,before,dict(stops)
    mask,before,stops=proposal();strict,_,_=proposal(True)
    region=measure(mask,o);rec.update(region=region,pre_retreat=measure(before,o),stops=stops,parameters=asdict(params))
    if np.any(before[[0,-1],:]) or np.any(before[:,[0,-1]]):rec['reasons'].append('interior-open')
    if before.sum()>params.maximum_pixels:rec['reasons'].append('interior-too-large')
    if not mask[seed[1],seed[0]]:rec['reasons'].append('peak-not-interior')
    if region['pixel_count']<(params.minimum_black_pixels if color=='black' else params.minimum_region_pixels):rec['reasons'].append('interior-too-small')
    holes=ndi.binary_fill_holes(mask)&~mask
    if holes.any():rec['reasons'].append('interior-holes')
    if not region['pixel_count']:return rec
    strict_m=measure(strict,o);retention=float(strict.sum()/mask.sum());shift=float(np.linalg.norm(np.array(strict_m['centroid'])-region['centroid'])) if strict.any() else None
    rec['region_stability']=dict(strict_pixel_count=int(strict.sum()),retained_fraction=retention,centroid_shift=shift)
    if retention<params.minimum_strict_retention or shift is None or shift>params.maximum_centroid_shift:rec['reasons'].append('interior-unstable')
    patch=component(mask&(l>=.85*peak),seed);patch_m=measure(patch,o);rec['bright_patch']=patch_m
    if patch.sum()<params.minimum_patch_pixels:rec['reasons'].append('brightest-patch-too-small')
    if patch.any() and np.linalg.norm(np.array(patch_m['centroid'])-[x,y])>params.maximum_patch_distance:rec['reasons'].append('brightest-patch-displaced')
    rivals=[]
    for other in all_locations:
        if other['id']==row['id'] or other['mean_y']<.8*row['mean_y']:continue
        ax,ay=other['x']-o[0],other['y']-o[1]
        if 0<=ay<mask.shape[0] and 0<=ax<mask.shape[1] and mask[ay,ax] and np.hypot(other['x']-x,other['y']-y)>=4:rivals.append(other['id'])
    rec['interior_rivals']=rivals
    if rivals:rec['reasons'].append('competing-location-inside')
    py,px=min(zip(*np.where(mask&(l==l[mask].max()))),key=lambda z:(z[0],z[1]));gx,gy=int(px+o[0]),int(py+o[1])
    rec['brightest']=dict(x=gx,y=gy,luminance=float(l[py,px]),rgb_srgb=srgb[gy,gx].tolist(),hsv_srgb=dict(h=float(hsv[gy,gx,0]*360),s=float(hsv[gy,gx,1]),v=float(hsv[gy,gx,2])),rgb_native=native[gy,gx].tolist(),hsv_native=dict(zip(('h','s','v'),(rgb_to_hsv(native[gy,gx]/255.)*np.array([360,1,1])).tolist())),ties=int(np.sum(mask&(l==l[mask].max()))),scope='brightest native pixel in accepted interior; deterministic y,x tie break')
    rec['outline']=outline(mask,o);rec['accepted']=not rec['reasons'];return rec

def inventory(native,srgb,locations,paper,params=Parameters()):
    hsv=rgb_to_hsv(srgb/255.);lum=linearize(srgb.astype(float)/255)@np.array([.2126,.7152,.0722]);proposals=[r for r in locations if r['trusted']]
    fs=[features(hsv,lum,paper,r['x'],r['y']) for r in proposals];palette=learn_palette(fs);records=[build_region(row,native,srgb,hsv,lum,paper,palette,f,locations,params) for row,f in zip(proposals,fs)]
    # No ownership assignment or forced partition: reject every overlapping proposal.
    owners={};conflicts=set()
    for i,rec in enumerate(records):
        if not rec['accepted']:continue
        for y,a,b in rec['region']['runs']:
            for x in range(a,b+1):
                if (x,y) in owners:conflicts.add(i);conflicts.add(owners[x,y])
                else:owners[x,y]=i
    for i in conflicts:records[i]['reasons'].append('ownership-overlap');records[i]['accepted']=False
    beads=[]
    for rec in sorted(records,key=lambda z:(z['anchor'][1],z['anchor'][0])):
        rec['explanations']=[REASONS[k] for k in rec['reasons']]
        if rec['accepted']:
            x,y=rec['anchor'];rec['id']=f'B-{x:04d}-{y:04d}';rec['inventory_number']=len(beads)+1;rec['acceptance_reasons']=['Stable well-lit location under the unchanged R271 gates.','Clear image-derived color with supporting local evidence.','Connected interior with strict native descending paths and one-pixel retreat.','Small threshold changes preserve the interior.','No substantial competing location inside or overlap with another accepted proposal.'];beads.append(rec)
    return beads,records,dict(palette=palette,parameters=asdict(params),proposals=len(proposals),accepted=len(beads),colors=dict(Counter(b['color'] for b in beads)),exclusions=dict(Counter(k for r in records for k in r['reasons'])))
