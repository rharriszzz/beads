"""R262: native brightest-first growth without spatial ownership partitions.

Only RGB enters detection. Each maximum grows independently; overlapping supports
remain explicit rather than imposing another partition. Every non-root accepted
pixel has an adjacent earlier predecessor. All thresholds are unchanged from R261.
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
VERSION = 'r262-monotone-no-partition-v1'
N8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]

@dataclass(frozen=True)
class Parameters:
    prominence_dn: int = 10
    patch_drop_dn: int = 10
    retreat_fraction: float = .30
    retreat_dn: int = 2
    dark_dn: int = 81
    reflection_drop_dn: int = 36
    hue_stop_deg: float = 20.
    reliable_saturation: float = .35
    saturation_drop: float = .40
    min_support: int = 3
    border_fraction: float = .035


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


def grow(value, hsv, seed, p=Parameters(), offset=(0,0)):
    """Single-pixel priority queue, all 8 neighbors, no positive noise tolerance.

    Queue ceiling is monotonically nonincreasing. Failed destinations are locked
    per region, not per path. No ownership map participates in eligibility.
    Equality is allowed without accumulating an uphill tolerance. Trace stores all accepted pixels and ALL directed frontier stops.
    """
    h,w = value.shape; sx,sy = seed; x0,y0 = offset
    seen = {} # sparse native pixels: missing unseen, 1 queued, 2 accepted, -1 locked
    anchors = {}; incoming = {}; queue = []; accepted = []; stops = []
    ceiling = int(value[sy,sx]); peak = ceiling
    heapq.heappush(queue,(-ceiling,sy,sx,-1)); seen[sy,sx]=1
    def chromatic(q): return q[1]>=p.reliable_saturation and q[2]>=.20 and q[1]*q[2]>=.08
    def stop(x,y,prev,reason):
        q=hsv[y,x]
        stops.append([x+x0,y+y0,prev,int(value[y,x]),float(q[0]*360),float(q[1]),float(q[2]),reason,len(accepted)])
    while queue:
        neg,y,x,prev = heapq.heappop(queue)
        if seen.get((y,x),0) == -1: continue
        v = int(value[y,x])
        if v > ceiling:
            seen[y,x]=-1;stop(x,y,prev,'global-rise-lock');continue
        ceiling=v
        index=len(accepted);seen[y,x]=2
        q=hsv[y,x]; anchor=anchors.get((y,x))
        if anchor is None and chromatic(q): anchor=q.copy()
        # x,y,predecessor acceptance index,V DN,H degrees,S,V normalized,keep
        accepted.append([x+x0,y+y0,prev,v,float(q[0]*360),float(q[1]),float(q[2]),True])
        incoming.pop((y,x),None)
        for dy,dx in N8:
            ny,nx=y+dy,x+dx
            if not (0<=ny<h and 0<=nx<w): continue
            if seen.get((ny,nx),0) == 2: continue
            nv=int(value[ny,nx]); nq=hsv[ny,nx]; reason=None
            if nv>v: reason='brightness-rise'
            elif nv<=p.dark_dn and peak-nv>=p.reflection_drop_dn: reason='dark-frontier'
            elif anchor is not None and chromatic(nq) and min(abs(float(nq[0]-anchor[0])),1-abs(float(nq[0]-anchor[0])))*360>=p.hue_stop_deg: reason='relative-hue-change'
            elif anchor is not None and float(anchor[1]-nq[1])>=p.saturation_drop and nv<peak-p.patch_drop_dn: reason='saturation-loss'
            if reason:
                # A later approach cannot reopen this pixel, even if already queued.
                if seen.get((ny,nx),0)!=-1:
                    seen[ny,nx]=-1
                    for pending in incoming.pop((ny,nx),[]):
                        stop(nx,ny,pending,'destination-locked-by-other-path')
                stop(nx,ny,index,reason)
            elif seen.get((ny,nx),0)==-1: stop(nx,ny,index,'previously-locked')
            elif seen.get((ny,nx),0)==0:
                seen[ny,nx]=1;anchors[(ny,nx)]=anchor;incoming[(ny,nx)]=[index]
                heapq.heappush(queue,(-nv,ny,nx,index))
            elif seen.get((ny,nx),0)==1: incoming[(ny,nx)].append(index)
    # Per-branch retreat: deepest accepted/terminal dark Value propagates up the
    # predecessor tree; every node on a dark tail is removable, even on the bead.
    lows=np.array([a[3] for a in accepted],dtype=float)
    for s in stops:
        if s[2]>=0 and s[7]=='dark-frontier': lows[s[2]]=min(lows[s[2]],s[3])
    for i in range(len(accepted)-1,0,-1):
        prev=accepted[i][2];lows[prev]=min(lows[prev],lows[i])
    # Crop storage AFTER growth. This bounding box never restricts eligibility.
    mx=min(a[0] for a in accepted);my=min(a[1] for a in accepted)
    ex=max(a[0] for a in accepted)+1;ey=max(a[1] for a in accepted)+1
    mask=np.zeros((ey-my,ex-mx),bool)
    for i,a in enumerate(accepted):
        threshold=lows[i]+max(p.retreat_dn,p.retreat_fraction*(peak-lows[i]))
        # Preserve the actual peak plateau; all other tails retreat strictly.
        keep=a[3]==peak or (a[3]>threshold and accepted[a[2]][7])
        a[7]=bool(keep)
        if keep: mask[a[1]-my,a[0]-mx]=True
    return mask, dict(accepted_columns=['x','y','predecessor','value_dn','hue_deg','saturation','value','retained'],
                     stop_columns=['x','y','predecessor','value_dn','hue_deg','saturation','value','reason','after_accept_count'],
                     accepted=accepted,stops=stops,retreat_floor_dn=lows.tolist(),mask_offset=[mx,my])


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
        if owner not in significant:
            candidate.update(status='rejected',reason='below-prominence',patch_centroid=candidate['plateau_centroid'],patch_runs=candidate['plateau_runs'])
            maxima.append(candidate);continue
        mask,trace=grow(value,hsv,(x,y),p)
        xa,ya=trace['mask_offset'];yb=ya+mask.shape[0];xb=xa+mask.shape[1]
        accepted_mask=np.zeros(mask.shape,bool)
        for a in trace['accepted']:accepted_mask[a[1]-ya,a[0]-xa]=True
        patch=accepted_mask & (value[ya:yb,xa:xb]>=int(value[y,x])-p.patch_drop_dn)
        pm=measure(patch,xa,ya);candidate.update(patch_centroid=pm['centroid'],patch_runs=runs(patch,xa,ya),patch_pixel_count=pm['pixel_count'])
        dark=enclosure(x,y) if int(value[y,x])>=p.dark_dn+p.reflection_drop_dn else None
        # Large connected bright structures are not compact reflection evidence.
        dark_ok=dark is not None and dark['meaningful_maxima']==[owner]
        reasons=[]
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
                    stop_count=len(trace['stops']),trace_file=f'traces/{rid}.json.gz')
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
                background=dict(chromaticity=paper.tolist(),tolerance=tolerance),
                namespaces='P = raw-maximum support; M = raw maximum. Match generation IDs for masks. Neither is a bead index.',
                label_schema='0 unretained; positive unique P ID; -1 overlap. Exact per-region runs retain all memberships.',
                unexpanded_maxima_reason='below-prominence; equal-valued plateau saved, no growth attempted',
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
        raw_maxima=len(data['maxima']),meaningful_maxima=sum(m['meaningful'] for m in data['maxima']),regions=len(sizes),
        ambiguous_candidates=len(sizes),rejected_candidates=sum(m['status']=='rejected' for m in data['maxima']),
        low_prominence=sum(not m['meaningful'] for m in data['maxima']),rejected_grown=len(data['rejected']),
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
    fig,ax=plt.subplots(figsize=(8,4));ax.hist(sizes,bins=edges,color='#008caa');ax.set(xlabel='Native pixels per retained support',ylabel='Regions',title='R262 region sizes (not bead areas)');fig.tight_layout();fig.savefig(output/'size-distribution.png',dpi=150);plt.close(fig)
    print(json.dumps(summary,indent=2),flush=True)
    return data


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg');ap.add_argument('--output',type=Path,default=ROOT/'photo2/output/detection-r262');ap.add_argument('--retreat-fraction',type=float,default=.30);ap.add_argument('--retreat-dn',type=int,default=2);a=ap.parse_args()
    if not 0<=a.retreat_fraction<1 or a.retreat_dn<0:ap.error('Retreat fraction must be [0,1); DN must be nonnegative')
    generate(a.image,a.output,Parameters(retreat_fraction=a.retreat_fraction,retreat_dn=a.retreat_dn))

if __name__=='__main__':main()
