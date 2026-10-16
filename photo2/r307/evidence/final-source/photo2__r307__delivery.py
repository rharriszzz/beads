"""Sealed native comparison, automatic triage and complete historical-safe export."""
from pathlib import Path
from copy import deepcopy
import json,shutil,time,resource
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r297.common import ROOT,read,save,sha,utc,pixels
from photo2.r306.evidence import load
from photo2.r306.geometry import Chain as Original
from photo2.r306.export import stats
from photo2.r306.diagnose import summary,red_checks
from .fast import Chain,predict
from .objective import Objective
from .search import initial,sources,move

def model_scene(model,data):
    if model.get('historical'):
        from photo2.r299.forward import Surface
        from types import MethodType
        s=Surface(model['parameters'],data);s.trace=MethodType(Chain.trace,s);s.blocked=MethodType(Chain.blocked,s)
        return s
    return Chain(model['parameters'],data)

def distribution(values):
    v=np.asarray([x for x in values if x is not None],float)
    return dict(n=len(v),mean=float(np.mean(v)),median=float(np.median(v)),p10=float(np.percentile(v,10)),p90=float(np.percentile(v,90)),worst_decile_high_mean=float(np.mean(np.sort(v)[-max(1,int(np.ceil(len(v)*.1))):])),worst_decile_low_mean=float(np.mean(np.sort(v)[:max(1,int(np.ceil(len(v)*.1)))]))) if len(v) else dict(n=0)

def analyze(out,models,data,m,obs):
    dense={split:Objective(data,m,obs,split,dense=True) for split in ['development','comparison']};rows=[];diagnosis=[];details={}
    for model in models:
        name=model['name'];file=out/'metrics'/f'{name}.json.gz'
        if file.exists():detail=read(file)
        else:
            s=model_scene(model,data);detail={split:obj.evaluate(s,step=1.,detail=True)[1] for split,obj in dense.items()};save(file,detail)
        details[name]=detail
        body_audit=body_diagnostics(out,model,data)
        if not model.get('reused_native_export'):attach_guided(model,detail,obs)
        save(out/'exports'/f'{name}.json.gz',model)
        row=summary(model);row['R307_metrics']={split:{k:v for k,v in result.items() if k not in ['supports','contours','separators','reflections','predictions','material']} for split,result in detail.items()}
        row['distributions']={split:dict(coherence=distribution([r['fraction'] for r in v['supports']]),strong_reflection=distribution([r['error_px'] for r in v['reflections']]),boundary=distribution([r['boundary_mae'] for r in v['contours']])) for split,v in detail.items()}
        rows.append(row)
        for region in model['regions']:
            j=region['section'];split=region['split'];d=detail[split];ss=[r for r in d['supports'] if r['section']==j];coh=float(np.mean([r['fraction'] for r in ss])) if ss else None
            priority=(1-(coh or 0))*3+4*(region['paper_occupation'] or 0)+(region['rms'] or 0)/12
            flags=[]
            if coh is not None and coh<.65:flags.append('fragmented observed interiors')
            if (region['paper_occupation'] or 0)>.08:flags.append('background occupation')
            if (region['rms'] or 999)<10 and (coh or 0)<.65:flags.append('good reflections coexist with poor visible bodies')
            local={k:v for k,v in body_audit['regions'][j].items() if k!='section'}
            diagnosis.append(dict(model=name,section=j,priority=priority,metrics=region,coherence=coh,coherence_distribution=distribution([r['fraction'] for r in ss]),flags=flags,**local))
        print('common metrics',name,detail['development']['coherence'],detail['comparison']['coherence'],flush=True)
    save(out/'comparison.json',rows);save(out/'diagnosis.json',sorted(diagnosis,key=lambda r:-r['priority']))
    baseline=next(r for r in rows if r['name']=='R306-primary');new=rows[0];regressions=[];checks=[]
    for split in ['development','comparison']:
        for key,tolerance in [('visible_boundary_mae',.3),('envelope_width_mae',.5),('paper_occupied',.01),('colored_missing',.02),('separator_error_px',.5)]:
            delta=new[split][key]-baseline[split][key];checks.append(dict(split=split,metric=key,before=baseline[split][key],after=new[split][key],delta=delta,tolerance=tolerance,passed=delta<=tolerance))
        a,b=baseline[split]['reflection'],new[split]['reflection'];checks.append(dict(split=split,metric='reflection_rms',before=a['rms'],after=b['rms'],delta=b['rms']-a['rms'],tolerance=.3,passed=b['rms']<=a['rms']+.3 and b['unmatched']<=a['unmatched']))
        a,b=baseline['R307_metrics'][split],new['R307_metrics'][split];checks.append(dict(split=split,metric='dense_coherent_ownership',before=a['coherence'],after=b['coherence'],delta=b['coherence']-a['coherence'],tolerance=-.01,passed=b['coherence']>=a['coherence']-.01))
    base_model=next(r for r in models if r['name']=='R306-primary')
    for a,b in zip(base_model['regions'],models[0]['regions']):
        delta=dict(section=a['section'],coherence=b['support_containment']-a['support_containment'] if a['support_containment'] is not None and b['support_containment'] is not None else None,paper=(b['paper_occupation'] or 0)-(a['paper_occupation'] or 0),reflection=(b['rms']-a['rms']) if a['rms'] is not None and b['rms'] is not None else None)
        if (delta['coherence'] is not None and delta['coherence']<-.1) or delta['paper']>.05 or (delta['reflection'] is not None and delta['reflection']>3):regressions.append(delta)
    significant=(new['comparison']['visible_boundary_mae']<=baseline['comparison']['visible_boundary_mae']*.95 and new['R307_metrics']['comparison']['coherence']>=baseline['R307_metrics']['comparison']['coherence']+.02)
    accept=dict(utc=utc(),physically_certified=models[0]['physical']['certified'],component_checks=checks,regional_regressions=regressions,substantial_photographic_improvement=bool(significant),demonstrably_better=bool(significant and all(r['passed'] for r in checks) and not regressions),policy='Report gate: >=5% comparison legacy boundary improvement and >=2 percentage-point dense coherence improvement, no substantial common-metric/regional regression, no added unmatched strong observations. Descriptive engineering thresholds, not significance tests. All comparison evidence is historically exposed.',baseline_preserved=True)
    save(out/'acceptance.json',accept)
    # These are strict same-gauge controls, without replacing missing lobes.
    state=read(out/'checkpoint.json');family=next((r for r in state['families'] if r['parameters']==models[0]['parameters']),None)
    if family:
        obj=Objective(data,m,obs);s=Chain(family['parameters'],data);v,fixed,_=obj.evaluate(s,family['initial_anchors'],step=1.,detail=True)
        save(out/'fixed-initial-assignment-control.json.gz',dict(initial=family['initial'],final_fixed=fixed,final_current=family['native'],initial_anchors=family['initial_anchors'],current_anchors=family['anchors'],rematch_trials=state.get('rematches',[])))
    from photo2.r306.objective import match
    init=base_model['correspondences']['records'];locked={r['id']:r['index'] for r in init if r['strong']};pred=[dict(index=b['index'],point=b['reflection']['centroid']) for b in models[0]['positions'] if b['reflection']]
    if all(models[0]['parameters'][k]==base_model['parameters'][k] for k in ['count','hand','topology','seam_fraction']):
        save(out/'R306-original-owner-control.json.gz',dict(initial=base_model['correspondences']['summary_strong'],final_fixed=match([r for r in obs if r['strong']],pred,fixed=locked),final_free=models[0]['correspondences']['summary_strong']))
        fixed_acceptance(out)
    save(out/'starting-red-diagnosis.json',[r for model in models for r in red_checks(model_scene(model,data),model)])
    shutil.copyfile(ROOT/'photo2/r306/results/campaign/R305-problem-cohorts.json',out/'R305-problem-cohorts.json')
    return details

