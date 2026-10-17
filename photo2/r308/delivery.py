"""Native stage comparisons, scientific plots, original-kernel verification."""
from pathlib import Path
from copy import deepcopy
import time,shutil,resource
import numpy as np
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r306.evidence import load
from photo2.r307.fast import Chain,predict
from photo2.r307.delivery import model_scene,analyze,attach_guided,distribution
from photo2.r307.objective import Objective as CommonObjective
from .objective import Objective
from .search import sources,correction,FIELD_LIMITS,Runner

def copy_model(out,folder,old,name):
    doc=read(folder/(old+'.json.gz'));doc['name']=name;doc['reused_native_export']=str(folder/(old+'.json.gz'));save(out/'exports'/f'{name}.json.gz',doc)
    for suffix in ['-raster.npz','-errors.csv','-regions.csv','-positions.csv']:
        target=out/'exports'/(name+suffix)
        if not target.exists():shutil.copyfile(folder/(old+suffix),target)
    return doc

def finalize(out):
    out=Path(out);began=time.monotonic();state=read(out/'checkpoint.json');assert state['sources']==sources(),'Scientific sources changed'
    data,m,obs=load();(out/'exports').mkdir(exist_ok=True)
    if not (out/'selection.json').exists():
        # Publish all stage winners. Also retain the strongest guarded completed
        # numerical trial if the budget interrupted its containing block.
        candidates=[]
        for stage,rec in state['stages'].items():candidates.append(dict(name=stage+'-only' if stage=='global' else stage,trial=rec['trial']))
        alltrials=[read(p) for p in sorted((out/'trials').glob('*.gz'))]
        if state.get('distributed_base_id') is not None:
            guard=alltrials[state['distributed_base_id']]
            eligible=[r for r in alltrials if r.get('correction') is not None and r.get('objective_sha')==sha(ROOT/'photo2/r308/objective.py') and Runner.guarded(None,r,guard)]
            if eligible:candidates.append(dict(name='best-completed-trial',trial=min(eligible,key=lambda r:r['result']['loss'])['id']))
        seen=set();candidates=[r for r in candidates if not (r['trial'] in seen or seen.add(r['trial']))]
        obj=Objective(data,m,obs,dense=True);ranking=[]
        for item in candidates:
            trial=alltrials[item['trial']];s=Chain(trial['parameters'],data);_,r,a=obj.evaluate(s,step=1.,detail=True)
            ranking.append(dict(**item,parameters=trial['parameters'],result=r,anchors=a))
        ranking.sort(key=lambda r:r['result']['loss']);save(out/'native-ranking.json.gz',ranking)
        # Historical models always stay available; this primary is a delivered
        # candidate, never adoption based only on the new weighted objective.
        selected=[dict(name='primary',parameters=ranking[0]['parameters'],trial=ranking[0]['trial'],stage=ranking[0]['name'])]
        for stage,rec in state['stages'].items():selected.append(dict(name='stage-'+stage,parameters=alltrials[rec['trial']]['parameters'],trial=rec['trial'],stage=stage))
        selection=dict(utc=utc(),models=selected,primary_stage=ranking[0]['name'],policy='Dense native development ranking sealed before retrospective comparisons. All stages and both historical baselines retained; photographic acceptance is separate.')
        save(out/'selection.json',selection);state['sealed']=True
        # Compatibility data for the reused, historically validated review.
        state['history']=[dict(id=r['id'],tag=r['tag'],loss=r.get('result',{}).get('loss'),seconds=r['seconds'],elapsed=r['elapsed']) for r in alltrials]
        state['families']=[]
        for item in selected:
            r=alltrials[item['trial']];base=alltrials[state['baseline_id']]
            state['families'].append(dict(name=item['name'],parameters=item['parameters'],initial_anchors=base['anchors'],anchors=r['anchors'],initial=base['result'],native=r['result']))
        save(out/'checkpoint.json',state)
    selection=read(out/'selection.json');models=[]
    from photo2.r306 import export as ex
    from photo2.r306.objective import Objective as Legacy,contour_samples
    oldchain,oldpredict=ex.Chain,ex.predict;ex.Chain,ex.predict=Chain,predict
    try:
        objects={s:Legacy(data,m,obs,s) for s in ['development','comparison']}
        for o in objects.values():o.contour_samples=contour_samples([m['beads'][i] for i in o.bi],1.)
        for item in selection['models']:
            path=out/'exports'/f"{item['name']}.json.gz"
            models.append(read(path) if path.exists() else ex.export_model(dict(item,historical=False,source='R308 sealed native hierarchical search'),out,data,m,obs,objects))
    finally:ex.Chain,ex.predict=oldchain,oldpredict
    for name,folder,old in [('R306-primary','r306','primary'),('R307-primary','r307','primary')]+[(f'R306-{s}','r306',s) for s in ['alternative-2665','alternative-1857','alternative-2433']]+[(s,'r306',s) for s in ['R297','R298-primary','R299-primary']]:
        models.append(copy_model(out,ROOT/f'photo2/{folder}/results/campaign/exports',old,name))
    analyze(out,models,data,m,obs)
    corrected_metrics(out,models,data,m,obs)
    from .replay import replay,all_candidates
    replay(out,data,m,obs)
    all_candidates(out,data,m,obs)
    periodic_controls(out,data,m,obs)
    acceptance(out,models,obs)
    field_data(out,models,data,state)
    derivative_reliability(out)
    from .review import build
    build(out,models,m,obs)
    pictures(out,models)
    from .uncertainty_figure import build as unknown_figure
    unknown_figure(out)
    plots(out,models)
    save(out/'export-manifest.json',dict(utc=utc(),models={r['name']:sha(out/'exports'/f'{r["name"]}.json.gz') for r in models},selection=selection))
    save(out/'model-parameters.json',[dict(name=r['name'],parameters=r['parameters']) for r in models])
    from .verify import verify
    verify(out)
    records=[read(p) for p in sorted((out/'trials').glob('*.gz'))];timing={}
    for r in records:
        kind=r['tag'].split(':')[0];kind='derivative' if (kind in ['discovery'] or ':' in r['tag'] and not any(t in r['tag'] for t in ['initial:','curve:','pair:','fourier:','LM:',':base'])) else 'LM' if ':LM:' in r['tag'] else kind
        timing.setdefault(kind,[]).append(r['seconds'])
    save(out/'computation.json',dict(postfit_all_candidate_repair_audit_seconds_estimate=read(out/'all-candidate-corrected-ranking.json').get('seconds',read(out/'all-candidate-corrected-ranking.json').get('seconds_estimate',0.)),fitting_seconds=state['elapsed'],peak_fitting_rss_mib=max([state['peak_rss_mib']]+[read(ROOT/r['archive']/'checkpoint.json')['peak_rss_mib'] for r in state.get('source_transitions',[])]),source_transitions=state.get('source_transitions',[]),adaptive=state.get('adaptive_started'),trials=state['next_id'],accepted=state['accepted'],stage_times=state['stages'],evaluation_timing={k:dict(calls=len(v),median=float(np.median(v)),total=sum(v)) for k,v in timing.items()},initial_native_benchmark=[dict(name=r['tag'],seconds=r['seconds'],rays=r.get('result',{}).get('rays')) for r in records if r['tag'].startswith('initial:')],finalization_seconds=time.monotonic()-began,peak_finalize_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,R306_seconds=5266.8419793,R307_seconds=1200.0190287,stop_reason=state.get('stop_reason')))
    report(out)

