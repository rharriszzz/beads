"""Photo-only generation. No imports from reconstruction experiments/annotations.

python -m photo2.bead_debugger.generate --output photo2/output/debugger/generated
"""
from __future__ import annotations
import argparse, contextlib, hashlib, io, json, os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-debugger-mpl')
import numpy as np
from PIL import Image, ImageOps
from matplotlib.colors import rgb_to_hsv
from scipy import ndimage as ndi
from scipy.interpolate import splprep, splev
from scipy.signal import find_peaks
from scipy.spatial import cKDTree
from .vendor.historical_splines import _run_image_only_hsv_mode

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'r256-interiors-v1'
PARAMS = dict(border_fraction=.035, hue_bins=360, hue_smoothing_deg=2.,
              saturation_floor=.25, value_floor=.18, core_radius_px=2.,
              peak_separation_px=9., min_patch_pixels=12, valley_fraction=.12,
              max_peak_neighborhood_px=65, reflection_contrast=.20)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def circular_distance(a,b): return abs((np.asarray(a)-b+180)%360-180)

def spline_from_photo(rgb):
    params=json.loads((Path(__file__).parent/'vendor/PROVENANCE.json').read_text())['parameters']
    with contextlib.redirect_stdout(io.StringIO()) as trace:
        raw=_run_image_only_hsv_mode(rgb,Path('beads-photo-2.jpg'),None,**params)
    if any(raw[k] is None for k in ['inner_spline','outer_spline','centerline_spline']):
        raise RuntimeError('Incomplete regenerated spline; refusing archived fallback')
    if 'PARTIAL' in trace.getvalue(): raise RuntimeError('Historical tracer returned a partial loop')
    points=np.array(raw['centerline_spline'],float)[:-1]
    area=np.sum(points[:,0]*np.roll(points[:,1],-1)-points[:,1]*np.roll(points[:,0],-1))
    if area<0: points=points[::-1]
    points=np.vstack((points,points[0]))
    tck,_=splprep(points.T,s=len(points)*2.**2,per=True,k=3)
    u=np.linspace(0,1,2049); center=np.array(splev(u,tck)).T
    d=np.array(splev(u,tck,der=1)).T; d/=np.linalg.norm(d,axis=1)[:,None]
    return dict(raw=raw,centerline=center.tolist(),tangents=d.tolist(),
                smoothing_rms_target_pixels=2.,parameters=params,
                provenance='Photo replay of historical HSV-calibrated boundary algorithm; no bead labels; not palette-independent'),trace.getvalue()

def learn_palette(rgb):
    hsv=rgb_to_hsv(rgb); h,s,v=np.moveaxis(hsv,-1,0); h=h*360
    H,W=h.shape; m=max(1,round(min(H,W)*PARAMS['border_fraction']))
    border=np.zeros((H,W),bool); border[:m]=True; border[-m:]=True; border[:,:m]=True; border[:,-m:]=True
    valid=(s>PARAMS['saturation_floor'])&(v>PARAMS['value_floor'])
    bins=np.minimum(h.astype(int),359)
    bg=ndi.gaussian_filter1d(np.bincount(bins[border&valid],minlength=360).astype(float),2,mode='wrap')
    bg_mode=int(bg.argmax()); bd=circular_distance(h[border&valid],bg_mode)
    bg_width=float(np.clip(np.percentile(bd,99) if len(bd) else 12,6,35))
    # Peak locations come entirely from this image, after generic framed-paper sampling.
    pool=valid&(v>float(np.quantile(v,.98))*.65)&(circular_distance(h,bg_mode)>bg_width+3)
    hist=ndi.gaussian_filter1d(np.bincount(bins[pool],minlength=360).astype(float),2,mode='wrap')
    peaks,_=find_peaks(np.tile(hist,3),distance=15,prominence=max(10,hist.max()*.015))
    peaks=peaks[(peaks>=360)&(peaks<720)]-360
    chosen=sorted(peaks,key=lambda j:-hist[j])[:4]; groups=[]
    for peak in chosen:
        if circular_distance(peak,bg_mode)<=bg_width+4: continue
        # Naming only: these broad semantic names do not set the mask or its hue bounds.
        name=min([('red',350),('yellow',45)],key=lambda pair:circular_distance(peak,pair[1]))[0] if min(circular_distance(peak,350),circular_distance(peak,45))<45 else 'other'
        if name=='other' or any(g['color']==name for g in groups): continue
        radius=2
        while radius<22 and hist[(peak-radius)%360]>.5*hist[peak] and hist[(peak+radius)%360]>.5*hist[peak]: radius+=1
        radius=min(radius,max(3,int(circular_distance(peak,bg_mode)-bg_width-2)))
        groups.append(dict(color=name,hue_deg=int(peak),radius_deg=int(radius),peak_pixels=float(hist[peak])))
    if not groups: raise RuntimeError('No separate chromatic modes found; detector will not import old color ranges')
    return hsv,dict(background_hue_deg=bg_mode,background_radius_deg=bg_width,groups=groups,histogram=hist.tolist())

