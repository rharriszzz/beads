"""One binary target solve combining A–E photographic evidence locally."""
import numpy as np
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow, breadth_first_order
from photo2.r282.common import runs,pixels
from photo2.r290.detector import arcs
from .evidence import measure,direct_access,separators,PARAMETERS as EVIDENCE_PARAMETERS

VERSION='R291-complementary-v3'
PARAMETERS=dict(initial_radius=48,maximum_radius=144,pairwise_weight=2.,unary_weight=.5,
                conductance_gain=5.,direct_stop_penalty=4.5,alternative_stop_penalty=2.7,
                perturbations=[.85,1.15],context_extra=16,evidence=EVIDENCE_PARAMETERS)

def solve(m,core,access,peers,*,strength=1.,alternative=False):
    lum=m['lum'];h,w=lum.shape;n=h*w;idx=np.arange(n).reshape(h,w);source=n;sink=n+1
    match=m['match'];rel=m['reliability'];floor=m['model']['floor_Y'];diffuse=max(m['model']['diffuse_Y'],.008)
    illuminated=np.clip((lum-floor)/max(diffuse-floor,.005),0,1)
    dark=np.clip((floor-lum)/max(floor,.004),0,1)
    logit=3*match*rel*illuminated*m['model']['continuation_exposure']-3*(1-match)*rel-2*dark
    stop=PARAMETERS['alternative_stop_penalty'] if alternative else PARAMETERS['direct_stop_penalty']
    logit-=stop*(~access)
    weight=PARAMETERS['unary_weight']*strength
    cost_fg=weight*np.logaddexp(0,-logit);cost_bg=weight*np.logaddexp(0,logit)
    row=[];col=[];values=[]
    for i,(a,b) in enumerate([(idx[:,:-1],idx[:,1:]),(idx[:-1,:],idx[1:,:])]):
        f=m['fields'][i];continuity=f['D_continuity']*(1-np.clip(f['A_dark_seam']*2,0,1))
        cap=PARAMETERS['pairwise_weight']*(.015+np.exp(-PARAMETERS['conductance_gain']*f['combined'])+.5*continuity)
        cap=cap[:,:-1] if i==0 else cap[:-1,:];v=np.maximum(1,np.rint(cap*10000)).astype(np.int64).ravel()
        row.extend([a.ravel(),b.ravel()]);col.extend([b.ravel(),a.ravel()]);values.extend([v,v])
    source_cap=np.maximum(0,np.rint(cost_bg*10000)).astype(np.int64).ravel();sink_cap=np.maximum(0,np.rint(cost_fg*10000)).astype(np.int64).ravel()
    source_cap[core.ravel()]=10**8
    frame=np.unique(np.r_[idx[0],idx[-1],idx[:,0],idx[:,-1]]);sink_cap[frame]=10**8
    for p in peers:
        if not p['supported']:continue
        x,y=np.rint(p['local_point']).astype(int)
        if 0<=x<w and 0<=y<h and not core[y,x]:sink_cap[idx[y,x]]=10**8 if not alternative else 5000
    row.extend([np.full(n,source),idx.ravel()]);col.extend([idx.ravel(),np.full(n,sink)]);values.extend([source_cap,sink_cap])
    graph=coo_matrix((np.concatenate(values),(np.concatenate(row),np.concatenate(col))),shape=(n+2,n+2),dtype=np.int64).tocsr()
    flow=maximum_flow(graph,source,sink);residual=graph-flow.flow;residual.data=(residual.data>0).astype(np.int8);residual.eliminate_zeros()
    reached=breadth_first_order(residual,source,directed=True,return_predecessors=False);owned=np.zeros(n+2,bool);owned[reached]=True;mask=owned[:n].reshape(h,w)
    # Only source-connected visible material is this invocation's candidate.
    labels,_=ndi.label(mask,np.ones((3,3)));ids=np.unique(labels[core]);mask=np.isin(labels,ids[ids>0])
    return mask