def controls(out,model,data,m,obs):
    target=out/'controlled-diagnosis.json.gz'
    if target.exists():return
    obj=Objective(data,m,obs);s=Chain(model['parameters'],data);_,base,anchors=obj.evaluate(s,step=1.,detail=True)
    problems=read(out/'diagnosis.json');sections=[r['section'] for r in problems if r['model']=='primary' and r['section']%4!=3][:3]
    # Required location is added in photographic coordinates, not another model's index.
    points=[[1110.23,336.04]]+[next(r['point'] for r in obj.rows if int(r['station']/data['length']*32)%32==j) for j in sections]
    rows=[]
    for point in points:
        from photo2.r297.geometry import reference
        axis=int(round(reference().project([point])['arc'][0]/reference().length*32))%32
        k=int(s.indices[s.tree.query(point)[1]]);field=int(round(((k/s.n+.5)%1)*32))%32
        keys=['axial','phase','minor','elevation',f'axis_nodes:{axis}',f'local_phase:{field}',f'local_spacing:{field}']
        near=[r['id'] for r in base['supports'] if np.linalg.norm(np.array(r['point'])-point)<100]
        for key in keys:
            for sign in [-1,1]:
                q=move(model['parameters'],[key],[sign]);sc=Chain(q,data);cert=sc.certify(iterations=80,witnesses=False);row=dict(point=point,key=key,sign=sign,physical=cert)
                if cert['certified']:
                    _,r,_=obj.evaluate(sc,anchors,step=1.,detail=True)
                    local=[x for x in r['supports'] if x['id'] in near];old=[x for x in base['supports'] if x['id'] in near]
                    row.update(delta_coherence=float(np.mean([x['fraction'] for x in local])-np.mean([x['fraction'] for x in old])) if local else None,delta_loss=r['loss']-base['loss'],material=r['material'],reflections=[x for x in r['reflections'] if np.linalg.norm(np.array(x['observed'])-point)<100])
                rows.append(row)
        save(target,dict(required_point=[1110.23,336.04],controls=rows,policy='Frozen-owner, evaluation-only perturbations; overlapping responses do not identify a unique cause. Full-chain geometry and occlusion retained. Training material only; comparison remains retrospective.'))
    explanations=[]
    for point in points:
        candidates=sorted([r for r in rows if r['point']==point and r.get('delta_coherence') is not None],key=lambda r:-r['delta_coherence'])
        explanations.append(dict(point=point,best_coherence_controls=[dict(key=r['key'],sign=r['sign'],delta=r['delta_coherence']) for r in candidates[:4]],conclusion='Coupled geometry/ownership; no unique corrective group' if len(candidates)>1 else 'insufficient supported interiors'))
    save(out/'corrective-groups.json',explanations)

