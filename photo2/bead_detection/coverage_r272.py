"""R272 coverage experiment. Runtime inputs are RGB pixels and fixed parameters only.

No reference coordinates, historical detections, truth, count target or geometry.
Raw luminance maxima feed the black pathway; mean7 maxima feed colored search.
"""
from dataclasses import dataclass,asdict
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import local_maxima
from matplotlib.colors import rgb_to_hsv
from .brightness_r270 import linearize,encode,SCALE,sums,Search
from .search_r269 import Policy
from .climb_r268 import background
from .inventory_r272 import hue_distance,circular_mean,component,measure,outline,features,learn_palette,CROSS
from .annular_detect import straight_pixels

@dataclass(frozen=True)
class Parameters:
    minimum_mean_y:float=.04
    minimum_lit_fraction:float=.45
    minimum_core_pixels:int=6
    minimum_window_ratio:float=.35
    minimum_contrast:float=.12
    background_clearance:int=1
    hue_tolerance:float=18.
    minimum_colored_core_fraction:float=.40
    minimum_region_pixels:int=12
    minimum_black_pixels:int=3
    maximum_pixels:int=870
    context_radius:int=24
    black_maximum_value:float=.32
    black_peak_value:float=.22
    black_contrast:float=.12
    black_surround_fraction:float=.50
    black_signal:str='icc-gray'
    black_sigma:float=0.
    colored_floor:float=.32
    raw_rise_allowance:float=.02
    black_enabled:bool=True

EXPLANATIONS={
'context':'The image edge prevents checking the surround.',
'background':'The candidate touches established paper evidence.',
'dim':'The neighborhood has too little measurable luminance.',
'illumination':'Too little of the local neighborhood supports the bright point.',
'patch':'The bright patch has too few supporting pixels.',
'window':'The signal disappears in the larger measurement window.',
'contrast':'The peak is too weak relative to its local surround.',
'color':'The image-derived color evidence is ambiguous or outside red/yellow.',
'black-color':'The peak is too chromatic to establish a black reflection.',
'black-contrast':'The reflection does not stand out from surrounding darkness.',
'black-open':'There is no complete dark enclosing perimeter before a neighbor or the analysis limit.',
'black-material':'The enclosing material lacks sufficient dark low-chroma evidence.',
'black-size':'The reflection support is too small, too broad, or has uncertain holes.',
'better-peak':'A guarded broader search reaches a better peak; its original maximum remains in the inventory.',
'region-small':'Too little connected interior survives the native brightness and color checks.',
'region-open':'The interior reaches the analysis limit or the established 870-pixel ceiling.',
'region-holes':'Uncertain holes prevent a single confident interior outline.',
'peak-lost':'The peak is not safely interior after retreat.',
'duplicate-support':'This maximum describes the same overlapping reflection/interior as the retained stronger proposal.',
'ownership-conflict':'Overlapping proposals have incompatible colors; neither is accepted.',
'nearby-rival':'Distinct nearby highlights lack sufficient evidence of separate bead ownership.'}

def peak_pixel(lum,mask,origin):
    yy,xx=np.where(mask&(lum==lum[mask].max()));j=np.lexsort((xx,yy))[0];return int(xx[j]+origin[0]),int(yy[j]+origin[1])

def maxima_rows(score,prefix):
    mask=local_maxima(score,connectivity=2,allow_borders=True)&(score>=0)
    lab,n=ndi.label(mask,np.ones((3,3)));rows=[]
    for i,sl in enumerate(ndi.find_objects(lab),1):
        yy,xx=np.where(lab[sl]==i);yy+=sl[0].start;xx+=sl[1].start
        j=min(range(len(xx)),key=lambda k:((xx[k]-xx.mean())**2+(yy[k]-yy.mean())**2,int(yy[k]),int(xx[k])))
        rows.append(dict(id=f'{prefix}-{int(xx[j]):04d}-{int(yy[j]):04d}',anchor=[int(xx[j]),int(yy[j])],plateau_pixels=np.c_[xx,yy].astype(int).tolist(),reasons=[],accepted=False,pathway='black' if prefix=='K' else 'colored'))
    return rows,mask

