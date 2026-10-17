"""Seal choices, measure dense whole circuits and publish reviewable evidence."""
from pathlib import Path
from copy import deepcopy,copy
import time,csv,json
import numpy as np
from scipy.ndimage import binary_erosion
from PIL import Image,ImageOps,ImageDraw
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r306.export import correspondences,complete_supports
from photo2.r305.forward import segments
from photo2.r309.render import predict
from photo2.r309.measure import Measures,reference_dimension,summarize,distances
from photo2.r309.delivery import combined,complete_boundary
from .model import starts,scene,VARIABLES,PAIRS
from .diagnostics import FirstErrors
from .search import coordinate_distance,sources

def publication_name(seed):
    # Immutable trial-family keys are retained for source/checkpoint replay.
    # User-facing control labels follow the actual stored count/hand/topology.
    if seed['name'].startswith('R306-plus'):
        p=seed['parameters'];return f"R306-{p['count']}-plus-{p['topology']}"
    return seed['name']

def neighbor_detail(s,targets,positions,data,D):
    """Conditional adjacent-body behavior; no photographic identity is added."""
    from scipy.spatial import cKDTree
    from photo2.r307.fast import Chain as Fast
    from photo2.r297.common import pixels
    byindex={b['index']:b for b in positions}
    for row in targets:
        source=next(r for r in data['rows'] if r['id']==row['id'] and r['kind']=='region')
        row['photographic_runs']=deepcopy(source['pixels']['runs'])
        pts=pixels(source['pixels']);full=s.trace(pts);good=(full['owner']>=0)&~full['unknown']
        for alt in row['isolated_candidates']:
            j=int(np.searchsorted(s.indices,alt['index']));one=copy(s);one.n=1;one.indices=s.indices[j:j+1];one.centers=s.centers[j:j+1];one.pc=s.pc[j:j+1]
            one.g={k:v[j:j+1] for k,v in s.g.items()};one.tree=cKDTree(one.pc)
            tr=Fast.trace(one,pts);hit=(tr['owner']>=0)&~tr['unknown']
            hidden=hit&good&(full['owner']!=j);js,counts=np.unique(full['owner'][hidden],return_counts=True)
            alt['resolved_occluded_fraction']=float(hidden.mean())
            alt['unknown_after_isolation_fraction']=float((hit&full['unknown']).mean())
            alt['nonvisible_fraction']=alt['occluded_fraction']
            alt['occluded_fraction']=alt['resolved_occluded_fraction']
            alt['occluding_owners']=[dict(index=int(s.indices[k]),fraction_of_original_interior=float(n/len(pts))) for k,n in zip(js,counts)]
            body=byindex[alt['index']];alt['whole_body_visible_area_px2']=body['visible_area_px2']
            alt['modeled_projected_center']=body['projected_center'];alt['modeled_depth_units']=float(s.centers[j]@s.eye)
            neighbors=[]
            for delta in [-7,-6,-1,1,6,7]:
                k=alt['index']+delta
                if s.closed:k=int(s.indices[0]+(k-s.indices[0])%s.n)
                if k not in byindex:continue
                b=byindex[k];v=np.array(b['projected_center'])-body['projected_center']
                neighbors.append(dict(conditional_step=delta,index=k,vector_px=v.tolist(),distance_D=float(np.linalg.norm(v)/D),
                                      whole_body_visible_area_px2=b['visible_area_px2'],modeled_projected_center=b['projected_center'],
                                      depth_difference_units=float((s.centers[k-int(s.indices[0])]-s.centers[j])@s.eye)))
            alt['conditional_neighbors']=neighbors
        row['occlusion_policy']='Resolved neighbor masking and full-scene unknown rays are separate. Centers and +/-1/6/7 vectors are modeled predictions, never photographic physical identities.'
    return targets