def pictures(out,models):
    src=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');base=next(r for r in models if r['name']=='R306-primary');new=models[0]
    point=np.array([1110.23,336.04]);lo=np.floor(point-90).astype(int);hi=lo+180;raw=src.crop((*lo,*hi));panels=[]
    for name,model in [('Raw photograph',None),('R306 native visible boundaries',base),('R307 native visible boundaries',new)]:
        im=raw.copy();d=ImageDraw.Draw(im)
        if model:
            nearest=min(model['positions'],key=lambda b:np.linalg.norm(np.array(b['projected_center'])-point))
            for b in model['positions']:
                if np.linalg.norm(np.array(b['projected_center'])-point)>130:continue
                for x,y,a,c in b['boundary_segments']:d.line((x-lo[0],y-lo[1],a-lo[0],c-lo[1]),fill='#ffea60' if b['index']==nearest['index'] else '#20d7ef')
        panel=Image.new('RGB',(540,575),'#182630');panel.paste(im.resize((540,540),Image.Resampling.NEAREST),(0,35));ImageDraw.Draw(panel).text((8,10),name,fill='white');panels.append(panel)
    combined=Image.new('RGB',(1620,575));[combined.paste(p,(540*i,0)) for i,p in enumerate(panels)];combined.save(out/'review/before-after.png')
    records=[]
    for model in [base,new]:
        rows=[r for r in model['supports'] if r['kind']=='region' and np.linalg.norm(np.array(r['point'])-point)<90]
        reflec=[r for r in model['correspondences']['records'] if r['strong'] and np.linalg.norm(np.array(r['observed'])-point)<90]
        records.append(dict(model=model['name'],point=point.tolist(),support_mean=float(np.mean([r['fraction'] for r in rows])),supports=rows,reflections=stats(reflec)))
    save(out/'required-location.json',records)

def finalize(out):
    out=Path(out);state=read(out/'checkpoint.json');data,m,obs=load();t=time.monotonic()
    if state['sources']!=sources():raise ValueError('Scientific sources changed after fitting')
    (out/'exports').mkdir(exist_ok=True)
    if not (out/'selection.json').exists():
        obj=Objective(data,m,obs,dense=True);ranking=[]
        for family in state['families']:
            p=family['parameters'];s=Chain(p,data);_,r,a=obj.evaluate(s,step=1.,detail=True);ranking.append(dict(name=family['name'],parameters=p,result=r,anchors=a))
        ranking.sort(key=lambda r:r['result']['loss']);save(out/'native-ranking.json.gz',ranking)
        selection=dict(utc=utc(),primary=ranking[0]['name'],models=[dict(name='primary' if i==0 else 'guided-'+r['name'],parameters=r['parameters']) for i,r in enumerate(ranking)],policy='Dense native training selection, before R307 comparison outcomes; all historical exposure acknowledged. Baseline retained regardless of new weighted objective.')
        save(out/'selection.json',selection);state['sealed']=True;save(out/'checkpoint.json',state)
    selection=read(out/'selection.json');models=[]
    from photo2.r306 import export as ex
    oldchain,oldpredict=ex.Chain,ex.predict
    ex.Chain,ex.predict=Chain,predict
    try:
        from photo2.r306.objective import Objective as Legacy,contour_samples
        objects={split:Legacy(data,m,obs,split) for split in ['development','comparison']}
        for o in objects.values():o.contour_samples=contour_samples([m['beads'][i] for i in o.bi],1.)
        for item in selection['models']:models.append(ex.export_model(dict(item,historical=False,source='R307 sealed guided search'),out,data,m,obs,objects))
    finally:ex.Chain,ex.predict=oldchain,oldpredict
    folder=ROOT/'photo2/r306/results/campaign/exports'
    for old,name in [('primary','R306-primary'),('R297','R297'),('R298-primary','R298-primary'),('R299-primary','R299-primary')]:
        doc=read(folder/(old+'.json.gz'));doc['name']=name;doc['reused_native_export']=str(folder/(old+'.json.gz'));save(out/'exports'/f'{name}.json.gz',doc)
        for suffix in ['-raster.npz','-errors.csv','-regions.csv','-positions.csv']:
            target=out/'exports'/(name+suffix)
            if not target.exists():shutil.copyfile(folder/(old+suffix),target)
        models.append(doc)
    details=analyze(out,models,data,m,obs);controls(out,models[0],data,m,obs)
    from .review import build
    build(out,models,m,obs);pictures(out,models)
    save(out/'export-manifest.json',dict(utc=utc(),models={r['name']:sha(out/'exports'/f'{r["name"]}.json.gz') for r in models},selection=selection))
    save(out/'model-parameters.json',[dict(name=r['name'],parameters=r['parameters']) for r in models])
    from .verify import verify
    verify(out)
    save(out/'computation.json',dict(fitting_seconds=state['elapsed'],peak_fitting_rss_mib=max([state['peak_rss_mib']]+[read(ROOT/r['archive']/'checkpoint.json')['peak_rss_mib'] for r in state.get('source_transitions',[])]),trials=state['next_id'],accepted=state.get('accepted',[]),cycles=state['cycle'],finalization_seconds=time.monotonic()-t,peak_finalize_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,benchmark=read(out/'benchmark.json'),R306_aggregate_fit_seconds=5266.84,fit_time_ratio=state['elapsed']/5266.84))
    report(out)
    print('R307 native delivery complete',time.monotonic()-t,flush=True)

