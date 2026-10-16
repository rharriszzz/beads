"""Native finalist ranking, sealed comparisons and complete visible-surface export."""
from pathlib import Path
from copy import deepcopy,copy
import csv,json,time
import numpy as np
from PIL import Image,ImageOps
from scipy.spatial import cKDTree
from photo2.r297.common import ROOT,read,save,sha,utc,pixels
from photo2.r297.geometry import reference,contact
from photo2.r299.forward import Surface
from photo2.r298.fft import diagnostic as fft_diagnostic
from photo2.r305.forward import segments
from .geometry import Chain
from .evidence import load
from .objective import Objective,predict,match,contour_samples,contours

def fft_for_scene(scene):
    # R298's diagnostic expects the rope tangent/planar normal, whereas R306's
    # body frame includes hole-axis tilt and rotation about that axis.
    from photo2.r295.geometry import AXES,unit
    proxy=copy(scene);original=scene.placement
    def placement(k):
        k=np.asarray(k);line,g,phase=original(k)
        tangent=unit(original(k+.005)[0]-original(k-.005)[0]);z=np.tile([0.,0.,1.],(len(k),1));normal=np.cross(z,tangent)
        return line,dict(zip(AXES,(tangent,normal,z)),radial=g['radial']),phase
    proxy.placement=placement
    result=fft_diagnostic(proxy);result['frame']='Geometric rope tangent and planar normal; independent of the tilted bead-hole frame.'
    return result

def historic_models():
    out=[]
    for tag,ident in [('R297',0),('R298-primary',49),('R298-hand-plus-open',29),('R298-hand-plus-closed',76)]:
        doc=read(ROOT/f'photo2/r299/results/fixed-{ident}-directional.json.gz');p=deepcopy(doc['parameters']);light=doc['fit']['light'];d=np.array(light['direction'])
        p.update(light_az=float(np.degrees(np.arctan2(d[1],d[0]))),light_el=float(np.degrees(np.arcsin(d[2]))),roughness=light['roughness_deg'])
        out.append(dict(name=tag,parameters=p,historical=True,source=f'photo2/r299/results/fixed-{ident}-directional.json.gz'))
    doc=read(ROOT/'photo2/r299/results/joint-history.json.gz')[15];p=deepcopy(doc['parameters']);light=doc['fit']['light'];d=np.array(light['direction'])
    p.update(light_az=float(np.degrees(np.arctan2(d[1],d[0]))),light_el=float(np.degrees(np.arcsin(d[2]))),roughness=light['roughness_deg'])
    out.append(dict(name='R299-primary',parameters=p,historical=True,source='photo2/r299/results/joint-history.json.gz:15'))
    return out

def native_envelope(scene,m,owner=None):
    xy=np.concatenate([np.asarray(r['samples_xy']) for r in m['envelope']]).astype(int)
    o=owner[xy[:,1],xy[:,0]] if owner is not None else scene.trace(xy)['owner']
    out=[]
    for lines in o.reshape(len(m['envelope']),9,191):
        bounds=[]
        for line in lines:
            hit=np.flatnonzero(line>=0);bounds.append([float(hit[0]-95),float(hit[-1]-95)] if len(hit) else [0.,0.])
        out.append(np.median(bounds,axis=0))
    return np.asarray(out)

def native_assess(scene,obj,pred,en):
    result=obj.assess(scene,reflections=True,pred=pred)
    er=en[obj.ei]-obj.targete[obj.ei]
    loss=float(np.mean(np.minimum((er/obj.envelope_uncertainty[obj.ei])**2,16)))
    result['loss']+=loss-result['envelope_loss'];result['structural_loss']+=loss-result['envelope_loss'];result['envelope_loss']=loss
    result.update(envelope=en.tolist(),envelope_edge_mae=float(np.mean(abs(er))),envelope_width_mae=float(np.mean(abs(np.diff(er,axis=1)))),envelope_common_mae=float(np.mean(abs(er.mean(1)))))
    return result

def stats(records):
    rows=[r for r in records if r['error_px'] is not None];e=np.array([r['error_px'] for r in rows])
    return dict(n=len(e),rms=float(np.sqrt(np.mean(e*e))) if len(e) else None,median=float(np.median(e)) if len(e) else None,
                p90=float(np.percentile(e,90)) if len(e) else None,tangent_mean=float(np.mean([r['tangent_px'] for r in rows])) if rows else None,
                normal_mean=float(np.mean([r['normal_px'] for r in rows])) if rows else None,
                unmatched=sum(r['error_px'] is None for r in records),ambiguous=sum(r['status']=='ambiguous' for r in records))

