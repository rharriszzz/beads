"""One-target edge-first harmonic graph contour. No case/reference inputs.

Pixels form a four-neighbor graph. A source is the measured bright patch; the
computational frame is a sink, never accepted as a photographic edge. Edge
conductances are low at coherent dark transitions or chromatic steps and high
through continuous illuminated material. Solve the harmonic potential (seed1,
exterior0) and inspect its .5 level contour. There are no area/shape unaries.
"""
import numpy as np
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve
from photo2.bead_detection.brightness_r270 import linearize
from photo2.r282.common import runs, pixels

VERSION='R290-edge-resistance-v4'
PARAMETERS=dict(initial_radius=38,maximum_radius=152,normal_offset=3,tangent_width=5,
                edge_floor=.0001,evidence_gain=20.,dark_support=.35,color_support=.25,
                dark_side_ratio=.22,dark_luminance=.02,recovery_support=.10,
                step_support=.38,tangent_support=.6,minimum_IoU=.90,
                perturbations=[.85,1.15],absolute_contrast=.012)

def shifted(a,dy=0,dx=0):
    y,x=np.indices(a.shape[:2]);return a[np.clip(y+dy,0,a.shape[0]-1),np.clip(x+dx,0,a.shape[1]-1)]

def fields(rgb):
    """All measurements remain in native pixels; no learned palette or mask."""
    lum=linearize(rgb.astype(float)/255.)@np.array([.2126,.7152,.0722])
    # Three samples reduce one-pixel noise while retaining one-native-pixel graph.
    smooth=ndi.uniform_filter(lum,3,mode='nearest')
    # Channel-difference direction is invariant to brightness scale AND an
    # additive neutral specular term. Saturation alone is not a material change.
    color_rgb=ndi.uniform_filter(rgb.astype(float),size=(3,3,1),mode='nearest')
    difference=color_rgb-color_rgb.min(2,keepdims=True)
    chroma=difference/np.maximum(difference.max(2,keepdims=True),1.)
    saturation=difference.max(2)/np.maximum(color_rgb.max(2),1.)
    result=[]
    for axis in (1,0):
        dy,dx=(0,1) if axis==1 else (1,0)
        a=shifted(smooth,-3*dy,-3*dx);b=shifted(smooth,3*dy,3*dx)
        center=(smooth+shifted(smooth,dy,dx))/2
        high=np.maximum(a,b);low=np.minimum(a,b);scale=np.maximum(high,.025)
        drop=np.maximum(high-center,0)/scale
        recovery=np.maximum(low-center,0)/scale
        step=np.abs(a-b)/scale
        ca=shifted(chroma,-3*dy,-3*dx);cb=shifted(chroma,3*dy,3*dx)
        color=np.linalg.norm(ca-cb,axis=2)*np.minimum(low/.035,1)
        color*=np.minimum(shifted(saturation,-3*dy,-3*dx),shifted(saturation,3*dy,3*dx))>=.25
        # Sustained neighboring tangent evidence; isolated pixels cannot dominate.
        dark_context=(recovery>=PARAMETERS['recovery_support'])|(low<=PARAMETERS['dark_luminance'])|(low/scale<=PARAMETERS['dark_side_ratio'])
        raw=(drop>=PARAMETERS['dark_support'])&((high-center)>=PARAMETERS['absolute_contrast'])&dark_context
        tangent_axis=0 if axis==1 else 1
        coherent=ndi.uniform_filter1d(raw.astype(float),5,axis=tangent_axis,mode='nearest')
        dark=drop*coherent*dark_context
        cc=ndi.uniform_filter1d((color>=PARAMETERS['color_support']).astype(float),5,axis=tangent_axis,mode='nearest')
        cs=color*cc
        ss=ndi.uniform_filter1d((step>=PARAMETERS['step_support']).astype(float),5,axis=tangent_axis,mode='nearest')
        continuous=np.minimum(center/scale,1)*(1-np.clip(color/.35,0,1))
        # Darkness is primary (weight1); independent color evidence may support an
        # occlusion step. Weak contour length floor only selects among hypotheses.
        evidence=np.maximum(dark,1.2*cs)
        capacity=PARAMETERS['edge_floor']+(1+continuous)*np.exp(-PARAMETERS['evidence_gain']*evidence)
        result.append(dict(capacity=capacity,dark=dark,drop=drop,recovery=recovery,step=step,
                           color=color,coherence=coherent,color_coherence=cc,step_coherence=ss,
                           continuous=continuous,dark_context=dark_context.astype(float),side_a=a,center=center,side_b=b))
    return lum,result