def complete(rec,mask,origin,native,srgb,hsv,lum,patch_fraction=.85):
    cut=np.s_[origin[1]:origin[1]+mask.shape[0],origin[0]:origin[0]+mask.shape[1]];l=lum[cut];x,y=peak_pixel(l,mask,origin);seed=(x-origin[0],y-origin[1]);peak=float(l[seed[1],seed[0]])
    patch=component(mask&(l>=peak*patch_fraction),seed)
    rec.update(region=measure(mask,origin),bright_patch=measure(patch,origin),outline=outline(mask,origin),brightest=dict(x=x,y=y,luminance=peak,rgb_native=native[y,x].tolist(),rgb_srgb=srgb[y,x].tolist(),hsv_srgb=dict(zip(('h','s','v'),(hsv[y,x]*[360,1,1]).tolist())),hsv_native=dict(zip(('h','s','v'),(rgb_to_hsv(native[y,x]/255)*[360,1,1]).tolist())),scope='absolute maximum ICC luminance of the accepted measured native interior; y,x ties',ties=int(np.sum(mask&(l==peak)))))
    rec['accepted']=not rec['reasons']

def black_region(rec,native,srgb,hsv,nhsv,lum,paper,p):
    x,y=rec['anchor'];r=p.context_radius;cut=np.s_[y-r:y+r+1,x-r:x+r+1];hs=nhsv[cut];l=lum[cut];pp=paper[cut]
    v=hs[:,:,2] if p.black_signal=='native-v' else encode(l)
    if p.black_sigma:v=ndi.gaussian_filter(v,p.black_sigma)
    peak=float(v[r,r]);level=min(p.black_maximum_value,.60*peak)
    rec['color']='black';rec['dark_threshold_v']=level
    if hsv[y,x,1]>.55:rec['reasons'].append('black-color')
    if peak<p.black_peak_value:rec['reasons'].append('black-contrast')
    if paper[y,x]:rec['reasons'].append('background')
    if rec['reasons']:return
    # No blur, rays or skipped gaps: first 8-connected above-dark component.
    labels,_=ndi.label(v>level,np.ones((3,3)));label=labels[r,r];core=labels==label if label else np.zeros_like(v,bool)
    shell=ndi.binary_dilation(core,np.ones((3,3)))&~core
    closed=bool(core.any() and not(core[0].any() or core[-1].any() or core[:,0].any() or core[:,-1].any()) and shell.any() and np.all(v[shell]<=level))
    rec['dark_perimeter']=dict(closed=closed,core_pixels=int(core.sum()),runs=measure(shell,(x-r,y-r))['runs'],maximum_value=float(v[shell].max()) if shell.any() else None,signal=p.black_signal,sigma=p.black_sigma,threshold=level,linear_luminance_threshold=float(linearize(level)) if p.black_signal=='icc-gray' else None)
    if not closed or core.sum()>p.maximum_pixels:rec['reasons'].append('black-open');return
    neutral=(hs[:,:,1]<=.45)|(hs[:,:,1]*hs[:,:,2]<=.10)
    fraction=float(np.mean(neutral[shell]));contrast=peak-float(np.median(v[shell]));paper_fraction=float(np.mean(pp[core|shell]>0));colored_core=float(np.mean(hsv[cut][:,:,1][core]>.55))
    rec['confidence'].update(dark_neutral_shell_fraction=fraction,peak_shell_value_contrast=contrast,paper_fraction=paper_fraction,chromatic_core_fraction=colored_core)
    if fraction<p.black_surround_fraction or colored_core>.25:rec['reasons'].append('black-material')
    if contrast<p.black_contrast:rec['reasons'].append('black-contrast')
    if paper_fraction:rec['reasons'].append('background')
    # Retain the reflection component, never add enclosing dark pixels or fill holes.
    mask=component(core,(r,r))
    if mask.sum()<p.minimum_black_pixels or mask.sum()>220 or np.any(ndi.binary_fill_holes(mask)&~mask):rec['reasons'].append('black-size')
    if mask.any():complete(rec,mask,(x-r,y-r),native,srgb,hsv,lum)
    rec['warnings']=['Reflection support only; not the whole black bead.','Dark material evidence is photographic, not a calibrated material probability.']