def profile(rgb, a, b):
    p=np.linspace(a,b,65)
    c=np.column_stack([ndi.map_coordinates(rgb[:,:,i],[p[:,1],p[:,0]],order=1) for i in range(3)])
    value=c.max(axis=1); edge=min(float(np.mean(value[:3])),float(np.mean(value[-3:])))
    valley=float(np.min(ndi.gaussian_filter1d(value,1)[len(value)//4:3*len(value)//4]))
    return dict(endpoints=[list(a),list(b)],value=value.round(5).tolist(),
                chroma=(c.max(axis=1)-c.min(axis=1)).round(5).tolist(),
                valley_fraction=float((edge-valley)/max(edge,.001)),
                reason='Straight line between colored interior maxima; intervening pixels remain unassigned')

def detect(rgb, image_hash):
    hsv,palette=learn_palette(rgb); hue=hsv[:,:,0]*360; sat=hsv[:,:,1]; value=hsv[:,:,2]
    rows=[]; masks=np.zeros(rgb.shape[:2],np.uint16); split_pairs=[]
    for group in palette['groups']:
        mask=(circular_distance(hue,group['hue_deg'])<=group['radius_deg'])&(sat>PARAMS['saturation_floor'])&(value>PARAMS['value_floor'])
        labels,n=ndi.label(mask)
        slices=ndi.find_objects(labels)
        for ci,sl in enumerate(slices,1):
            comp=labels[sl]==ci; area=int(comp.sum())
            if area<3: continue
            y0,x0=sl[0].start,sl[1].start
            # Padding makes distance to the component boundary correct even at crop edges.
            dist=ndi.distance_transform_edt(np.pad(comp,1))[1:-1,1:-1]
            score=ndi.gaussian_filter(value[sl]*comp,1)*np.minimum(dist,8)
            maxima=(score==ndi.maximum_filter(score,size=9))&comp&(dist>=PARAMS['core_radius_px'])
            yy,xx=np.where(maxima); ordered=sorted(zip(yy,xx),key=lambda p:(-score[p],p))
            seeds=[]
            for y,x in ordered:
                if all(np.hypot(x-p[1],y-p[0])>=PARAMS['peak_separation_px'] for p in seeds): seeds.append((int(y),int(x)))
            if not seeds:
                y,x=np.unravel_index(np.argmax(score),score.shape); seeds=[(int(y),int(x))]
            # No dark seams are assigned: support consists only of eroded positive colored pixels.
            yy,xx=np.where(comp&(dist>=1.5)); pixels=np.c_[xx,yy]
            if len(pixels): owners=cKDTree(np.array(seeds)[:,::-1]).query(pixels)[1]
            else: owners=np.array([],int)
            local=[]
            for j,(y,x) in enumerate(seeds):
                patch=pixels[owners==j]; support=len(patch); X,Y=x+x0,y+y0
                ident=f'I256-{image_hash[:8]}-{group["color"][0].upper()}-{X:04d}-{Y:04d}'
                status='interior' if support>=PARAMS['min_patch_pixels'] and dist[y,x]>=2 else 'small-patch'
                if area<12 or support<3: status='rejected'
                row=dict(id=ident,color=group['color'],x=X,y=Y,kind='colored-interior',evidence_class=status,
                         component=f'{group["color"]}-{ci}',component_area=area,patch_area=support,
                         interior_radius_px=float(dist[y,x]),hsv=[float(z) for z in hsv[Y,X]],
                         patch=(patch[::max(1,len(patch)//160)]+[x0,y0]).tolist(),
                         centroid=(patch.mean(axis=0)+[x0,y0]).tolist() if len(patch) else None,
                         physical_center=None,bead_index=None,split_evidence=[],
                         reason='Independent colored interior; not a certified distinct physical bead')
                local.append(row);rows.append(row)
                if len(patch): masks[patch[:,1]+y0,patch[:,0]+x0]=len(rows)
            for i,a in enumerate(local):
                for b in local[i+1:]:
                    if np.hypot(a['x']-b['x'],a['y']-b['y'])>PARAMS['max_peak_neighborhood_px']: continue
                    ev=profile(rgb,[a['x'],a['y']],[b['x'],b['y']])
                    credible=ev['valley_fraction']>=PARAMS['valley_fraction'] and min(a['patch_area'],b['patch_area'])>=12
                    pair=dict(a=a['id'],b=b['id'],credible_split_evidence=credible,**ev);split_pairs.append(pair)
                    for row in [a,b]:
                        row['split_evidence'].append(len(split_pairs)-1)
                        if not credible and row['evidence_class']!='rejected': row['evidence_class']='ambiguous-split'
    # Reflection-plus-dark-surround evidence; never create a black bead from an empty index.
    smooth=ndi.gaussian_filter(value,1); surround=ndi.uniform_filter(value,17)
    maxima=(smooth==ndi.maximum_filter(smooth,13))&(smooth-surround>PARAMS['reflection_contrast'])&(smooth>.52)
    yy,xx=np.where(maxima)
    for y,x in zip(yy,xx):
        if x<12 or y<12 or x>=rgb.shape[1]-12 or y>=rgb.shape[0]-12: continue
        ys,xs=np.mgrid[y-10:y+11,x-10:x+11]; radius=np.hypot(xs-x,ys-y); ring=(radius>=4)&(radius<=10)
        dark=value[y-10:y+11,x-10:x+11]<.24; fraction=float(dark[ring].mean())
        if fraction<.55: continue
        rr=rgb[y-10:y+11,x-10:x+11]; chrom=rr.max(axis=2)-rr.min(axis=2)
        if np.median(chrom[ring])>.12: continue
        rows.append(dict(id=f'I256-{image_hash[:8]}-B-{x:04d}-{y:04d}',x=int(x),y=int(y),color='black?',
                         kind='reflection-on-dark-body',evidence_class='black-candidate',patch=[],patch_area=0,
                         physical_center=None,bead_index=None,split_evidence=[],
                         dark_annulus_fraction=fraction,reflection_contrast=float(smooth[y,x]-surround[y,x]),
                         reason='Bright local maximum with dark low-chroma surround; reflection, not body center; needs review'))
    return dict(version=VERSION,image_sha256=image_hash,parameters=PARAMS,palette=palette,observations=rows,split_pairs=split_pairs,
                exclusions='No historical positions, adjacency, classifications, spline coordinates, fitted model or review decisions are inputs'),masks

def generate(image,output):
    image=Path(image);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(image)).convert('RGB'),dtype=np.float32)/255
    image_hash=sha(image)
    splines,trace=spline_from_photo(rgb);save(output/'splines.json',splines);(output/'spline-trace.txt').write_text(trace)
    inventory,masks=detect(rgb,image_hash);save(output/'observations.json',inventory)
    np.savez_compressed(output/'positive-patches.npz',labels=masks)
    sources={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(__file__).parent/'vendor/historical_splines.py',Path(__file__).parent/'vendor/PROVENANCE.json']}
    manifest=dict(schema=1,image_sha256=image_hash,image_size=[rgb.shape[1],rgb.shape[0]],detector_version=VERSION,sources=sources,
                  artifacts={p.name:sha(p) for p in sorted(output.iterdir()) if p.name in ['splines.json','observations.json','positive-patches.npz']})
    manifest['generation_id']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    save(output/'manifest.json',manifest)
    return manifest

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg');ap.add_argument('--output',type=Path,default=ROOT/'photo2/output/debugger/generated')
    a=ap.parse_args();print(json.dumps(generate(a.image,a.output),indent=2))