def choose(out):
    state=read(out/'checkpoint.json');assert state['sources']==sources()
    rows=[read(p) for p in sorted((out/'trials').glob('*.gz'))];items=[]
    for seed in starts():
        base=next(r for r in rows if r['kind']=='start' and r['family']==seed['name'])
        label=publication_name(seed)
        items.append(dict(name=label+'-baseline',family=seed['name'],parameters=base['parameters'],implementation=seed['implementation'],trial=base['id'],baseline=True))
        rr=[r for r in rows if r['family']==seed['name'] and r['feasible']]
        selected=[]
        for criterion in ['global','first-errors']:
            reference=base['first_errors'][0]['modal_fraction']
            pool=rr if criterion=='global' else [r for r in rr if r['global_score']<=base['global_score']*1.15 and r['first_errors'][0]['modal_fraction']>=reference-.05]
            best=min(pool,key=lambda r:r['global_score'] if criterion=='global' else r['target_loss'])
            if best['key']==base['key'] or any(best['key']==r['key'] for r in selected):continue
            selected.append(best)
            items.append(dict(name=label+'-'+criterion,family=seed['name'],parameters=best['parameters'],implementation=seed['implementation'],trial=best['id'],baseline=False,selection=criterion))
    save(out/'selection.json',dict(utc=utc(),models=items,policy='Sealed before dense/comparison evaluation: global development winner and first-error winner constrained to <=115% baseline global score and <=5pp reference-coverage loss per family. Reference preservation was already an acceptance condition; do not export a dominated local winner that sacrifices the trusted reference. All rejected tradeoffs remain in trials. Baselines retained even if no candidate wins. No fresh validation claim.'))
    state['sealed']=True;save(out/'checkpoint.json',state)
    return items

def export(item,out,data,m,obs):
    name=item['name'];file=out/'exports'/f'{name}.json.gz'
    if file.exists():return read(file)
    began=time.monotonic();s=scene(item['parameters'],data,item['implementation'])
    cert=s.certify(iterations=220,witnesses=True);assert cert['certified']
    pred,meta=predict(s,1.,detail=True)
    xy=meta.pop('xy');own=meta.pop('owner');intensity=meta.pop('intensity');unc=meta.pop('unknown')
    owner=np.full((3182,2540),-1,np.int16);unknown=np.zeros(owner.shape,bool)
    ij=xy.astype(int);owner[ij[:,1],ij[:,0]]=own;unknown[ij[:,1],ij[:,0]]=unc
    address=np.full(owner.shape,-32768,np.int16);good=(owner>=0)&~unknown;address[good]=s.indices[owner[good]]
    np.savez_compressed(out/'exports'/f'{name}-raster.npz',owner=owner,address=address,unknown=unknown,xy=xy,intensity=intensity)
    lookup={p['index']:p for p in pred};positions=[]
    for j,k in enumerate(s.indices):
        x,y=s.pc[j];rad=s.query_radius+3
        low=np.maximum([0,0],np.floor([x-rad,y-rad])).astype(int)
        hi=np.minimum([2540,3182],np.ceil([x+rad,y+rad])).astype(int)
        mask=(owner[low[1]:hi[1],low[0]:hi[0]]==j)&~unknown[low[1]:hi[1],low[0]:hi[0]]
        h=lookup.get(int(k))
        positions.append(dict(index=int(k),center=s.centers[j].tolist(),projected_center=s.pc[j].tolist(),axis_xy=s.project(s.line[j:j+1])[0].tolist(),phase=float(s.phase[j]),visible_area_px2=int(mask.sum()),reflection=h,boundary_segments=segments(mask,int(low[0]),int(low[1]))))
    corr=correspondences(obs,pred,s)
    targets=neighbor_detail(s,FirstErrors(data).evaluate(s),positions,data,reference_dimension(m)['D_px'])
    model=dict(**item,physical=cert,positions=positions,closure=s.closure(),predictions=pred,correspondences=corr,
               supports=complete_supports(s,data,owner,unknown),first_errors=targets,numerics=meta,
               all_observations=len(obs),seconds=time.monotonic()-began)
    save(file,model);print('export',name,'seconds',round(model['seconds'],1),flush=True)
    return model