def attach_guided(model,detail,obs):
    """Viewer optical path uses surface-compatible associations; legacy metric stays."""
    from photo2.r306.objective import match
    guided=deepcopy(model['correspondences']);old={r['id']:r for r in guided['records']};strong=[]
    for split in ['development','comparison']:
        for r in detail[split]['reflections']:
            x=deepcopy(old[r['id']]);x.update(r);x['status']='ambiguous';x['quality']='strong localized; surface-compatible conditional owner';x['stable_across_gap_penalties']=False
            x['penalty_owners']={};x['assignment_method']='one-to-one distance plus compatible positive-interior coverage; 48px unmatched cost';strong.append(x)
    used={r['index'] for r in strong if r['predicted'] is not None};pred=[dict(index=b['index'],point=b['reflection']['centroid']) for b in model['positions'] if b['reflection'] and b['index'] not in used]
    weak=match([r for r in obs if not r['strong']],pred,24.)['records'];records=strong
    for r in weak:
        x=deepcopy(old[r['id']]);x.update(r);x['observation']=x['id'];x['quality']='weak / diffuse / uncertain';x['status']='ambiguous' if x['index'] is not None else 'unmatched';records.append(x)
    records.sort(key=lambda r:r['arc']);guided['records']=records;guided['summary_strong']=stats(strong);guided['policy']='R307 surface-compatible association; legacy nearest-only common metrics retained separately in the export.'
    guided['unmatched_predictions']=[b['index'] for b in model['positions'] if b['reflection'] and b['index'] not in {r['index'] for r in records}]
    for g in guided['groups']:
        rr=[r for r in records if r['index'] is not None and g['first']<=r['index']<=g['last']];g.update(stats([r for r in rr if r['strong']]));g['insufficient_evidence']=g['n']<3
        g['examples']['ambiguous']=[r['index'] for r in rr if r['status']=='ambiguous'];g['examples']['unassigned_predicted']=[k for k in guided['unmatched_predictions'] if g['first']<=k<=g['last']]
    guided['rolling']=[dict(index=k,**stats([r for r in strong if r['index'] is not None and abs(r['index']-k)<=25])) for k in range(model['positions'][0]['index'],model['positions'][-1]['index']+1,10)]
    model['guided_correspondences']=guided

