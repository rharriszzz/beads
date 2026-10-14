"""Brightness/color determine supports; no physical identity, old mask or review input.

D: diffuse-contrast isophote. S: persistent intensity-saddle separation, merging
weakly separated maxima. G: image-conductance harmonic ownership. No opening,
erosion, compactness objective, circular cut or bead-count quota. Computation
window contact is uncertainty, never a photographic boundary certificate.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import h_maxima
from skimage.segmentation import watershed,random_walker
from photo2.r282.common import circular_distance
from photo2.r284b.methods import contour
PARAMETERS=dict(sigma=.65,diffuse_quantile=.60,contrast_fraction=.20,hue_width=28,
    background_margin=8,minimum_saturation=.24,log_prominence=.20,
    saddle_ratio=.65,minimum_interface=3,walker_beta=90,walker_level=.55,
    domains=[32,48],cap=870,semantics='Experimental photographic features; all ownership uncalibrated')

def component(mask,seed):
    x,y=map(int,seed);labels,n=ndi.label(mask)
    return labels==labels[y,x] if n and labels[y,x] else np.zeros_like(mask)

def measurements(lum,hsv,paper,palette,background_hue,color):
    n=lum.shape[0]//2;yy,xx=np.indices(lum.shape);distance=np.hypot(xx-n,yy-n)
    smooth=ndi.gaussian_filter(lum,.65)
    own=circular_distance(hsv[:,:,0]*360,palette[color]);rival=min((v for k,v in palette.items() if k!=color),default=(palette[color]+180)%360)
    opposite=circular_distance(hsv[:,:,0]*360,rival);background=circular_distance(hsv[:,:,0]*360,background_hue)
    pigment=(hsv[:,:,1]>.24)&(own<28)&(opposite>own)&(background-own>8)&~paper
    core=pigment&(distance<=8)
    noise=float(np.median(np.abs(lum-ndi.median_filter(lum,3))))
    floor=max(.001,3*noise)
    diffuse=float(np.quantile(smooth[core],.60)) if core.any() else 0.
    # Dark local photographic samples estimate baseline; no A-mask ring or peak.
    samples=smooth[(distance>=10)&(distance<=24)]
    bg=float(np.quantile(samples,.10)) if len(samples) else floor
    level=max(floor,bg+.20*max(0,diffuse-bg))
    highlight=(hsv[:,:,1]<.40)&(lum>diffuse)&(ndi.distance_transform_edt(~pigment)<=2)&~paper
    eligible=(pigment|highlight)&(smooth>=level)
    peak_pool=pigment&(distance<=4)&(smooth>=level)
    if peak_pool.any():
        j=np.argmax(np.where(peak_pool,smooth,-1));y,x=np.unravel_index(j,lum.shape);seed=[int(x),int(y)]
    else:seed=None
    meta=dict(diffuse_Y=diffuse,background_Y=bg,noise_floor=floor,level=level,refined_seed=seed,
        seed_pigment_pixels=int(core.sum()),seed_material_eligible=bool(pigment[n,n]),
        seed_missing=seed is None,level_kind='local dark baseline +20% diffuse60 contrast; no specular-peak anchor')
    return smooth,pigment,eligible,seed,meta

def basins(smooth,pigment,domain,seed):
    """Merge adjacent basins unless a sustained dark saddle separates them.

    Saddle is the highest connecting boundary intensity. References use diffuse
    pigment near each maximum, not its specular peak. Multiple maxima alone never
    establish multiple bodies. Separation/merge evidence is retained for review.
    """
    log=np.log(smooth+.003);markers,count=ndi.label(h_maxima(log,.20)&domain)
    x,y=seed
    positions=np.argwhere(markers>0)
    if len(positions):
        q=positions[np.argmin(np.sum((positions-[y,x])**2,axis=1))]
        target=int(markers[tuple(q)]) if np.linalg.norm(q-[y,x])<=5 else 0
    else:target=0
    if not target:count+=1;markers[y,x]=count;target=count
    labels=watershed(-log,markers,mask=domain)
    refs={};peaks={};yy,xx=np.indices(domain.shape)
    for k in range(1,count+1):
        p=np.argwhere(markers==k);v=smooth[p[:,0],p[:,1]];py,px=p[np.argmax(v)];peaks[k]=[int(px),int(py)]
        core=(labels==k)&pigment&((xx-px)**2+(yy-py)**2<=36)
        refs[k]=float(np.quantile(smooth[core],.60)) if core.any() else float(smooth[py,px])
    boundaries={}
    for dy,dx in ((1,0),(0,1)):
        a=labels[:labels.shape[0]-dy or None,:labels.shape[1]-dx or None]
        b=labels[dy:,dx:];iy,ix=np.where((a>0)&(b>0)&(a!=b))
        for py,px in zip(iy,ix):
            ka,kb=sorted((int(a[py,px]),int(b[py,px])));boundaries.setdefault((ka,kb),[]).append((int(px),int(py),int(px+dx),int(py+dy)))
    parent=list(range(count+1))
    def root(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    edges=[]
    for (a,b),points in sorted(boundaries.items()):
        pts=np.array(points);values=np.minimum(smooth[pts[:,1],pts[:,0]],smooth[pts[:,3],pts[:,2]])
        saddle=float(values.max());ref=min(refs[a],refs[b]);ratio=saddle/max(ref,1e-8)
        separated=bool(len(points)>=3 and ratio<.65)
        if not separated:parent[root(b)]=root(a)
        edges.append(dict(markers=[a,b],peaks=[peaks[a],peaks[b]],saddle_Y=saddle,diffuse_references=[refs[a],refs[b]],
            saddle_ratio=ratio,interface_pixels=len(points),separated=separated,boundary_pixels=points))
    group=[k for k in range(1,count+1) if root(k)==root(target)];owned=np.isin(labels,group)
    # Remove dark interface pixels only where the two surviving groups differ.
    # This uses measured intensity; a narrow bright bridge is not eroded.
    seam=np.zeros_like(domain)
    for edge in edges:
        a,b=edge['markers']
        edge['separate_after_merging']=bool(root(a)!=root(b))
        if edge['separate_after_merging']:
            floor=.65*min(refs[a],refs[b])
            for px,py,qx,qy in edge['boundary_pixels']:
                if smooth[py,px]<=floor:seam[py,px]=True
                if smooth[qy,qx]<=floor:seam[qy,qx]=True
    return component(owned&~seam,seed),labels,group,refs,edges,markers

def infer(lum,hsv,paper,palette,background_hue,color):
    smooth,pigment,domain,seed,meta=measurements(lum,hsv,paper,palette,background_hue,color)
    empty=np.zeros_like(domain);results={}
    if seed is None:return {m:(empty.copy(),dict(meta,reason='no-supported-pigment-cue')) for m in ('D','S','G')}
    d=component(domain,seed);s,labels,group,refs,edges,markers=basins(smooth,pigment,domain,seed)
    results['D']=(d,dict(meta));results['S']=(s,dict(meta,saddles=edges,merged_marker_ids=group,
        marker_count=int(markers.max()),interpretation='Intensity features; not body identities'))
    target=np.isin(labels,group);walker_marks=np.zeros_like(labels)
    walker_marks[~domain]=2
    for k,ref in refs.items():
        bright=(labels==k)&(smooth>=ref)
        walker_marks[bright]=1 if k in group else 2
    walker_marks[seed[1],seed[0]]=1
    # A common illumination scaling drops out of normalized log conductance.
    field=np.log(smooth+.003);field=(field-field.min())/max(float(np.ptp(field)),1e-8)
    if (walker_marks==2).any() and (walker_marks==1).any():
        prob=random_walker(field,walker_marks,beta=90,mode='cg_j',return_full_prob=True)[0]
        g=component((prob>=.55)&domain,seed)
        ambiguity=int(((prob>.35)&(prob<.65)&domain).sum())
    else:g=s.copy();ambiguity=0
    results['G']=(g,dict(meta,saddles=edges,merged_marker_ids=group,ambiguous_harmonic_pixels=ambiguity,
        harmonic_field_kind='Dirichlet graph potential, NOT calibrated ownership probability'))
    for m,(mask,info) in results.items():
        edge=np.zeros_like(mask);edge[[0,-1],:]=True;edge[:,[0,-1]]=True
        info.update(window_contact_pixels=int((mask&edge).sum()),area_cap_exceeded=bool(mask.sum()>870),
            native_mask_rule='Photographic intensity/material/ownership; no opening, erosion or shape rank')
    return results
