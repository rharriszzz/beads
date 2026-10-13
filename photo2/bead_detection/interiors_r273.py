"""Image-only R273 ownership and interior refinement. No review inputs or models."""
from dataclasses import dataclass,asdict
from collections import Counter
from copy import deepcopy
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.morphology import disk,convex_hull_image
from skimage.measure import perimeter_crofton
from matplotlib.colors import rgb_to_hsv
from .brightness_r270 import linearize,encode
from .climb_r268 import background
from .inventory_r272 import component,measure,hue_distance,CROSS
from .coverage_r272 import complete,detect as baseline_detect
from .annular_detect import straight_pixels

@dataclass(frozen=True)
class Parameters:
    method:str='star-valley'
    radius:int=26
    hue_degrees:float=22.
    step_hue_degrees:float=12.
    floor_fraction:float=.15
    valley_fraction:float=.08
    valley_retreat:int=0
    opening_radius:int=2
    retreat:int=1
    uncertain_bridge:bool=False
    minimum_area:int=45
    minimum_solidity:float=.88
    maximum_area:int=870
    black_radius:float=12.
    black_rule:str='margin'
    secondary_peak_ratio:float=.75
    secondary_contrast_ratio:float=.85

SELECTED=Parameters(method='relative-valley',radius=32,floor_fraction=.035,hue_degrees=32,step_hue_degrees=18,valley_fraction=.25,valley_retreat=1,retreat=2,minimum_solidity=.84)

REASONS={
'black-secondary':'A stronger nearby reflection wins the peak/contrast comparison; this weaker reflection is retained only for diagnosis.',
'black-ambiguous':'Nearby reflections have similar strength or uncertain ownership; the entire close group is withheld.',
'interior-open':'Supported growth reaches the context limit or exceeds the 870-pixel pre-cleanup ceiling.',
'interior-small':'Too little broad interior remains after removing unsupported edges and narrow protrusions.',
'interior-peak-lost':'Cleanup cannot keep the starting bright point confidently interior.',
'interior-holes':'An unsupported hole prevents a single confident interior.',
'interior-irregular':'This growth rule produced a deeply indented region; ownership remains unresolved. This does not establish that photographic support is absent.',
'interior-rival':'Growth reaches another automatically detected bright point; ownership is unresolved.',
'interior-overlap':'Two proposed interiors overlap; both are withheld rather than partitioned or merged.'}

def pixels(rec,key='region'):
    return {(x,y) for y,a,b in rec[key]['runs'] for x in range(a,b+1)}

def shape(mask):
    area=int(mask.sum())
    if not area:return dict(area=0,solidity=0.,perimeter=0.,perimeter_per_sqrt_area=0.)
    perimeter=float(perimeter_crofton(mask,4));hull=int(convex_hull_image(mask).sum())
    return dict(area=area,solidity=area/hull,perimeter=perimeter,perimeter_per_sqrt_area=perimeter/area**.5)

