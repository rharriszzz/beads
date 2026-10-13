"""R274 native color boundaries. Runtime input is pixels and automatic proposals."""
from dataclasses import dataclass,asdict
from copy import deepcopy
from collections import Counter
import numpy as np
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv
from skimage.morphology import disk
from .brightness_r270 import linearize,encode
from .climb_r268 import background
from .inventory_r272 import component,measure,hue_distance,circular_mean,CROSS
from .coverage_r272 import complete,detect as candidates
from .interiors_r273 import SELECTED as OLD,refine as old_refine,pixels,shape,REASONS
from .annular_detect import straight_pixels

@dataclass(frozen=True)
class Parameters:
    rule:str='contrast'
    hue_limit:float=32.
    step_limit:float=18.
    palette_margin:float=4.
    drift_limit:float=22.
    contrast_limit:float=10.
    chroma_min:float=.055
    highlight_bridge:bool=False

VARIANTS={'r273':Parameters(rule='baseline'),
          'seed-hue18':Parameters(rule='seed',hue_limit=18,step_limit=10),
          'palette':Parameters(rule='palette'),
          'contrast':Parameters(),
          'seed-palette':Parameters(rule='seed-palette',palette_margin=2.),
          'highlight-palette':Parameters(rule='seed-palette',palette_margin=2.,highlight_bridge=True),
          'local-contrast':Parameters(rule='local-contrast',palette_margin=2.),
          'path-contrast':Parameters(rule='path-contrast',contrast_limit=12.,drift_limit=26.)}

SELECTED=VARIANTS['highlight-palette']

def palette_from(base):
    # Prototypes already learned independently of review crops by R272.
    result={}
    for color in ('red','yellow'):
        vals=[r['color_evidence']['prototype']['hue'] for r in base if r['color']==color and 'prototype' in r['color_evidence']]
        if vals:result[color]=float(circular_mean(np.array(vals)))
    return result

def color_surface(hsv):
    weights=hsv[:,:,1]*hsv[:,:,2]*(hsv[:,:,1]>=.20);angle=hsv[:,:,0]*2*np.pi
    a=ndi.uniform_filter(weights*np.cos(angle),3);b=ndi.uniform_filter(weights*np.sin(angle),3);w=ndi.uniform_filter(weights,3)
    return (np.arctan2(b,a)*180/np.pi)%360,np.hypot(a,b)/np.maximum(w,1e-12),w