def correspondences(obs,pred,scene):
    # Strong observations matched first; weak/diffuse catalog cannot steal owners.
    strong=[r for r in obs if r['strong']];weak=[r for r in obs if not r['strong']]
    paths={q:match(strong,pred,q) for q in [12.,24.,48.]};best=paths[24.]
    used={r['index'] for r in best['records'] if r['index'] is not None}
    other=match(weak,[r for r in pred if r['index'] not in used],24.)
    mappings={q:{r['id']:r['index'] for r in v['records']} for q,v in paths.items()}
    rows=best['records']+other['records']
    for r in rows:
        r['observation']=r['id'];r['quality']='strong localized' if r['strong'] else 'weak / diffuse / uncertain'
        r['penalty_owners']={str(int(q)):m.get(r['id']) for q,m in mappings.items()} if r['strong'] else {}
        r['stable_across_gap_penalties']=all(m.get(r['id'])==r['index'] for m in mappings.values()) if r['strong'] else False
        if r['status']=='conditional':r['status']='confident conditional' if r['strong'] and r['stable_across_gap_penalties'] else 'ambiguous'
    rows.sort(key=lambda r:r['arc'])
    # Unconstrained-nearest control exposes the gain from allowing duplicate owners.
    distances=cKDTree([p['point'] for p in pred]).query([r['point'] for r in strong])[0]
    return dict(records=rows,summary_strong=stats([r for r in rows if r['strong']]),
                assignment_sensitivity=sum(not r['stable_across_gap_penalties'] for r in rows if r['strong']),
                gap_controls={str(int(q)):{k:v for k,v in a.items() if k!='records'} for q,a in paths.items()},
                nearest_nonunique_rms=float(np.sqrt(np.mean(distances**2))),
                unmatched_predictions=[p['index'] for p in pred if p['index'] not in {r['index'] for r in rows}],
                policy='One-to-one global spatial assignment with explicit 24px unmatched cost; strong evidence first, weak evidence on unused predictions. Helical projection can reverse local order. 12/48px costs, duplicate-owner nearest control and fixed-owner controls expose assignment dependence. No historic bead identity enforced.',
                unmatched_outside_model_geography=[])

def complete_supports(scene,data,owner,unknown):
    out=[]
    for r in data['rows']:
        xy=pixels(r['pixels']);o=owner[xy[:,1],xy[:,0]];ids,count=np.unique(o[o>=0],return_counts=True);order=np.argsort(-count)
        alternatives=[dict(index=int(scene.indices[ids[j]]),fraction=float(count[j]/len(xy))) for j in order]
        fraction=alternatives[0]['fraction'] if alternatives else 0.
        out.append(dict(id=r['id'],kind=r['kind'],split=r['split'],point=r['point'],station=r['station'],fraction=fraction,
                        index=alternatives[0]['index'] if alternatives else None,alternatives=alternatives,
                        compatible=bool(fraction>=.8 and (len(alternatives)<2 or fraction-alternatives[1]['fraction']>=.2)),
                        pixels=len(xy),unknown=int(unknown[xy[:,1],xy[:,0]].sum())))
    return out

def neighbor_predictions(scene):
    """Preserve +1/+6/+7 predictions without inventing observed identities."""
    from photo2.r295.geometry import AXES
    rows=[]
    for lag in [1,6,7]:
        a=np.arange(scene.n if scene.closed else scene.n-lag);b=(a+lag)%scene.n
        world=scene.centers[b]-scene.centers[a];distance=np.linalg.norm(world,axis=1);v=world/distance[:,None]
        margin=distance-scene.support(v,scene.g[AXES[0]][a])-scene.support(v,scene.g[AXES[0]][b])
        projected=scene.pc[b]-scene.pc[a]
        rows.append(dict(lag=lag,from_indices=scene.indices[a].tolist(),to_indices=scene.indices[b].tolist(),
            projected_vectors_px=projected.tolist(),center_distance_units=distance.tolist(),directional_support_margin_units=margin.tolist()))
    return dict(rows=rows,historical_context=['photo2/R300_REPORT.md','photo2/r302/results/gap-sensitivity.json'],
        interpretation='Conditional model predictions only. No verified photographic +1/+6/+7 identities exist. These margins use center-direction support and are not minimum surface distances or the full contact certificate. No penalty or training information is added.')

