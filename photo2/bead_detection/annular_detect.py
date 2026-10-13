"""R266: separate annular/straight experiments, peak evidence and paper deferral.

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
VERSION = 'r266-annular-v1'
N8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]

@dataclass(frozen=True)
class Parameters:
    method: str = "straight"
    background_guard: bool = False
    peak_selection: bool = False
    recover_peaks: bool = False
    recovery_prominence_dn: int = 12
    association_radius: int = 18
    split_regions: bool = False
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


def grow(value, hsv, seed, p=Parameters(), offset=(0,0), valleys=None, paper=None):
    from . import repaired_detect as baseline
    if p.method == 'straight':
        # Preserve exact R265 geometry; paper is an additional irreversible barrier.
        if paper is not None:
            valleys = (valley_pixels(value,p.valley_depth_dn) if valleys is None else valleys) | paper
        bp=baseline.Parameters(**{k:getattr(p,k) for k in baseline.Parameters.__dataclass_fields__})
        mask,t=baseline.grow(value,hsv,seed,bp,offset,valleys)
        t['method']='straight'
        if paper is not None:
            for row,detail in zip(t['stops'],t['stop_details']):
                if detail and detail.get('blocker'):
                    bx,by=detail['blocker'];bx-=offset[0];by-=offset[1]
                    if paper[by,bx] and row[7]=='local-valley':row[7]='probable-paper'
        return mask,t
    if p.method != 'annular':raise ValueError('Unknown method')
    return grow_annular(value,hsv,seed,p,offset,valleys,paper)


def grow_annular(value,hsv,seed,p,offset=(0,0),valleys=None,paper=None):
    """One-pixel square annuli from the native maximum plateau (L-infinity metric).

    The bright patch is the plateau visible along straight raster prefixes from
    its representative. Fixed nearest-patch origins and fixed inward parents are
    geometric, never chosen to avoid a stop. No lateral route can reopen a stopped
    branch. Every encountered neighbor has an explicit decision and native value.
    """
    h,w=value.shape;sx,sy=seed;ox,oy=offset;peak=int(value[sy,sx])
    if valleys is None:valleys=valley_pixels(value,p.valley_depth_dn) if p.valley_guard else np.zeros(value.shape,bool)
    # Bounded plateau discovery only, not brightness flood growth.
    patch={(sx,sy)};todo=[(sx,sy)]
    while todo and len(patch)<=p.max_region_pixels:
        x,y=todo.pop()
        for dy,dx in N8:
            q=(x+dx,y+dy);nx,ny=q
            if 0<=nx<w and 0<=ny<h and q not in patch and value[ny,nx]==peak:
                if all(value[ty,tx]==peak for tx,ty in straight_pixels(seed,q)):
                    patch.add(q);todo.append(q)
    # Cache geometry. Distance ties resolved by Euclidean distance, then y/x.
    roots=sorted(patch,key=lambda q:(max(abs(q[0]-sx),abs(q[1]-sy)),q[1],q[0]))
    def geom(x,y):
        if (x,y) in patch:
            line=straight_pixels(seed,(x,y));return 0,line[-2] if len(line)>1 else None
        root=min(roots,key=lambda q:(max(abs(x-q[0]),abs(y-q[1])),(x-q[0])**2+(y-q[1])**2,q[1],q[0]))
        return max(abs(x-root[0]),abs(y-root[1])),straight_pixels(root,(x,y))[-2]
    a=[];seen={};blocked={};incoming={};queued=set();queue=[];stops=[];details=[];floors=[];anchors=[];layers=[];paths=[]
    def enqueue(x,y):
        if (x,y) not in queued:
            queued.add((x,y));layer,parent=geom(x,y)
            heapq.heappush(queue,(layer,max(abs(x-sx),abs(y-sy)) if layer==0 else 0,-int(value[y,x]),y,x,parent))
    for x,y in roots:enqueue(x,y)
    limited=False
    def chrom(q):return q[1]>=p.reliable_saturation and q[2]>=.2 and q[1]*q[2]>=.08
    def dark(x,y):
        nv=int(value[y,x]);return nv<=p.dark_dn and ((nv<=p.black_peak_fraction*peak and neutral_gray(hsv[y,x],p)) or peak-nv>=p.reflection_drop_dn)
    def emit(x,y,prev,reason,detail):
        q=hsv[y,x];stops.append([x+ox,y+oy,prev,int(value[y,x]),float(q[0]*360),float(q[1]),float(q[2]),reason,len(a)]);details.append(detail)
    while queue:
        layer,_,_,y,x,parent=heapq.heappop(queue);prev=seen.get(parent,-1);nv=int(value[y,x]);q=hsv[y,x]
        reason=None;floor=peak if prev<0 else floors[prev];anchor=(tuple(q) if chrom(q) else None) if prev<0 else anchors[prev]
        if (x,y)!=seed:
            if prev<0:reason='stopped-sector'
            elif nv>floor+p.rise_budget_dn:reason='brightness-rise'
            elif dark(x,y):reason='dark-frontier'
            elif paper is not None and paper[y,x]:reason='probable-paper'
            elif p.valley_guard and valleys[y,x]:reason='local-valley'
            elif p.valley_guard and parent[0]!=x and parent[1]!=y and any(dark(tx,ty) or valleys[ty,tx] or (paper is not None and paper[ty,tx]) for tx,ty in [(parent[0],y),(x,parent[1])]):reason='valley-corner'
            elif anchor is not None and chrom(q) and abs((float(q[0]-anchor[0])+.5)%1-.5)*360>=p.hue_stop_deg-1e-12:reason='relative-hue-change'
            elif anchor is not None and anchor[1]-q[1]>=p.saturation_drop and nv<peak-p.patch_drop_dn:reason='saturation-loss'
        if reason:
            detail=dict(blocker=[x+ox,y+oy],fixed_parent=[parent[0]+ox,parent[1]+oy] if parent else None,layer=layer)
            blocked[x,y]=(reason,detail)
            for i in incoming.pop((x,y),[]):emit(x,y,i,reason,detail)
            continue
        if len(a)>=p.max_region_pixels:
            limited=True
            for (tx,ty),parents in incoming.items():
                for i in parents:emit(tx,ty,i,'maximum-region-pixels',None)
            break
        i=len(a);seen[x,y]=i;incoming.pop((x,y),None)
        a.append([x+ox,y+oy,prev,nv,float(q[0]*360),float(q[1]),float(q[2]),True])
        floors.append(min(floor,nv));anchors.append(anchor if anchor is not None else tuple(q) if chrom(q) else None);layers.append(layer)
        paths.append((paths[prev] if prev>=0 else [])+[i])
        for dy,dx in N8:
            nx,ny=x+dx,y+dy
            if not (0<=nx<w and 0<=ny<h) or (nx,ny) in seen:continue
            if (nx,ny) in blocked:emit(nx,ny,i,*blocked[nx,ny])
            else:incoming.setdefault((nx,ny),[]).append(i);enqueue(nx,ny)
    mx=min(r[0] for r in a);my=min(r[1] for r in a)
    t=dict(method='annular',accepted_columns=['x','y','predecessor','value_dn','hue_deg','saturation','value','retained'],stop_columns=['x','y','predecessor','value_dn','hue_deg','saturation','value','reason','after_accept_count'],accepted=a,stops=stops,stop_details=details,path_floor_dn=floors,annular_path_indices=paths,annular_layer=layers,bright_patch_plateau=[[x+ox,y+oy] for x,y in roots],mask_offset=[mx,my],source_offset=list(offset),size_limited=limited,max_region_pixels=p.max_region_pixels)
    mask=retreat(value,t,p)
    return mask,t


def split_supported_mask(mask,value,hsv,offset,seed_points,depth=12,min_piece=12):
    """Cut only native dark-valley samples; require two independently seeded pieces.

    No nearest-seed partition, watershed, filling or unobserved bridge. Child masks
    are subsets of the parent and retain original pixel coordinates. Empty result
    means insufficient evidence. This helper also supports future interactive split.
    """
    x0,y0=offset;v=value[y0:y0+mask.shape[0],x0:x0+mask.shape[1]]
    q=hsv[y0:y0+mask.shape[0],x0:x0+mask.shape[1]]
    valleys=valley_pixels(v,depth)
    # Absolute dark evidence as well as opposing-neighbor contrast is required.
    cut=mask & valleys & (v<=max(81,float(np.max(v[mask]))*.55))
    parts,n=ndi.label(mask & ~cut,np.ones((3,3)))
    if n<2:return []
    children=[]
    for k in range(1,n+1):
        part=parts==k
        seeds=[(x,y) for x,y in seed_points if 0<=y-y0<mask.shape[0] and 0<=x-x0<mask.shape[1] and part[y-y0,x-x0]]
        if part.sum()<min_piece or not seeds:return []
        children.append(dict(pixel_runs=runs(part,x0,y0),seed_points=[list(p) for p in seeds],**measure(part,x0,y0)))
    return children


def background_maps(hsv,border):
    """Learn border H/S/V plus raw local texture; no photograph-specific palette.

    Bright extrapolation is uncertain, so clipped paper-like edges are deferred,
    not confidently rejected. Smooth shadow paper can be recognized locally.
    """
    model=learn_background(hsv,border);c=np.array(model['center']);tol=np.array(model['tolerance'])
    dh=abs((hsv[:,:,0]-c[0]+.5)%1-.5)
    v=hsv[:,:,2]*255
    texture=ndi.maximum_filter(v,5)-ndi.minimum_filter(v,5)
    if not model['enabled']:return model,np.zeros(v.shape,bool),np.zeros(v.shape,bool)
    hue_ok=(dh<=max(tol[0]*1.5,5/360)) if c[1]>=.1 else (hsv[:,:,1]<=max(.1,c[1]+tol[1]))
    saturation_ok=abs(hsv[:,:,1]-c[1])<=max(.06,tol[1]*1.5)
    plausible=hue_ok & saturation_ok & (hsv[:,:,2]>=max(.15,c[2]*.45))
    texture_limit=max(8.,float(np.percentile(texture[border],99)))
    paper=plausible & (texture<=texture_limit)
    # Broader hue is ONLY boundary uncertainty, never a seed-rejection rule.
    uncertainty=(dh<=max(tol[0]*3,30/360)) & saturation_ok & (hsv[:,:,2]>=c[2]*.45)
    model.update(texture_limit_dn=texture_limit,uncertainty_hue_deg=max(tol[0]*3,30/360)*360)
    return model,paper,uncertainty


def region_quality(r,value,hsv):
    pts=[(x,y) for y,a,b in r['pixel_runs'] for x in range(a,b+1)]
    x0,y0,x1,y1=r['bbox'];mask=np.zeros((y1-y0+2,x1-x0+2),bool)
    for x,y in pts:mask[y-y0+1,x-x0+1]=True
    perimeter=int(np.count_nonzero(mask & ~ndi.binary_erosion(mask)))
    compactness=len(pts)/max(perimeter,1)**2
    x,y=r['bright_patch']['peak'];q=hsv[y,x]
    prominence=r['bright_patch']['prominence_lower_bound_dn']
    score=float(value[y,x])*.12+min(prominence,60)*.25+min(len(pts),150)*.08+compactness*60
    return dict(score=score,brightness_dn=int(value[y,x]),prominence_lower_bound_dn=prominence,hsv=(q*[360,1,1]).tolist(),compactness=compactness,perimeter_pixels=perimeter)


def associate(regions,value,hsv,p):
    """Complete-link evidence relative to retained winner; never transitive merging.

    Every bridge sample and its transverse +/-2px ribbon must remain chromatic,
    bright and compatible. A pronounced valley or unknown gray association keeps
    alternatives. Distance/overlap only shortlist pairs.
    """
    from scipy.spatial import cKDTree
    if not regions:return [],[],[]
    peaks=np.array([r['bright_patch']['peak'] for r in regions]);tree=cKDTree(peaks)
    qualities=[region_quality(r,value,hsv) for r in regions]
    for r,q in zip(regions,qualities):r['peak_quality']=q
    order=sorted(range(len(regions)),key=lambda i:(-qualities[i]['score'],regions[i]['id']))
    winners=[];suppressed=[];evidence=[];removed=set();h,w=value.shape
    for i in order:
        if i in removed:continue
        winners.append(regions[i]);x,y=peaks[i]
        for j in tree.query_ball_point(peaks[i],p.association_radius):
            if j==i or j in removed or qualities[j]['score']>qualities[i]['score'] or regions[j] in winners:continue
            tx,ty=peaks[j];line=straight_pixels((x,y),(tx,ty));dx=tx-x;dy=ty-y
            transverse=(0,1) if abs(dx)>=abs(dy) else (1,0)
            ribbon=[(lx+transverse[0]*d,ly+transverse[1]*d) for lx,ly in line for d in (-2,-1,0,1,2)]
            if any(not(0<=lx<w and 0<=ly<h) for lx,ly in ribbon):continue
            qs=np.array([hsv[ly,lx] for lx,ly in ribbon]);vs=np.array([value[ly,lx] for lx,ly in ribbon],float)
            endmin=float(min(value[y,x],value[ty,tx]));center=np.array([value[ly,lx] for lx,ly in line],float)
            neutral=np.all(qs[:,1]<=.25)
            hd=abs((qs[:,0]-hsv[y,x,0]+.5)%1-.5)*360
            color=bool(np.quantile(hd,.9)<8 and np.ptp(qs[:,1])<.28) if not neutral else bool(np.max(qs[:,1])<.18)
            # Broad bridge, bounded saddle: proximity never sufficient.
            shallow=bool(center.min()>=max(100,.60*endmin,endmin-75) and np.quantile(vs,.1)>=max(90,.50*endmin))
            strong=color and shallow and len(line)>=2
            rec=dict(ids=[regions[i]['id'],regions[j]['id']],distance=float(np.linalg.norm(peaks[i]-peaks[j])),bridge_min_dn=float(center.min()),ribbon_p10_dn=float(np.quantile(vs,.1)),color_compatible=color,shallow_broad_bridge=shallow,decision='suppress' if strong else 'uncertain-alternatives')
            evidence.append(rec)
            if strong:
                removed.add(j);r=regions[j];r.update(status='suppressed',suppressed_by=regions[i]['id'],suppression_reason='inferior-quality-maximum; compatible broad bright bridge with bounded saddle');r['bright_patch'].update(status='suppressed',reason=r['suppression_reason']);suppressed.append(r)
    return winners,suppressed,evidence


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
    meaningful=h_maxima(value,p.recovery_prominence_dn if p.recover_peaks else p.prominence_dn,footprint=np.ones((3,3))) if value.max()>value.min() else np.zeros_like(value)
    significant=set(np.unique(markers[meaningful.astype(bool)]))-{0}
    high=h_maxima(value,p.prominence_dn,footprint=np.ones((3,3))) if p.recover_peaks else meaningful
    strong_ids=set(np.unique(markers[high.astype(bool)]))-{0}
    peak_slices=ndi.find_objects(markers)
    m=max(1,round(min(h,w)*p.border_fraction));border=np.zeros((h,w),bool)
    border[:m]=border[-m:]=True;border[:,:m]=border[:,-m:]=True
    background_model,paper_stop,paper_uncertain=background_maps(hsv,border)
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
                       prominence_lower_bound_dn=(p.prominence_dn if owner in strong_ids else p.recovery_prominence_dn if owner in significant else 0),recovered_low_prominence=owner not in strong_ids and owner in significant,seed_hsv=(hsv[y,x]*[360,1,1]).tolist(),plateau_pixel_count=len(xx),plateau_centroid=[float(xx.mean()+ps[1].start),float(yy.mean()+ps[0].start)],
                       plateau_runs=runs(markers[ps]==owner,ps[1].start,ps[0].start))
        if owner not in significant or int(value[y,x])<p.minimum_peak_dn:
            candidate.update(status='rejected',reason='below-prominence' if owner not in significant else 'below-minimum-peak',patch_centroid=candidate['plateau_centroid'],patch_runs=candidate['plateau_runs'])
            maxima.append(candidate);continue
        if p.first_dark_stop and int(value[y,x])==0:
            candidate.update(status='rejected',reason='first-dark-seed',patch_centroid=candidate['plateau_centroid'],patch_runs=candidate['plateau_runs'])
            maxima.append(candidate);continue
        if (p.background_precheck and obvious_background(hsv,x,y,background_model)) or (p.background_guard and np.all(paper_stop[max(0,y-1):y+2,max(0,x-1):x+2]) and abs(hsv[y,x,2]-background_model["center"][2])<=background_model["tolerance"][2]):
            candidate.update(status='rejected',reason='obvious-background-before-growth',patch_centroid=candidate['plateau_centroid'],patch_runs=candidate['plateau_runs'])
            maxima.append(candidate);continue
        mask,trace=grow(value,hsv,(x,y),p,valleys=valleys,paper=paper_stop if p.background_guard else None)
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
        if not reasons and p.background_guard:
            # Direct photographic context only: uncertain seed chroma + nearby
            # learned paper, or substantial accepted contamination => defer.
            neighborhood=paper_stop[max(0,y-12):y+13,max(0,x-12):x+13]
            contamination=float(np.mean(paper_uncertain[ya:yb,xa:xb][mask]))
            near_paper=float(np.mean(neighborhood))
            record['background_evidence']=dict(uncertain_fraction=contamination,nearby_paper_fraction=near_paper)
            if (paper_uncertain[y,x] and near_paper>.08) or (contamination>.35 and near_paper>.08):
                record.update(status='deferred',deferred_reason='uncertain-paper-boundary')
        if not reasons and candidate['recovered_low_prominence']:
            # Small weak proposals stay reviewable; no automatic acceptance from
            # lowering prominence alone.
            if record['pixel_count']<12:
                record.update(status='deferred',deferred_reason='weak-recovery-support')
        candidate.update(status=record['status'],reason=';'.join(reasons) or record.get('deferred_reason','ambiguous-candidate'))
        maxima.append(candidate)
        (rejected if reasons else regions).append(record)
        if not reasons:
            target=labels[ya:yb,xa:xb];count=coverage[ya:yb,xa:xb]
            target[mask & (count==0)]=owner
            target[mask & (count>0)]=-1
            count[mask]+=1
    split_evidence=[]
    if p.split_regions:
        eligible=[tuple(m['peak']) for m in maxima if m['meaningful']]
        for r in regions:
            x0,y0,x1,y1=r['bbox'];inside=[q for q in eligible if x0<=q[0]<x1 and y0<=q[1]<y1]
            if len(inside)<2:continue
            mask=np.zeros((y1-y0,x1-x0),bool)
            for yy,aa,bb in r['pixel_runs']:mask[yy-y0,aa-x0:bb-x0+1]=True
            children=split_supported_mask(mask,value,hsv,(x0,y0),inside)
            if children:
                r.update(status='deferred',deferred_reason='split-supported-pieces-use-independent-maxima')
                split_evidence.append(dict(parent_id=r['id'],children=children,reason='native-dark-valley; independently seeded pieces',decision='parent deferred; independent original maxima remain eligible'))
    deferred=[r for r in regions if r['status']=='deferred']
    regions=[r for r in regions if r['status']=='retained']
    suppressed=[];associations=[]
    if p.peak_selection:regions,suppressed,associations=associate(regions,value,hsv,p)
    # Rebuild selection arrays: deferred/suppressed pixels are not accepted beads.
    labels.fill(0);coverage.fill(0)
    for r in regions:
        for y,a,b in r['pixel_runs']:
            q=coverage[y,a:b+1];labels[y,a:b+1]=np.where(q>0,-1,int(r['id'][1:]));q+=1
    for record in regions:
        overlap=sum(int(np.count_nonzero(coverage[y,a:b+1]>1)) for y,a,b in record['pixel_runs'])
        record['overlap_pixel_count']=overlap
        if overlap:record['ambiguity'].append('overlapping-independent-supports')
    return dict(version=VERSION,parameters=asdict(p),width=w,height=h,maxima=maxima,regions=regions,rejected=rejected,deferred=deferred,suppressed=suppressed,associations=associations,split_evidence=split_evidence,
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
        precheck_rejected=sum(m['reason']=='obvious-background-before-growth' for m in data['maxima']),raw_maxima=len(data['maxima']),meaningful_maxima=sum(m['meaningful'] for m in data['maxima']),deferred=len(data['deferred']),suppressed=len(data['suppressed']),grown_maxima=sum(len(data[k]) for k in ('regions','rejected','deferred','suppressed')),regions=len(sizes),
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
        for r in data['regions']+data['rejected']+data['deferred']+data['suppressed']:writer.writerow([r['id'],r['status'],*r['location'],*r['centroid'],r['pixel_count'],r['kind']])
    with (output/'rank-size.csv').open('w') as f:
        f.write('rank,region_id,pixel_count\n')
        for i,r in enumerate(sorted(data['regions'],key=lambda r:-r['pixel_count']),1):f.write(f'{i},{r["id"]},{r["pixel_count"]}\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4));ax.hist(sizes,bins=edges,color='#008caa');ax.set(xlabel='Native pixels per retained support',ylabel='Regions',title='R266 region sizes (not bead areas)');fig.tight_layout();fig.savefig(output/'size-distribution.png',dpi=150);plt.close(fig)
    print(json.dumps(summary,indent=2),flush=True)
    return data


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    ap.add_argument('--output',type=Path,default=ROOT/'photo2/output/r266/annular-2-joint')
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