def cut(edge_fields,core,factor=1.):
    h,w=core.shape;n=h*w;idx=np.arange(n).reshape(h,w)
    row=[];col=[];vals=[]
    for f,a,b in [(edge_fields[0],idx[:,:-1],idx[:,1:]),(edge_fields[1],idx[:-1,:],idx[1:,:])]:
        cap=f['capacity'][:,:-1] if a.shape[0]==h else f['capacity'][:-1,:]
        # Perturb barrier strength; no area or perimeter term is introduced.
        cap=PARAMETERS['edge_floor']+np.maximum(cap-PARAMETERS['edge_floor'],1e-12)**factor
        v=cap.ravel()
        row.extend([a.ravel(),b.ravel()]);col.extend([b.ravel(),a.ravel()]);vals.extend([v,v])
    graph=coo_matrix((np.concatenate(vals),(np.concatenate(row),np.concatenate(col))),shape=(n,n)).tocsr()
    laplacian=diags(np.asarray(graph.sum(1)).ravel())-graph
    source=np.flatnonzero(core);frame=np.unique(np.r_[idx[0],idx[-1],idx[:,0],idx[:,-1]])
    fixed=np.zeros(n,bool);fixed[source]=True;fixed[frame]=True;unknown=~fixed
    u=np.zeros(n);u[source]=1.
    u[unknown]=spsolve(laplacian[unknown][:,unknown],-laplacian[unknown][:,fixed]@u[fixed])
    return (u.reshape(h,w)>=.5),float(u@laplacian@u)

def edges(mask,ff,origin,other_masks):
    """Exact pixel-square sides; each side has its own photographic justification."""
    result=[];ox,oy=origin
    variant_edges=[ndi.maximum_filter((q^ndi.binary_erosion(q)).astype(np.uint8),3)>0 for q in other_masks]
    for axis,f in enumerate(ff):
        changed=mask[:,:-1]!=mask[:,1:] if axis==0 else mask[:-1,:]!=mask[1:,:]
        yy,xx=np.where(changed)
        for y,x in zip(yy,xx):
            if axis==0:
                endpoints=[[x+ox+.5,y+oy-.5],[x+ox+.5,y+oy+.5]]
                inner=(x,y) if mask[y,x] else (x+1,y)
            else:
                endpoints=[[x+ox-.5,y+oy+.5],[x+ox+.5,y+oy+.5]]
                inner=(x,y) if mask[y,x] else (x,y+1)
            values={k:float(v[y,x]) for k,v in f.items() if k!='capacity'}
            dark=values['drop']>=PARAMETERS['dark_support'] and values['coherence']>=PARAMETERS['tangent_support'] and values['dark_context']>0 and max(values['side_a'],values['side_b'])-values['center']>=PARAMETERS['absolute_contrast']
            chromatic=values['color']>=PARAMETERS['color_support'] and values['color_coherence']>=PARAMETERS['tangent_support']
            step=values['step']>=PARAMETERS['step_support'] and values['step_coherence']>=.8 and values['dark_context']>0 and values['drop']>=PARAMETERS['dark_support']
            # Every accepted side must persist within one pixel across all perturbations.
            mx,my=inner
            stable=all(q[my,mx] for q in variant_edges)
            frame=min(x,y,mask.shape[1]-2-x,mask.shape[0]-2-y)<4
            reasons=[]
            if dark:reasons.append('T1 sustained dark transition')
            if chromatic:reasons.append('T3/T6 coherent chromatic step')
            if step:reasons.append('T2/T6 sustained brightness step')
            if not stable:reasons.append('T8 boundary moves under perturbation')
            if frame:reasons.append('T7 computational frame cannot support an edge')
            result.append(dict(endpoints=endpoints,supported=bool((dark or chromatic or step) and stable and not frame),stable=bool(stable),evidence=values,reasons=reasons or ['No sustained photographic transition']))
    return result

def arcs(segments,supported=True):
    selected=[i for i,s in enumerate(segments) if s['supported']==supported];by_vertex={}
    for i in selected:
        for p in segments[i]['endpoints']:by_vertex.setdefault(tuple(p),[]).append(i)
    remaining=set(selected);groups=[]
    while remaining:
        todo=[min(remaining)];group=[]
        while todo:
            i=todo.pop()
            if i not in remaining:continue
            remaining.remove(i);group.append(i)
            for p in segments[i]['endpoints']:todo.extend(j for j in by_vertex[tuple(p)] if j in remaining)
        groups.append(sorted(group))
    return groups