def export_model(item,out,data,m,obs,objects):
    name=item['name'];target=out/'exports'/f'{name}.json.gz'
    if target.exists():return read(target)
    t=time.monotonic();scene=(Surface if item.get('historical') else Chain)(item['parameters'],data)
    cert=contact(scene,exact=True)
    if not cert['certified']:raise ValueError(f'Finalist {name} fails full-chain audit')
    pred,meta=predict(scene,1.,None,True);xy=meta.pop('xy');own=meta.pop('owner');intensity=meta.pop('intensity')
    owner=np.full((3182,2540),-1,np.int16);owner[xy[:,1].astype(int),xy[:,0].astype(int)]=own
    # Recompute unknown flags only when needed for native evidence; the sparse
    # renderer records counts, while exact flags are independently replayed here.
    unknown=np.zeros(owner.shape,bool)
    for i in range(0,len(xy),24000):unknown[xy[i:i+24000,1].astype(int),xy[i:i+24000,0].astype(int)]=scene.trace(xy[i:i+24000])['unknown']
    address=np.full(owner.shape,-32768,np.int16);good=owner>=0;address[good]=scene.indices[owner[good]]
    np.savez_compressed(out/'exports'/f'{name}-raster.npz',owner=owner,address=address,unknown=unknown,xy=xy,intensity=intensity)
    en=native_envelope(scene,m,owner);evaluation={s:native_assess(scene,o,pred,en) for s,o in objects.items()}
    corr=correspondences(obs,pred,scene);supports=complete_supports(scene,data,owner,unknown)
    projected_axis=scene.project(scene.line);arc=reference().project(projected_axis)['arc'];lookup={p['index']:p for p in pred};positions=[]
    # One full-circuit model: all N bodies are retained even when wholly hidden.
    for j,k in enumerate(scene.indices):
        x,y=scene.pc[j];rad=scene.query_radius+2;x0=max(0,int(x-rad));x1=min(2540,int(x+rad)+2);y0=max(0,int(y-rad));y1=min(3182,int(y+rad)+2)
        mask=owner[y0:y1,x0:x1]==j;visible=int(mask.sum());h=lookup.get(int(k))
        positions.append(dict(index=int(k),center=scene.centers[j].tolist(),projected_center=scene.pc[j].tolist(),axis_xy=projected_axis[j].tolist(),
            phase=float(scene.phase[j]),photo_arc=float(arc[j]),visible_area_px2=visible,visible_fraction=None,
            visibility='native visible surface' if visible else 'no native visible samples; body retained',
            reflection=dict(centroid=h['point'],peak=h['peak'],peak_intensity=h['strength'],area_px2=h['area_px2']) if h else None,
            boundary_segments=segments(mask,x0,y0) if visible else [],uncertified_pairs=[],numerical=None))
    # Same immutable material cues, grouped by geographic arc and conditional index.
    cues=np.load(ROOT/'photo2/r296/evidence/cues.npz');ij=cues['xy'].astype(int);go=owner[ij[:,1],ij[:,0]]
    regions=[]
    for j in range(32):
        keep=(cues['station']/data['length']*32).astype(int)%32==j;pp=keep&cues['paper'];cc=keep&(cues['color']>0)
        rr=[r for r in corr['records'] if r['section']==j and r['strong']]
        ss=[r for r in supports if r['kind']=='region' and int(r['station']/data['length']*32)%32==j]
        regions.append(dict(section=j,**stats(rr),paper_samples=int(pp.sum()),colored_samples=int(cc.sum()),
            paper_occupation=float(np.mean(go[pp]>=0)) if pp.any() else None,colored_omission=float(np.mean(go[cc]<0)) if cc.any() else None,
            support_count=len(ss),support_containment=float(np.mean([r['fraction'] for r in ss])) if ss else None,
            split='comparison' if j%4==3 else 'development'))
    nearest=scene.tree.query(cues['xy'])[1];cue_index=scene.indices[nearest];groups=[]
    for first in range(int(scene.indices[0]),int(scene.indices[-1])+1,50):
        last=min(first+49,int(scene.indices[-1]));bs=[b for b in positions if first<=b['index']<=last]
        rr=[r for r in corr['records'] if r['index'] is not None and first<=r['index']<=last];strong=[r for r in rr if r['strong']]
        pp=(cue_index>=first)&(cue_index<=last)&cues['paper'];cc=(cue_index>=first)&(cue_index<=last)&(cues['color']>0)
        groups.append(dict(first=first,last=last,**stats(strong),insufficient_evidence=len(strong)<3,
            colored_omission=float(np.mean(go[cc]<0)) if cc.any() else None,paper_occupation=float(np.mean(go[pp]>=0)) if pp.any() else None,
            examples=dict(unmatched_observed=[],unassigned_predicted=[b['index'] for b in bs if b['reflection'] and b['index'] in corr['unmatched_predictions']],
                no_predicted_reflection=[b['index'] for b in bs if b['visible_area_px2'] and not b['reflection']],occluded=[b['index'] for b in bs if not b['visible_area_px2']],
                ambiguous=[r['index'] for r in rr if r['status']=='ambiguous'],physical_failure=[])))
    for r in corr['records']:
        if r['index'] is None:
            k=int(scene.indices[scene.tree.query(r['observed'])[1]])
            next(g for g in groups if g['first']<=k<=g['last'])['examples']['unmatched_observed'].append(dict(index=k,id=r['id']))
    corr['groups']=groups;corr['rolling']=[dict(index=k,**stats([r for r in corr['records'] if r['strong'] and r['index'] is not None and abs(r['index']-k)<=25])) for k in range(int(scene.indices[0]),int(scene.indices[-1])+1,10)]
    outmodel=dict(**item,physical=cert,closure=scene.closure(),positions=positions,bounds=[0,0,2539,3181],
        evaluation=evaluation,correspondences=corr,supports=supports,regions=regions,numerics=meta,seconds=time.monotonic()-t,
        reference_departure_px=reference().project(projected_axis)['signed'].tolist(),fft=fft_for_scene(scene))
    if not item.get('historical'):
        u=np.linspace(0,reference().length,16385);d1=scene.spline(u,1);d2=scene.spline(u,2)
        curvature=abs(d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])/np.linalg.norm(d1,axis=1)**3
        dense_axis=scene.project(np.c_[scene.spline(u),np.zeros(len(u))])
        outmodel['geometric_axis_xy']=dense_axis[::8].tolist()
        outmodel['geometry_definition']=dict(reference='photo2/r282/results/centerline.json',reference_unchanged=True,
            axis='One periodic planar normal-displacement spline,32 adjustable nodes; numerical true-arclength inversion, no circle splice.',
            reference_length_px=reference().length,projected_geometric_length_px=float(np.linalg.norm(np.diff(dense_axis,axis=0),axis=1).sum()),
            radius_is_unit_gauge=True,arclength_integration_samples=16385,maximum_curvature_per_radius=float(curvature.max()*scene.radius),
            actual_mean_advance_units=scene.extent/scene.n,unused_historical_parameters=['pitch','bend','strain','phase_knots','local_bend','local_metric','local_turn','phase_transport','local_phase_bias','yaw'],
            guards='All N physical bodies retained in every ray/contact query. Closed seam uses the same bodies once; open models have real conditional endpoints, no invented guard bodies.')
    outmodel['native_contours']=contours(scene,contour_samples(m['beads'],1.))
    save(out/'exports'/f'{name}-neighbor-predictions.json.gz',neighbor_predictions(scene))
    save(target,outmodel)
    for label,rows in [('errors',corr['records']),('regions',regions),('positions',[{k:v for k,v in b.items() if k in ('index','projected_center','center','visible_area_px2','phase','photo_arc')} for b in positions])]:
        with (out/'exports'/f'{name}-{label}.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(name,'export',round(outmodel['seconds'],2),'seconds',cert['pairs'],'pairs',corr['summary_strong'],flush=True)
    return outmodel

def finalize(out,native_seconds=0.):
    out=Path(out);(out/'exports').mkdir(exist_ok=True);data,m,obs=load();state=read(out/'checkpoint.json')
    from .search import fingerprints
    if state['sources']!=fingerprints():raise ValueError('Scientific source changed since fitting; native selection requires the frozen implementation')
    if any(sha(ROOT/p)!=h for p,h in state['evidence'].items()):raise ValueError('Evidence changed since fitting')
    objectives={s:Objective(data,m,obs,s) for s in ['development','comparison']}
    for o in objectives.values():o.contour_samples=contour_samples([m['beads'][i] for i in o.bi],1.)
    seal=out/'selection.json'
    if not seal.exists():
        ranking=[]
        extra=[]
        if (out/'native-progress.json.gz').exists():
            extra=[r['id'] for r in sorted(read(out/'native-progress.json.gz'),key=lambda r:r['native']['loss'])[:4]]
        candidates=[(i,f'candidates/{i:06d}.json.gz') for i in dict.fromkeys(state['pool']+extra)]
        if (out/'additional-runs.json').exists():
            from .pack import restore
            for relative in read(out/'additional-runs.json')['runs']:
                source=out/relative;other=read(source/'checkpoint.json')
                if other['sources']!=state['sources'] or other['evidence']!=state['evidence']:raise ValueError('Additional run uses a different scientific objective/evidence')
                if not other['stop_reason']:raise ValueError('Additional fitting run must finish before joint selection')
                restore(source);families=set()
                for i in other['pool']:
                    r=read(source/'candidates'/f'{i:06d}.json.gz');family=(r['parameters']['hand'],r['parameters']['topology'])
                    if family not in families:
                        candidates.append((f'{source.name}-{i}',f'{relative}/candidates/{i:06d}.json.gz'));families.add(family)
        for i,source in candidates:
            t=time.monotonic();r=read(out/source);s=Chain(r['parameters'],data)
            cert=contact(s,exact=True)
            if not cert['certified']:raise ValueError('Promoted candidate failed exact contact')
            p,meta=predict(s,1.,objectives['development'].obs);en=native_envelope(s,m)
            result=native_assess(s,objectives['development'],p,en)
            ranking.append(dict(id=i,source=source,parameters=r['parameters'],loss=result['loss'],train=result,numerics=meta,seconds=time.monotonic()-t))
            save(out/'native-ranking.json.gz',ranking);print('native rank',i,result['loss'],flush=True)
        ranking.sort(key=lambda r:r['loss'])
        if native_seconds:
            from .native_refine import refine
            best=refine(out,ranking[0],data,m,obs,native_seconds)
            if best['id']!=ranking[0]['id']:ranking.append(best);ranking.sort(key=lambda r:r['loss'])
        selected=[ranking[0]];families={(ranking[0]['parameters']['hand'],ranking[0]['parameters']['topology'])}
        for r in ranking[1:]:
            family=(r['parameters']['hand'],r['parameters']['topology'])
            if family not in families:selected.append(r);families.add(family)
        selection=dict(utc=utc(),primary=ranking[0]['id'],finalists=[r['id'] for r in selected],ranking=[dict(id=r['id'],loss=r['loss']) for r in ranking],
            selected_sources=[dict(id=r['id'],source=r['source'],parameters=r['parameters']) for r in selected],
            policy='Native training only, full contact required. One per hand/topology, no comparison outcomes inspected before this seal.')
        save(seal,selection);state['sealed']=True;state['selection']=selection;save(out/'checkpoint.json',state)
        if (out/'additional-runs.json').exists():
            for relative in read(out/'additional-runs.json')['runs']:
                path=out/relative/'checkpoint.json';other=read(path);other['sealed']=True;other['joint_selection']=str(seal);save(path,other)
    selection=read(seal);items=[]
    sources=selection.get('selected_sources')
    if sources is None:sources=[dict(id=i,source=f'candidates/{i:06d}.json.gz') for i in selection['finalists']]
    for source in sources:
        i=source['id'];row=read(out/source['source']);items.append(dict(name='primary' if i==selection['primary'] else f'alternative-{i}',candidate=i,parameters=row['parameters'],historical=False,source=source['source']))
    items+=historic_models()
    models=[export_model(item,out,data,m,obs,objectives) for item in items]
    from .diagnose import diagnose
    diagnose(out,models,data,m,obs)
    from .review import build
    build(out,models,m,obs)
    save(out/'export-manifest.json',dict(utc=utc(),models={r['name']:sha(out/'exports'/f'{r["name"]}.json.gz') for r in models},selection=selection))
    from .ledger import build as computation_ledger
    computation_ledger(out)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);finalize(ap.parse_args().output)
