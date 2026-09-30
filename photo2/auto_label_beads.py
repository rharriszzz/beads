"""Image-derived whole-photo bead/neighbor proposals, not confirmed string indices.

Manual labels are optional evaluator data and are read ONLY after detect() and
adjacency(). The input image supplies background, palette, scale and strip axis.
Live maker annotations are never written. No physical-necklace measurements.
"""
import argparse,hashlib,json,os,uuid
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-auto-mpl')
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from scipy.spatial import cKDTree
from scipy.optimize import linear_sum_assignment
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.measure import regionprops
from skimage.morphology import skeletonize
from skimage.segmentation import watershed
from matplotlib.colors import rgb_to_hsv
from label_beads import DIRECTIONS,validate_annotations,validate_series

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def small_components(mask,minimum):
    labels,_=ndi.label(mask);sizes=np.bincount(labels.ravel())
    keep=sizes>=minimum;keep[0]=False
    return keep[labels]


def fill_small_holes(mask,maximum):
    labels,_=ndi.label(~mask);sizes=np.bincount(labels.ravel())
    border=np.unique(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]])
    fill=sizes<=maximum;fill[border]=False;fill[0]=False
    return mask|fill[labels]


def strip_axis(band):
    """Prune skeleton spurs; preserve the supported closed image-strip route.

    This approximate image axis is not a measured physical centerline or bead
    index closure. Fail explicitly if a unique simple cycle is unsupported.
    """
    sk=skeletonize(band);pixels=set(map(tuple,np.argwhere(sk)))
    adj={p:[] for p in pixels}
    for y,x in pixels:
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                if not dx and not dy:continue
                q=(y+dy,x+dx)
                if q not in pixels:continue
                if dx and dy and ((y,x+dx) in pixels or (y+dy,x) in pixels):continue
                adj[(y,x)].append(q)
    keep=set(pixels);leaves=[p for p in keep if len(adj[p])<2]
    while leaves:
        p=leaves.pop()
        if p not in keep:continue
        keep.remove(p)
        for q in adj[p]:
            if q in keep and sum(r in keep for r in adj[q])<2:leaves.append(q)
    if not keep or any(sum(q in keep for q in adj[p])!=2 for p in keep):
        raise ValueError('Strip skeleton does not have a supported unique simple cycle; retain uncertainty, do not invent a route.')
    start=min(keep);route=[start];previous=None;current=start
    while True:
        following=next(q for q in sorted(adj[current]) if q in keep and q!=previous)
        if following==start:break
        route.append(following);previous,current=current,following
        if len(route)>len(keep):raise ValueError('Failed to trace the image-strip cycle')
    if len(route)!=len(keep):raise ValueError('Multiple strip cycles; do not silently discard regions')
    xy=np.array(route,float)[:,::-1]
    area=np.sum(xy[:,0]*np.roll(xy[:,1],-1)-xy[:,1]*np.roll(xy[:,0],-1))
    if area<0:xy=xy[::-1]
    xy=np.concatenate([xy,xy[:1]])
    distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]
    stations=np.arange(0,distance[-1],1.)
    xy=np.column_stack([np.interp(stations,distance,xy[:,a]) for a in [0,1]])
    dt=ndi.distance_transform_edt(band)
    width=float(np.median(dt[sk]))
    xy=ndi.gaussian_filter1d(xy,max(2,width*.45),axis=0,mode='wrap')
    tangent=np.roll(xy,-1,axis=0)-np.roll(xy,1,axis=0)
    tangent/=np.linalg.norm(tangent,axis=1)[:,None]
    normal=np.column_stack([-tangent[:,1],tangent[:,0]])
    return dict(xy=xy,tangent=tangent,normal=normal,length=float(distance[-1]),
        width=width,pruned_pixels=int(sk.sum())-len(keep)),dt