def acceptance(out,models,obs):
    rows=read(out/'comparison.json');primary=rows[0];new=models[0];checks=[];fixed=[];regions=[]
    from photo2.r306.objective import match
    pred=[dict(index=b['index'],point=b['reflection']['centroid']) for b in new['positions'] if b['reflection']]
    for name in ['R306-primary','R307-primary']:
        old=next(r for r in models if r['name']==name);base=next(r for r in rows if r['name']==name)
        for split in ['development','comparison']:
            a,b=base[split],primary[split]
            for k,tol in [('visible_boundary_mae',.3),('envelope_width_mae',.5),('paper_occupied',.01),('colored_missing',.02),('separator_error_px',.5)]:checks.append(dict(baseline=name,split=split,metric=k,before=a[k],after=b[k],passed=b[k]<=a[k]+tol,tolerance=tol))
            checks.append(dict(baseline=name,split=split,metric='reflection_rms',before=a['reflection']['rms'],after=b['reflection']['rms'],passed=b['reflection']['rms']<=a['reflection']['rms']+.3 and b['reflection']['unmatched']<=a['reflection']['unmatched']))
        improved=primary['comparison']['visible_boundary_mae']<=base['comparison']['visible_boundary_mae']*.95 and primary['R307_metrics']['comparison']['coherence']>=base['R307_metrics']['comparison']['coherence']+.02
        checks.append(dict(baseline=name,metric='substantial_boundary_and_coherence_improvement',passed=improved))
        same=all(new['parameters'][k]==old['parameters'][k] for k in ['count','hand','topology','seam_fraction'])
        if same:
            locked={r['id']:r['index'] for r in old['correspondences']['records'] if r['strong']};result=match([r for r in obs if r['strong']],pred,fixed=locked)
            penalized=float(np.sqrt(np.mean([(r['error_px'] if r['error_px'] is not None else 24.)**2 for r in result['records']])))
            fixed.append(dict(baseline=name,initial=old['correspondences']['summary_strong'],final=result,penalized_rms_24px=penalized))
            checks.append(dict(baseline=name,metric='no_added_original_owner_missing_lobes',passed=result['unmatched']<=old['correspondences']['summary_strong']['unmatched']))
        else:fixed.append(dict(baseline=name,same_address_gauge=False,interpretation='Discrete-family difference: fixed integer addresses not physical identities; no identity-recovery claim.'))
        for a,b in zip(old['regions'],new['regions']):
            delta=dict(baseline=name,section=a['section'],coherence=b['support_containment']-a['support_containment'] if a['support_containment'] is not None and b['support_containment'] is not None else None,paper=(b['paper_occupation'] or 0)-(a['paper_occupation'] or 0),reflection=b['rms']-a['rms'] if b['rms'] is not None and a['rms'] is not None else None)
            delta['large_regression']=(delta['coherence'] is not None and delta['coherence']<-.1) or delta['paper']>.05 or (delta['reflection'] is not None and delta['reflection']>3);regions.append(delta)
    save(out/'fixed-historical-owners.json.gz',fixed);save(out/'regional-changes.json',regions)
    save(out/'acceptance.json',dict(physically_certified=new['physical']['certified'],demonstrably_better=all(r['passed'] for r in checks) and not any(r['large_regression'] for r in regions),checks=checks,large_regressions=[r for r in regions if r['large_regression']],baseline_preserved=True,recommended_reference='R306-primary; candidate not adopted unless all tests pass',policy='Same R307 native common metrics; >=5% comparison boundary and >=2pp dense coherent ownership improvement against each baseline, no substantial component/regional regressions or extra missing original-owner lobes. Historical comparison evidence exposed; no new validation claim.'))