def candidate(mask,ff,lum,origin,variants,nearby,core,rgb):
    seg=edges(mask,ff,origin,variants);xy=np.c_[np.where(mask)[1]+origin[0],np.where(mask)[0]+origin[1]]
    ious=[float((mask&q).sum()/max((mask|q).sum(),1)) for q in variants]
    center=xy.mean(0);spread=max((float(np.linalg.norm(np.c_[np.where(q)[1]+origin[0],np.where(q)[0]+origin[1]].mean(0)-center)) for q in variants),default=0.)
    included=[]
    for f in nearby:
        x,y=np.array(f['point'])-origin
        if 0<=x<mask.shape[1] and 0<=y<mask.shape[0] and mask[y,x]:included.append(f['id'])
    border=bool(np.any(mask[:5]) or np.any(mask[-5:]) or np.any(mask[:,:5]) or np.any(mask[:,-5:]))
    support_fraction=sum(s['supported'] for s in seg)/max(len(seg),1)
    dark_inside=(lum<max(.012,float(np.median(lum[core]))*.18))&mask
    holes=ndi.binary_fill_holes(mask)&~mask
    # Internal edge evidence is explicitly retained; no inference that a hole is
    # external and no fill operation changes the candidate mask.
    internal=[]
    for axis,f in enumerate(ff):
        inside=mask&ndi.binary_erosion(mask,iterations=3)
        internal.append(int(np.sum(inside&(f['recovery']>.24)&(f['coherence']>=.6))))
    adequate=bool(core.sum()>=3 and np.max(lum[core])-np.percentile(lum,20)>=.012)
    # Neutral illuminated patches can bound a reflection on an otherwise dark
    # visible surface. Without material evidence this is not a complete bead edge.
    saturation=(rgb.max(2).astype(float)-rgb.min(2))/np.maximum(rgb.max(2),1)
    pigment_fraction=float(np.mean(saturation[mask]>.25))
    reflection_ambiguous=pigment_fraction<.5
    contradiction=bool(included or sum(internal)>0 or reflection_ambiguous)
    reliable=adequate and bool(seg) and all(s['supported'] for s in seg) and min(ious,default=0)>=PARAMETERS['minimum_IoU'] and not border and not contradiction
    status='Reliable boundary' if reliable else ('Partial boundary / unresolved' if any(s['supported'] for s in seg) and adequate else 'Insufficient measurement')
    reasons=[]
    if support_fraction<1:reasons.append('Unsupported contour sides remain unresolved; optimizer closure is not accepted.')
    if included:reasons.append('Other bright features share the candidate; physical ownership is unresolved.')
    if sum(internal):reasons.append('Internal coherent valleys could be shading, holes or an overlooked separation.')
    if reflection_ambiguous:reasons.append('Neutral bright-region edge could bound a reflection rather than the visible bead surface.')
    if border:reasons.append('Candidate reaches computational context; frame sides excluded.')
    if min(ious,default=0)<.9:reasons.append('Contour is sensitive to modest edge-cost changes.')
    if not adequate:reasons.append('Illuminated core or local contrast is insufficient.')
    if reliable:reasons.append('Every contour side has persistent photographic support; human correctness still awaits review.')
    evidence={
      'T1':dict(sustained_dark_sides=sum('T1 sustained dark transition' in s['reasons'] for s in seg),mean_coherence=float(np.mean([s['evidence']['coherence'] for s in seg])) if seg else None),
      'T2':dict(mean_drop=float(np.mean([s['evidence']['drop'] for s in seg])) if seg else None,recovering_valley_sides=sum(s['evidence']['recovery']>.2 for s in seg),continuous_material_cut_sides=sum(s['evidence']['continuous']>.8 for s in seg)),
      'T3':dict(chromatic_sides=sum('T3/T6 coherent chromatic step' in s['reasons'] for s in seg),interpretation='Channel-difference color direction; invariant to intensity scale/additive neutral reflection; dim/neutral evidence unavailable.'),
      'T4':dict(other_features_inside=included,ownership='unresolved; inclusion is not same-bead identity'),
      'T5':dict(internal_dark_pixels=int(dark_inside.sum()),enclosed_excluded_pixels=int(holes.sum()),internal_valley_pixels_by_axis=internal,interpretation='Hole/shadow/separation alternatives retained; no automatic fill.'),
      'T6':dict(color_or_step_sides=sum(any('T6' in r for r in s['reasons']) for s in seg),occluder_identity=None),
      'T7':dict(total_sides=len(seg),supported_fraction=support_fraction,supported_arcs=len(arcs(seg)),unresolved_arcs=len(arcs(seg,False)),frame_contact=border,complete_photographic_contour=reliable),
      'T8':dict(core_pixels=int(core.sum()),core_peak_Y=float(np.max(lum[core])),contrast_Y=float(np.max(lum[core])-np.percentile(lum,20)),pigment_fraction=pigment_fraction,reflection_edge_ambiguous=reflection_ambiguous,perturbation_IoU=ious,centroid_spread_px=spread,interpretation='Sensitivity only; no calibrated accuracy interval.')}
    return dict(status=status,reasons=reasons,evidence=evidence,candidate_pixels=dict(runs=runs(xy),pixel_count=len(xy)),candidate_centroid=center.tolist(),visible_region_centroid=center.tolist() if reliable else None,photographically_supported_visible_pixels=dict(runs=runs(xy),pixel_count=len(xy)) if reliable else None,segments=seg,supported_arcs=arcs(seg),unresolved_arcs=arcs(seg,False),uncertainty=dict(centroid_sensitivity_px=spread,physical_center=None,ownership=None))