def line_evidence(rgb,a,b,mode):
    """Interior sampling, not an edge trace; check a possible same-body bridge."""
    xy=np.linspace(a,b,25)
    encoded=np.column_stack([ndi.map_coordinates(rgb[:,:,k],[xy[:,1],xy[:,0]],order=1) for k in [0,1,2]])
    samples=rgb_to_hsv(encoded)
    inside=samples[4:-4]
    ratio=float(inside[:,2].min()/max(.02,min(samples[0,2],samples[-1,2])))
    chrom=inside[:,1]>.35
    hue=abs((inside[:,0]*360-mode+180)%360-180)
    fraction=float(np.mean(hue[chrom]<20)) if chrom.any() else 0.
    return ratio,fraction


def detect(image,max_dimension=1600):
    """No manual coordinates, selected colors or saved masks enter this function."""
    full=np.asarray(image,dtype=np.uint8);height,width=full.shape[:2]
    factor=min(1.,max_dimension/max(height,width))
    nw,nh=int(round(width*factor)),int(round(height*factor))
    rgb=np.asarray(Image.fromarray(full).resize((nw,nh),Image.Resampling.LANCZOS),dtype=np.float32)/255
    scale=np.array([nw/width,nh/height])
    hsv=rgb_to_hsv(rgb);v=hsv[:,:,2];sat=hsv[:,:,1];hue=hsv[:,:,0]*360
    border=np.zeros((nh,nw),bool);margin=max(1,int(min(nh,nw)*.025))
    border[:margin]=True;border[-margin:]=True;border[:,:margin]=True;border[:,-margin:]=True
    chrom=rgb[:,:,:2]/np.maximum(rgb.sum(axis=2,keepdims=True),.01)
    bg=np.median(chrom[border],axis=0)
    mad=np.median(abs(chrom[border]-bg),axis=0)*1.4826
    score=np.sqrt(np.sum(((chrom-bg)/np.maximum(mad,.003))**2,axis=2))
    threshold=max(float(np.quantile(score[border],.999)),float(threshold_otsu(np.minimum(score,50))))
    foreground=score>threshold
    background_value=float(np.median(v[border]))
    foreground|=v<background_value*.15
    sigma=max(1,max(nh,nw)/520)
    foreground=small_components(foreground,max(4,int(sigma*sigma)))
    band=ndi.gaussian_filter(foreground.astype(float),sigma)>.2
    band=fill_small_holes(band,int((sigma*10)**2))
    band=small_components(band,int((sigma*10)**2))
    labels,_=ndi.label(band);sizes=np.bincount(labels.ravel());sizes[0]=0
    if not sizes.max():raise ValueError('No supported necklace band')
    other_component_area=int(band.sum()-sizes.max())
    band=labels==sizes.argmax()
    axis,dt=strip_axis(band)
    useful=foreground&band&(v>np.quantile(v[foreground],.4))&(sat>np.quantile(sat[foreground],.25))
    hist,_=np.histogram(hue[useful],bins=360,range=(0,360),weights=(v*sat)[useful])
    hist=ndi.gaussian_filter1d(hist,3,mode='wrap')
    peaks,_=find_peaks(np.r_[hist[-30:],hist,hist[:30]],distance=18,prominence=hist.max()*.08)
    modes=[int(i-30) for i in sorted((p for p in peaks if 30<=p<390),key=lambda p:hist[p-30],reverse=True)]
    masks=[]
    smin=max(.2,float(np.quantile(sat[foreground],.18)*.75))
    local_value=ndi.gaussian_filter(v,4)
    for mode in modes:
        mask=foreground&band&(abs((hue-mode+180)%360-180)<15)&(sat>smin)
        mask&=(v>background_value*.15)&(v>local_value*.5)
        masks.append(small_components(mask,15))
    props=[p for mask in masks for p in regionprops(ndi.label(mask)[0]) if 20<=p.area<2000 and p.axis_minor_length>3]
    internal_width=float(np.median([p.axis_minor_length for p in props])) if props else axis['width']*.56
    diameter=max(internal_width,axis['width']*2*.28)
    allmask=np.zeros(band.shape,int)
    points=[];excluded=[]
    for i,mask in enumerate(masks):
        allmask[mask]=i+1
        distance=ndi.distance_transform_edt(mask);smooth=ndi.gaussian_filter(distance,diameter/12)
        locations=peak_local_max(smooth,min_distance=max(2,int(diameter*.55)),
            threshold_abs=max(1.5,diameter*.13),labels=mask)
        markers=np.zeros(mask.shape,int)
        for j,(y,x) in enumerate(locations,1):markers[y,x]=j
        regions=watershed(-smooth,markers,mask=mask)
        for p in regionprops(regions):
            y,x=locations[p.label-1]
            if p.area<diameter**2*.10 or p.axis_minor_length<diameter*.35:continue
            core=p.coords[smooth[p.coords[:,0],p.coords[:,1]]>smooth[y,x]*.5]
            yy,xx=np.average(core,axis=0,weights=smooth[core[:,0],core[:,1]]**2)
            q=dict(x=float(xx),y=float(yy),kind='chromatic',appearance_mode=i+1,
                support_area=float(p.area),inset_support_radius=float(smooth[y,x]),
                band_clearance=float(dt[y,x]),status='automatic interior proposal; unreviewed')
            if dt[y,x]<diameter*.30:excluded.append(dict(**q,reason='near approximate band edge'));continue
            # Merge nearby same-mode peaks only with a bright coherent interior bridge.
            candidates=[r for r in points if r['appearance_mode']==i+1 and np.hypot(r['x']-xx,r['y']-yy)<diameter*.5]
            merge=False
            for r in candidates:
                ratio,coherence=line_evidence(rgb,[xx,yy],[r['x'],r['y']],modes[i])
                if ratio>.85 and coherence>.9:merge=True;break
            if not merge:points.append(q)
    # A reflection can occupy only a few pixels even on a large apparent body.
    # Keep its first filter narrow; a bead-sized blur can erase black-bead seeds.
    response=ndi.gaussian_filter(v,max(.65,min(1.5,diameter*.08)))-ndi.gaussian_filter(v,diameter*.40)
    noise=float(np.median(abs(response[border]-np.median(response[border])))*1.4826)
    # Classify the local surroundings before bead-scale peak suppression. A
    # colored bead's stronger highlight must not erase a nearby black seed.
    # The two-pixel floor suppresses pixel noise, not neighboring bead bodies.
    locations=peak_local_max(response,min_distance=2,
        threshold_abs=max(.015,4*noise),labels=band)
    dark_max=float(np.quantile(v[foreground],.48))
    colored=list(points);reflection_rejections=[];dark_seeds=[]
    for y,x in locations:
        if dt[y,x]<diameter*.35:
            excluded.append(dict(x=float(x),y=float(y),kind='dark-reflection',reason='near approximate band edge'))
            continue
        radius=max(2,int(round(diameter*.30)))
        yy,xx=np.mgrid[max(0,y-radius):min(nh,y+radius+1),max(0,x-radius):min(nw,x+radius+1)]
        d2=(xx-x)**2+(yy-y)**2
        ring=(d2<=radius**2)&(d2>(diameter*.13)**2)
        chromatic_fraction=float(np.mean(allmask[yy[ring],xx[ring]]>0))
        ring_value=float(np.median(v[yy[ring],xx[ring]]))
        near=sorted(colored,key=lambda p:np.hypot(p['x']-x,p['y']-y))[:3]
        associated=False
        for q in near:
            length=np.hypot(q['x']-x,q['y']-y)
            if length<diameter*.25:associated=True;break
            if length>diameter*.70:continue
            ratio,coherence=line_evidence(rgb,[x,y],[q['x'],q['y']],modes[q['appearance_mode']-1])
            if ratio>.6 and coherence>.85:associated=True;break
        if associated or chromatic_fraction>.55 or ring_value>dark_max:
            reflection_rejections.append(dict(x=float(x),y=float(y),
                reason='associated colored interior' if associated else 'chromatic surround' if chromatic_fraction>.55 else 'surround insufficiently dark',
                chromatic_ring_fraction=chromatic_fraction,ring_value=ring_value))
            continue
        if any(max(abs(x-xx),abs(y-yy))<=max(2,int(diameter*.4)) for yy,xx in dark_seeds):
            reflection_rejections.append(dict(x=float(x),y=float(y),
                reason='near stronger accepted dark-surround reflection',
                chromatic_ring_fraction=chromatic_fraction,ring_value=ring_value))
            continue
        dark_seeds.append((int(y),int(x)))
        points.append(dict(x=float(x),y=float(y),kind='dark-reflection',appearance_mode=0,
            support_area=1.,band_clearance=float(dt[y,x]),reflection_response=float(response[y,x]),
            chromatic_ring_fraction=chromatic_fraction,ring_value=ring_value,
            status='reflection/dark-surround body proposal; full extent/color uncertainty retained'))
    if not points:raise ValueError('No supported interior/reflection proposals')
    tree=cKDTree(axis['xy']);xy=np.array([[p['x'],p['y']] for p in points]);_,stations=tree.query(xy)
    for p,station in zip(points,stations):
        p.update(station=int(station),cross=float(np.dot([p['x'],p['y']]-axis['xy'][station],axis['normal'][station])),
            source_xy=((np.array([p['x'],p['y']])+.5)/scale-.5).tolist())
    points.sort(key=lambda p:(p['station'],p['cross']))
    parameters=dict(analysis_size=[nw,nh],scale_xy=scale.tolist(),background_chromaticity=bg.tolist(),
        background_mad=mad.tolist(),background_value=background_value,foreground_threshold=threshold,
        border_fraction=.025,band_smoothing_sigma=sigma,other_component_area=other_component_area,
        apparent_internal_width=internal_width,apparent_diameter=diameter,strip_halfwidth=axis['width'],
        hue_modes_degrees=modes,saturation_floor=smin,reflection_response_floor=max(.015,4*noise),
        reflection_suppression='two-pixel peak extraction, then bead-scale suppression only among accepted dark-surround seeds',
        role='Image-derived approximate strip/interiors; not a verified boundary, centerline, outward anchor or automatic completeness guarantee')
    for rows in (excluded,reflection_rejections):
        for p in rows:p['source_xy']=((np.array([p['x'],p['y']])+.5)/scale-.5).tolist()
    return dict(points=points,excluded=excluded,reflection_rejections=reflection_rejections,parameters=parameters,axis=axis,
        rgb=rgb,foreground=foreground,band=band,score=score,scale=scale,diameter=diameter)