def field_data(out,models,data,state):
    ref=state['correction_reference'];rows=[]
    for model in models:
        if model['name'] not in ['primary','stage-global','stage-distributed','stage-joint']:continue
        p=model['parameters'];s=Chain(p,data);q=deepcopy(p)
        for k in FIELD_LIMITS:q[k]=ref[k]
        base=Chain(q,data)
        from photo2.r297.geometry import periodic_field
        zero=deepcopy(p)
        for k in FIELD_LIMITS:zero[k]=[0.]*32
        nofield=Chain(zero,data);u=np.linspace(-.5,.5,4097)
        total_effect=dict(projected_displacement_from_zero_fields_max_px=float(np.max(np.linalg.norm(s.pc-nofield.pc,axis=1))),phase_rate_fraction_max=float(np.max(abs(periodic_field(p['local_phase'],u,1)/s.n))/(2*np.pi/6.5)),spacing_fraction_max=float(np.max(abs(periodic_field(p['local_spacing'],u)))),interpretation='Counterfactual removal of inherited plus new fields; not a separately certified candidate or measurement of string strain.')
        rows.append(dict(total_field_effect=total_effect,model=model['name'],correction=correction(p,ref,data),fields={k:dict(original=ref[k],fitted=p[k],delta=(np.array(p[k])-ref[k]).tolist()) for k in FIELD_LIMITS},projected_displacements=(s.pc-base.pc).tolist(),indices=s.indices.tolist(),closure=s.closure(),face_diameter_px=2*p['radius']*p['scale'],axial_face_ratio=.7*p['axial']))
    save(out/'distributed-corrections.json',rows)

def pictures(out,models):
    from PIL import Image,ImageOps,ImageDraw
    src=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');point=np.array([1110.23,336.04]);lo=np.floor(point-90).astype(int);raw=src.crop((*lo,*(lo+180)));panels=[];records=[]
    selected=[None]+[next(r for r in models if r['name']==n) for n in ['R306-primary','R307-primary','primary']]
    for model in selected:
        im=raw.copy();d=ImageDraw.Draw(im)
        if model:
            for b in model['positions']:
                if np.linalg.norm(np.array(b['projected_center'])-point)>130:continue
                for x,y,a,c in b['boundary_segments']:d.line((x-lo[0],y-lo[1],a-lo[0],c-lo[1]),fill='#20d7ef')
            detail=read(out/'metrics'/f"{model['name']}.json.gz");supports=[r for v in detail.values() for r in v['supports'] if np.linalg.norm(np.array(r['point'])-point)<90];rr=[r for v in detail.values() for r in v['reflections'] if np.linalg.norm(np.array(r['observed'])-point)<90]
            records.append(dict(model=model['name'],point=point.tolist(),support_count=len(supports),support_definition='All nonreflection positive-interior regions within90px; identical native pixels for all models. Earlier R307 local headline included reflection regions, so its percentages have a different denominator.',coherence=float(np.mean([r['fraction'] for r in supports])),reflection=dict(distribution([r['error_px'] for r in rr]),rms=float(np.sqrt(np.mean([r['error_px']**2 for r in rr if r['error_px'] is not None])))),supports=supports,reflections=rr))
        panel=Image.new('RGB',(450,485),'#182630');panel.paste(im.resize((450,450),Image.Resampling.NEAREST),(0,35));ImageDraw.Draw(panel).text((8,10),model['name'] if model else 'Original photograph',fill='white');panels.append(panel)
    image=Image.new('RGB',(1800,485));[image.paste(p,(450*i,0)) for i,p in enumerate(panels)];image.save(out/'review/before-after.png');save(out/'required-location.json',records)