def measure(item,model,out,data,m,obs,baseline):
    file=out/'metrics'/f"{item['name']}.json.gz"
    if file.exists():return read(file)
    s=scene(item['parameters'],data,item['implementation']);raster=np.load(out/'exports'/f"{item['name']}-raster.npz")
    detail={};fixed={}
    for split in ['development','comparison']:
        obj=Measures(data,m,obs,split,dense=True);result=obj.evaluate(s)
        complete_boundary(model,raster,obj,result);detail[split]=result
        if item['baseline']:fx=result
        else:fx=obj.evaluate(s,baseline['detail'][split]['anchors'])
        refs=fx['reflections'];errors=[r['error_px'] if r['error_px'] is not None else 48. for r in refs]
        fixed[split]=dict(reflections=refs,metrics=distances(refs,obj.D),penalized_RMS_px=float(np.sqrt(np.mean(np.square(errors)))),
                          penalized_RMS_D=float(np.sqrt(np.mean(np.square(errors)))/obj.D),missing=fx['missing'],
                          fixed_interior_percent=100*float(np.mean([r['fraction'] for r in fx['supports']])),
                          policy='Conditional original family owners; missing lobes retain48px penalty. These are not verified physical identities.')
    both=combined(detail);D=reference_dimension(m)['D_px'];overall=summarize(both,D)
    refs=sum([f['reflections'] for f in fixed.values()],[]);e=[r['error_px'] if r['error_px'] is not None else 48. for r in refs]
    fixed['overall']=dict(metrics=distances(refs,D),penalized_RMS_px=float(np.sqrt(np.mean(np.square(e)))),penalized_RMS_D=float(np.sqrt(np.mean(np.square(e)))/D),missing=sum(fixed[k]['missing'] for k in ['development','comparison']))
    regional=[]
    for section in range(32):
        su=[r for r in both['supports'] if r['section']==section]
        rf=[r for r in both['reflections'] if r['section']==section]
        mat=next((r for r in both['material'] if r['section']==section),None)
        regional.append(dict(section=section,interior_regions=len(su),
                             ownership_percent=100*float(np.mean([r['modal_fraction'] for r in su])) if su else None,
                             reflection=distances(rf,D),material=mat))
    result=dict(detail=detail,overall=overall,fixed=fixed,D_px=D,first_errors=model['first_errors'],regional=regional)
    save(file,result);return result

def acceptance(metrics,baseline):
    a,b=metrics['overall'],baseline['overall'];x={r['id']:r for r in metrics['first_errors']};y={r['id']:r for r in baseline['first_errors']}
    thresholds={k:max(.8,y[k]['modal_fraction']-.05) if y[k]['modal_fraction']>=.8 else max(.8,min(.9,y[k]['modal_fraction']+.15)) for k in ['C-1477-0290','C-1608-0253']}
    checks={
      'negative_first_error_repaired_or_preserved':x['C-1477-0290']['modal_fraction']>=thresholds['C-1477-0290'],
      'positive_first_error_repaired_or_preserved':x['C-1608-0253']['modal_fraction']>=thresholds['C-1608-0253'],
      'reference_no5pp_regression':x['C-1497-0271']['modal_fraction']>=y['C-1497-0271']['modal_fraction']-.05,
      'whole_ownership_plus2pp':a['ownership']['coherent_percent']>=b['ownership']['coherent_percent']+2.,
      'reflection_RMS_improves5percent':a['reflection']['rms_D']<=b['reflection']['rms_D']*.95,
      'boundary_RMS_no_point02D_regression':a['boundary']['rms_D']<=b['boundary']['rms_D']+.02,
      'background_no1pp_regression':a['material']['background_occupation_percent']<=b['material']['background_occupation_percent']+1.,
      'foreground_no1pp_regression':a['material']['foreground_omission_percent']<=b['material']['foreground_omission_percent']+1.,
      'missing_no_regression':a['reflection']['missing']<=b['reflection']['missing'],
      'supported_boundary_missing_no_regression':a['boundary']['missing']<=b['boundary']['missing'],
      'fixed_owners_no_point02D_regression':metrics['fixed']['overall']['penalized_RMS_D']<=baseline['fixed']['overall']['penalized_RMS_D']+.02,
    }
    geometric={k:v for k,v in checks.items() if not k.startswith('fixed_owners')}
    return dict(checks=checks,passes=bool(all(checks.values())),geometric_passes=bool(all(geometric.values())),first_error_coverage_thresholds=thresholds,
                policy='Engineering review thresholds, not confidence intervals or new physical identity evidence. Coverage-ceiling clarification was recorded before selection/comparison; objective/proposals unchanged. Conditional raw fixed-index errors are also reported separately: regression alone does not prove bad material geometry when identity is unverified.')