def adjacency(result):
    """Tentative local directional proposals, with gap/ambiguity accounting."""
    points=result['points'];axis=result['axis'];n=len(points)
    xy=np.array([[p['x'],p['y']] for p in points]);stations=np.array([p['station'] for p in points])
    if n<3:raise ValueError('At least three point proposals are required for directional adjacency')
    cross=np.array([p['cross'] for p in points]);tree=cKDTree(xy)
    distances,neighbors=tree.query(xy,k=min(12,n))
    nearest=distances[:,1];spacing=float(np.median(nearest))
    trial=[]
    for i in range(n):
        for j,d in zip(neighbors[i,1:],distances[i,1:]):
            j=int(j)
            if d>spacing*2.3:continue
            ds=float(stations[j]-stations[i]);length=len(axis['xy'])
            ds=(ds+length/2)%length-length/2
            dt=float(cross[j]-cross[i])
            if np.hypot(ds,dt)<spacing*.35:continue
            angle=float(np.degrees(np.arctan2(dt,ds))%180)
            trial.append((i,j,float(d),ds,dt,angle))
    angles=np.array([v[5] for v in trial]);hist,_=np.histogram(angles,bins=180,range=(0,180))
    hist=ndi.gaussian_filter1d(hist.astype(float),4,mode='wrap')
    # d1 is the predominantly transverse family; each diagonal advances clockwise.
    modes=[int(np.argmax(hist[20:70])+20),int(np.argmax(hist[70:115])+70),int(np.argmax(hist[115:165])+115)]
    direction_modes={'d2':modes[0],'d1':modes[1],'d3':modes[2]}
    # Perspective and local viewing direction change the projected angles
    # around the rope. Estimate modes in nearby strip stations as well as globally.
    local_modes=[];length=len(axis['xy']);trial_stations=np.array([stations[e[0]] for e in trial])
    ranges={'d2':(20,70),'d1':(70,115),'d3':(115,165)}
    for station in stations:
        ds=(trial_stations-station+length/2)%length-length/2
        local=abs(ds)<axis['width']*3
        if local.sum()<24:local_modes.append(direction_modes);continue
        counts,_=np.histogram(angles[local],bins=180,range=(0,180))
        counts=ndi.gaussian_filter1d(counts.astype(float),5,mode='wrap')
        local_modes.append({name:int(np.argmax(counts[lo:hi])+lo) for name,(lo,hi) in ranges.items()})
    selected={};ambiguous=[]
    for i,j,d,ds,dt,angle in trial:
        # Both directions of the same pair use the same angle estimate. Using
        # each endpoint's mode separately can break reciprocal classification.
        pair_modes={name:(local_modes[i][name]+local_modes[j][name])/2 for name in DIRECTIONS}
        deviations={name:abs((angle-mode+90)%180-90) for name,mode in pair_modes.items()}
        name=min(deviations,key=deviations.get);deviation=deviations[name]
        if deviation>22:continue
        sign=1 if (dt>0 if name=='d1' else ds>0) else -1
        key=(i,name,sign);score=d*(1+deviation/30)
        candidate=dict(start=i,end=j,direction=name,sign=sign,distance=d,angle=angle,
            angle_deviation=deviation,selection_score=score,station_delta=ds,cross_delta=dt)
        selected.setdefault(key,[]).append(candidate)
    accepted=[];seen=set();lengths={d:[] for d in DIRECTIONS}
    for key,choices in selected.items():
        choices.sort(key=lambda q:q['selection_score']);best=choices[0]
        reverse=selected.get((best['end'],best['direction'],-best['sign']),[])
        if not reverse or min(reverse,key=lambda q:q['selection_score'])['end']!=best['start']:continue
        if len(choices)>1 and choices[1]['selection_score']<best['selection_score']*1.15:
            ambiguous.append(dict(**best,reason='Two nearby directional choices'));continue
        i,j=best['start'],best['end']
        if best['sign']<0:i,j=j,i
        ident=(i,j,best['direction'])
        if ident in seen:continue
        seen.add(ident);lengths[best['direction']].append(best['distance'])
        accepted.append({**best,'start':i,'end':j,'sign':1,'status':'tentative mutual-neighbor relation; unit count unverified'})
    median={d:float(np.median(v)) if v else None for d,v in lengths.items()}
    edges=[];gaps=[]
    for e in accepted:
        typical=median[e['direction']]
        if typical and e['distance']>typical*1.45:gaps.append(dict(**e,reason='Possible skipped/missing body; do not compress index'));continue
        edges.append(e)
    return dict(edges=edges,ambiguous_choices=ambiguous,possible_gaps=gaps,
        nearest_spacing=spacing,direction_modes_degrees=direction_modes,local_direction_modes_degrees=local_modes,median_direction_lengths=median,
        meaning='Photo-strip direction proposals; no selected 6/7 assignment, verified unit steps or full-string indices')