def plots(out,models):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    dest=out/'review';repaired={r['trial']:r['corrected_loss'] for r in read(out/'corrected-response-replay.json')['records']};curves=read(out/'response-curves.json') if (out/'response-curves.json').exists() else []
    fig,axes=plt.subplots(max(1,len(curves)),1,figsize=(10,3*max(1,len(curves))),layout='constrained',squeeze=False)
    for ax,curve in zip(axes[:,0],curves):
        rows=curve['rows'];ax.plot([r['offset'] for r in rows],[r['loss'] if r['feasible'] else np.nan for r in rows],'.-',label='Native; conditional reassignment')
        ax.plot([r['offset'] for r in rows],[repaired.get(r['trial'],np.nan) for r in rows],'s--',label='Corrected unknown-ray treatment, same candidates')
        mins=curve['minima'];ax.scatter([r['offset'] for r in mins],[r['loss'] for r in mins],marker='*',s=110,label='Sampled minima');ax.set(xlabel=curve['parameter']+' offset in physical units',ylabel='Full-circuit training loss');ax.grid(alpha=.3);ax.legend()
    fig.savefig(dest/'global-response-curves.png',dpi=140);plt.close(fig)
    grids=read(out/'response-pairs.json') if (out/'response-pairs.json').exists() else []
    fig,axes=plt.subplots(1,max(1,len(grids)),figsize=(6*max(1,len(grids)),5),layout='constrained',squeeze=False)
    for ax,g in zip(axes[0],grids):
        xs=sorted({r['x'] for r in g['rows']});ys=sorted({r['y'] for r in g['rows']});z=np.full((len(ys),len(xs)),np.nan)
        for r in g['rows']:
            if r['feasible']:z[ys.index(r['y']),xs.index(r['x'])]=repaired.get(r['trial'],r['loss'])
        im=ax.pcolormesh(xs,ys,z,shading='nearest',cmap='viridis_r');fig.colorbar(im,ax=ax,label='Native training loss');ax.set(xlabel=g['a']+' offset',ylabel=g['b']+' offset',title='Corrected score; same native coupled trials')
    fig.savefig(dest/'coupled-response.png',dpi=140);plt.close(fig)
    prediction=[read(p) for p in sorted((out/'predictions').glob('*.json'))];good=[r for r in prediction if r['actual'] is not None]
    fig,ax=plt.subplots(figsize=(7,5),layout='constrained');ax.scatter([r['predicted'] for r in good],[r['actual'] for r in good],s=20);ax.axhline(0,color='gray');ax.axvline(0,color='gray');ax.set(xlabel='Derivative-predicted loss decrease',ylabel='Actual native loss decrease',title='Trust-region predictions (negative means worsening)');fig.savefig(dest/'predicted-versus-actual.png',dpi=140);plt.close(fig)
    fields=read(out/'distributed-corrections.json');fig,axes=plt.subplots(4,1,figsize=(11,11),layout='constrained')
    for row in fields:
        if row['model']=='stage-global':continue
        for ax,key in zip(axes,FIELD_LIMITS):ax.plot(np.arange(32)/32,row['fields'][key]['delta'],label=row['model']);ax.set_ylabel(key+' increment')
        axes[3].plot(np.array(row['indices'])/len(row['indices']),np.linalg.norm(row['projected_displacements'],axis=1),label=row['model'])
    for ax in axes:ax.grid(alpha=.2);ax.legend()
    axes[3].set(xlabel='Fractional knot/address coordinate (each field keeps its own origin)',ylabel='Projected motion (px)');fig.savefig(dest/'distributed-fields.png',dpi=140);plt.close(fig)
    fig,axes=plt.subplots(3,1,figsize=(11,9),layout='constrained')
    for row in fields:
        if row['model'] not in ['stage-global','primary']:continue
        for ax,key in zip(axes,FIELD_LIMITS):ax.plot(np.arange(32)/32,row['fields'][key]['fitted'],'.-',label=row['model']);ax.set_ylabel(key+' total')
    for ax in axes:ax.grid(alpha=.2);ax.legend()
    axes[-1].set_xlabel('Fractional knot coordinate; inherited plus new fields, not just increments')
    fig.savefig(dest/'total-distributed-fields.png',dpi=140);plt.close(fig)
    rows=read(out/'comparison.json');diagnosis=read(out/'diagnosis.json');fig,axes=plt.subplots(3,1,figsize=(12,10),layout='constrained')
    for name in ['R306-primary','R307-primary','stage-global','stage-distributed','primary']:
        d=sorted([r for r in diagnosis if r['model']==name],key=lambda r:r['section'])
        if not d:continue
        axes[0].plot([r['section'] for r in d],[100*r['coherence'] if r['coherence'] is not None else np.nan for r in d],'.-',label=name)
        axes[1].plot([r['section'] for r in d],[r['metrics']['rms'] for r in d],'.-',label=name)
        axes[2].plot([r['section'] for r in d],[100*(r['metrics']['paper_occupation'] or 0) for r in d],'.-',label=name)
    for ax,label in zip(axes,['Dense modal ownership (%)','Strong reflection RMS (px)','Paper occupation (%)']):ax.set_ylabel(label);ax.grid(alpha=.2)
    axes[0].legend(ncol=2);axes[2].set_xlabel('Common photographic circuit section');fig.savefig(dest/'regional-comparison.png',dpi=140);plt.close(fig)
    # Extend the actual viewer with reviewable scientific plots and downloads.
    import re
    html=(dest/'index.html').read_text();html=re.sub(r'<section class="panel"><h2>R308 global and distributed experiments</h2>.*?</section>','',html,flags=re.S);panel='<section class="panel"><h2>R308 global and distributed experiments</h2>'
    for file in ['global-response-curves.png','coupled-response.png','predicted-versus-actual.png','distributed-fields.png','total-distributed-fields.png','regional-comparison.png','before-after.png','unknown-ray-separator.png']:panel+=f'<a href="{file}"><img src="{file}" style="width:100%;max-width:1100px" loading="lazy" alt="{file}"></a>'
    panel+='<p><a href="../analysis-summary.json">Machine-readable scientific summary</a> · <a href="../comparison.json">Common metrics</a> · <a href="../distributed-corrections.json">Correction fields and physical effects</a></p></section>'
    html=html.replace('</main>',panel+'</main>');(dest/'index.html').write_text(html)