def black_ownership(rows,native,srgb,p=Parameters()):
    """No transitive merging; ambiguous clusters are excluded, never partitioned."""
    black=[r for r in rows if r['color']=='black'];xy=np.array([[r['brightest']['x'],r['brightest']['y']] for r in black]);edges=[]
    if len(black)<2:return edges
    hs=rgb_to_hsv(native/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);_,paper,_=background(native);adj=[set() for _ in black];supports=[pixels(r) for r in black]
    for i,j in sorted(cKDTree(xy).query_pairs(p.black_radius)):
        path=straight_pixels(tuple(xy[i]),tuple(xy[j]));between=[(x,y) for x,y in path if (x,y) not in supports[i]|supports[j]]
        clear=all(paper[y,x]==0 and encode(lum[y,x])<=.40 and (hs[y,x,1]<=.55 or hs[y,x,1]*hs[y,x,2]<=.14) for x,y in between)
        edge=dict(a=black[i]['id'],b=black[j]['id'],distance=float(np.linalg.norm(xy[i]-xy[j])),dark_bridge=clear,path=[[int(v) for v in z] for z in path]);edges.append(edge)
        # Every close pair enters competition. A clear intervening barrier does
        # not justify suppressing a weaker peak on a possibly different body.
        adj[i].add(j);adj[j].add(i)
    seen=set()
    for i in range(len(black)):
        if i in seen or not adj[i]:continue
        group={i};todo=[i]
        while todo:
            k=todo.pop()
            for j in adj[k]-group:group.add(j);todo.append(j)
        seen|=group
        ranked=sorted(group,key=lambda k:(-black[k]['brightest']['luminance'],-black[k]['confidence']['peak_shell_value_contrast'],black[k]['id']));winner=ranked[0];ids=[black[k]['id'] for k in ranked];diameter=float(max(np.linalg.norm(xy[a]-xy[b]) for a in group for b in group))
        group_edges=[e for e in edges if e['a'] in ids and e['b'] in ids];peak=black[winner]['brightest']['luminance'];contrast=black[winner]['confidence']['peak_shell_value_contrast'];clear=diameter<=p.black_radius and all(e['dark_bridge'] for e in group_edges)
        dominant=all(black[k]['brightest']['luminance']<=p.secondary_peak_ratio*peak and black[k]['confidence']['peak_shell_value_contrast']<=p.secondary_contrast_ratio*contrast for k in ranked[1:])
        keep=p.black_rule=='winner' or (p.black_rule=='margin' and clear and dominant)
        for k in ranked:
            rec=black[k];rec['black_ownership']=dict(group=ids,winner=black[winner]['id'] if keep else None,diameter=diameter,dark_bridge=clear,dominant=dominant,rule=p.black_rule,peak_ratio_to_strongest=rec['brightest']['luminance']/peak,contrast_ratio_to_strongest=rec['confidence']['peak_shell_value_contrast']/contrast)
            if not keep or k!=winner:rec['accepted']=False;rec['reasons'].append('black-secondary' if keep else 'black-ambiguous')
            else:rec.setdefault('warnings',[]).append('Nearby weaker reflections suppressed by an image-only ownership heuristic; a distinct close bead can also be lost.')
    return edges

def background_allowance(pp,hs,l,native_v,hue,highlight,floor,enabled):
    """Only textured, color-supported uncertainty within three native pixels."""
    background_ok=pp==0
    if enabled:
        texture=ndi.maximum_filter(native_v,5)-ndi.minimum_filter(native_v,5)
        consistent=(hs[:,:,1]>=.25)&(hue_distance(hs[:,:,0]*360,hue)<=12)
        strong=(pp==0)&consistent&(l>=floor)
        near=ndi.distance_transform_edt(~strong)<=3 if strong.any() else np.zeros_like(strong)
        bridge=(pp==2)&near&(texture>=32)&(consistent|highlight)
        background_ok=background_ok|bridge
    return background_ok

