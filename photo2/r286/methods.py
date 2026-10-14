"""R286 photographic separation: no review coordinates, identities or old masks.

M repairs marker loss only. A uses persistent dark-ridge visibility barriers.
B retains dark watershed interfaces as immutable cannot-link evidence. C stops
native direct paths at a deep valley followed by renewed brightness. Multiple
features remain uncertain photographic observations, never certified bodies.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import h_maxima
from skimage.segmentation import watershed
from photo2.r285.methods import measurements,component
PARAMETERS=dict(marker_context_radius=3,marker_context_fraction=.5,log_prominence=.20,
    ridge_offsets=[4,7],ridge_ratio=.70,ridge_component=5,interface_ratio=.65,
    interface_dark_fraction=.60,interface_min_pairs=3,marker_separation=6,
    valley_ratio=.65,valley_rise_fraction=.18,valley_run=2,domains=[32,48],cap=870,
    inherited_measurements='Unchanged R285 diffuse/material floor; no shape optimization')

def marker_field(smooth,pigment,domain,paper,seed):
    raw,n=ndi.label(h_maxima(np.log(smooth+.003),PARAMETERS['log_prominence']));markers=np.zeros_like(raw);ledger=[];yy,xx=np.indices(domain.shape)
    for k in range(1,n+1):
        py,px=np.where(raw==k);j=np.argmax(smooth[py,px]);x,y=int(px[j]),int(py[j]);near=(xx-x)**2+(yy-y)**2<=PARAMETERS['marker_context_radius']**2
        fraction=float(pigment[near].mean());eligible=near&domain;reason='native eligible maximum';placed=None
        if domain[y,x]:placed=[x,y]
        elif not paper[y,x] and fraction>=PARAMETERS['marker_context_fraction'] and eligible.any():
            ry,rx=np.where(eligible);distance=(rx-x)**2+(ry-y)**2;j=np.lexsort((-smooth[ry,rx],distance))[0];placed=[int(rx[j]),int(ry[j])];reason='context-supported maximum projected to eligible pigment'
        else:reason='unsupported maximum; retained in ledger only'
        if placed:
            x2,y2=placed
            if markers[y2,x2]:reason='same supported marker location';label=int(markers[y2,x2])
            else:label=int(markers.max())+1;markers[y2,x2]=label
        else:label=None
        ledger.append(dict(raw_peak=[x,y],placed=placed,label=label,pigment_fraction=fraction,reason=reason))
    x,y=seed;pos=np.argwhere(markers>0)
    target=0
    if len(pos):
        q=pos[np.argmin(np.sum((pos-[y,x])**2,axis=1))]
        if np.linalg.norm(q-[y,x])<=5:target=int(markers[tuple(q)])
    if not target:target=int(markers.max())+1;markers[y,x]=target;ledger.append(dict(raw_peak=seed,placed=seed,label=target,reason='supported input cue'))
    return markers,target,ledger

def watershed_support(smooth,pigment,domain,paper,seed,protected):
    markers,target,ledger=marker_field(smooth,pigment,domain,paper,seed);labels=watershed(-np.log(smooth+.003),markers,mask=domain);refs={};peaks={};yy,xx=np.indices(domain.shape)
    for k in range(1,int(markers.max())+1):
        py,px=np.argwhere(markers==k)[0];peaks[k]=[int(px),int(py)];core=(labels==k)&pigment&((xx-px)**2+(yy-py)**2<=36);refs[k]=float(np.quantile(smooth[core],.60)) if core.any() else float(smooth[py,px])
    interfaces={}
    for dy,dx in ((1,0),(0,1)):
        a=labels[:labels.shape[0]-dy,:labels.shape[1]-dx];b=labels[dy:,dx:];py,px=np.where((a>0)&(b>0)&(a!=b))
        for y,x in zip(py,px):
            pair=tuple(sorted((int(a[y,x]),int(b[y,x]))));interfaces.setdefault(pair,[]).append([int(x),int(y),int(x+dx),int(y+dy)])
    edges=[];forbidden=set();parent=list(range(int(markers.max())+1))
    def root(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    for (a,b),points in sorted(interfaces.items()):
        q=np.array(points);values=np.minimum(smooth[q[:,1],q[:,0]],smooth[q[:,3],q[:,2]]);reference=min(refs[a],refs[b]);ratios=values/max(reference,1e-9);fraction=float((ratios<PARAMETERS['interface_ratio']).mean());separation=float(np.linalg.norm(np.array(peaks[a])-peaks[b]))
        strong=bool(len(points)>=PARAMETERS['interface_min_pairs'] and (fraction>=PARAMETERS['interface_dark_fraction'] and separation>=PARAMETERS['marker_separation'] if protected else ratios.max()<PARAMETERS['interface_ratio']))
        if strong:forbidden.add((a,b))
        edges.append(dict(markers=[a,b],peaks=[peaks[a],peaks[b]],references=[refs[a],refs[b]],maximum_ratio=float(ratios.max()),median_ratio=float(np.median(ratios)),dark_fraction=fraction,protected=strong,interface=points))
    for e in sorted(edges,key=lambda e:-e['median_ratio']):
        a,b=e['markers'];ra,rb=root(a),root(b)
        if ra==rb:continue
        blocked=e['protected'] or (protected and any({root(x),root(y)}=={ra,rb} for x,y in forbidden))
        e['merge_blocked_by_separation']=bool(blocked)
        if not blocked:parent[rb]=ra
    group=[k for k in refs if root(k)==root(target)];owned=np.isin(labels,group);barrier=np.zeros_like(domain)
    for e in edges:
        a,b=e['markers'];e['separate_after_merging']=bool(root(a)!=root(b))
        if not e['separate_after_merging']:continue
        limit=PARAMETERS['interface_ratio']*min(refs[a],refs[b])
        for x,y,qx,qy in e['interface']:
            if smooth[y,x]<=limit:barrier[y,x]=True
            if smooth[qy,qx]<=limit:barrier[qy,qx]=True
    mask=component(owned&~barrier,seed)
    return mask,dict(marker_ledger=ledger,target_marker=target,group=group,interfaces=edges,
        separation_kind='protected median/fraction interface' if protected else 'original maximum saddle with completed markers'),barrier

def ridge_barriers(smooth,pigment):
    yy,xx=np.indices(smooth.shape);barrier=np.zeros_like(pigment)
    for angle in np.arange(8)*np.pi/8:
        dx,dy=np.cos(angle),np.sin(angle);persistent=np.ones_like(pigment)
        for radius in PARAMETERS['ridge_offsets']:
            coords1=np.array([yy+radius*dy,xx+radius*dx]);coords2=np.array([yy-radius*dy,xx-radius*dx]);a=ndi.map_coordinates(smooth,coords1,order=1,mode='nearest');b=ndi.map_coordinates(smooth,coords2,order=1,mode='nearest');pa=ndi.map_coordinates(pigment.astype(float),coords1,order=1,mode='nearest');pb=ndi.map_coordinates(pigment.astype(float),coords2,order=1,mode='nearest')
            persistent &= (smooth<PARAMETERS['ridge_ratio']*np.minimum(a,b))&(pa>.5)&(pb>.5)
        a=ndi.map_coordinates(smooth,[yy+dy,xx+dx],order=1,mode='nearest');b=ndi.map_coordinates(smooth,[yy-dy,xx-dx],order=1,mode='nearest');barrier |= persistent&(smooth<=a)&(smooth<=b)
    labels,n=ndi.label(barrier,structure=np.ones((3,3)));counts=np.bincount(labels.ravel());keep=counts>=PARAMETERS['ridge_component'];keep[0]=False
    return keep[labels]

def path_support(smooth,domain,seed,diffuse,barrier=None):
    yy,xx=np.where(domain);end=np.c_[xx,yy];start=np.array(seed);delta=end-start
    if not len(end):return domain.copy(),0
    length=np.linalg.norm(delta,axis=1);steps=max(2,int(np.max(np.abs(delta)))*2+1);t=np.linspace(0,1,steps)[:,None];xs=np.rint(start[0]+t*delta[:,0]).astype(int);ys=np.rint(start[1]+t*delta[:,1]).astype(int)
    if barrier is not None:blocked=np.any(barrier[ys,xs]&(t*length>3),axis=0)
    else:
        values=smooth[ys,xs];minimum=np.minimum.accumulate(values,axis=0);indices=np.arange(steps)[:,None];newminimum=values<=minimum;lowindex=np.maximum.accumulate(np.where(newminimum,indices,0),axis=0);run=(indices-lowindex)/max(1,steps-1)*length
        blocked=np.any((minimum<PARAMETERS['valley_ratio']*diffuse)&(values-minimum>PARAMETERS['valley_rise_fraction']*diffuse)&(run>=PARAMETERS['valley_run'])&(t*length>3),axis=0)
    mask=np.zeros_like(domain);mask[yy[~blocked],xx[~blocked]]=True
    return component(mask,seed),int(blocked.sum())

def infer(lum,hsv,paper,palette,background_hue,color):
    smooth,pigment,domain,seed,meta=measurements(lum,hsv,paper,palette,background_hue,color)
    if seed is None:return {m:(np.zeros_like(domain),dict(meta,reason='no-supported-pigment-cue'),np.zeros_like(domain)) for m in ('M','A','B','C')}
    out={}
    for method,protected in [('M',False),('B',True)]:
        mask,info,barrier=watershed_support(smooth,pigment,domain,paper,seed,protected);out[method]=(mask,dict(meta,**info),barrier)
    ridge=ridge_barriers(smooth,pigment);a,blocked=path_support(smooth,domain,seed,meta['diffuse_Y'],ridge);out['A']=(a,dict(meta,ridge_pixels=int(ridge.sum()),blocked_direct_routes=blocked),ridge)
    c,blocked=path_support(smooth,domain,seed,meta['diffuse_Y']);out['C']=(c,dict(meta,blocked_direct_routes=blocked),np.zeros_like(domain))
    for m,(mask,info,barrier) in out.items():
        edge=np.zeros_like(mask);edge[[0,-1],:]=True;edge[:,[0,-1]]=True;info.update(window_contact_pixels=int((mask&edge).sum()),area_cap_exceeded=bool(mask.sum()>870),native_components=int(ndi.label(mask)[1]),physical_identity='unknown')
    return out