def colored_region(rec,native,srgb,hsv,lum,paper,p,hue):
    x,y=rec['anchor'];r=p.context_radius;origin=(x-r,y-r);cut=np.s_[y-r:y+r+1,x-r:x+r+1];l=lum[cut];hs=hsv[cut];pp=paper[cut];yy,xx=np.mgrid[-r:r+1,-r:r+1]
    color=(hue_distance(hs[:,:,0]*360,hue)<=p.hue_tolerance)&(hs[:,:,1]>=.25)
    core=(abs(xx)<=4)&(abs(yy)<=4)&(pp==0)&(color|(hs[:,:,1]<.25))
    if not core.any():rec['reasons'].append('color');return
    gx,gy=peak_pixel(l,core,origin);sx,sy=gx-origin[0],gy-origin[1];peak=float(l[sy,sx]);neutral=(xx*xx+yy*yy<=36)&(hs[:,:,1]<.25)&(l>=.80*peak)
    rec['interior_attempts']=[]
    for fraction in sorted(set([p.colored_floor,.45,.60,.75])):
        allowed=(color|neutral)&(pp==0)&(l>=max(.008,fraction*peak))
        pathmask=np.zeros_like(allowed);stops=Counter()
        for ty,tx in zip(*np.where(allowed)):
            running=peak;reason=None
            for ax,ay in straight_pixels((sx,sy),(int(tx),int(ty))):
                if not allowed[ay,ax]:reason='color-background-floor';break
                if l[ay,ax]>running+p.raw_rise_allowance:reason='native-valley';break
                running=min(running,float(l[ay,ax]))
            if reason:stops[reason]+=1
            else:pathmask[ty,tx]=True
        before=component(pathmask,(sx,sy));mask=component(ndi.binary_erosion(before,CROSS),(sx,sy));rec['stops']=dict(stops)
        open_region=bool(before[0].any() or before[-1].any() or before[:,0].any() or before[:,-1].any())
        rec['interior_attempts'].append(dict(floor_fraction=fraction,pre_retreat_pixels=int(before.sum()),pixels=int(mask.sum()),open=open_region))
        # Try a brighter observed interior if the broader one cannot establish
        # a bounded support. No invented pixels, arbitrary geometric clipping or
        # relaxation of the pre-retreat 870-pixel ceiling.
        if before.sum()<=p.maximum_pixels and not open_region:break
    if before.sum()>p.maximum_pixels or before[0].any() or before[-1].any() or before[:,0].any() or before[:,-1].any():rec['reasons'].append('region-open')
    if mask.sum()<p.minimum_region_pixels:rec['reasons'].append('region-small')
    if not mask[sy,sx]:rec['reasons'].append('peak-lost')
    if np.any(ndi.binary_fill_holes(mask)&~mask):rec['reasons'].append('region-holes')
    rec['confidence']['pre_retreat_pixels']=int(before.sum());rec['warnings']=['Interior under declared photographic guards, not an estimated full bead boundary.']
    if mask.any():complete(rec,mask,origin,native,srgb,hsv,lum)

def select_nonoverlap(rows,lum):
    eligible=sorted((r for r in rows if r['accepted']),key=lambda r:(-r['brightest']['luminance'],r['id']));owners={};kept=[]
    for rec in eligible:
        pixels={(x,y) for y,a,b in rec['region']['runs'] for x in range(a,b+1)};others={owners[pt] for pt in pixels if pt in owners}
        if others:
            matches=[kept[j] for j in sorted(others)]
            # Overlap or matching color alone cannot establish bead identity.
            # Suppression requires the SAME brightest native pixel. Otherwise
            # preserve both candidates as an unresolved ownership conflict.
            same=all(r['accepted'] and r['color']==rec['color'] and
                     (r['brightest']['x'],r['brightest']['y'])==
                     (rec['brightest']['x'],rec['brightest']['y']) for r in matches)
            reason='duplicate-support' if same else 'ownership-conflict';rec['reasons'].append(reason);rec['accepted']=False;rec['competing_ids']=[r['id'] for r in matches]
            if not same:
                for m in matches:m['accepted']=False;m['reasons'].append(reason)
            continue
        # Mere distance is never enough to merge identities. Separate disjoint
        # supports within 6px remain unresolved and are both withheld.
        close=[m for m in kept if m['accepted'] and np.hypot(rec['brightest']['x']-m['brightest']['x'],rec['brightest']['y']-m['brightest']['y'])<=6]
        if close:
            rec['accepted']=False;rec['reasons'].append('nearby-rival')
            for m in close:m['accepted']=False;m['reasons'].append('nearby-rival')
        j=len(kept);kept.append(rec)
        for pt in pixels:owners[pt]=j
    return rows