def colored_interior(old,native,srgb,hsv,lum,mean3,paper,p=Parameters()):
    rec=deepcopy(old);rec['reasons']=[];rec['accepted']=False;rec['r272_measurements']={k:deepcopy(old[k]) for k in ('brightest','bright_patch','region')}
    for k in ('region','bright_patch','outline','brightest','interior_attempts','stops'):rec.pop(k,None)
    x,y=old['brightest']['x'],old['brightest']['y'];r=p.radius
    if min(x,y,lum.shape[1]-1-x,lum.shape[0]-1-y)<r:
        rec['reasons']=['interior-open'];return rec
    origin=(x-r,y-r);cut=np.s_[y-r:y+r+1,x-r:x+r+1];l=lum[cut];m=mean3[cut];hs=hsv[cut];pp=paper[cut];peak=float(l[r,r]);hue=old['color_evidence']['hue'];yy,xx=np.mgrid[-r:r+1,-r:r+1]
    chromatic=(hs[:,:,1]>=.20)&(hue_distance(hs[:,:,0]*360,hue)<=p.hue_degrees)
    highlight=(xx*xx+yy*yy<=64)&(hs[:,:,1]<.20)&(l>=.60*peak)
    background_ok=background_allowance(pp,hs,l,native[cut].max(axis=2).astype(float),hue,highlight,max(.008,p.floor_fraction*peak),p.uncertain_bridge)
    rec['interior_attempts']=[]
    for floor in ([p.floor_fraction] if p.method=='relative-valley' else sorted(set([p.floor_fraction,.25,.35,.50]))):
        allowed=(chromatic|highlight)&background_ok&(l>=max(.008,floor*peak));allowed &= ~((hs[:,:,1]<.20)&(encode(l)<.32))
        grown=component(allowed,(r,r));stops=Counter()
        if p.method in ('first-valley','relative-valley'):
            # Follow native paths all the way to an image-derived barrier, then
            # retreat to the first supported trough before a substantial rise.
            # One open direction must not brighten the cutoff in every direction.
            visible=np.zeros_like(grown);ray_records=[]
            perimeter=[(ax,ay) for ay in range(2*r+1) for ax in range(2*r+1) if ax in (0,2*r) or ay in (0,2*r)]
            for tx,ty in perimeter:
                path=[];minimum=float(m[r,r]);minimum_index=0;last=(r,r);reason='context-limit'
                for ax,ay in straight_pixels((r,r),(tx,ty)):
                    if not allowed[ay,ax]:
                        reason='background' if not background_ok[ay,ax] else 'brightness-floor' if l[ay,ax]<max(.008,floor*peak) else 'neutral-dark' if hs[ay,ax,1]<.20 and encode(l[ay,ax])<.32 else 'color-boundary'
                        break
                    a=hs[last[1],last[0]];b=hs[ay,ax]
                    if min(a[1],b[1])>=.30 and hue_distance(a[0]*360,b[0]*360)>p.step_hue_degrees:reason='hue-boundary';break
                    value=float(m[ay,ax])
                    valley=(minimum<.60*peak and value>minimum+max(.003,p.valley_fraction*minimum)) if p.method=='relative-valley' else value>minimum+max(.006,p.valley_fraction*peak)
                    if valley:
                        path=path[:max(1,minimum_index+1-p.valley_retreat)];reason='first-valley';break
                    path.append((ax,ay))
                    if value<minimum:minimum=value;minimum_index=len(path)-1
                    last=(ax,ay)
                stops[reason]+=1
                for ax,ay in path:visible[ay,ax]=True
                ray_records.append(dict(target=[tx+origin[0],ty+origin[1]],end=[path[-1][0]+origin[0],path[-1][1]+origin[1]] if path else None,reason=reason,pixels=len(path),trigger=[ax+origin[0],ay+origin[1]],trigger_luminance=float(l[ay,ax]),trigger_mean3=float(m[ay,ax]),running_minimum_mean3=minimum,peak_luminance=peak))
            grown=component(visible,(r,r));rec['direction_stops']=ray_records
        elif p.method!='connected':
            visible=np.zeros_like(grown)
            for ty,tx in zip(*np.where(grown)):
                running=float(m[r,r]);last=(r,r);reason=None
                for ax,ay in straight_pixels((r,r),(int(tx),int(ty))):
                    if not allowed[ay,ax]:reason='unsupported-pixel';break
                    a=hs[last[1],last[0]];b=hs[ay,ax]
                    if min(a[1],b[1])>=.30 and hue_distance(a[0]*360,b[0]*360)>p.step_hue_degrees:reason='hue-boundary';break
                    if p.method=='star-valley' and m[ay,ax]>running+max(.006,p.valley_fraction*peak):reason='brightness-valley';break
                    running=min(running,float(m[ay,ax]));last=(ax,ay)
                if reason:stops[reason]+=1
                else:visible[ty,tx]=True
            grown=component(visible,(r,r))
        opened=ndi.binary_opening(grown,structure=disk(p.opening_radius));clean=ndi.binary_erosion(opened,CROSS,iterations=p.retreat) if p.retreat else opened;clean=component(clean,(r,r))
        open_region=bool(grown[0].any() or grown[-1].any() or grown[:,0].any() or grown[:,-1].any());rec['interior_attempts'].append(dict(floor_fraction=floor,supported_pixels=int(grown.sum()),clean_pixels=int(clean.sum()),context_open=open_region,stops=dict(stops)))
        if not open_region and grown.sum()<=p.maximum_area:break
    rec['background_continuation']=dict(enabled=p.uncertain_bridge,supported_uncertain_pixels=int(np.sum(grown&(pp==2))),retained_uncertain_pixels=int(np.sum(clean&(pp==2))),confident_paper_pixels=int(np.sum(clean&(pp==1))))
    rec['supported_region']=measure(grown,origin);rec['support_parameters']=asdict(p);rec['shape']=shape(clean);rec['old_shape']=shape(mask_local(old['region']))
    if open_region or grown.sum()>p.maximum_area:rec['reasons'].append('interior-open')
    if clean.sum()<p.minimum_area:rec['reasons'].append('interior-small')
    if not clean[r,r]:rec['reasons'].append('interior-peak-lost')
    if np.any(ndi.binary_fill_holes(clean)&~clean):rec['reasons'].append('interior-holes')
    if rec['shape']['solidity']<p.minimum_solidity:rec['reasons'].append('interior-irregular')
    if clean.any():complete(rec,clean,origin,native,srgb,hsv,lum)
    rec['warnings']=['Photographically supported interior, not a recovered physical bead boundary.','Opening and inward retreat only remove pixels; displayed contour smoothing does not change measurements.']
    return rec

