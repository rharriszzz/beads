"""One-target R291 graph with measured separator arcs and local continuation."""
import numpy as np
from scipy import ndimage as ndi
from photo2.r282.common import pixels,runs
from photo2.r291.evidence import measure,direct_access,separators
from photo2.r291.detector import describe,PARAMETERS as BASE
from .graph import solve
from .separators import trace,crossing,PARAMETERS as TRACE
from .continuation import select

VERSION='R292-observed-separators-v3'
PARAMETERS=dict(base=BASE,tracing=TRACE,continuation='Local continuity-conflicted cut; no increase in unresolved outer sides',perturbations=[.85,1.15],context_extra=16)

def process(m,seed,core,near,*,strength=1.,access=None,peers=None):
    if access is None:access=direct_access(m,seed)
    if peers is None:peers=separators(m,seed,near)
    initial=solve(m,core,access,peers,strength=strength)
    arcs,barrier=trace(m,seed,peers,initial,core=core);barrier&=~core
    strict=solve(m,core,access,peers,strength=strength,seam_background=barrier)
    soft=solve(m,core,access,peers,strength=strength,stop_penalty=2.7,seam_background=barrier)
    relax,continuation=select(m,strict,soft)
    final=solve(m,core,access,peers,strength=strength,local_relax=relax,seam_background=barrier) if relax.any() else strict
    return final,strict,peers,arcs,barrier,continuation,initial

def detect(rgb,feature,nearby=()):
    p=np.array(feature['point'],int);h,w=rgb.shape[:2];radius=48;search=[];patch=pixels(feature)
    if not len(patch):patch=p.reshape(1,2)
    cache={}
    def setup(r,strength=1.):
        if r not in cache:
            lo=np.maximum(p-r,0);hi=np.minimum(p+r+1,[w,h]);m=measure(rgb[lo[1]:hi[1],lo[0]:hi[0]],p-lo);core=np.zeros(m['lum'].shape,bool);q=patch-lo;core[q[:,1],q[:,0]]=True
            near=[dict(id=q['id'],point=q['point'],local_point=(np.array(q['point'])-lo).tolist()) for q in nearby if q['id']!=feature['id'] and np.all(np.array(q['point'])>=lo+2) and np.all(np.array(q['point'])<hi-2)]
            access=direct_access(m,p-lo);peers=separators(m,p-lo,near);cache[r]=(lo,hi,m,core,near,access,peers)
        lo,hi,m,core,near,access,peers=cache[r]
        return lo,hi,m,core,near,process(m,p-lo,core,near,strength=strength,access=access,peers=peers)
    while True:
        lo,hi,m,core,near,result=setup(radius);mask,strict,peers,arcs,barrier,continuation,initial=result
        contact=bool(mask[:5].any() or mask[-5:].any() or mask[:,:5].any() or mask[:,-5:].any());search.append(dict(radius=radius,contact=contact))
        if not contact or radius>=144:break
        radius=min(radius*2,144)
    variants=[setup(radius,s)[-1][0] for s in (.85,1.15)]
    biglo,bighi,bigm,bigcore,bignear,bigresult=setup(min(radius+16,144));delta=lo-biglo;variants.append(bigresult[0][delta[1]:delta[1]+mask.shape[0],delta[0]:delta[0]+mask.shape[1]])
    def description(candidate):
        d=describe(candidate,m,lo,variants,near,peers,core);cross=crossing(candidate,arcs)
        d['evidence']['T1'].update(tracked_separator_arcs=len(arcs),enforced_arcs=sum(a['enforced'] for a in arcs),arc_crossings=cross)
        d['evidence']['T5']['enclosed_dark_arcs_not_enforced']=sum(not a['enforced'] for a in arcs)
        d['evidence']['T7']['unresolved_separator_endings']=2*len(arcs)
        d['evidence']['T8']['separator_and_continuation_recomputed_under_perturbations']=True
        d['evidence']['T4']['remaining_separator_bank_connections']=sum(q['routed_around_samples'] for q in cross if q['enforced'])
        if d['evidence']['T4']['remaining_separator_bank_connections']:d['reasons'].append('Both banks remain source-connected around an unresolved separator end; possible merger remains.')
        d['status']='Partial boundary / unresolved';d['reasons'].append('Tracked separator endings remain unresolved; exterior connection is evidence, not certified ownership.')
        d['uncertainty']['photographic_insufficiency_asserted']=False
        return d
    A=description(mask);iou=float((mask&strict).sum()/max((mask|strict).sum(),1));B=description(strict) if iou<.97 else None
    recorded=[]
    for a in arcs:
        recorded.append(dict(a,path=(np.asarray(a['local_path'])+lo).tolist(),endings=[dict(point=(np.array(e['point'])+lo).tolist(),status=e['status']) for e in a['endings']]))
    context=[]
    for axis,f in enumerate(m['fields']):
        for y,x in zip(*np.where((f['A_dark_seam']>=.35)&ndi.binary_erosion(mask,iterations=2))):
            ends=[[x+lo[0]+.5,y+lo[1]-.5],[x+lo[0]+.5,y+lo[1]+.5]] if axis==0 else [[x+lo[0]-.5,y+lo[1]+.5],[x+lo[0]+.5,y+lo[1]+.5]]
            context.append(dict(endpoints=ends,strength=float(f['A_dark_seam'][y,x]),interpretation='Coherent internal edge remains an unresolved shadow/hole/separator alternative.'))
    return dict(algorithm=VERSION,parameters=PARAMETERS,feature=feature,box=[*lo.tolist(),*hi.tolist()],search=search,A=A,B=B,alternative_explanation='B keeps the same separator constraints but omits locally supported continuation across dark interruptions.',separator_arcs=recorded,separators=peers,separator_comparison=dict(before=crossing(initial,arcs),after=crossing(mask,arcs)),continuation=continuation,internal_edges=context,neighboring_features=[dict(feature_id=q['id'],point=q['point'],ownership=None) for q in near if np.linalg.norm(np.array(q['point'])-p)<=45],source_scope='Original pixels, selected independent patch and nearby independent features only; no case IDs, previous contours or user judgments.')