def evaluate(result,graph,path,expected_source=None):
    """Read maker data only here, after all detection/adjacency decisions."""
    from analyze_label_series import edges_from_document
    doc=json.loads(path.read_text());points=result['points'];manual=doc['annotations']
    if expected_source is not None and doc.get('source',{}).get('sha256')!=expected_source:
        raise ValueError('Evaluator annotations belong to a different source image')
    xy=np.array([p['source_xy'] for p in points]);truth=np.array([[p['x'],p['y']] for p in manual])
    cost=np.linalg.norm(truth[:,None,:]-xy[None,:,:],axis=2)
    threshold=result['diameter']/float(np.sqrt(np.prod(result['scale'])))*.75
    # Allow unmatched maker marks. Forced full assignment otherwise sends local
    # missing beads to remote parts of the rope and displaces valid associations.
    penalty=threshold*(len(manual)+1)
    eligible=np.where(cost<=threshold,cost,penalty*2)
    rows,cols=linear_sum_assignment(np.column_stack([eligible,np.full((len(manual),len(manual)),penalty)]))
    mapping={manual[i]['number']:int(j) for i,j in zip(rows,cols) if j<len(points) and cost[i,j]<=threshold}
    matches=[dict(number=a['number'],automatic_point=mapping.get(a['number']),
        distance=float(cost[i,mapping[a['number']]]) if a['number'] in mapping else None,
        nearest_distance=float(cost[i].min()),status='proximity association for validation; bead identity not proven') for i,a in enumerate(manual)]
    supplied=edges_from_document(doc);proposed={(e['start'],e['end'],e['direction']) for e in graph['edges']}
    relations=[]
    for e in supplied:
        a,b=mapping.get(e.start),mapping.get(e.end)
        forward=(a,b,e.direction) in proposed if a is not None and b is not None else False
        reverse=(b,a,e.direction) in proposed if a is not None and b is not None else False
        relations.append(dict(start=e.start,end=e.end,direction=e.direction,
            endpoints_associated=a is not None and b is not None,forward_agrees=forward,reverse_only=reverse))
    return dict(annotation_sha256=sha(path),revision=doc['revision'],manual_beads=len(manual),
        matched_within_gate=len(mapping),gate_pixels=threshold,matches=matches,
        manual_links=len(supplied),forward_links_agree=sum(q['forward_agrees'] for q in relations),
        reverse_links=sum(q['reverse_only'] for q in relations),relations=relations,
        limitation='No true body boundaries supplied; nearest point association is provisional, and completed series can contain skipped steps')


