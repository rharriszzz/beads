"""Local photographic evidence, never calibrated ownership or physical labels."""
import numpy as np
from scipy import ndimage as ndi
from photo2.r285.methods import measurements
from photo2.r286.methods import marker_field

def boundary(lum,pigment,mask):
    edge=mask&~ndi.binary_erosion(mask);y,x=np.where(edge)
    if not len(x):return dict(dark_fraction=0.,bright_continuation_fraction=0.,coherent_bright_pixels=0,boundary_pixels=0,samples=[])
    sd=ndi.distance_transform_edt(mask)-ndi.distance_transform_edt(~mask);gy,gx=np.gradient(ndi.gaussian_filter(sd,1));norm=np.hypot(gx[y,x],gy[y,x]);nx=-gx[y,x]/np.maximum(norm,1e-9);ny=-gy[y,x]/np.maximum(norm,1e-9);sm=ndi.gaussian_filter(lum,.65);inside=[];outside=[];pg=[]
    for d in (2,4):
        inside.append(ndi.map_coordinates(sm,[y-d*ny,x-d*nx],order=1,mode='nearest'));outside.append(ndi.map_coordinates(sm,[y+d*ny,x+d*nx],order=1,mode='nearest'));pg.append(ndi.map_coordinates(pigment.astype(float),[y+d*ny,x+d*nx],order=1,mode='nearest'))
    a=np.mean(inside,axis=0);b=np.mean(outside,axis=0);ratio=b/np.maximum(a,.003);bright=(ratio>.70)&(np.mean(pg,axis=0)>.5)&(b>.025);bm=np.zeros_like(mask);bm[y[bright],x[bright]]=True;labels,n=ndi.label(bm,structure=np.ones((3,3)));counts=np.bincount(labels.ravel());coherent=int(sum(v for v in counts[1:] if v>=6));dark=(ratio<.65)&(a>.025)
    return dict(dark_fraction=float(dark.mean()),bright_continuation_fraction=float(bright.mean()),coherent_bright_pixels=coherent,boundary_pixels=len(x),median_outside_inside=float(np.median(ratio)),median_inside_Y=float(np.median(a)),median_outside_Y=float(np.median(b)),samples=[dict(x=int(px),y=int(py),inside=float(aa),outside=float(bb),ratio=float(rr),bright=bool(br)) for px,py,aa,bb,rr,br in zip(x,y,a,b,ratio,bright)])

def marker_seams(smooth,pigment,domain,paper,seed,masks):
    if seed is None:return [],[]
    markers,target,ledger=marker_field(smooth,pigment,domain,paper,seed);primary=next((r['placed'] for r in ledger if r['label']==target),seed);p=np.array(primary,float);yy,xx=np.indices(domain.shape);pairs=[]
    for r in ledger:
        if r.get('placed') is None or r['label']==target:continue
        q=np.array(r['placed'],float);delta=q-p;dist=float(np.linalg.norm(delta))
        if not 10<=dist<=42:continue
        refs=[];fractions=[]
        for xy in (p,q):
            circ=(xx-xy[0])**2+(yy-xy[1])**2<=36;core=circ&pigment;fractions.append(float(pigment[circ].mean()));refs.append(float(np.quantile(smooth[core],.6)) if core.any() else 0.)
        if min(refs)<=.025:continue
        normal=np.array([-delta[1],delta[0]])/dist;t=np.linspace(0,1,max(25,int(dist)*2));profiles=[];ratios=[];troughs=[]
        for offset in (-3,-1.5,0,1.5,3):
            route=p+t[:,None]*delta+offset*normal;vals=ndi.map_coordinates(smooth,route[:,::-1].T,order=1,mode='nearest');vals=ndi.uniform_filter1d(vals,3);valid=(t>=.2)&(t<=.8);ix=np.where(valid)[0][np.argmin(vals[valid])];ratios.append(float(vals[ix]/min(refs)));troughs.append(float(t[ix]));profiles.append(dict(offset=offset,route=route.tolist(),Y=vals.tolist(),trough_index=int(ix)))
        coherent=bool(sum(v<.55 for v in ratios)>=4 and np.std(troughs)<.15 and min(fractions)>=.4)
        cores=[]
        for xy in (p,q):cores.append((xx-xy[0])**2+(yy-xy[1])**2<=4)
        ownership={m:[float((mask&core).sum()/core.sum()) for core in cores] for m,mask in masks.items()};conflicts={m:bool(coherent and own[0]>=.5 and own[1]>=.35) for m,own in ownership.items()}
        pairs.append(dict(peaks=[p.tolist(),q.tolist()],distance=dist,diffuse_refs=refs,pigment_fractions=fractions,valley_ratios=ratios,trough_positions=troughs,coherent_seam=coherent,core_coverage=ownership,conflicts=conflicts,profiles=profiles))
    return pairs,ledger