def detect(native,srgb=None,p=Parameters(),progress=None):
    if srgb is None:srgb=native
    nhsv,paper,model=background(native);hsv=rgb_to_hsv(srgb/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);q=np.rint(lum*255*SCALE).astype(np.int64);ss={n:sums(q,n) for n in (5,7,9)}
    colored,cm=maxima_rows(ss[7],'C');black,bm=maxima_rows(q,'K') if p.black_enabled else ([],np.zeros_like(cm));h,w=lum.shape;rows=colored+black;traces=[]
    fs=[]
    for rec in colored:
        x,y=rec['anchor']
        if min(x,y,w-1-x,h-1-y)>=max(21,p.context_radius+1) and paper[y,x]==0:
            f=features(hsv,lum,paper,x,y);fs.append(f)
    palette=learn_palette(fs)
    yy,xx=np.mgrid[-12:13,-12:13];ann=(xx*xx+yy*yy>=64)&(xx*xx+yy*yy<=144)
    for i,rec in enumerate(rows):
        x,y=rec['anchor'];rec['confidence']=dict(raw_y=float(lum[y,x]),mean5_y=float(ss[5][y,x]/(25*SCALE*255)),mean7_y=float(ss[7][y,x]/(49*SCALE*255)),mean9_y=float(ss[9][y,x]/(81*SCALE*255)))
        if min(x,y,w-1-x,h-1-y)<max(21,p.context_radius+1):rec['reasons'].append('context');continue
        if rec['pathway']=='black':black_region(rec,native,srgb,hsv,nhsv,lum,paper,p);continue
        mean=rec['confidence']['mean7_y'];patch=lum[y-4:y+5,x-4:x+5];contrast=(mean-float(np.median(lum[y-12:y+13,x-12:x+13][ann])))/max(mean,1e-12);lit=float(np.mean(patch>=.5*mean));core=int(np.sum(patch>=.8*mean));ratio=rec['confidence']['mean9_y']/max(rec['confidence']['mean5_y'],1e-12);br=p.background_clearance
        rec['confidence'].update(local_contrast=contrast,lit_fraction=lit,core_pixels=core,window_ratio=ratio,background_pixels=int(np.sum(paper[y-br:y+br+1,x-br:x+br+1]>0)))
        for failed,reason in [(mean<p.minimum_mean_y,'dim'),(lit<p.minimum_lit_fraction,'illumination'),(core<p.minimum_core_pixels,'patch'),(ratio<p.minimum_window_ratio,'window'),(contrast<p.minimum_contrast,'contrast'),(rec['confidence']['background_pixels']>0,'background')]:
            if failed:rec['reasons'].append(reason)
        if rec['reasons']:continue
        f=features(hsv,lum,paper,x,y);hue=f['hue'];d=sorted((float(hue_distance(hue,c['hue'])),j) for j,c in enumerate(palette)) if hue is not None else []
        rec['color_features']=f
        if not d or d[0][0]>16 or (len(d)>1 and d[1][0]-d[0][0]<6) or f['color_samples']<10 or f['colored_core_fraction']<p.minimum_colored_core_fraction or f['hue_deviation90']>22 or palette[d[0][1]]['name'] is None:rec['reasons'].append('color');continue
        rec['color']=palette[d[0][1]]['name'];rec['color_evidence']=dict(**f,prototype=palette[d[0][1]],distance=d[0][0])
        cut=np.s_[y-21:y+22,x-21:x+22];ends=[];searches=[]
        for n in (5,7,9):
            g=Search(q[cut],nhsv[cut],paper[cut],ss[n][cut],n,(21,21),'Y');policy=Policy(24,2);result=g.search(16,policy);path=g.path(result['pred'],result['end']);g.audit_path(path,16,policy);end=(g.xy[result['end']]+[x-21,y-21]).astype(int).tolist();ends.append(end)
            for step in path:step['x']+=x-21;step['y']+=y-21
            searches.append(dict(window=n,endpoint=end,path=path,floors=list(g.floors(policy))))
            if n==7:rec['primary_endpoint']=end
        traces.append(dict(id=rec['id'],searches=searches));rec['confidence']['window_endpoint_spread']=float(max(np.linalg.norm(np.array(a)-b) for a in ends for b in ends))
        if rec['primary_endpoint']!=[x,y]:rec['reasons'].append('better-peak');continue
        colored_region(rec,native,srgb,hsv,lum,paper,p,hue)
        if rec['confidence']['window_endpoint_spread']>3:
            rec.setdefault('warnings',[]).append('5/7/9 measurement windows disagree by more than 3 pixels; retained interior is local, not a physical center.')
        if progress and len(traces)%200==0:progress('searched',len(traces))
    select_nonoverlap(rows,lum)
    beads=[]
    for rec in sorted(rows,key=lambda r:(r['anchor'][1],r['anchor'][0],r['id'])):
        rec['explanations']=[EXPLANATIONS[k] for k in rec['reasons']]
        if rec['accepted']:
            rec['inventory_number']=len(beads)+1;rec['acceptance_reasons']=['Image-derived peak and color/background evidence.','Connected native interior and distinct retained support.','Complete dark perimeter around a compact reflection.' if rec['pathway']=='black' else 'ICC luminance mean7 peak survives guarded radius16 search; native brightness/color paths stop and retreat before uncertainty.'];beads.append(rec)
    return beads,rows,traces,dict(parameters=asdict(p),palette=palette,background_model=model,raw_maxima=len(black),mean7_maxima=len(colored),accepted=len(beads),colors=dict(Counter(r['color'] for r in beads)),reasons=dict(Counter(k for r in rows for k in r['reasons']))),dict(raw=bm,mean7=cm)