def detect(rgb,feature,nearby=()):
    """Only pixels, independent bright feature and optional independent neighbors.

    No case IDs, category tags, split, review evidence or historical masks enter.
    """
    p=np.array(feature['point'],int);h,w=rgb.shape[:2];r=PARAMETERS['initial_radius'];expansions=[]
    while True:
        lo=np.maximum(p-r,0);hi=np.minimum(p+r+1,[w,h]);a=rgb[lo[1]:hi[1],lo[0]:hi[0]]
        lum,ff=fields(a);core=np.zeros(lum.shape,bool)
        patch=pixels(dict(runs=feature.get('runs',[])))
        if not len(patch):patch=p.reshape(1,2)
        local=patch-lo;valid=(local[:,0]>0)&(local[:,0]<a.shape[1]-1)&(local[:,1]>0)&(local[:,1]<a.shape[0]-1);local=local[valid]
        if not len(local):raise ValueError('Bright patch not in valid photograph context')
        core[local[:,1],local[:,0]]=True
        mask,energy=cut(ff,core)
        border=bool(np.any(mask[:5]) or np.any(mask[-5:]) or np.any(mask[:,:5]) or np.any(mask[:,-5:]))
        expansions.append(dict(radius=r,border_contact=border,dirichlet_energy=energy))
        if not border or r>=PARAMETERS['maximum_radius']:break
        r=min(2*r,PARAMETERS['maximum_radius'])
    variants=[cut(ff,core,v)[0] for v in PARAMETERS['perturbations']]
    # Frame location can influence harmonic potentials even without mask contact.
    # Measure that uncertainty with a larger context; never call the frame an edge.
    rr=min(PARAMETERS['maximum_radius'],r+19);biglo=np.maximum(p-rr,0);bighi=np.minimum(p+rr+1,[w,h]);big=rgb[biglo[1]:bighi[1],biglo[0]:bighi[0]]
    _,bigff=fields(big);bigcore=np.zeros(big.shape[:2],bool);local=patch-biglo
    bigcore[local[:,1],local[:,0]]=True;bigmask,_=cut(bigff,bigcore)
    offset=lo-biglo;context_variant=bigmask[offset[1]:offset[1]+lum.shape[0],offset[0]:offset[0]+lum.shape[1]];variants.append(context_variant)
    # A meaningful alternative is a genuinely different contour from the same
    # evidence objective, rather than a hand-built repair or mask union.
    near=[q for q in nearby if q['id']!=feature['id']]
    ca=candidate(mask,ff,lum,lo,variants,near,core,a);alternatives=[]
    for q in variants[:2]:
        iou=float((mask&q).sum()/max((mask|q).sum(),1))
        if iou<.97:
            alternatives.append(candidate(q,ff,lum,lo,[mask]+variants,near,core,a));break
    pairs=[]
    for q in near:
        if np.linalg.norm(np.array(q['point'])-p)>45:continue
        route=np.linspace(p,q['point'],31)-lo;values=ndi.map_coordinates(lum,route[:,::-1].T,order=1,mode='nearest')
        pairs.append(dict(feature_id=q['id'],point=q['point'],profile_Y=values.tolist(),valley_ratio=float(values.min()/max(min(values[0],values[-1]),.001)),ownership=None))
    return dict(algorithm=VERSION,parameters=PARAMETERS,feature=feature,box=[int(lo[0]),int(lo[1]),int(hi[0]),int(hi[1])],search=expansions,A=ca,B=alternatives[0] if alternatives else None,
                neighboring_features=pairs,context_sensitivity_radius=rr,
                source_scope='One target; no physical identity, geometry, reference mask, case category or judgment input.')