def export(result,graph,image_path,size,out):
    from datetime import datetime,timezone
    source_hash=sha(image_path);rows=[]
    for i,p in enumerate(result['points'],1):
        x,y=p['source_xy'];ident=str(uuid.uuid5(uuid.NAMESPACE_URL,f'{source_hash}:automatic:{x:.3f}:{y:.3f}'))
        rows.append(dict(id=ident,number=i,x=x,y=y,label_dx=6.,label_dy=-6.))
    series=[]
    for e in graph['edges']:
        series.append(dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,f'{source_hash}:{e["start"]}:{e["end"]}:{e["direction"]}')),
            direction=e['direction'],status='complete',bead_ids=[rows[e['start']]['id'],rows[e['end']]['id']]))
    now=datetime.now(timezone.utc).isoformat()
    doc=dict(schema_version=2,source=dict(filename=image_path.name,sha256=source_hash,oriented_size=list(size),
        coordinates='source pixels after EXIF orientation; x right, y down'),view_crop=[0,0,*size],revision=0,
        annotation_kind='Automatic unreviewed point and adjacency proposals; numbers are observation names, not bead_index',
        created_at=now,updated_at=now,annotations=rows,series=series,direction_definitions=DIRECTIONS,
        automatic_proposals=True,automatic_origin=dict(detector_sha256=sha(Path(__file__)),
            point_role='interior or reflection proposal; not physical center or exposed outward anchor',
            adjacency_role='tentative relations; consecutive unit steps unverified'))
    validate_annotations(rows,size);validate_series(series,rows)
    (out/'annotations.json').write_text(json.dumps(doc,indent=2)+'\n')
    return doc