def grow(old,native,srgb,hsv,lum,mean3,paper,surface,palette,p):
    rec=deepcopy(old);rec['accepted']=False;rec['reasons']=[]
    rec['source_location']=deepcopy(old['brightest']);rec['source_patch']=deepcopy(old['bright_patch'])
    for key in ('region','outline','brightest','bright_patch'):rec.pop(key,None)
    x,y=old['brightest']['x'],old['brightest']['y'];r=OLD.radius;origin=(x-r,y-r)
    if min(x,y,lum.shape[1]-1-x,lum.shape[0]-1-y)<r:rec['reasons']=['interior-open'];return rec
    cut=np.s_[y-r:y+r+1,x-r:x+r+1];hs=hsv[cut];l=lum[cut];m=mean3[cut];pp=paper[cut];local_h,coherence,weight=[v[cut] for v in surface];peak=float(l[r,r]);seed_h=float(old['color_evidence']['hue']);yy,xx=np.mgrid[-r:r+1,-r:r+1]
    chromatic=(hs[:,:,1]>=.20)&(hue_distance(hs[:,:,0]*360,seed_h)<=p.hue_limit)
    highlight=(xx*xx+yy*yy<=64)&(hs[:,:,1]<.20)&(l>=.60*peak)
    if p.highlight_bridge:
        body=(hs[:,:,1]>=.35)&(hue_distance(hs[:,:,0]*360,seed_h)<=18)&(pp==0)
        near=ndi.distance_transform_edt(~body)<=6 if body.any() else np.zeros_like(body)
        highlight=(xx*xx+yy*yy<=64)&(hs[:,:,1]<.35)&(l>=max(.04,.20*peak))&near
    reliable=(hs[:,:,1]>=(.35 if p.highlight_bridge else .20))&(hs[:,:,1]*hs[:,:,2]>=p.chroma_min)
    local_reliable=(weight>=p.chroma_min)&(coherence>=.85)
    own=seed_h if p.rule in ('seed-palette','local-contrast','path-contrast') else palette.get(old['color'],seed_h);other=palette.get('yellow' if old['color']=='red' else 'red')
    competitive=p.rule in ('palette','contrast','seed-palette','local-contrast') and other is not None
    native_margin=hue_distance(hs[:,:,0]*360,other)-hue_distance(hs[:,:,0]*360,own) if other is not None else np.full(l.shape,180.)
    local_margin=hue_distance(local_h,other)-hue_distance(local_h,own) if other is not None else np.full(l.shape,180.)
    color_ok=~reliable|(native_margin>=p.palette_margin) if competitive else np.ones(l.shape,bool)
    floor=max(.008,OLD.floor_fraction*peak)
    allowed=(chromatic|highlight)&(pp==0)&(l>=floor)&~((hs[:,:,1]<.20)&(encode(l)<.32))&color_ok
    visible=np.zeros_like(allowed);traces=[];stops=Counter()
    for tx,ty in [(ax,ay) for ay in range(2*r+1) for ax in range(2*r+1) if ax in (0,2*r) or ay in (0,2*r)]:
        route=straight_pixels((r,r),(tx,ty));path=[];minimum=float(m[r,r]);minimum_index=0;last=(r,r);reason='context-limit';history=[]
        for index,(ax,ay) in enumerate(route):
            if not allowed[ay,ax]:
                reason='background' if pp[ay,ax] else 'brightness-floor' if l[ay,ax]<floor else 'rival-hue' if not color_ok[ay,ax] else 'neutral-dark' if hs[ay,ax,1]<.20 and encode(l[ay,ax])<.32 else 'seed-hue'
                break
            a=hs[last[1],last[0]];b=hs[ay,ax]
            if min(a[1],b[1])>=.30 and hue_distance(a[0]*360,b[0]*360)>p.step_limit:reason='hue-step';break
            if p.rule in ('contrast','local-contrast') and local_reliable[ay,ax]:
                # Evidence is saturation-weighted; neutral highlights never create
                # a fabricated hue. Compare local drift and a native look-ahead.
                if local_margin[ay,ax]<p.palette_margin:reason='local-rival-hue';break
                if p.rule=='contrast' and hue_distance(local_h[ay,ax],seed_h)>p.drift_limit:reason='hue-drift';break
                if index>=3 and index+2<len(route):
                    bx,by=route[index-3];fx,fy=route[index+2]
                    if local_reliable[by,bx] and local_reliable[fy,fx] and hue_distance(local_h[by,bx],local_h[fy,fx])>=p.contrast_limit and local_margin[fy,fx]<local_margin[by,bx]-p.contrast_limit and local_margin[fy,fx]<p.palette_margin+8:
                        reason='across-boundary-hue';break
            if p.rule=='path-contrast' and local_reliable[ay,ax] and b[1]>=.25:
                # Spatial contrast distinguishes a color interface from slow
                # within-bead hue shading. No global palette membership cut.
                if index>=3 and index+2<len(route):
                    bx,by=route[index-3];fx,fy=route[index+2]
                    delta=float(hue_distance(local_h[by,bx],local_h[fy,fx]))
                    toward=local_margin[fy,fx]<local_margin[by,bx]-8
                    if local_reliable[by,bx] and local_reliable[fy,fx] and toward and delta>=p.contrast_limit and hue_distance(local_h[fy,fx],seed_h)>=8:
                        reason='across-boundary-hue';break
                    if local_reliable[by,bx] and local_margin[ay,ax]<-p.palette_margin and local_margin[by,bx]<0 and hue_distance(local_h[ay,ax],seed_h)>=p.drift_limit:
                        reason='sustained-hue-drift';break
            value=float(m[ay,ax])
            if minimum<.60*peak and value>minimum+max(.003,OLD.valley_fraction*minimum):path=path[:max(1,minimum_index+1-OLD.valley_retreat)];reason='first-valley';break
            path.append((ax,ay))
            if value<minimum:minimum=value;minimum_index=len(path)-1
            last=(ax,ay)
        stops[reason]+=1
        for ax0,ay0 in path:visible[ay0,ax0]=True
        traces.append(dict(target=[tx+origin[0],ty+origin[1]],end=[path[-1][0]+origin[0],path[-1][1]+origin[1]] if path else None,trigger=[ax+origin[0],ay+origin[1]],reason=reason,pixels=len(path),luminance=float(l[ay,ax]),mean3=float(m[ay,ax]),hue=float(hs[ay,ax,0]*360),saturation=float(hs[ay,ax,1]),local_hue=float(local_h[ay,ax]),native_palette_margin=float(native_margin[ay,ax]),local_palette_margin=float(local_margin[ay,ax])))
    grown=component(visible,(r,r));clean=component(ndi.binary_erosion(ndi.binary_opening(grown,structure=disk(OLD.opening_radius)),CROSS,iterations=OLD.retreat),(r,r))
    rec.update(supported_region=measure(grown,origin),shape=shape(clean),color_parameters=asdict(p),palette=palette,seed_hue=seed_h,stops=dict(stops),direction_stops=traces)
    if grown[0].any() or grown[-1].any() or grown[:,0].any() or grown[:,-1].any() or grown.sum()>OLD.maximum_area:rec['reasons'].append('interior-open')
    if clean.sum()<OLD.minimum_area:rec['reasons'].append('interior-small')
    if not clean[r,r]:rec['reasons'].append('interior-peak-lost')
    if np.any(ndi.binary_fill_holes(clean)&~clean):rec['reasons'].append('interior-holes')
    if rec['shape']['solidity']<OLD.minimum_solidity:rec['reasons'].append('interior-irregular')
    if clean.any():complete(rec,clean,origin,native,srgb,hsv,lum)
    rec['warnings']=['Photographic interior proposal, not a recovered physical boundary.','Native mask measured separately from smoothed display contour.']
    return rec