def diffuse_routes(lum,pigment,j,m,diffuse):
    """Test shading continuity along three direct routes, never a bright detour.

    A monotone decline is allowed. A valley followed by renewed bright material
    fails. This is evidence for choosing a whole candidate, not growth/union.
    """
    y,x=np.where(m&~j&pigment)
    if not len(x) or not j.any():return dict(supported_pixels=0,eligible_pixels=len(x),supported_fraction=0.,pixels=[],route_examples=[])
    _,nearest=ndi.distance_transform_edt(~j,return_indices=True);ends=np.c_[x,y];starts=nearest[:,y,x].T[:,::-1];delta=ends-starts;length=np.maximum(np.linalg.norm(delta,axis=1),1.);normal=np.c_[-delta[:,1],delta[:,0]]/length[:,None];t=np.linspace(0,1,25)[:,None,None];smooth=ndi.gaussian_filter(lum,.65);passes=[];examples=[]
    for off in (-1.5,0,1.5):
        route=starts[None,:,:]+t*delta[None,:,:]+off*normal[None,:,:];values=ndi.map_coordinates(smooth,[route[:,:,1],route[:,:,0]],order=1,mode='nearest');pg=ndi.map_coordinates(pigment.astype(float),[route[:,:,1],route[:,:,0]],order=1,mode='nearest');low=values.min(axis=0);end=values[-1];start=values[0];valley=(low<.6*np.minimum(start,end))&((end-low)>.1*diffuse);ok=(pg.mean(axis=0)>=.8)&~valley&(end>=max(.015,.15*diffuse));passes.append(ok)
        if off==0:
            # Deterministic nearest, median and farthest examples; never picked by decision.
            for idx in np.unique(np.argsort(length)[[0,len(length)//2,-1]]):examples.append(dict(route=route[:,idx,:].tolist(),Y=values[:,idx].tolist(),pigment=pg[:,idx].tolist(),valley=bool(valley[idx])))
    supported=np.sum(passes,axis=0)>=2
    return dict(supported_pixels=int(supported.sum()),eligible_pixels=len(x),supported_fraction=float(supported.mean()),pixels=ends[supported].tolist(),rejected_pixels=ends[~supported].tolist(),route_examples=examples)

def measure(lum,hsv,paper,palette,bgh,color,masks,stability):
    sm,pg,domain,seed,meta=measurements(lum,hsv,paper,palette,bgh,color);seams,ledger=marker_seams(sm,pg,domain,paper,seed,masks);out={};n=len(lum)//2;yy,xx=np.indices(lum.shape);core=(xx-n)**2+(yy-n)**2<=36;exposure=float(np.median(lum[core]));pigmentfraction=float(pg[core].mean())
    for name,mask in masks.items():
        b=boundary(lum,pg,mask);out[name]=dict(boundary=b,area=int(mask.sum()),components=int(ndi.label(mask)[1]),pigment_fraction=float(pg[mask].mean()) if mask.any() else 0.,paper_fraction=float(paper[mask].mean()) if mask.any() else 0.,seed_supported=bool(mask[n-3:n+4,n-3:n+4].any()),coherent_seam_conflicts=sum(s['conflicts'][name] for s in seams),seams_outside=sum(s['coherent_seam'] and s['core_coverage'][name][0]>=.5 and s['core_coverage'][name][1]<.35 for s in seams),stability=stability[name])
    j,m=masks['J'],masks['M'];gain=m&~j;loss=j&~m;diffuse=gain&pg&(lum>=max(.015,.15*meta['diffuse_Y']));vals=lum[diffuse];peak=float(sm[n-4:n+5,n-4:n+5].max())
    routes=diffuse_routes(lum,pg,j,m,meta['diffuse_Y'])
    return dict(diffuse_routes=routes,candidates=out,agreement_iou=float((j&m).sum()/max(1,(j|m).sum())),M_minus_J=int(gain.sum()),J_minus_M=int(loss.sum()),diffuse_gain_pixels=int(diffuse.sum()),diffuse_gain_fraction_of_J=float(diffuse.sum()/max(1,j.sum())),diffuse_gain_median_Y=float(np.median(vals)) if len(vals) else None,peak_to_diffuse=peak/max(.001,meta['diffuse_Y']),core_exposure_Y=exposure,core_pigment_fraction=pigmentfraction,measurement=meta,marker_ledger=ledger,seams=seams,semantics='Brightness and ownership evidence proxies; not calibrated physical identity truth.')