def report(out):
    state=read(out/'checkpoint.json');comp=read(out/'comparison.json');accept=read(out/'acceptance.json');discovery=read(out/'global-discovery.json');compute=read(out/'computation.json');fields=read(out/'distributed-corrections.json');loc=read(out/'required-location.json');rank=read(out/'native-ranking.json.gz')
    primary=read(out/'exports/primary.json.gz');names=discovery['selected'];yes=accept['demonstrably_better'];p=primary['parameters'];curves=read(out/'response-curves.json') if (out/'response-curves.json').exists() else [];basins=read(out/'basins.json') if (out/'basins.json').exists() else []
    table=[]
    for name in ['R306-primary','R307-primary','stage-global','stage-distributed','stage-joint','primary']:
        r=next((r for r in comp if r['name']==name),None)
        if r:
            d=r['comparison'];q=r['R307_metrics']['comparison'];table.append(f"| {name} | {100*q['coherence']:.2f}% | {d['visible_boundary_mae']:.2f} | {d['reflection']['rms']:.2f} | {100*d['paper_occupied']:.2f}% | {100*d['colored_missing']:.2f}% | {d['envelope_width_mae']:.2f} |")
    sens='\n'.join(f"| {r['parameter']} | {r['physical_step']:.4g} | {r['scaled_sensitivity']:.3f} | {r['qr_order']+1} | {'yes' if r['selected'] else 'no'} |" for r in discovery['ranking'])
    stages=[]
    for stage in ['global','distributed','joint']:
        rec=state['stages'][stage]
        tr=read(out/'trials'/f"{rec['trial']:06d}.json.gz");stages.append(dict(stage=stage,trial=tr['id'],training_loss=tr['result']['loss'],result=tr['result'],elapsed=rec['elapsed']))
    fixed=read(out/'fixed-historical-owners.json.gz');original=next((r for r in fixed if r['baseline']=='R306-primary'),None)
    control_note=f"Original R306 fixed owners retain {original['final']['matched']} matches." if original and 'final' in original and 'matched' in original['final'] else ''
    if original and 'final' in original:control_note=f"Original R306 fixed owners have {original['final']['unmatched']} missing lobes; RMS with24px penalties is {original['penalized_rms_24px']:.2f}px. Their surviving-only RMS is not evidence of identity recovery."
    f=next(r for r in fields if r['model']=='primary');limits=f['correction'];baseline=read(out/'trials'/f"{state['baseline_id']:06d}.json.gz");globalrow=read(out/'trials'/f"{state['stages']['global']['trial']:06d}.json.gz")
    stage_text='; '.join(f"{r['stage']} {r['training_loss']:.4f}" for r in stages)
    totals=[]
    for k in FIELD_LIMITS:
        values=np.array(p[k]);totals.append(f"{k} max absolute {abs(values).max():.5g}, knot RMS {np.sqrt(np.mean(values*values)):.5g}")
    periodic=read(out/'periodic-controls.json.gz')
    periodic_compact=[dict(trial=r['trial'],phase_offset=r['offset'],original_native_loss=r['native_free']['loss'],repaired_native_loss=r['native_repaired_free']['loss'],half_pixel_loss=r['half_pixel_free']['loss'],fixed_initial_loss=r['native_fixed_initial']['loss'],changed_owners=r['changed_reflection_owners'],fixed_missing=r['native_fixed_initial']['unmatched']) for r in periodic['rows']]
    audit=read(out/'all-candidate-corrected-ranking.json');best_no_missing=next(r for r in audit['records'] if r['native_missing']==0);raw_best=audit['records'][0]
    audit_note=f"Best retained score with no additional missing fitting owners: trial{best_no_missing['trial']}. Raw minimum: trial{raw_best['trial']}, with{raw_best['native_missing']} missing fitting owners. All proposals and repeated copies remain saved."
    summary=dict(periodic_numerical_controls=periodic_compact,schema=308,answer_demonstrably_better=yes,global_parameters=names,ranked_sensitivities=discovery['ranking'],couplings=discovery['couplings'][:10],fitting={k:v for k,v in compute.items() if k not in ['accepted','initial_native_benchmark','evaluation_timing']},stages=[{k:v for k,v in r.items() if k!='result'} for r in stages],primary_stage=read(out/'selection.json')['primary_stage'],physical=dict(count=p['count'],hand=p['hand'],topology=p['topology'],certified=primary['physical']['certified'],pairs=primary['physical']['pairs']),corrections=limits,total_inherited_field_effect=f['total_field_effect'],required_location=[{k:v for k,v in r.items() if k not in ['supports','reflections']} for r in loc],acceptance=dict(demonstrably_better=accept['demonstrably_better'],failed_checks=[r for r in accept['checks'] if not r['passed']],large_regressions=accept['large_regressions']),limitations=['Historically exposed comparison data, not fresh validation','Conditional owners and discrete family identities','Nonsmooth native visibility and owner switching; finite-difference predictions must be tested','Bounded global/low-mode experiment does not exhaust geometric models'],links={k:v for k,v in [('report','R308_REPORT.md'),('comparison','comparison.json'),('corrected_metrics','corrected-comparison.json'),('regional_changes','regional-changes.json'),('sensitivity','global-discovery.json'),('derivative_reliability','derivative-reliability.json'),('curves','response-curves.json'),('repaired_curve_scores','corrected-response-replay.json'),('periodic_controls','periodic-controls.json.gz'),('timing','computation.json'),('all_stage_metrics','comparison.json'),('coupled_responses','response-pairs.json'),('corrections','distributed-corrections.json'),('fixed_owner_controls','fixed-historical-owners.json.gz'),('verification','verification.json'),('browser','browser-check.json'),('all_retained_candidate_audit','all-candidate-corrected-ranking.json'),('viewer','review/index.html'),('search','checkpoint.json')]})
    save(out/'analysis-summary.json',summary)
    repair=next((r for r in state.get('source_transitions',[]) if 'S25' in r.get('reason','')),None)
    repair_lead=(f"It was repaired after {repair['elapsed']/60:.2f} fitting minutes; the remaining {(state['elapsed']-repair['elapsed'])/60:.2f} minutes test the corrected treatment, not a complete new global campaign." if repair else 'This execution uses the corrected uncertainty treatment from its start.')
    version_note=('Earlier stage losses use the inherited treatment; repaired joint losses use the corrected treatment and cannot be directly subtracted.' if repair else 'All stage losses use the same corrected uncertainty treatment.')
    repair_detail=(f"A verified inherited defect was repaired at {repair['elapsed']:.3f} fitting seconds in this delivered campaign:" if repair else 'The inherited defect, corrected before this execution, was:')
    exposure_limit=('Most fitting predates the numerical-uncertainty repair, so this is not a complete-budget test of the corrected hierarchy.' if repair else 'This execution uses the corrected objective throughout; all historical comparison exposure remains acknowledged.')
    phase_curve=next((r for r in curves if r['parameter']=='phase'),dict(minima=[],rows=[]))
    repaired_scores={r['trial']:r['corrected_loss'] for r in read(out/'corrected-response-replay.json')['records']}
    phase_zero=next((r for r in phase_curve['rows'] if abs(r['offset'])<1e-10),None)
    better_phase=bool(phase_zero and any(r['feasible'] and repaired_scores[r['trial']]<repaired_scores[phase_zero['trial']]-1e-8 for r in phase_curve['rows']))
    periodic_note=f"The phase sweep contains {len(phase_curve['minima'])} sampled minima. {'A different sampled phase improves the corrected training score; common metrics still govern acceptance.' if better_phase else 'No sampled phase minimum improves the corrected training score over the original basin.'} {len(basins)} basin(s) met the guard conditions for derivative refinement. Other sampled minima remain saved."
    text=f'''# R308 — global basins and bounded distributed corrections

**{'Yes' if yes else 'No'}: this run {'meets' if yes else 'does not meet'} the stated substantial whole-necklace photographic improvement checks against both R306 and R307.**
Executed all three stages in **{compute['fitting_seconds']/60:.2f} fitting minutes**, including initial native profiling, global sensitivities, response sweeps, distributed and joint work. R306 used87.78 aggregate minutes; R30720.00. The final all-candidate repaired-score audit adds approximately **{compute.get('postfit_all_candidate_repair_audit_seconds_estimate',0)/60:.2f} minutes** (no new proposals); optimization plus this audit is **{(compute['fitting_seconds']+compute.get('postfit_all_candidate_repair_audit_seconds_estimate',0))/60:.2f} minutes**. These are warm starts using substantial historical computation, not equal cold-start benchmarks. The concrete scientific finding is an inherited false-boundary reward from unresolved native rays. {repair_lead}

[Launch viewer](review/r308/launch.sh) · [Reproduce](R308_REPRODUCE.md) · [JSON analysis summary](r308/results/campaign/analysis-summary.json) · [Before/after](r308/results/campaign/review/before-after.png).

## Which globals matter?

Pivoted QR selects **{', '.join(names)}** from the native full-circuit Jacobian with correction fields fixed. Finite-difference scales have physical units, so this ordering is conditional on the declared exploration scales; SVD values are not confidence intervals or a statistical identifiability rank. This initial ranking includes dropout/unknown-ray responses in the inherited score; it is not a claim to have identified eight physical constants. Corrected smaller-step matrices and unavailable derivative directions are saved separately.

| Parameter | Perturbation scale | Residual sensitivity norm | Independent QR order | Selected |
|---|---:|---:|---:|---|
{sens}

Strongest couplings: {', '.join(r['a']+'/'+r['b']+' '+format(r['cosine'],'.3f') for r in discovery['couplings'][:5])}. Shared directional illumination stays fixed. Integer count, helicity and topology remain discrete; five starts cover the R306/R307 primary and all four R306 physical families. Fixed count and true total arclength determine mean longitudinal spacing, so an independent redundant pitch variable is not added. No physical+1/+6/+7 neighbor identity is invented from highlights; exported neighbor geometry remains conditional.

## Periodic basins and stage contributions

Saved **{len(curves)} broad one-dimensional curves**, phase/registration and sensitivity-selected coupled grids, and **{len(basins)} qualifying refinement basin**. {periodic_note} Phase spans a complete2pi cycle; registration spans26px. Grid evaluations may cross worse intermediate states. Curves use native surface-compatible reassignment; derivatives inside each basin use fixed owners. Trial owners, missingness and physical failures are retained, so apparent periodic minima cannot be interpreted as verified bead identities.

The global-only training objective changed **{baseline['result']['loss']:.4f}→{globalrow['result']['loss']:.4f}**. Stage training losses are **{stage_text}** (distributed/joint include the declared small correction penalty). {version_note} The common photographic table compares every stage consistently. This is an objective measurement, not independent evidence of photographic improvement. The following unchanged R307 common metrics determine the scientific conclusion. Comparison evidence has already been exposed historically; it is retrospective, never a new independent test.

| Model | Dense coherent ownership | Visible boundary MAE px | Strong RMS px | Paper | Unexplained color | Rope-width MAE px |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

Development and comparison components, signed tangent/normal errors, dimensions,
separator errors and worst-decile distributions are in comparison.json; all32
geographic regions and regression flags are in regional-changes.json and diagnosis.json.
{control_note}

## Distributed corrections and physical validity

Fourier modes1–4 perturb the existing periodic32-knot axis, phase and spacing
fields. Global geometry is fixed during the distributed stage, then alternated
with four selected correction directions at a time. This avoids repeated dense
96-column local Jacobians. Full-chain arclength, phase and occlusion remain active
for every evaluation; no regions are detached and no bead has independent motion.

Maximum new increments: axis **{limits['axis_nodes']['maximum']:.4f}px**,
phase **{limits['local_phase']['maximum']:.5f}rad**, spacing **{100*limits['local_spacing']['maximum']:.4f}%**.
Their combined projected center displacement is at most **{limits['projected_center_displacement_max_px']:.3f}px** (limit **{limits['displacement_limit_px']:.3f}px**,10% of reference face diameter).
Total inherited-plus-new fields: {'; '.join(totals)}. Removing all inherited and new fields counterfactually changes projected centers by up to **{f['total_field_effect']['projected_displacement_from_zero_fields_max_px']:.2f}px**; the10%-diameter bound applies only to new R308 increments. Total phase-rate departure is **{100*f['total_field_effect']['phase_rate_fraction_max']:.3f}%** and spacing departure **{100*f['total_field_effect']['spacing_fraction_max']:.3f}%**. The inherited fields and total values are exported separately from new increments.
Conservative amplitude/rate limits and penalties are phenomenological exploration
controls, not measured thread strain or a complete mechanical crochet model.
The primary has **{p['count']} bodies, hand{p['hand']:+d}, {p['topology']} string**,
one closed periodic geometric axis and **{primary['physical']['pairs']} certified spatial close pairs**.
All physical bodies and all811 photographic observations remain represented.

## Native numerical performance and limitations

There are **{compute['trials']} native trials**. {audit_note} No coarse optics guided this run.
The first five actual whole-chain objective evaluations serve as representative
profiling measurements; every sensitivity, response sweep and contact check is
charged to fitting time. Peak fitting memory **{compute['peak_fitting_rss_mib']:.1f}MiB**;
export/diagnosis/verification **{compute['finalization_seconds']:.1f}s** separately.
Stopped because: **{compute['stop_reason']}**. Native step-size adaptation, if present, is part of the final joint stage and the same cumulative budget; its protocol/source transition is explicitly archived. Per-type evaluation costs, accepted
improvements/time, Jacobians/SVDs and predicted-versus-actual trust reductions
are saved. Native raster ownership and reflection lobes are nonsmooth; a derivative
can mispredict even when the renderer is accurate. Rejected steps and unmatched
lobes stay visible rather than disappearing from the score.

[The S25 diagnostic](r308/results/campaign/review/unknown-ray-separator.png) shows why numerical uncertainty must stay distinct from photographic gaps. {repair_detail} unresolved native rays had created false separator/contour edges and could appear as empty paper. S25 alone jumps5.31→9.62px under a0.06-degree tilt when one unknown ray resolves. The repair excludes uncertain edge transitions and treats uncertain paper conservatively. All old sources/trials survive; only the remaining original budget uses the repair. Post-seal response replays retrace the changed structural blocks at the SAME candidates, with original native optical blocks retained and independently checked against full predictions. Original and corrected objective losses are not interchangeable.

The principal remaining limitation is the measured inability of the tested global
basins plus small corrections to satisfy body ownership, visible boundaries,
background and reflections together. The acceptance record distinguishes actual
photographic gains from lower weighted loss. A failure here is evidence about this
bounded parameterization and explored basins, not proof that a longer run or new
maker labels would fix it. The(1110,336) case was never optimized separately;
before/after metrics and images remain in required-location.json and the atlas. Using only nonreflection positive interiors within90px, local coherence is **{' → '.join(format(100*r['coherence'],'.2f')+'%' for r in loc)}** (R306, R307, R308). This uses identical denominators across models; the earlier R307 local headline also included reflection regions and is not directly comparable. {exposure_limit}

## Delivery and stopping point

Standalone workflow: `python3 photo2/phase2_hierarchical_fit.py`; restart and output
options are documented in R308_REPRODUCE.md. Atomic transactions, native kernel and
periodicity/effect-bound contracts, original-Python geometry/contact/ray replays,
all-region preservation and actual browser navigation are recorded in the receipts.
The viewer preserves raw pixels, native owner picking, photographic/geometric axes,
recenter/follow, signed error plots, positive-interior overlap and competing owners.
Good, typical, poor and historical failure cases accompany all scientific plots.

Keep the strongest historical candidate available. No adoption unless the explicit
photographic checks pass; no Phase3, pattern inference or automatic R309. Stop after
verified commit/push. Current session/model may be retained for review; no /new needed.
'''
    if out.resolve()==(ROOT/'photo2/r308/results/campaign').resolve():(ROOT/'photo2/R308_REPORT.md').write_text(text)
    (out/'R308_REPORT.md').write_text(text.replace('r308/results/campaign/','').replace('review/r308/launch.sh','../../../../review/r308/launch.sh').replace('R308_REPRODUCE.md','../../../R308_REPRODUCE.md'))