def check_output(out,replace=False):
    """Never silently overwrite a maker save or a reviewed automatic document."""
    target=out/'annotations.json'
    if target.resolve()==(ROOT/'photo2/output/labeler/annotations.json').resolve():
        raise ValueError('Choose a separate output directory; the maker live file is protected')
    if not target.exists():return
    if not replace:raise ValueError('Output annotations already exist. Choose a new --output, or --replace-proposals for unchanged generated proposals only.')
    doc=json.loads(target.read_text());report=json.loads((out/'report.json').read_text())
    if doc.get('automatic_proposals') is not True or doc.get('revision')!=0 or sha(target)!=report.get('automatic_annotation_sha256'):
        raise ValueError('Existing annotations were edited or are not unchanged automatic proposals; choose a new --output')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,default=ROOT/'beads-photo-2.jpg')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/output/automatic-labeler')
    parser.add_argument('--max-dimension',type=int,default=1600)
    parser.add_argument('--validation',type=Path,help='Optional evaluator file; never detector input')
    parser.add_argument('--replace-proposals',action='store_true',help='Replace only an unchanged generated annotation file; reviewed/maker files remain protected')
    args=parser.parse_args()
    if args.max_dimension<64:parser.error('--max-dimension must be at least 64')
    try:check_output(args.output,args.replace_proposals)
    except (ValueError,OSError) as exc:parser.error(str(exc))
    args.output.mkdir(parents=True,exist_ok=True)
    image=ImageOps.exif_transpose(Image.open(args.image)).convert('RGB')
    result=detect(np.array(image),args.max_dimension);graph=adjacency(result)
    evaluation=evaluate(result,graph,args.validation,sha(args.image)) if args.validation else None
    export(result,graph,args.image,image.size,args.output)
    report=dict(image_sha256=sha(args.image),script_sha256=sha(Path(__file__)),parameters=result['parameters'],
        observations=result['points'],excluded_near_edge=result['excluded'],reflection_rejections=result['reflection_rejections'],adjacency=graph,
        inventory=dict(proposed_bodies=len(result['points']),chromatic=sum(p['kind']=='chromatic' for p in result['points']),
            dark_reflection=sum(p['kind']=='dark-reflection' for p in result['points']),
            candidate_links=len(graph['edges']),excluded_edge_features=len(result['excluded'])),
        automatic_annotation_sha256=sha(args.output/'annotations.json'),
        caveat='Unreviewed automatic candidates; no completeness, body identity, helicity, N, closure or color-repeat claim')
    if evaluation is not None:report['manual_evaluation']=evaluation
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    np.savez_compressed(args.output/'analysis.npz',foreground=result['foreground'],band=result['band'],
        axis=result['axis']['xy'],scale=result['scale'])
    os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-auto-mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,12),constrained_layout=True);ax.imshow(image)
    for kind,color in [('chromatic','lime'),('dark-reflection','cyan')]:
        q=np.array([p['source_xy'] for p in result['points'] if p['kind']==kind])
        if len(q):ax.scatter(q[:,0],q[:,1],s=5,c=color,marker='+',label=kind)
    ax.set_title('Whole-photo automatic interior/reflection proposals; no bead boundaries');ax.legend()
    fig.savefig(args.output/'overview.png',dpi=170);plt.close(fig)
    print(json.dumps(dict(**report['inventory'],manual_evaluation={k:report.get('manual_evaluation',{}).get(k)
        for k in ['revision','manual_beads','matched_within_gate','manual_links','forward_links_agree']}),indent=2))


if __name__=='__main__':main()