def refine(native,srgb,base,old_records=None,p=SELECTED):
    if old_records is None:old_records=old_refine(native,srgb,base)[1]
    old_map={r['id']:r for r in old_records};hsv=rgb_to_hsv(srgb/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);mean3=ndi.uniform_filter(lum,3);_,paper,_=background(native);surface=color_surface(hsv);palette=palette_from(base)
    rows=[deepcopy(old_map[b['id']]) if b['color']=='black' or p.rule=='baseline' else grow(b,native,srgb,hsv,lum,mean3,paper,surface,palette,p) for b in base]
    rivals=[(b['id'],b['brightest']['x'],b['brightest']['y']) for b in base]
    for r in rows:
        if not r['accepted'] or r['color']=='black':continue
        support=pixels(r);r['interior_rivals']=[id for id,x,y in rivals if id!=r['id'] and (x,y) in support]
        if r['interior_rivals']:r['reasons'].append('interior-rival');r['accepted']=False
    # Freeze accepted black-reflection ownership: a new colored conflict with one
    # of these cores withholds only the colored region, not its location.
    owner={};bad=set()
    for i,r in sorted(enumerate(rows),key=lambda z:z[1]['color']!='black'):
        if not r['accepted']:continue
        for pt in pixels(r):
            if pt in owner:
                bad.add(i)
                if rows[owner[pt]]['color']!='black':bad.add(owner[pt])
            else:owner[pt]=i
    for i in bad:rows[i]['accepted']=False;rows[i]['reasons'].append('interior-overlap')
    beads=[];locations=[]
    for r in rows:
        old=old_map[r['id']];r['explanations']=[REASONS[k] for k in r['reasons']];r['interior_status']='accepted' if r['accepted'] else 'uncertain';r['location_status']='trusted' if old['accepted'] or r['accepted'] else 'proposal'
        # A previously supported location is retained unchanged even if new
        # boundaries fail. Interior peak and location coordinate stay distinct.
        if r['location_status']=='trusted':
            reference=old if old['accepted'] else r
            loc=dict(id=r['id'],color=r['color'],inventory_number=len(locations)+1,point=deepcopy(reference['brightest']),bright_patch=deepcopy(reference['bright_patch']),interior_status=r['interior_status'],reasons=r['reasons'],explanations=r['explanations'],source='image-only R273' if old['accepted'] else 'image-only R274',location_confidence=deepcopy(reference.get('confidence',{})))
            r['inventory_number']=loc['inventory_number'];locations.append(loc)
        if r['accepted']:beads.append(r)
    summary=dict(parameters=asdict(p),palette=palette,interiors=len(beads),colors=dict(Counter(b['color'] for b in beads)),locations=len(locations),location_colors=dict(Counter(b['color'] for b in locations)),locations_without_interior=sum(r['interior_status']!='accepted' for r in locations),reasons=dict(Counter(k for r in rows for k in r['reasons'])))
    return beads,locations,rows,summary

def detect(native,srgb=None,p=SELECTED):
    if srgb is None:srgb=native
    base=candidates(native,srgb)[0]
    return refine(native,srgb,base,p=p)