def report(out):
    out=Path(out);rows=read(out/'comparison.json');new=rows[0];base=next(r for r in rows if r['name']=='R306-primary');accept=read(out/'acceptance.json');state=read(out/'checkpoint.json');comp=read(out/'computation.json');verification=read(out/'verification.json');loc=read(out/'required-location.json');controls=read(out/'corrective-groups.json');benchmark=read(out/'benchmark.json')
    fixed=read(out/'fixed-initial-assignment-control.json.gz') if (out/'fixed-initial-assignment-control.json.gz').exists() else None
    original_fixed=read(out/'R306-original-owner-control.json.gz') if (out/'R306-original-owner-control.json.gz').exists() else None
    table=[]
    for r in rows:
        if r['name'] not in ['primary','R306-primary','R297','R298-primary','R299-primary']:continue
        z=r['comparison'];d=r['R307_metrics']['comparison'];table.append(f"| {r['name']} | {z['visible_boundary_mae']:.2f} | {100*d['coherence']:.2f}% | {z['reflection']['rms']:.2f} | {100*z['paper_occupied']:.2f}% | {z['envelope_width_mae']:.2f} | {z['separator_error_px']:.2f} |")
    split_table=[]
    for split in ['development','comparison']:
        for r in [base,new]:
            d=r['R307_metrics'][split];old=r[split];split_table.append(f"| {r['name']} / {split} | {100*d['coherence']:.2f}% | {d['boundary']:.2f}/{d['reverse_boundary']:.2f} | {100*d['paper']:.2f}% | {d['reflection_rms']:.2f} | {d['unmatched']} |")
    primary=read(out/'exports/primary.json.gz');dims=primary['parameters'];diag=read(ROOT/'photo2/r307/evidence/R306-minus101.json')
    sensitivity=[read(p) for p in sorted(out.glob('sensitivity-*.json.gz'))];pairs=[(abs(c['cosine']),c) for r in sensitivity for c in r['couplings']];pairs.sort(key=lambda v:-v[0]);couplings='; '.join(f"{c['a']} / {c['b']} ({c['cosine']:+.3f})" for _,c in pairs[:5])
    times={}
    for r in state['history']:
        key='sensitivity' if r['tag'].startswith('sensitivity:') else r['tag'].split('-R306')[0]
        times.setdefault(key,[]).append(r['seconds'])
    time_table='\n'.join(f"| {k} | {len(v)} | {np.median(v):.3f} | {sum(v):.2f} |" for k,v in times.items())
    yes=accept['demonstrably_better'];answer='Yes' if yes else 'No'
    transitions=state.get('source_transitions',[])
    correction_note=(f"The initial .8-correlation-only gate was inadequate: native best-quartile recall was .5. After {transitions[0]['elapsed']/60:.2f} minutes the first stage stagnated; the remaining {(state['elapsed']-transitions[0]['elapsed'])/60:.2f} minutes used native sensitivities. A scheduling defect also grouped equal coefficient numbers despite different geographic origins. Both decisions and all earlier source/state/Jacobians are preserved in the explicit source transition. Geometry, evidence and objective weights did not change." if transitions else "This run uses the corrected native-predictor gate and geographically aligned blocks from the beginning; no source transition occurred.")
    limitation_note=(f"Most of this campaign used an inadequate approximation gate and geographically misaligned blocks. The corrected {(state['elapsed']-transitions[0]['elapsed'])/60:.2f}-minute stage did not improve the primary; this is not a full-budget test of the corrected method." if transitions else "The reported component measurements and fixed-owner controls determine whether this bounded run improves the baseline; the outcome does not establish a unique physical cause or falsify the model family.")
    profile_note=(f"The preflight benchmark adds an estimated {comp['profile_elapsed_estimate_seconds']:.2f}s, or {(state['elapsed']+comp['profile_elapsed_estimate_seconds'])/60:.2f} minutes including profiling; timing provenance is in computation.json." if 'profile_elapsed_estimate_seconds' in comp else "Profiling is separate; individual evaluation timings are in benchmark.json.")
    text=f'''# R307 — faster guided fitting, measured photographic limits

**{answer}: R307 {'passes the stated photographic improvement checks' if yes else 'does not establish a substantially better photographic reconstruction of the entire necklace'}.** It executes
{state['elapsed']/60:.2f} minutes of fitting versus R306's 87.78 aggregate minutes,
retains a physically feasible full necklace, and delivers the best achieved
native-training candidate. {'The component and regional gates pass.' if yes else 'Small objective gains do not overcome the remaining visible-body failures and photographic regressions.'}
The baseline remains preserved; no production adoption, Phase 3 or pattern follows.

[Launch review](review/r307/launch.sh) · [Offline viewer](r307/results/campaign/review/index.html) ·
[Reproduce](R307_REPRODUCE.md) · [Before/after](r307/results/campaign/review/before-after.png) ·
[Complete metrics](r307/results/campaign/comparison.json) · [Acceptance checks](r307/results/campaign/acceptance.json).

## Required location and the objective defect

At R306 −101, (1110.23,336.04), fresh original-kernel ownership and all saved
viewer boundary segments agree exactly. The isolated projection has **{diag['isolated_pixels']} pixels**;
only **{diag['visible_pixels']}** remain visible and **{diag['occluded_pixels']}** are hidden by neighbors.
Pixel stair-steps are raster sampling; larger cutouts include modeled occlusion and the annular hole. It is
not a display error. The raw crop also shows the lower modeled row extending
into background. Yellow denotes selection, never photographed bead color.
[Isolated/visible/observed diagnostic](r307/evidence/R306-minus101.png).

R306 sampled24 pixels per region, measured contour distances mainly at polygon
vertices, used a .35-weighted reflection term, and omitted local ownership and
reflection residuals from its sensitivity vector. Those measurements could
reward material/envelope averages while tolerating bodies spread across several
photographic interiors. A contact certificate cannot detect that mismatch.

Within90 pixels of the required location, complete positive-region modal coverage
changes **{100*loc[0]['support_mean']:.2f}% → {100*loc[1]['support_mean']:.2f}%**.
Strong nearest-assignment RMS changes **{loc[0]['reflections']['rms']:.2f} → {loc[1]['reflections']['rms']:.2f}px**.
These are the same photographic supports, not the same conditional indices.
The images and [individual supports](r307/results/campaign/required-location.json)
retain competing owners. No independently measured complete external contour
exists for every bead in this crop; interior coverage is not silhouette truth.

## Common photographic measurements

The following are identical historical comparison evidence and legacy metric
definitions, except coherent ownership uses all nonreflection interior pixels
(an unweighted mean of modal fractions; confidence weights affect fitting). These cases were exposed previously;
**they are retrospective comparisons, not fresh independent validation**.

| Model | Legacy visible boundary MAE px | Dense coherent ownership | Strong reflection RMS px | Paper occupation | Envelope width MAE px | Separator MAE px |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

The new bidirectional boundary metric applies a3px uncertainty band before
averaging dense boundary distances. Its numerical values cannot be compared
directly with legacy vertex MAE. New reflection associations include compatible
positive-surface evidence; legacy nearest-only scores above remain separate.

| Model / evidence | Dense modal ownership | Banded boundary forward/reverse px | Region-balanced paper | Compatible-owner reflection RMS px | Missing strong lobes |
|---|---:|---:|---:|---:|---:|
{chr(10).join(split_table)}

The explicit acceptance checks record **{sum(not r['passed'] for r in accept['component_checks'])} component failures**
and **{len(accept['regional_regressions'])} large regional regressions**. Distributions,
worst-decile means, all32 geographic regions, and good/median/poor ownership
quantile examples are retained. Low-reflection/high-body-error regions are
flagged automatically. The gallery includes the required location and historical
problem cohorts; it is not a selection of only attractive fits.

## What was implemented and executed

Positive interiors use up to256 spatially distributed original pixels per region
in fitting and every original pixel at final evaluation. Qualitative accepted
regions carry full coherence weight, compact automatic interiors half weight,
and possible same-color mergers .12 weight. These are engineering uncertainty
weights, not verified single-bead labels. Every region still contributes positive
material evidence. Red/yellow conflicts and preserved separator-bank mergers test
the reverse mapping; same-color masks without separation evidence are not forced
to be distinct bodies. Background cues and uncertain external contours remain
separate from positive interiors, highlights, and complete isolated projections.

Residual vectors include per-region ownership, material/background contradiction,
dense two-sided visible-contour error, separator mismatch, envelope edges, and
signed tangent/normal reflection displacement under one shared light. Reflection
outliers use a Huber tail rather than disappearing; missing lobes incur a48px
penalty and remain in the denominator. Native training acceptance disallows
additional missing assigned lobes and substantial structural deterioration.

Measured finite differences drive damped block Gauss–Newton and bounded line
search. All32 geometric-axis,32 phase and32 spacing coefficients participate,
alongside shared shape/camera/phase/light parameters. Global derivatives are
two-sided; local derivatives are forward with a backward feasibility fallback.
Every trial retains the entire coherent chain for occlusion and hard contact
screening. No independent bead shifts, curve splices or phase resets are added.
Fields retain R306's bounds and true geometric arclength. Cache reuse is limited
to unchanged geometry inputs and fixed photographic structures; local spacing
can affect global arclength, so unaffected residuals are not assumed unchanged.

Executed **{state['next_id']} trials**, **{state['cycle']} complete numerical blocks**,
and **{len(state.get('accepted',[]))} native accepted improvements**. Small accepted
finite-difference steps are retained alongside coupled proposals; they are not
all Gauss–Newton successes. The full Jacobians, singular values, right vectors,
step predictions, actual reductions and rejections are saved. Strongest measured
couplings include {couplings}. These scaled responses are not statistical ranks
or confidence intervals. No broad new count search was needed or performed;
four R306 count/hand/topology families remain available with earlier feasible
R297/R298/R299 controls.

## Speed, physical validity and limitations

Compiled marching preserves the existing shape,450-iteration limit and tolerances.
At the full R306 start it reproduces all **{benchmark['native_equivalence']['lobes']} native lobes exactly**.
Original versus compiled trace timings were {benchmark['kernel'][1]['seconds']:.3f}s versus
{benchmark['kernel'][0]['seconds']:.3f}s for62,795 rays. Full compiled native prediction took
{benchmark['native_equivalence']['seconds']:.2f}s. Two-pixel/native trial ranking correlation was
{benchmark['spearman']:.3f}; it **did not select the same best small perturbation**.
{correction_note}
The corrected gate requires correlation .9, best-quartile recall .8, and no extra
missing assigned lobes before using a coarse predictor. Native checks protected
accepted models throughout. Corrected blocks project phase/spacing knot stations
to photographic geography before combining them with axis coefficients.


| Evaluation type | Calls | Median seconds | Total seconds |
|---|---:|---:|---:|
{time_table}

Cumulative fitting time includes sensitivities, physical gates, native acceptance
and checkpointing. {profile_note} Final export, post-seal diagnostic controls,
verification and browser checks are additional work, not hidden fitting runs.
Fitting peak RSS was **{comp['peak_fitting_rss_mib']:.1f}MiB**; finalization peak was
**{comp['peak_finalize_rss_mib']:.1f}MiB**. The fitting-time ratio to R306 is
**{comp['fit_time_ratio']:.3f}**. Initialization from R306 supplies substantial
prior work; this is not a cold-start speed comparison.

The primary has **{dims['count']} bodies, hand{dims['hand']:+d}, {dims['topology']} string**,
a closed periodic geometric axis, and **{primary['physical']['pairs']} certified close pairs**.
Independent minimum support margin is **{primary['physical']['independent_minimum_gap']:.6f} source units**.
Every body, hidden surface, weak observation, missing lobe and ambiguity is retained.
Native/half-pixel centroid changes at prespecified observations have median {verification['numerical']['median']:.3f}px and maximum {verification['numerical']['maximum']:.3f}px, with {len(verification['numerical']['half_only'])} extra marginal half-pixel lobes. These sampling effects limit interpretation of tiny optical gains. True-arclength refinement is recorded in verification.

The immediate demonstrated obstacle is **native, jointly compatible body ownership
and geometry**, not insufficient evidence proved by this experiment. {limitation_note}


The smallest remaining scientific test is whether a native coupled step can
improve fixed-owner visible interiors and their independent boundary/background
constraints together at the required location while preserving the rest of the
circuit. Existing same-color mergers, sparse dark-body boundaries and uncertain
physical identities complicate that test; this run does **not** prove that new
maker labels are necessary. Frozen-owner shape/phase/spacing/axis/camera controls
have partial, competing effects and do not establish a unique physical cause.
No further fitting is authorized automatically by this negative result.

## Verification and stopping point

Six scientific contracts and real SIGTERM/resume/publication-recovery tests pass.
Independent original Python verification checks all exported physical positions,
complete spatial close pairs, native ownership samples, full support denominators,
required-location pixels, **{verification['boundary_segments_exact']} primary boundary segments**,
and **{verification['original_kernel_dense_evidence_rays']} dense evidence rays**.
The original photograph and historical scientific files are preserved.
The [verification receipt](r307/results/campaign/verification.json) records
{verification['protected_R307_start_files']} protected start-of-R307 files.
The [browser receipt](r307/results/campaign/browser-check.json) records the actual
UI checks: eight models at80 locations, geographic model switching, overlap/competing-owner controls, raw invariance, desktop/narrow/offline operation and the actual launcher. Windows browser dispatch is mocked, not physically observed.
An initialization shadowed-name defect was fixed before fitting; source/log retained.

Deliver the achieved candidate and unchanged baseline for review. Stop after
verified commit/push. No automatic R308, further campaign, Phase3 or adoption.
'''
    if fixed:text+=f"\nFixed initial fitting owners: RMS {fixed['initial']['reflection_rms']:.3f} → {fixed['final_fixed']['reflection_rms']:.3f}px, missing {fixed['initial']['unmatched']} → {fixed['final_fixed']['unmatched']}. Correspondence refresh trials: {len(fixed['rematch_trials'])}.\n"
    if original_fixed:text+=f"\nR306's original nearest-owner control: initial RMS {original_fixed['initial']['rms']:.3f}px; final fixed RMS {original_fixed['final_fixed']['rms']:.3f}px on {original_fixed['final_fixed']['matched']} surviving lobes, with {original_fixed['final_fixed']['unmatched']} missing. RMS including a24px penalty for each missing original-owner lobe is {original_fixed.get('penalized_rms_24px',float('nan')):.3f}px. The surviving-only decrease is not a complete fixed-owner improvement; these remain conditional mathematical owners, not physical identities.\n"
    import os
    local=text.replace('r307/results/campaign/','').replace('review/r307/launch.sh',os.path.relpath(ROOT/'photo2/review/r307/launch.sh',out)).replace('R307_REPRODUCE.md',os.path.relpath(ROOT/'photo2/R307_REPRODUCE.md',out)).replace('r307/evidence/',os.path.relpath(ROOT/'photo2/r307/evidence',out)+'/')
    (out/'R307_REPORT.md').write_text(local)
    if out.resolve()==(ROOT/'photo2/r307/results/campaign').resolve():(ROOT/'photo2/R307_REPORT.md').write_text(text)