def mask_local(region):
    box=region['bbox'];m=np.zeros((box[3]-box[1]+4,box[2]-box[0]+4),bool)
    for y,a,b in region['runs']:m[y-box[1]+2,a-box[0]+2:b-box[0]+3]=True
    return m

def refine(native,srgb,base,p=SELECTED):
    hsv=rgb_to_hsv(srgb/255.);lum=linearize(srgb/255.)@np.array([.2126,.7152,.0722]);mean3=ndi.uniform_filter(lum,3);_,paper,_=background(native);records=[]
    for old in base:
        if old['color']=='black':rec=deepcopy(old);rec['reasons']=[];rec['accepted']=True
        else:rec=colored_interior(old,native,srgb,hsv,lum,mean3,paper,p)
        records.append(rec)
    edges=black_ownership(records,native,srgb,p)
    # Other observed R272 peaks are barriers even if their new region fails.
    rivals=[(b['id'],b['brightest']['x'],b['brightest']['y']) for b in base]
    for rec in records:
        if not rec['accepted'] or rec['color']=='black':continue
        support=pixels(rec);inside=[id for id,x,y in rivals if id!=rec['id'] and (x,y) in support]
        rec['interior_rivals']=inside
        if inside:rec['accepted']=False;rec['reasons'].append('interior-rival')
    owners={};conflicts=set()
    for i,rec in enumerate(records):
        if not rec['accepted']:continue
        for point in pixels(rec):
            if point in owners:conflicts.add(i);conflicts.add(owners[point])
            else:owners[point]=i
    for i in conflicts:records[i]['accepted']=False;records[i]['reasons'].append('interior-overlap')
    beads=[]
    for r in records:
        r['explanations']=[REASONS[k] for k in r['reasons']]
        if r['accepted']:
            r['inventory_number']=len(beads)+1;r['acceptance_reasons']=['Image-only R272 location/color/ICC brightness evidence.','Native closed reflection support survives conservative close-reflection competition.' if r['color']=='black' else 'Broad connected native support survives photographic guards, removal-only cleanup, shape and ownership checks.'];beads.append(r)
    colored=[r for r in beads if r['color']!='black'];ratios=[r['region']['pixel_count']/r['r272_measurements']['region']['pixel_count'] for r in colored]
    summary=dict(parameters=asdict(p),accepted=len(beads),colors=dict(Counter(r['color'] for r in beads)),reasons=dict(Counter(k for r in records for k in r['reasons'])),colored_area_median=float(np.median([r['region']['pixel_count'] for r in colored])) if colored else None,paired_area_ratio_median=float(np.median(ratios)) if ratios else None,colored_larger=sum(a>1 for a in ratios),colored_count=len(colored),paired_boundary_metric_median=float(np.median([r['shape']['perimeter_per_sqrt_area']/r['old_shape']['perimeter_per_sqrt_area'] for r in colored])) if colored else None)
    return beads,records,edges,summary

def detect(native,srgb=None,p=SELECTED):
    if srgb is None:srgb=native
    base,*_=baseline_detect(native,srgb)
    return refine(native,srgb,base,p)
