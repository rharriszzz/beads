"""R265: straight-path native growth, local valley fences and connected local retreat.

Only RGB enters detection. Each maximum grows independently; overlapping supports
remain explicit rather than imposing another partition. Every non-root accepted
pixel has an adjacent earlier predecessor. Archived R262 remains unchanged. Noise allowance never accumulates uphill.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import heapq
import json
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/beads-r261-mpl")
from dataclasses import asdict, dataclass
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from matplotlib.colors import rgb_to_hsv
from scipy import ndimage as ndi
from skimage.morphology import local_maxima, h_maxima
from skimage.measure import find_contours

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'r265-first-dark-v2'
N8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]

@dataclass(frozen=True)
class Parameters:
    first_dark_stop: bool = True
    black_peak_fraction: float = .5
    neutral_saturation: float = .25
    neutral_chroma_dn: int = 12
    local_growth: bool = True
    valley_guard: bool = True
    local_retreat: bool = True
    background_precheck: bool = True
    valley_depth_dn: int = 6
    max_region_pixels: int = 870
    minimum_peak_dn: int = 0
    rise_budget_dn: int = 0
    prominence_dn: int = 35
    patch_drop_dn: int = 10
    retreat_fraction: float = .30
    retreat_dn: int = 2
    dark_dn: int = 81
    reflection_drop_dn: int = 36
    hue_stop_deg: float = 10.
    reliable_saturation: float = .35
    saturation_drop: float = .40
    min_support: int = 3
    border_fraction: float = .035

    def __post_init__(self):
        if not 1<=self.max_region_pixels<=870:
            raise ValueError("Maximum region pixels must be1..870")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, separators=(',', ':'), allow_nan=False)+'\n')


def runs(mask, x0=0, y0=0):
    out = []
    for y, row in enumerate(mask):
        d = np.diff(np.r_[False, row, False].astype(np.int8))
        out.extend([[y+y0, int(a)+x0, int(b)-1+x0] for a,b in zip(np.where(d==1)[0], np.where(d==-1)[0])])
    return out


def contours(mask, x0=0, y0=0):
    """One cyclic 1:2:1 pass ONLY on display coordinates; never rasterized."""
    out = []
    for curve in find_contours(np.pad(mask.astype(float),1), .5):
        c = curve[:-1, ::-1] + [x0-1, y0-1]
        if len(c) < 3: continue
        c = (np.roll(c,1,axis=0)+2*c+np.roll(c,-1,axis=0))/4
        out.append(np.vstack([c,c[0]]).tolist())
    return out


def measure(mask, x0=0, y0=0):
    yy,xx = np.where(mask)
    centroid = [float(xx.mean()+x0),float(yy.mean()+y0)]
    j = int(np.argmin((xx-xx.mean())**2+(yy-yy.mean())**2))
    return dict(centroid=centroid, location=[int(xx[j]+x0),int(yy[j]+y0)],
                pixel_count=len(xx), area_px2=len(xx),
                bbox=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1)])


def valley_pixels(value, depth=6):
    """Native local saddle/minimum: opposing neighbors both exceed this pixel.

    No ownership, smoothing, seed location or photographic labels enter this map.
    A six-DN margin prevents one-level quantization from erecting a fence.
    """
    v=value.astype(np.int16); out=np.zeros(v.shape,bool)
    h,w=v.shape
    for dy,dx in [(0,1),(1,0),(1,1),(1,-1)]:
        ya,yb=abs(dy),h-abs(dy);xa,xb=abs(dx),w-abs(dx)
        if ya>=yb or xa>=xb:continue
        c=v[ya:yb,xa:xb]
        out[ya:yb,xa:xb] |= ((v[ya+dy:yb+dy,xa+dx:xb+dx]>=c+depth) &
                                (v[ya-dy:yb-dy,xa-dx:xb-dx]>=c+depth))
    return out


def retreat(value, trace, p):
    """Local raw darkness test, then retain the seed's eight-connected component.

    No descendant minima or leaf-count test. The local 3x3 floor is capped at the
    dark reference: a bright terminal pixel cannot call itself a dark boundary.
    The cap makes this conservative about removing dim bodies; this is support,
    not a physical outline. Components detached by removal are recorded explicitly.
    """
    a=trace['accepted'];mx,my=trace['mask_offset'];peak=a[0][3]
    shape=(max(r[1] for r in a)-my+1,max(r[0] for r in a)-mx+1)
    provisional=np.zeros(shape,bool);floors=[];thresholds=[];reasons=[]
    ox,oy=trace.get('source_offset',[0,0])
    for row in a:
        x,y=row[0]-ox,row[1]-oy
        floor=min(p.dark_dn,int(value[max(0,y-1):y+2,max(0,x-1):x+2].min()))
        threshold=floor+max(p.retreat_dn,p.retreat_fraction*(peak-floor))
        keep=row[3]==peak or row[3]>threshold
        provisional[row[1]-my,row[0]-mx]=keep
        floors.append(floor);thresholds.append(threshold)
    labels,_=ndi.label(provisional,structure=np.ones((3,3)))
    mask=labels==labels[a[0][1]-my,a[0][0]-mx]
    for row in a:
        y,x=row[1]-my,row[0]-mx;row[7]=bool(mask[y,x])
        reasons.append('retained' if row[7] else 'local-darkness' if not provisional[y,x] else 'disconnected-after-retreat')
    trace.update(retreat_floor_dn=floors,retreat_threshold_dn=thresholds,retreat_reasons=reasons)
    return mask


def neutral_gray(q, p=Parameters()):
    """Low saturation or small absolute channel spread; hue alone is unreliable here."""
    return bool(q[1]<=p.neutral_saturation or q[1]*q[2]*255<=p.neutral_chroma_dn)


def straight_pixels(seed, target):
    """Integer Bresenham sampling of one straight segment; no sampled interpolation.

    Pixel centers form the native raster approximation to the straight segment,
    not an obstacle-dependent route. Every step is an eight-neighbor step.
    """
    x,y=seed;ex,ey=target;dx=abs(ex-x);dy=-abs(ey-y)
    sx=1 if x<ex else -1;sy=1 if y<ey else -1;err=dx+dy;out=[]
    while True:
        out.append((x,y))
        if (x,y)==(ex,ey):return out
        twice=2*err
        if twice>=dy:err+=dy;x+=sx
        if twice<=dx:err+=dx;y+=sy


def grow(value, hsv, seed, p=Parameters(), offset=(0,0), valleys=None):
    """Independent straight seed-to-pixel histories on the original native raster.

    Each candidate is checked along its complete integer straight segment. A dark,
    uphill or color stop anywhere on that segment blocks the destination. No
    curved/winding route is eligible. Earlier segment pixels must already have
    been accepted, ensuring connected support without alternative-route repair.
    Process distance shells then brightness so prefixes are decided first. The
    acceptance predecessor is the adjacent last segment pixel; straight_path_indices
    preserves the complete history, because different raster segments can have
    different prefixes. Stops are irreversible per destination's fixed segment.
    """
    from . import bounded_detect as old
    if not p.local_growth:
        base=old.Parameters(**{k:getattr(p,k) for k in old.Parameters.__dataclass_fields__})
        mask,t=old.grow(value,hsv,seed,base,offset);t['source_offset']=list(offset)
        if p.local_retreat:mask=retreat(value,t,p)
        return mask,t
    h,w=value.shape;sx,sy=seed;ox,oy=offset;peak=int(value[sy,sx])
    if p.first_dark_stop and peak==0:
        raise ValueError("Seed is already at or below the first-dark limit")
    if valleys is None:valleys=valley_pixels(value,p.valley_depth_dn) if p.valley_guard else None
    accepted=[];stops=[];details=[];seen={};incoming={};blocked={};queue=[(0,-peak,sy,sx)]
    queued={(sy,sx)};size_limited=False;floors=[];histories=[];gray_fractions=[]
    def chromatic(q):return q[1]>=p.reliable_saturation and q[2]>=.20 and q[1]*q[2]>=.08
    def stop(x,y,prev,reason,detail=None):
        q=hsv[y,x];stops.append([x+ox,y+oy,prev,int(value[y,x]),float(q[0]*360),float(q[1]),float(q[2]),reason,len(accepted)])
        details.append(detail)
    def barrier(x,y):
        return bool(valleys[y,x]) or (int(value[y,x])<=p.dark_dn and ((p.first_dark_stop and int(value[y,x])<=p.black_peak_fraction*peak and neutral_gray(hsv[y,x],p)) or peak-int(value[y,x])>=p.reflection_drop_dn))
    while queue:
        _,neg,y,x=heapq.heappop(queue);line=straight_pixels(seed,(x,y))
        floor=peak;anchor=tuple(hsv[sy,sx]) if chromatic(hsv[sy,sx]) else None;reason=None;block=None
        for j,(tx,ty) in enumerate(line[1:],1):
            px,py=line[j-1];nv=int(value[ty,tx]);nq=hsv[ty,tx]
            if nv>floor+p.rise_budget_dn:reason='brightness-rise'
            elif nv<=p.dark_dn and ((p.first_dark_stop and nv<=p.black_peak_fraction*peak and neutral_gray(nq,p)) or peak-nv>=p.reflection_drop_dn):reason='dark-frontier'
            elif p.valley_guard and valleys[ty,tx]:reason='local-valley'
            elif p.valley_guard and tx!=px and ty!=py and (barrier(tx,py) or barrier(px,ty)):reason='valley-corner'
            elif anchor is not None and chromatic(nq) and min(abs(float(nq[0]-anchor[0])),1-abs(float(nq[0]-anchor[0])))*360>=p.hue_stop_deg-1e-12:reason='relative-hue-change'
            elif anchor is not None and anchor[1]-nq[1]>=p.saturation_drop and nv<peak-p.patch_drop_dn:reason='saturation-loss'
            elif j<len(line)-1 and (ty,tx) not in seen:reason='straight-prefix-blocked'
            if reason:block=[tx+ox,ty+oy];break
            floor=min(floor,nv)
            if anchor is None and chromatic(nq):anchor=tuple(nq)
        if reason:
            detail=dict(blocker=block,straight_target=[x+ox,y+oy],blocker_is_neutral=neutral_gray(nq,p),gray_fraction_before_stop=float(np.mean([neutral_gray(hsv[ly,lx],p) for lx,ly in line[:j]])));blocked[y,x]=(reason,detail)
            for prev in incoming.pop((y,x),[]):stop(x,y,prev,reason,detail)
            continue
        prev=seen[line[-2][1],line[-2][0]] if len(line)>1 else -1
        if len(accepted)>=p.max_region_pixels:
            size_limited=True
            for (qy,qx),parents in incoming.items():
                for qi in parents:stop(qx,qy,qi,'maximum-region-pixels')
            break
        v=int(value[y,x]);q=hsv[y,x];i=len(accepted);seen[y,x]=i;incoming.pop((y,x),None)
        floors.append(floor);accepted.append([x+ox,y+oy,prev,v,float(q[0]*360),float(q[1]),float(q[2]),True])
        histories.append([seen[ty,tx] for tx,ty in line])
        gray_fractions.append(float(np.mean([neutral_gray(hsv[ty,tx],p) for tx,ty in line])))
        for dy,dx in N8:
            ny,nx=y+dy,x+dx
            if not (0<=ny<h and 0<=nx<w) or (ny,nx) in seen:continue
            if (ny,nx) in blocked:
                why,detail=blocked[ny,nx];stop(nx,ny,i,why,detail)
            else:
                incoming.setdefault((ny,nx),[]).append(i)
                if (ny,nx) not in queued:
                    queued.add((ny,nx));heapq.heappush(queue,(max(abs(nx-sx),abs(ny-sy)),-int(value[ny,nx]),ny,nx))
    mx=min(a[0] for a in accepted);my=min(a[1] for a in accepted)
    t=dict(accepted_columns=['x','y','predecessor','value_dn','hue_deg','saturation','value','retained'],
           stop_columns=['x','y','predecessor','value_dn','hue_deg','saturation','value','reason','after_accept_count'],
           accepted=accepted,stops=stops,stop_details=details,path_floor_dn=floors,straight_path_indices=histories,neutral_path_fraction=gray_fractions,
           mask_offset=[mx,my],source_offset=list(offset),size_limited=size_limited,max_region_pixels=p.max_region_pixels)
    if p.local_retreat:mask=retreat(value,t,p)
    else:
        lows=np.array([a[3] for a in accepted],float)
        for row in stops:
            if row[7]=='dark-frontier':lows[row[2]]=min(lows[row[2]],row[3])
        for i in range(len(accepted)-1,0,-1):lows[accepted[i][2]]=min(lows[accepted[i][2]],lows[i])
        mask=np.zeros((max(a[1] for a in accepted)-my+1,max(a[0] for a in accepted)-mx+1),bool)
        for i,a in enumerate(accepted):
            a[7]=bool(a[3]==peak or (a[3]>lows[i]+max(p.retreat_dn,p.retreat_fraction*(peak-lows[i])) and accepted[a[2]][7]))
            if a[7]:mask[a[1]-my,a[0]-mx]=True
        t['retreat_floor_dn']=lows.tolist()
    return mask,t


def learn_background(hsv, border):
    """Robust circular H, S, V model from generic image margins, no palette box.

    Only narrow, consistent margin evidence is enabled. The value interval is
    observed, never extrapolated into deep shadows; uncertain colors are retained.
    """
    samples=hsv[border];angle=2*np.pi*samples[:,0]
    z=np.mean(np.exp(1j*angle));h=float(np.angle(z)/(2*np.pi)%1)
    dh=np.abs((samples[:,0]-h+.5)%1-.5)
    center=np.median(samples,axis=0);center[0]=h
    tol=np.maximum([2/360,.025,.025],np.percentile(np.column_stack([dh,abs(samples[:,1]-center[1]),abs(samples[:,2]-center[2])]),95,axis=0))
    enabled=bool(tol[0]<=12/360 and tol[1]<=.15 and tol[2]<=.18)
    return dict(center=center.tolist(),tolerance=tol.tolist(),enabled=enabled,sample_count=len(samples),source='generic border HSV; conservative 95-percent intervals')


def obvious_background(hsv, x, y, model):
    if not model['enabled']:return False
    patch=hsv[max(0,y-1):y+2,max(0,x-1):x+2];c=np.array(model['center']);t=np.array(model['tolerance'])
    delta=abs(patch-c);delta[:,:,0]=abs((patch[:,:,0]-c[0]+.5)%1-.5)
    # Every local sample must agree in all three channels. Hue is uninformative
    # for neutral paper: disable rejection there rather than invent a color prior.
    return bool(c[1]>=.10 and np.all(delta<=t))


def detect(rgb, p=Parameters(), trace_dir=None):
    value=rgb.max(axis=2);h,w=value.shape
    hsv=rgb_to_hsv(rgb.astype(np.float64)/255)
    maxima_mask=local_maxima(value, connectivity=2, allow_borders=True)
    markers,n=ndi.label(maxima_mask,structure=np.ones((3,3)))
    meaningful=h_maxima(value,p.prominence_dn,footprint=np.ones((3,3))) if value.max()>value.min() else np.zeros_like(value)
    significant=set(np.unique(markers[meaningful.astype(bool)]))-{0}
    peak_slices=ndi.find_objects(markers)
    m=max(1,round(min(h,w)*p.border_fraction));border=np.zeros((h,w),bool)
    border[:m]=border[-m:]=True;border[:,:m]=border[:,-m:]=True
    background_model=learn_background(hsv,border)
    valleys=valley_pixels(value,p.valley_depth_dn) if p.valley_guard else np.zeros(value.shape,bool)
    chroma=rgb.astype(float)/np.maximum(value[:,:,None],1)
    paper=np.median(chroma[border],axis=0);dist=np.linalg.norm(chroma-paper,axis=2)
    tolerance=max(.09,float(np.percentile(dist[border],99.5))*1.7)
    paper_like=dist<tolerance
    # Image-wide raw bright connectivity is used only to VERIFY a first dark
    # enclosure, never to grow a region or assign black material.
    bright,nb=ndi.label(value>p.dark_dn,structure=np.ones((3,3)))
    bslices=ndi.find_objects(bright); dark_cache={}
    def enclosure(x,y):
        b=int(bright[y,x])
        if not b:return None
        if b not in dark_cache:
            sl=bslices[b-1];ya,xa=sl[0].start,sl[1].start;yb,xb=sl[0].stop,sl[1].stop
            if ya==0 or xa==0 or yb==h or xb==w:dark_cache[b]=None
            else:
                core=bright[ya-1:yb+1,xa-1:xb+1]==b
                shell=ndi.binary_dilation(core,structure=np.ones((3,3))) & ~core
                dark_cache[b]=dict(pixel_count=int(core.sum()),perimeter_runs=runs(shell,xa-1,ya-1),
                    perimeter_max_dn=int(value[ya-1:yb+1,xa-1:xb+1][shell].max()),
                    meaningful_maxima=sorted(int(k) for k in np.unique(markers[ya:yb,xa:xb][bright[ya:yb,xa:xb]==b]) if k in significant))
        return dark_cache[b]
    regions=[];rejected=[];maxima=[];labels=np.zeros((h,w),np.int32)
    coverage=np.zeros((h,w),np.uint32)
    for owner,ps in enumerate(peak_slices,1):
        if ps is None:continue
        yy,xx=np.where(markers[ps]==owner);j=int(np.argmin((xx-xx.mean())**2+(yy-yy.mean())**2))
        x,y=int(xx[j]+ps[1].start),int(yy[j]+ps[0].start)
        mid=f'M{owner:06d}';rid=f'P{owner:06d}'
        candidate=dict(id=mid,region_id=rid,peak=[x,y],value_dn=int(value[y,x]),meaningful=owner in significant,
                       plateau_pixel_count=len(xx),plateau_centroid=[float(xx.mean()+ps[1].start),float(yy.mean()+ps[0].start)],
                       plateau_runs=runs(markers[ps]==owner,ps[1].start,ps[0].start))
        if owner not in significant or int(value[y,x])<p.minimum_peak_dn:
            candidate.update(status='rejected',reason='below-prominence' if owner not in significant else 'below-minimum-peak',patch_centroid=candidate['plateau_centroid'],patch_runs=candidate['plateau_runs'])
            maxima.append(candidate);continue
        if p.first_dark_stop and int(value[y,x])==0:
            candidate.update(status='rejected',reason='first-dark-seed',patch_centroid=candidate['plateau_centroid'],patch_runs=candidate['plateau_runs'])
            maxima.append(candidate);continue
        if p.background_precheck and obvious_background(hsv,x,y,background_model):
            candidate.update(status='rejected',reason='obvious-background-before-growth',patch_centroid=candidate['plateau_centroid'],patch_runs=candidate['plateau_runs'])
            maxima.append(candidate);continue
        mask,trace=grow(value,hsv,(x,y),p,valleys=valleys)
        xa,ya=trace['mask_offset'];yb=ya+mask.shape[0];xb=xa+mask.shape[1]
        accepted_mask=np.zeros(mask.shape,bool)
        for a in trace['accepted']:accepted_mask[a[1]-ya,a[0]-xa]=True
        patch=accepted_mask & (value[ya:yb,xa:xb]>=int(value[y,x])-p.patch_drop_dn)
        pm=measure(patch,xa,ya);candidate.update(patch_centroid=pm['centroid'],patch_runs=runs(patch,xa,ya),patch_pixel_count=pm['pixel_count'])
        dark=enclosure(x,y) if int(value[y,x])>=p.dark_dn+p.reflection_drop_dn else None
        # Large connected bright structures are not compact reflection evidence.
        dark_ok=dark is not None and dark['meaningful_maxima']==[owner]
        reasons=['maximum-region-pixels'] if trace['size_limited'] else []
        if not dark_ok and bool(np.all(paper_like[ya:yb,xa:xb][patch])):reasons.append('paper-compatible-patch')
        ambiguity=['physical-bead-identity-unverified','multiple-highlights-not-merged']
        if int(mask.sum())<p.min_support:ambiguity.append('tiny-support')
        if not dark_ok:ambiguity.append('reflection-versus-interior-unresolved')
        if xa==0 or ya==0 or xb==w or yb==h:ambiguity.append('image-edge-growth')
        record=dict(id=rid,maxima_ids=[mid],status='rejected' if reasons else 'retained',
                    kind='dark-enclosed-bright-support' if dark_ok else 'ambiguous-bright-support',
                    ambiguity=ambiguity,rejected_reasons=reasons,**measure(mask,xa,ya),
                    pixel_runs=runs(mask,xa,ya),contours=contours(mask,xa,ya),bright_patch=candidate,
                    dark_enclosure=dark if dark_ok else None,growth_pixel_count=len(trace['accepted']),
                    stop_count=len(trace['stops']),size_limited=trace['size_limited'],trace_file=f'traces/{rid}.json.gz')
        if trace_dir is not None:
            with gzip.GzipFile(filename=str(trace_dir/f'{rid}.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(trace,separators=(',',':')).encode())
        else:record['trace']=trace
        candidate.update(status=record['status'],reason=';'.join(reasons) or 'ambiguous-candidate')
        maxima.append(candidate)
        (rejected if reasons else regions).append(record)
        if not reasons:
            target=labels[ya:yb,xa:xb];count=coverage[ya:yb,xa:xb]
            target[mask & (count==0)]=owner
            target[mask & (count>0)]=-1
            count[mask]+=1
    for record in regions:
        overlap=sum(int(np.count_nonzero(coverage[y,a:b+1]>1)) for y,a,b in record['pixel_runs'])
        record['overlap_pixel_count']=overlap
        if overlap:record['ambiguity'].append('overlapping-independent-supports')
    return dict(version=VERSION,parameters=asdict(p),width=w,height=h,maxima=maxima,regions=regions,rejected=rejected,
                background=dict(chromaticity=paper.tolist(),tolerance=tolerance,hsv_seed_model=background_model),
                namespaces='P = raw-maximum support; M = raw maximum. Match generation IDs for masks. Neither is a bead index.',
                label_schema='0 unretained; positive unique P ID; -1 overlap. Exact per-region runs retain all memberships.',
                unexpanded_maxima_reason='below-prominence, below-minimum-peak or obvious-background-before-growth; equal-valued plateau saved, no growth attempted',
                trace_schema='Per-region accepted order is array index; predecessor is earlier array index, -1 root. Stops are directed edges. Raw source defines unvisited pixels.'),labels,coverage


def generate(image_path, output, p=Parameters()):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);td=output/'traces';td.mkdir(exist_ok=True)
    image=ImageOps.exif_transpose(Image.open(image_path)).convert('RGB');rgb=np.asarray(image)
    data,labels,coverage=detect(rgb,p,td)
    data.update(image_sha256=sha(image_path),detector_sha256=sha(__file__))
    data['generation_id']=hashlib.sha256((data['image_sha256']+data['detector_sha256']+json.dumps(asdict(p),sort_keys=True)).encode()).hexdigest()[:16]
    save(output/'regions.json',data);np.savez_compressed(output/'labels.npz',labels=labels,membership_count=coverage)
    image.save(output/'photo.png',icc_profile=None)
    sizes=np.array([r['pixel_count'] for r in data['regions']]);hist,edges=np.histogram(sizes,bins=30)
    summary=dict(generation_id=data['generation_id'],image_sha256=data['image_sha256'],detector_sha256=data['detector_sha256'],
        precheck_rejected=sum(m['reason']=='obvious-background-before-growth' for m in data['maxima']),raw_maxima=len(data['maxima']),meaningful_maxima=sum(m['meaningful'] for m in data['maxima']),grown_maxima=len(data['regions'])+len(data['rejected']),regions=len(sizes),
        ambiguous_candidates=len(sizes),rejected_candidates=sum(m['status']=='rejected' for m in data['maxima']),
        below_minimum_peak=sum(m['reason']=='below-minimum-peak' for m in data['maxima']),low_prominence=sum(not m['meaningful'] for m in data['maxima']),rejected_grown=len(data['rejected']),
        size_limited=sum(r.get('size_limited',False) for r in data['regions']+data['rejected']),
        dark_enclosed=sum(r['dark_enclosure'] is not None for r in data['regions']),
        overlapping_regions=sum(r['overlap_pixel_count']>0 for r in data['regions']),overlap_pixels=int(np.count_nonzero(coverage>1)),
        sizes=dict(min=int(sizes.min()),median=float(np.median(sizes)),max=int(sizes.max()),total=int(sizes.sum())) if len(sizes) else None,
        histogram=dict(counts=hist.tolist(),edges=edges.tolist()),parameters=asdict(p))
    save(output/'summary.json',summary)
    with (output/'coordinates.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['region_id','status','location_x','location_y','centroid_x','centroid_y','pixels','kind'])
        for r in data['regions']+data['rejected']:writer.writerow([r['id'],r['status'],*r['location'],*r['centroid'],r['pixel_count'],r['kind']])
    with (output/'rank-size.csv').open('w') as f:
        f.write('rank,region_id,pixel_count\n')
        for i,r in enumerate(sorted(data['regions'],key=lambda r:-r['pixel_count']),1):f.write(f'{i},{r["id"]},{r["pixel_count"]}\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4));ax.hist(sizes,bins=edges,color='#008caa');ax.set(xlabel='Native pixels per retained support',ylabel='Regions',title='R265 region sizes (not bead areas)');fig.tight_layout();fig.savefig(output/'size-distribution.png',dpi=150);plt.close(fig)
    print(json.dumps(summary,indent=2),flush=True)
    return data


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    ap.add_argument('--output',type=Path,default=ROOT/'photo2/output/r265-first-dark/joint')
    from dataclasses import fields
    for field in fields(Parameters):
        default=getattr(Parameters(),field.name)
        ap.add_argument('--'+field.name.replace('_','-'),type=(lambda v:v.lower()=='true') if isinstance(default,bool) else type(default),default=default)
    a=ap.parse_args();p=Parameters(**{f.name:getattr(a,f.name) for f in fields(Parameters)})
    if not 0<=p.minimum_peak_dn<=255 or not 1<=p.prominence_dn<=255 or not 0<=p.rise_budget_dn<=255:
        ap.error('Minimum peak/rise budget must be 0..255; prominence must be 1..255')
    if not 0<=p.retreat_fraction<1 or not 0<=p.retreat_dn<=255 or not 0<=p.dark_dn<=255 or not 0<=p.reflection_drop_dn<=255 or not 0<=p.patch_drop_dn<=255:
        ap.error('Brightness thresholds must be 0..255; retreat fraction must be [0,1)')
    if not 0<=p.hue_stop_deg<=180 or not 0<=p.reliable_saturation<=1 or not 0<=p.saturation_drop<=1 or p.min_support<1 or not 0<p.border_fraction<=.5:
        ap.error('Invalid color, support or border parameter')
    generate(a.image,a.output,p)

if __name__=='__main__':main()