def body_diagnostics(out,model,data):
    """Sample-supported reverse contradictions and genuinely local contact margins."""
    from photo2.r297.geometry import periodic_field
    raster=np.load(out/'exports'/f'{model["name"]}-raster.npz');owner=raster['owner'];cues=np.load(ROOT/'photo2/r296/evidence/cues.npz');xy=cues['xy'].astype(int);o=owner[xy[:,1],xy[:,0]];good=o>=0;n=len(model['positions'])
    counts=np.zeros((n,4),int)
    for col,keep in enumerate([np.ones(len(o),bool),cues['paper'],cues['color']==1,cues['color']==2]):
        counts[:,col]=np.bincount(o[good&keep],minlength=n)
    body_sections=np.array([int(((b['photo_arc']-data['arc0'])*data['direction'])%data['length']/data['length']*32)%32 for b in model['positions']])
    records=[];phases=np.array(model['parameters'].get('local_phase',[0.]*32));spacing=np.array(model['parameters'].get('local_spacing',[0.]*32));indices=np.array([b['index'] for b in model['positions']]);ph=periodic_field(phases,indices/n);sp=periodic_field(spacing,indices/n)
    margins=[[] for _ in range(32)]
    for w in model['physical']['witnesses']:
        a,b=w['pair']
        for j in set([int(body_sections[a]),int(body_sections[b])]):margins[j].append(w['gap_units'])
    source={r['id']:r for r in data['rows']};perbody={}
    for r in model['supports']:
        if r['kind']!='region' or source[r['id']]['reflection']:continue
        for a in r['alternatives']:
            if a['fraction']>=.15:perbody.setdefault(a['index'],[]).append(dict(id=r['id'],color=source[r['id']]['color'],fraction=a['fraction'],accepted=source[r['id']]['accepted']))
    for i,b in enumerate(model['positions']):
        total,paper,red,yellow=map(int,counts[i]);material=red+yellow;links=perbody.get(b['index'],[])
        records.append(dict(index=b['index'],point=b['projected_center'],section=int(body_sections[i]),visible_area_px2=b['visible_area_px2'],classified_cue_samples=total,paper_cue_samples=paper,paper_fraction_of_visible_cue_samples=paper/total if total else None,red_cue_samples=red,yellow_cue_samples=yellow,incompatible_material_fraction=min(red,yellow)/material if material else None,interior_links=links,opposite_color_regions=len({r['color'] for r in links})>1,local_phase=float(ph[i]),local_spacing=float(sp[i])))
    regions=[]
    for j in range(32):
        rows=[r for r in records if r['section']==j];ix=body_sections==j
        regions.append(dict(section=j,contact_minimum_margin=min(margins[j]) if margins[j] else None,contact_witnesses=len(margins[j]),paper_body_distribution=distribution([r['paper_fraction_of_visible_cue_samples'] for r in rows]),material_conflict_distribution=distribution([r['incompatible_material_fraction'] for r in rows]),opposite_color_crossing_bodies=sum(r['opposite_color_regions'] for r in rows),local_phase_range=[float(ph[ix].min()),float(ph[ix].max())] if ix.any() else None,local_spacing_range=[float(sp[ix].min()),float(sp[ix].max())] if ix.any() else None))
    result=dict(bodies=records,regions=regions,policy='Fraction of frozen visible cue samples, not an assertion that every visible pixel has a photo label. Same-color regions can share a physical body unless independent separation establishes otherwise. Local contact margin covers every close pair touching the geographic region.')
    save(out/'metrics'/f'{model["name"]}-body-diagnostics.json.gz',result);return result


def fixed_acceptance(out):
    path=out/'R306-original-owner-control.json.gz'
    if not path.exists():return
    r=read(path);f=r['final_fixed'];e=[x['error_px'] if x['error_px'] is not None else 24. for x in f['records']]
    r['penalized_rms_24px']=float(np.sqrt(np.mean(np.square(e))));save(path,r)
    a=read(out/'acceptance.json');a['component_checks']=[x for x in a['component_checks'] if x['metric']!='R306_fixed_owner_missing_lobes']
    a['component_checks'].append(dict(split='all original R306 owners',metric='R306_fixed_owner_missing_lobes',before=r['initial']['unmatched'],after=f['unmatched'],delta=f['unmatched']-r['initial']['unmatched'],tolerance=0,passed=f['unmatched']<=r['initial']['unmatched'],interpretation='Conditional mathematical owners; loss of original lobes cannot count as geometric improvement through rematching.'))
    a['demonstrably_better']=a['demonstrably_better'] and f['unmatched']<=r['initial']['unmatched'];save(out/'acceptance.json',a)