def periodic_controls(out,data,m,obs):
    """Post-seal numerical controls only; never select or update a candidate."""
    path=out/'periodic-controls.json.gz'
    if path.exists():return
    state=read(out/'checkpoint.json');base=read(out/'trials'/f"{state['baseline_id']:06d}.json.gz");curves=read(out/'response-curves.json');phase=next(r for r in curves if r['parameter']=='phase')
    nonzero=sorted([r for r in phase['minima'] if abs(r['offset'])>.1],key=lambda r:r['loss'])[:2]
    targets=[dict(trial=base['id'],offset=0.)]+nonzero;obj=Objective(data,m,obs);rows=[];start=time.monotonic()
    for item in targets:
        trial=read(out/'trials'/f"{item['trial']:06d}.json.gz");s=Chain(trial['parameters'],data)
        _,fixed,a=obj.evaluate(s,base['anchors'],step=1.)
        _,repaired_native,_=obj.evaluate(s,trial['anchors'],step=1.)
        from .replay import structural
        blocks=structural(obj,s);expected=trial['result']['loss']+sum(blocks[k]-trial['result']['blocks'][k] for k in blocks)
        assert abs(repaired_native['loss']-expected)<1e-8,(repaired_native['loss'],expected)
        _,half,b=obj.evaluate(s,step=.5)
        rows.append(dict(trial=item['trial'],offset=item['offset'],native_free=trial['result'],native_repaired_free=repaired_native,native_fixed_initial=fixed,half_pixel_free=half,changed_reflection_owners=sum(trial['anchors']['reflections'][k]!=base['anchors']['reflections'][k] for k in base['anchors']['reflections']),native_half_owner_changes=sum(trial['anchors']['reflections'][k]!=b['reflections'][k] for k in b['reflections'])))
    save(path,dict(rows=rows,seconds=time.monotonic()-start,selection_sealed=read(out/'selection.json')['utc'],policy='Post-seal numerical/owner controls, never fitting. Entire circuit and all occluding bodies retained; missing fixed owners penalized. Half-pixel changes measure raster and assignment instability, not confidence intervals.'))