def segment_records(mask,m,origin,variants):
    result=[];variant_edges=[ndi.maximum_filter((q^ndi.binary_erosion(q)).astype(int),3)>0 for q in variants]
    for axis,f in enumerate(m['fields']):
        change=mask[:,:-1]!=mask[:,1:] if axis==0 else mask[:-1,:]!=mask[1:,:]
        for y,x in zip(*np.where(change)):
            if axis==0:
                ends=[[x+origin[0]+.5,y+origin[1]-.5],[x+origin[0]+.5,y+origin[1]+.5]];inner=(x,y) if mask[y,x] else (x+1,y)
            else:
                ends=[[x+origin[0]-.5,y+origin[1]+.5],[x+origin[0]+.5,y+origin[1]+.5]];inner=(x,y) if mask[y,x] else (x,y+1)
            vals={k:float(v[y,x]) for k,v in f.items() if not k.startswith('profile_')}
            methods=[]
            if vals['A_dark_seam']>=.22:methods.append('A: coherent dark transition')
            if vals['B_multiscale']>=.22:methods.append('B: tracked multiscale illumination edge')
            if vals['C_material']>=.18:methods.append('C: coherent material-color transition')
            conflict=bool(vals['D_continuity']>.6 and vals['A_dark_seam']<.22 and vals['C_material']<.18)
            if conflict:methods.append('D conflicts: illuminated material continues across this cut')
            if vals['E_junction']>0:methods.append('E: nearby edge junction; possible occlusion or internal crossing')
            if vals['E_termination']>0:methods.append('E: nearby terminating edge; closure remains uncertain')
            stable=all(q[inner[1],inner[0]] for q in variant_edges)
            frame=min(x,y,mask.shape[1]-2-x,mask.shape[0]-2-y)<4
            supported=bool(any(v.startswith(('A:','B:','C:')) for v in methods) and not conflict and not frame)
            result.append(dict(endpoints=ends,supported=supported,stable=bool(stable),conflicted=conflict,methods=methods or ['No coherent local edge'],evidence=vals,profile_near=m['fields'][axis]['profile_near'][:,y,x].tolist(),profile_far=m['fields'][axis]['profile_far'][:,y,x].tolist(),frame=bool(frame)))
    return result

def describe(mask,m,origin,variants,nearby,peers,core):
    segments=segment_records(mask,m,origin,variants);xy=np.c_[np.where(mask)[1]+origin[0],np.where(mask)[0]+origin[1]]
    center=xy.mean(0);ious=[float((mask&q).sum()/max((mask|q).sum(),1)) for q in variants]
    spread=max(float(np.linalg.norm(np.c_[np.where(q)[1]+origin[0],np.where(q)[0]+origin[1]].mean(0)-center)) for q in variants)
    included=[]
    for q in nearby:
        x,y=q['local_point']
        if 0<=x<mask.shape[1] and 0<=y<mask.shape[0] and mask[y,x]:included.append(q['id'])
    T1=sum(s['evidence']['A_dark_seam']>=.22 for s in segments);T2=sum(s['evidence']['B_multiscale']>=.22 for s in segments);T3=sum(s['evidence']['C_material']>=.18 for s in segments)
    conflicts=sum(s['conflicted'] for s in segments);support=sum(s['supported'] for s in segments)/max(len(segments),1);stable=sum(s['stable'] for s in segments)/max(len(segments),1)
    bypass=[]
    for p in peers:
        x,y=p['local_point']
        if p['supported'] and mask[y,x]:bypass.append(p['feature_id'])
    reflection=bool(np.mean(m['hsv'][:,:,1][mask]>.3)<.5)
    complete=bool(segments and all(s['supported'] for s in segments) and min(ious)>=.9 and not bypass and not reflection)
    status='Supported complete proposal' if complete else ('Partial boundary / unresolved' if any(s['supported'] for s in segments) else 'Methods disagree / unresolved')
    reasons=[]
    if support<1:reasons.append('Some portions still lack a supported outer edge.')
    if conflicts:reasons.append('Some edges conflict with illuminated material continuity.')
    if min(ious)<.9:reasons.append('Parameter or context changes move parts of the proposal.')
    if included:reasons.append('Other bright points share the region; this alone does not mean different beads.')
    if bypass:reasons.append('A supported separator is still bypassed; possible neighboring material remains.')
    if reflection:reasons.append('This may outline a reflection rather than the visible bead surface.')
    if complete:reasons.append('Local measurements support the full contour; correctness awaits review.')
    dark_inside=(m['lum']<m['model']['floor_Y'])&mask;holes=ndi.binary_fill_holes(mask)&~mask
    evidence=dict(
      T1=dict(dark_supported_sides=T1,protected_separators=sum(p['supported'] for p in peers),bypassed_separators=bypass),
      T2=dict(multiscale_sides=T2,continuity_conflict_sides=conflicts),
      T3=dict(material_transition_sides=T3,target_material=m['model']),
      T4=dict(other_features_inside=included,interpretation='Shared visible region does not certify physical ownership.'),
      T5=dict(internal_dark_pixels=int(dark_inside.sum()),enclosed_excluded_pixels=int(holes.sum()),interpretation='Internal shadows/holes remain alternatives; no automatic hole fill.'),
      T6=dict(junction_sides=sum(s['evidence']['E_junction']>0 for s in segments),termination_sides=sum(s['evidence']['E_termination']>0 for s in segments),occluder_identity=None),
      T7=dict(total_sides=len(segments),supported_fraction=support,stable_fraction=stable,supported_arcs=len(arcs(segments)),unresolved_arcs=len(arcs(segments,False)),complete_proposal=complete,mechanism_agreement_sides=sum(sum(s['evidence'][k]>=t for k,t in [('A_dark_seam',.22),('B_multiscale',.22),('C_material',.18)])>=2 for s in segments)),
      T8=dict(core_pixels=int(core.sum()),peak_Y=float(m['lum'][core].max()),contrast_Y=float(m['lum'][core].max()-np.percentile(m['lum'],20)),perturbation_IoU=ious,centroid_spread_px=spread,reflection_edge_ambiguous=reflection,all_complementary_methods_attempted=True,photographic_insufficiency_asserted=False))
    return dict(status=status,reasons=reasons,candidate_pixels=dict(runs=runs(xy),pixel_count=len(xy)),candidate_centroid=center.tolist(),visible_region_centroid=None,segments=segments,supported_arcs=arcs(segments),unresolved_arcs=arcs(segments,False),evidence=evidence,uncertainty=dict(centroid_sensitivity_px=spread,physical_center=None,ownership=None))