def atlas(out,models):
    review=ROOT/'photo2/review/r311';review.mkdir(parents=True,exist_ok=True)
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');photo.save(review/'photo.png')
    records=[]
    centers=[(1499,271),(1480,291),(1460,313),(1613,253),(1110,336),(550,603),(2301,1896)]
    for i,(x,y) in enumerate(centers):
        crop=[x-85,y-70,x+85,y+70];raw=photo.crop(crop);raw.save(review/f'raw-{i}.png')
        for model in models:
            canvas=raw.copy();draw=ImageDraw.Draw(canvas)
            for b in model['positions']:
                xx,yy=b['projected_center']
                if not crop[0]-60<xx<crop[2]+60 or not crop[1]-60<yy<crop[3]+60:continue
                for a,c,d,e in b['boundary_segments']:draw.line((a-crop[0],c-crop[1],d-crop[0],e-crop[1]),fill='#00efff',width=1)
                draw.ellipse([xx-crop[0]-1,yy-crop[1]-1,xx-crop[0]+1,yy-crop[1]+1],fill='white')
            stem=f"atlas-{model['name']}-{i}.png";canvas.save(review/stem)
            records.append(dict(model=model['name'],point=[x,y],crop=crop,raw=f'raw-{i}.png',overlay=stem))
    save(out/'atlas.json',records)
    return records

def finalize(out):
    out=Path(out);began=time.monotonic();assert read(out/'checkpoint.json')['sources']==sources()
    initial_elapsed=read(out/'checkpoint.json')['elapsed']
    if not (out.parent/'audit/coverage.json').exists():
        from .audit import run as audit
        audit(out.parent/'audit')
    if not read(out/'checkpoint.json')['sealed']:
        from .coupled_refine import run as coupled
        if coupled(out)['stop_reason']=='signal':return
    for folder in ['exports','metrics','review']:(out/folder).mkdir(exist_ok=True)
    if not (out/'selection.json').exists():items=choose(out)
    else:items=read(out/'selection.json')['models']
    data,m,obs=load();save(out/'D.json',reference_dimension(m));models=[];metrics={};baselines={};results=[]
    from .diagnostics import TARGETS
    exposure=[]
    for ident in TARGETS:
        row=next(r for r in data['rows'] if r['id']==ident and r['kind']=='region');section=int(row['station']/data['length']*32)%32
        exposure.append(dict(id=ident,structural_section=section,original_structural_split='comparison' if section%4==3 else 'development',
                             use='direct first-error ranking constraint' if ident in ['C-1477-0290','C-1608-0253'] else 'reference preservation guard' if ident==TARGETS[0] else 'adjacent-body diagnostic'))
    save(out/'exposure.json',dict(targets=exposure,first_error_evidence_used_during_search=True,
         dense_global_comparison_computed_after_selection=True,fresh_holdout=False,
         policy='First-error constraints intentionally include old comparison geography. Whole-circuit comparison is retrospective and partly target-exposed; distinct measurements are not statistically independent validation.'))
    save(out/'family-labels.json',[dict(trial_family_key=s['name'],publication_name=publication_name(s),count=s['parameters']['count'],hand=s['parameters']['hand'],topology=s['parameters']['topology'],source=s['source']) for s in starts()])
    for item in items:
        model=export(item,out,data,m,obs);models.append(model)
        baseline=baselines.get(item['family'])
        metric=measure(item,model,out,data,m,obs,baseline);metrics[item['name']]=metric
        if item['baseline']:baselines[item['family']]=metric
        if not item['baseline']:results.append(dict(model=item['name'],family=item['family'],**acceptance(metric,baseline)))
    save(out/'acceptance.json',dict(models=results,any_pass=any(r['passes'] for r in results),any_geometric_pass=any(r['geometric_passes'] for r in results)))
    atlas(out,models)
    from .plots import run as plots
    plots(out)
    from .review import build
    build(out,models,metrics)
    from .verify import run as verify
    verify(out)
    total_entry_seconds=time.monotonic()-began
    included_search_seconds=max(0,read(out/'checkpoint.json')['elapsed']-initial_elapsed)
    save(out/'finalization.json',dict(seconds=total_entry_seconds-included_search_seconds,total_entry_seconds=total_entry_seconds,
         included_contingent_search_seconds=included_search_seconds,models=len(models),utc=utc(),policy='seconds excludes the already-budgeted contingent search; total_entry_seconds includes it. No double counting.'))
    from .report import write
    write(out,models,metrics)
    print('R311 finalized',len(models),'models',flush=True)