def derivative_reliability(out):
    records=[]
    for path in sorted((out/'sensitivities').glob('*.gz')):
        d=read(path);base=read(out/'trials'/f"{d['base']:06d}.json.gz");v=np.array(base['residual']);rows=[]
        for i,name in enumerate(d['names']):
            pair=[read(out/'trials'/f'{k:06d}.json.gz') for k in d['trials'][2*i:2*i+2]]
            row=dict(parameter=name,available_sides=sum(r['feasible'] for r in pair),missing_lobes=[r.get('result',{}).get('unmatched') for r in pair],base_missing=base['result']['unmatched'])
            if len(pair)==2 and all(r['feasible'] for r in pair):
                a,b=[np.array(r['residual']) for r in pair];row['second_difference_over_linear_difference']=float(np.linalg.norm(a+b-2*v)/max(1e-12,np.linalg.norm(b-a)))
                row['both_sides_worse']=all(r['result']['loss']>base['result']['loss'] for r in pair)
            rows.append(row)
        records.append(dict(block=path.stem,radius=d.get('radius',1.),rows=rows,methods=d.get('methods')))
    save(out/'derivative-reliability.json',dict(blocks=records,interpretation='Large second/first differences or lobe loss limit a local linear model. Unavailable derivative sides remain scored failures, not zero photographic information.'))

def corrected_metrics(out,models,data,m,obs):
    objects={split:Objective(data,m,obs,split,dense=True) for split in ['development','comparison']};rows=[]
    for model in models:
        path=out/'metrics'/f"{model['name']}-corrected.json.gz"
        if path.exists():details=read(path)
        else:
            scene=model_scene(model,data);details={split:o.evaluate(scene,step=1.,detail=True)[1] for split,o in objects.items()};save(path,details)
        rows.append(dict(model=model['name'],**{split:{k:v for k,v in d.items() if k not in ['supports','predictions','reflections']} for split,d in details.items()}))
    save(out/'corrected-comparison.json',dict(models=rows,policy='Same real evidence and corrected unknown-ray treatment for every historical and stage model. Legacy R307/common metrics remain separately intact in comparison.json. Never use a newly weighted loss alone as photographic acceptance.'))