def detect(rgb,feature,nearby=()):
    p=np.array(feature['point'],int);h,w=rgb.shape[:2];radius=PARAMETERS['initial_radius'];search=[]
    patch=pixels(dict(runs=feature.get('runs',[])))
    if not len(patch):patch=p.reshape(1,2)
    def setup(r):
        lo=np.maximum(p-r,0);hi=np.minimum(p+r+1,[w,h]);a=rgb[lo[1]:hi[1],lo[0]:hi[0]];seed=p-lo;m=measure(a,seed)
        core=np.zeros(a.shape[:2],bool);q=patch-lo;core[q[:,1],q[:,0]]=True
        near=[dict(id=q['id'],point=q['point'],local_point=(np.array(q['point'])-lo).tolist()) for q in nearby if q['id']!=feature['id'] and np.all(np.array(q['point'])>=lo+2) and np.all(np.array(q['point'])<hi-2)]
        access=direct_access(m,seed);peers=separators(m,seed,near)
        return lo,hi,m,core,near,access,peers
    while True:
        lo,hi,m,core,near,access,peers=setup(radius);mask=solve(m,core,access,peers)
        contact=bool(mask[:5].any() or mask[-5:].any() or mask[:,:5].any() or mask[:,-5:].any());search.append(dict(radius=radius,contact=contact))
        if not contact or radius>=PARAMETERS['maximum_radius']:break
        radius=min(2*radius,PARAMETERS['maximum_radius'])
    variants=[solve(m,core,access,peers,strength=s) for s in PARAMETERS['perturbations']]
    biglo,bighi,bigm,bigcore,bignear,bigaccess,bigpeers=setup(min(radius+16,PARAMETERS['maximum_radius']))
    bigmask=solve(bigm,bigcore,bigaccess,bigpeers);offset=lo-biglo;variants.append(bigmask[offset[1]:offset[1]+mask.shape[0],offset[0]:offset[0]+mask.shape[1]])
    alternative=solve(m,core,access,peers,alternative=True)
    A=describe(mask,m,lo,variants,near,peers,core)
    iou=float((mask&alternative).sum()/max((mask|alternative).sum(),1));B=describe(alternative,m,lo,[mask]+variants,near,peers,core) if iou<.97 else None
    # Keep coherent internal evidence even if the chosen contour bypasses it.
    context=[]
    for axis,f in enumerate(m['fields']):
        strong=f['A_dark_seam']>=.35
        for y,x in zip(*np.where(strong&ndi.binary_erosion(mask,iterations=2))):
            ends=[[x+lo[0]+.5,y+lo[1]-.5],[x+lo[0]+.5,y+lo[1]+.5]] if axis==0 else [[x+lo[0]-.5,y+lo[1]+.5],[x+lo[0]+.5,y+lo[1]+.5]]
            context.append(dict(endpoints=ends,strength=float(f['A_dark_seam'][y,x]),interpretation='Internal coherent dark edge: possible shadow/hole or missed separator.'))
    return dict(algorithm=VERSION,parameters=PARAMETERS,feature=feature,box=[int(lo[0]),int(lo[1]),int(hi[0]),int(hi[1])],search=search,A=A,B=B,alternative_explanation='B softens direct-dark interruptions and ambiguous separator ownership, preserving the same local evidence fields.',separators=peers,internal_edges=context,neighboring_features=[dict(feature_id=q['id'],point=q['point'],ownership=None) for q in near if np.linalg.norm(np.array(q['point'])-p)<=45],source_scope='One target, original pixels and independent features only. No case category, prior mask, judgment or physical model input.')
