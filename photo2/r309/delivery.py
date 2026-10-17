"""Native common-metric export, controlled explanations, review and report."""
from pathlib import Path
from copy import deepcopy
import time,shutil,resource
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import binary_erosion,binary_dilation,binary_fill_holes
from PIL import Image,ImageDraw,ImageOps
from photo2.r297.common import ROOT,read,save,sha,utc
from photo2.r297.geometry import reference
from photo2.r306.evidence import load
from photo2.r306.export import export_model
from photo2.r306.objective import Objective as Legacy
from photo2.r307.delivery import attach_guided
from .geometry import Chain
from .render import predict
from .search import sources,starts,OBJECTIVES
from .measure import Measures,reference_dimension,distances,summarize

def model_scene(model,data):return Chain(model['parameters'],data)

def export_predict(*args,**kwargs):
    pred,meta=predict(*args,**kwargs);meta.pop('unknown',None)
    return pred,meta

def complete_boundary(model,raster,measures,result):
    """Final both-way distances use the WHOLE selected native body, never ROI cuts."""
    from photo2.r305.forward import segments
    owner=raster['owner'];unknown=raster['unknown'];lookup={b['index']:b for b in model['positions']};rows=[]
    for cnt,cr in zip(measures.o.contours,result['contours']):
        b=lookup[cr['index']];seg=np.array(b['boundary_segments']).reshape(-1,4)
        # Observed polygons describe external visible silhouettes, not annotated holes.
        # Keep actual holes in the viewer; do not invent photographic hole boundaries.
        if len(seg):
            lo=np.maximum(0,np.floor(seg.reshape(-1,2).min(0)-2)).astype(int);hi=np.minimum([2540,3182],np.ceil(seg.reshape(-1,2).max(0)+2)).astype(int)
            mask=owner[lo[1]:hi[1],lo[0]:hi[0]]==cr['index']-model['positions'][0]['index']
            exterior=np.array(segments(binary_fill_holes(mask),int(lo[0]),int(lo[1]))).reshape(-1,4)
            cr['modeled_internal_boundary_segments_unmeasured']=len(seg)-len(exterior);seg=exterior
        ep=(seg[:,:2]+seg[:,2:])/2
        inside_xy=cnt['xy'][cnt['inside'].ravel()].astype(int);local_index=cr['index']-model['positions'][0]['index']
        if not np.any(owner[inside_xy[:,1],inside_xy[:,0]]==local_index):ep=np.empty((0,2))
        if len(ep):
            ij=np.clip(np.rint(ep).astype(int),[0,0],[2539,3181]);safe=~binary_dilation(unknown)[ij[:,1],ij[:,0]];ep=ep[safe]
        poly=np.asarray(cnt['row']['polygon']);op=[]
        for a,z in zip(poly,np.roll(poly,-1,axis=0)):
            t=np.linspace(0,1,max(2,int(np.ceil(np.linalg.norm(z-a)))+1))[:-1];op.extend(a[None]+t[:,None]*(z-a))
        op=np.array(op)
        for direction,source,target in [('observed-to-predicted',op,ep),('predicted-to-observed',ep,op)]:
            d=cKDTree(target).query(source)[0] if len(target) else np.full(len(source),np.nan)
            for p,e in zip(source,d):rows.append(dict(id=cnt['row']['id'],point=p.tolist(),direction=direction,error_px=float(e) if np.isfinite(e) else None,banded_error_px=float(max(0,e-3)) if np.isfinite(e) else None,index=cr['index'],split=measures.split,ambiguous=True,reliability='independent digitized visible contour, ±3px; conditional modeled owner'))
    result['fitting_roi_boundary_metrics']=result['metrics']['boundary'];result['boundary']=rows;result['metrics']=summarize(result,measures.D)

def combined(detail):
    keys=['reflections','boundary','supports','reverse_conflicts','material','separators','contours'];r={k:sum((v[k] for v in detail.values()),[]) for k in keys};r['unknown']=sum(v['unknown'] for v in detail.values());return r

def finalize(out):
    out=Path(out);began=time.monotonic();state=read(out/'checkpoint.json');assert state['sources']==sources();data,m,obs=load();D=reference_dimension(m);save(out/'D.json',D)
    for path in ['exports','metrics','review']:(out/path).mkdir(exist_ok=True)
    if not (out/'selection.json').exists():
        items=[];audit_started=time.monotonic();audit=[];training=Measures(data,m,obs)
        trialrows=[read(f) for f in sorted((out/'trials').glob('*.gz'))]
        for kind in OBJECTIVES:
            branch=state['branches'][kind];objective_audit_started=time.monotonic()
            pool=sorted([r for r in trialrows if r['feasible'] and (r['id'] in state['shared'] or r['tag'].startswith(kind+':'))],key=lambda r:r['result']['scores'][kind]);chosen=[]
            for row in pool:
                if not any(row['parameters']==x['parameters'] for x in chosen):chosen.append(row)
                if len(chosen)==2:break
            best=next(r for r in trialrows if r['id']==branch['best'])
            if not any(best['parameters']==r['parameters'] for r in chosen):chosen.append(best)
            ranked=[]
            for row in chosen:
                result=training.evaluate(Chain(row['parameters'],data));ranked.append(dict(trial=row['id'],parameters=row['parameters'],free_native_scores=result['scores'],missing=result['missing']))
            ranked.sort(key=lambda r:r['free_native_scores'][kind]);r=ranked[0];audit.append(dict(objective=kind,seconds=time.monotonic()-objective_audit_started,accepted_incumbent=branch['best'],ranked=ranked))
            items.append(dict(name='R309-'+kind,parameters=r['parameters'],trial=r['trial'],objective=kind))
            g=read(out/'trials'/f"{branch['global_only_best']:06d}.json.gz")
            if kind=='balanced':items.append(dict(name='R309-global-control',parameters=g['parameters'],trial=g['id'],objective=kind))
        save(out/'selection-audit.json',dict(seconds=time.monotonic()-audit_started,objectives=audit,policy='Native free-owner training reevaluation of the two best unique completed settings plus accepted incumbent per objective. No new parameter proposals; includes completed steps from interrupted final numerical blocks. Separate from fitting time, before comparison.'))
        best=next(r for r in items if r['name']=='R309-balanced')
        for item in list(items):
            if item['name'] not in ['R309-balanced','R309-reflection']:continue
            if any(item['parameters'].get(k,0) for k in ['minor_y','tilt_y','tilt_y2']):
                q=deepcopy(item['parameters']);q.update(minor_y=0.,tilt_y=0.,tilt_y2=0.);items.append(dict(name=item['name']+'-zeroheight',parameters=q,diagnostic_only=True,objective=item['objective']))
        items.insert(0,dict(best,name='primary'))
        items+=starts();save(out/'selection.json',dict(utc=utc(),models=items,policy='Each winner selected by its OWN native training score; primary is balanced for inspection, not adopted physical truth. Seal before comparison outcomes.'))
        state['sealed']=True;save(out/'checkpoint.json',state)
    items=read(out/'selection.json')['models'];models=[];details={};summary=[]
    import photo2.r306.export as ex
    ex.Chain=Chain;ex.predict=export_predict
    oldobjects={s:Legacy(data,m,obs,s) for s in ['development','comparison']};objects={s:Measures(data,m,obs,s,dense=True) for s in oldobjects}
    for item in items:
        model=ex.export_model(item,out,data,m,obs,oldobjects);name=model['name'];file=out/'metrics'/f'{name}.json.gz'
        if file.exists():detail=read(file)
        else:
            scene=Chain(model['parameters'],data);raster=np.load(out/'exports'/f'{name}-raster.npz');detail={}
            for split,obj in objects.items():
                result=obj.evaluate(scene);complete_boundary(model,raster,obj,result);detail[split]=result
            save(file,detail)
        attach_guided(model,detail,obs);save(out/'exports'/f'{name}.json.gz',model);details[name]=detail;models.append(model)
        allr=combined(detail);metric=summarize(allr,D['D_px']);catalog=model['guided_correspondences']['records']
        # Absolute maxima include weak/uncertain observations; missing stays explicit.
        for row in catalog:row['reliability']='strong localized' if row['strong'] else 'weak/diffuse/uncertain';row['ambiguous']=True
        owners={}
        for row in allr['reflections']:
            if row['index'] is not None:owners.setdefault(str(row['index']),[]).append(row['id'])
        metric['cross_split_duplicate_strong_owners']={k:v for k,v in owners.items() if len(v)>1}
        metric['assignment_policy']='One-to-one within each historically frozen training/comparison split; cross-split duplicates retained explicitly, not certified physical identities.'
        metric['ownership_by_confidence']={}
        for label,predicate in [('qualitatively_accepted',lambda x:x['confidence']==1),('compact_automatic',lambda x:x['confidence']==.5),('possible_same_color_merger',lambda x:x['confidence']<.5)]:
            subset=[x for x in allr['supports'] if predicate(x)];metric['ownership_by_confidence'][label]=dict(regions=len(subset),coherent_percent=100*float(np.mean([x['modal_fraction'] for x in subset])) if subset else None,competing_percent=100*float(np.mean([x['competing_fraction'] for x in subset])) if subset else None,major_conflicts=sum(x['major_conflict'] for x in subset))
        metric['catalog_absolute']=distances(catalog,D['D_px']);metric['boundary']['independent_contours']=len(allr['contours']);metric['boundary']['observation_unit']='correlated boundary sample points; independent contours counted separately'
        metric['catalog_reliable']=distances([r for r in catalog if r['strong']],D['D_px']);metric['catalog_by_color']={c:distances([r for r in catalog if r['color']==c],D['D_px']) for c in ['black','red','yellow']}
        departure=[dict(id=b['index'],point=b['axis_xy'],error_px=abs(v),ambiguous=False) for b,v in zip(model['positions'],model['reference_departure_px'])]
        metric['geometric_axis_departure']=distances(departure,D['D_px']);metric['separator']=distances([dict(id=x['id'],error_px=x['error'],ambiguous=True,reliability='dark separator; not necessarily empty paper') for x in allr['separators']],D['D_px'])
        metric['smooth_intensity_surrogate']=distances(allr['reflections'],D['D_px'],'smooth_distance_px')
        metric['signed_tangent_magnitude']=distances([dict(x,error_px=abs(x['tangent_px']) if x['tangent_px'] is not None else None) for x in allr['reflections']],D['D_px'])
        metric['signed_normal_magnitude']=distances([dict(x,error_px=abs(x['normal_px']) if x['normal_px'] is not None else None) for x in allr['reflections']],D['D_px'])
        raster=np.load(out/'exports'/f'{name}-raster.npz');en=ex.native_envelope(Chain(model['parameters'],data),m,raster['owner']);edges=[];widths=[]
        for er,pair in zip(m['envelope'],en):
            if not er['fit_eligible']:continue
            for side in range(2):edges.append(dict(id=er['id']+':'+str(side),point=er['point'],error_px=float(abs(pair[side]-er['bounds'][side])),ambiguous=True,reliability=er['meaning']))
            widths.append(dict(id=er['id'],point=er['point'],error_px=float(abs(np.diff(pair)[0]-np.diff(er['bounds'])[0])),ambiguous=True,reliability=er['meaning']))
        metric['foreground_supported_edge_distance']=distances(edges,D['D_px']);metric['rope_width_discrepancy']=distances(widths,D['D_px'])
        metric['dimensions']=dict(reference_face_model_px=2*model['parameters']['radius']*model['parameters']['scale'],axial_to_face=.7*model['parameters']['axial'],minor_y=model['parameters'].get('minor_y',0),tilt_y=model['parameters'].get('tilt_y',0),tilt_y2=model['parameters'].get('tilt_y2',0),perspective=model['parameters']['perspective'],light_inverse=model['parameters'].get('light_inverse',0))
        summary.append(dict(model=name,all=metric,splits={s:d['metrics'] for s,d in detail.items()},parameters=model['parameters'],physical={k:v for k,v in model['physical'].items() if k not in ['witnesses','index_pairs']},closure=model['closure']))
        print('R309 outcomes',name,metric['reflection']['rms_D'],metric['boundary']['rms_D'],metric['ownership']['coherent_percent'],flush=True)
    save(out/'comparison.json',summary)
    diagnostics(out,models,details,D['D_px']);acceptance(out,summary,details,D['D_px']);fixed_controls(out,models,details,data,objects,D['D_px'])
    # Reuse native interactive navigation without mutating old implementations.
    from . import review
    review.prepare_guided_review(out,models)
    state['history']=[dict(id=r['id'],loss=r['result']['scores']['balanced']) for f in sorted((out/'trials').glob('*.gz')) if (r:=read(f))['feasible']];save(out/'checkpoint.json',state)
    shutil.copyfile(ROOT/'photo2/r306/results/campaign/R305-problem-cohorts.json',out/'R305-problem-cohorts.json')
    review.build(out,models,m,obs);atlas(out,models,details,D['D_px']);plots(out,summary,details,state,D['D_px']);dashboard(out,summary,D['D_px'])
    from .verify import verify,boundary_audit
    verification=verify(out)
    boundary_audit(out)
    save(out/'computation.json',dict(postfit_native_selection_seconds=read(out/'selection-audit.json')['seconds'],fitting_seconds=state['elapsed'],preflight_seconds=read(ROOT/'photo2/r309/results/preflight/preflight.json')['seconds'],trials=state['next_id'],peak_fit_rss_mib=state['peak_rss_mib'],finalization_seconds=time.monotonic()-began,peak_finalize_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,branches={k:{j:v for j,v in b.items() if j!='controls'} for k,b in state['branches'].items()},shared_trials=len(state['shared'])))
    from .analysis import run as analyze_numerics
    analyze_numerics(out)
    from .analysis import predictiveness
    predictiveness(out)
    report(out)


def diagnostics(out,models,details,D):
    regional=[];height=[];phase=[];ref=reference()
    for model in models:
        name=model['name'];r=combined(details[name]);refs=r['reflections']
        for j in range(32):
            rr=[x for x in refs if x['section']==j];ss=[x for x in r['supports'] if x['section']==j];mat=[x for x in r['material'] if x['section']==j]
            if not ss:continue
            regional.append(dict(model=name,section=j,priority=1-np.mean([s['modal_fraction'] for s in ss]),coherence=float(np.mean([s['modal_fraction'] for s in ss])),metrics=dict(n=len(rr),paper_occupation=float(np.mean([z['paper'] for z in mat])) if mat else None),reflection=distances(rr,D),support_count=len(ss)))
        for side in ['left','right']:
            for bin in range(6):
                subset=[x for x in refs if (x['observed'][0]<1270)==(side=='left') and int(min(5,x['observed'][1]/3182*6))==bin];valid=[x for x in subset if x['predicted']]
                height.append(dict(model=name,side=side,height_midpoint=(bin+.5)*3182/6,reflection=distances(subset,D),tangent_mean_px=float(np.mean([x['tangent_px'] for x in valid])) if valid else None,normal_mean_px=float(np.mean([x['normal_px'] for x in valid])) if valid else None))
        # Conditional phase proxy only. No catalog pair certifies physical identity.
        rows=[];positions={b['index']:b for b in model['positions']}
        for x in refs:
            b=positions.get(x['index']);near=positions.get(x['index']+1) if x['index'] is not None else None
            if b and near and x['tangent_px'] is not None:
                step=np.linalg.norm(np.array(b['axis_xy'])-near['axis_xy']);proxy=x['tangent_px']/max(.1,step)*2*np.pi/model['parameters']['turn']
                rows.append(dict(id=x['id'],arc=x['arc'],signed_tangent_px=x['tangent_px'],conditional_phase_proxy_rad=float(proxy),wrapped_proxy_rad=float((proxy+np.pi)%(2*np.pi)-np.pi),unwrapped_phase_error=None,physical_identity_verified=False,possible_integer_slips=True,ambiguous=x['ambiguous']))
        valid=[x for x in refs if x['error_px'] is not None];slopes={k:float(np.polyfit([x['arc']/ref.length for x in valid],[x[k] for x in valid],1)[0]) for k in ['error_px','tangent_px','normal_px']}
        phase.append(dict(model=name,rows=rows,descriptive_slopes_px_per_circuit=slopes,unwrapped_identified=False,reason='No verified physical owners or connected sequence of unambiguous adjacent beads. Dividing signed tangent displacement by projected axial advance is conditional; never unwrap across gaps or infer an integer index drift.'))
    save(out/'diagnosis.json',regional);save(out/'height-diagnostics.json',height);save(out/'phase-diagnostics.json.gz',phase)
    required=[]
    for model in models:
        r=combined(details[model['name']]);point=np.array([1110.23,336.04]);ss=[x for x in r['supports'] if np.linalg.norm(np.array(x['point'])-point)<90];rr=[x for x in r['reflections'] if np.linalg.norm(np.array(x['observed'])-point)<90]
        required.append(dict(model=model['name'],point=point.tolist(),coherence_percent=100*float(np.mean([x['modal_fraction'] for x in ss])),supports=ss,reflection=distances(rr,D)))
    save(out/'required-location.json',required)


def acceptance(out,summary,details,D):
    baselines=[r for r in summary if r['model'] in ['R306-primary','R307-primary','R308-primary']];results=[];regional=read(out/'diagnosis.json')
    for r in summary:
        if not r['model'].startswith('R309-'):continue
        tests=[];regressions=[];z=r['all']
        for b in baselines:
            a=b['all'];checks=dict(reflection_rms=z['reflection']['rms_px']<=.95*a['reflection']['rms_px'],boundary_rms=z['boundary']['rms_px']<=.95*a['boundary']['rms_px'],ownership=z['ownership']['coherent_percent']>=a['ownership']['coherent_percent']+2,reflection_max=z['reflection']['maximum_px']<=a['reflection']['maximum_px']+.05*D,boundary_max=z['boundary']['maximum_px']<=a['boundary']['maximum_px']+.05*D,missing=z['reflection']['missing']<=a['reflection']['missing'],paper=z['material']['background_occupation_percent']<=a['material']['background_occupation_percent']+1,foreground=z['material']['foreground_omission_percent']<=a['material']['foreground_omission_percent']+1)
            tests.append(dict(baseline=b['model'],checks=checks))
            before={x['section']:x for x in regional if x['model']==b['model']}
            for x in [v for v in regional if v['model']==r['model']]:
                old=before[x['section']];bad=[]
                if x['coherence']<old['coherence']-.1:bad.append('ownership')
                if (x['metrics']['paper_occupation'] or 0)>(old['metrics']['paper_occupation'] or 0)+.05:bad.append('background')
                if min(x['reflection']['measured'],old['reflection']['measured'])>=3 and x['reflection']['rms_px']>old['reflection']['rms_px']+3:bad.append('reflection')
                if bad:regressions.append(dict(baseline=b['model'],section=x['section'],failures=bad))
        results.append(dict(model=r['model'],tests=tests,regional_regressions=regressions,passed=all(all(t['checks'].values()) for t in tests) and not regressions))
    save(out/'acceptance.json',dict(demonstrably_better=any(r['passed'] for r in results),models=results,baseline_preserved=True,policy='Predeclared component, maxima, missingness and geographic gates in R309_SPECIFICATION.md. Retrospective evidence; no statistical-significance claim.'))


def fixed_controls(out,models,details,data,objects,D):
    path=out/'fixed-owner-controls.json.gz'
    if path.exists():return
    rows=[]
    for model in models:
        if not model['name'].startswith('R309-'):continue
        p=model['parameters'];base=next((b for b in models if b['name'].startswith('R306-') and all(b['parameters'][k]==p[k] for k in ['count','hand','topology','seam_fraction'])),None)
        if not base:rows.append(dict(model=model['name'],fixed_owner_control=None,reason='Different discrete count/topology: no asserted physical index equivalence.'));continue
        for split,obj in objects.items():
            r=obj.evaluate(Chain(p,data),details[base['name']][split]['anchors']);rows.append(dict(model=model['name'],baseline=base['name'],split=split,fixed=r['metrics']['reflection'],free=details[model['name']][split]['metrics']['reflection'],records=r['reflections']))
    save(path,rows)


def atlas(out,models,details,D):
    image=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');primary=models[0];base=next(r for r in models if r['name']=='R306-primary');rs=combined(details['primary'])['supports'];sort=sorted(rs,key=lambda r:r['modal_fraction']);locations=[([1110.23,336.04],'Required location')]
    locations += [(sort[int(q*(len(sort)-1))]['point'],label) for q,label in [(.9,'Good ownership'),(.5,'Typical ownership'),(.1,'Poor ownership')]]
    old={r['id']:r for r in combined(details['R306-primary'])['supports']};worst=min(rs,key=lambda r:r['modal_fraction']-old[r['id']]['modal_fraction']);locations.append((worst['point'],'Largest ownership regression'))
    locations += [([2300,1650],'Right middle'),([1300,2970],'Bottom'),([550,603],'D reference upper left')]
    gallery=[]
    for num,(point,label) in enumerate(locations):
        pos=primary['positions'];j=int(np.argmin([np.linalg.norm(np.array(b['projected_center'])-point) for b in pos]));chosen=pos[max(0,j-25):min(len(pos),j+25)];xy=np.array([b['projected_center'] for b in chosen]);lo=np.maximum(0,np.floor(xy.min(0)-50)).astype(int);hi=np.minimum([2540,3182],np.ceil(xy.max(0)+50)).astype(int)
        raw=image.crop((*lo,*hi));panels=[raw]
        for model in [base,primary]:
            panel=raw.copy();d=ImageDraw.Draw(panel)
            for b in model['positions']:
                x,y=b['projected_center']
                if not lo[0]-60<x<hi[0]+60 or not lo[1]-60<y<hi[1]+60:continue
                for x,y,a,c in b['boundary_segments']:d.line((x-lo[0],y-lo[1],a-lo[0],c-lo[1]),fill='#22ddeb')
            for r in model['guided_correspondences']['records']:
                a=np.array(r['observed']);b=r['predicted']
                if b is None or not np.all((a>=lo)&(a<hi)):continue
                a=a-lo;b=np.array(b)-lo;d.line((*a,*b),fill='#ff831f',width=1);d.ellipse((*(a-2),*(a+2)),outline='yellow');d.ellipse((*(b-2),*(b+2)),outline='white')
            panels.append(panel)
        canvas=Image.new('RGB',(3*raw.width,raw.height+55),'#182832');draw=ImageDraw.Draw(canvas)
        for i,(im,title) in enumerate(zip(panels,['Original photograph','R306','R309 balanced'])):canvas.paste(im,(i*raw.width,55));draw.text((i*raw.width+5,5),title,fill='white')
        draw.text((5,23),f'{label}; {len(chosen)} consecutive conditional bodies; all panels native1px/px',fill='white');draw.line((5,44,5+D,44),fill='white',width=2)
        file=f'atlas-{num:02d}.png';canvas.save(out/'review'/file);raw.save(out/'review'/f'atlas-raw-{num:02d}.png');gallery.append(dict(image=file,point=point,label=label,crop=[*map(int,lo),*map(int,hi)],body_count=len(chosen),indices=[chosen[0]['index'],chosen[-1]['index']],raw=f'atlas-raw-{num:02d}.png'))
        if num==0:canvas.save(out/'review/before-after.png')
    save(out/'atlas.json',gallery)


def plots(out,summary,details,state,D):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    selected=['R306-primary','R307-primary','R308-primary']+['R309-'+k for k in OBJECTIVES];ref=reference()
    fig,ax=plt.subplots(3,1,figsize=(13,10),sharex=True,layout='constrained')
    for name in selected:
        rows=sorted(combined(details[name])['reflections'],key=lambda r:r['arc']);x=[r['arc']/ref.length for r in rows]
        for a,key in zip(ax,['error_px','tangent_px','normal_px']):a.plot(x,[r[key]/D if r[key] is not None else np.nan for r in rows],'.-',ms=2,lw=.5,label=name)
    for a,label in zip(ax,['Euclidean reflection displacement / D','Signed tangent / D','Signed normal / D']):a.set_ylabel(label);a.grid(alpha=.2)
    ax[0].legend(ncol=3,fontsize=8);ax[-1].set_xlabel('Original photographic geographic arclength / circuit length');fig.savefig(out/'review/circuit-errors.png',dpi=130);plt.close(fig)
    fig,ax=plt.subplots(1,2,figsize=(13,5),layout='constrained');names=[r['model'] for r in summary if r['model'] in selected]
    for a,key in zip(ax,['reflection','boundary']):
        for stat in ['rms_D','maximum_D','p95_D']:a.plot(names,[next(r for r in summary if r['model']==n)['all'][key][stat] for n in names],'.-',label=stat)
        a.set_title(key+' distance / fixed D');a.tick_params(axis='x',rotation=35);a.legend();a.grid(alpha=.2)
    fig.savefig(out/'review/normalized-errors.png',dpi=130);plt.close(fig)
    h=read(out/'height-diagnostics.json');fig,ax=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for name in ['R306-primary','R309-balanced','R309-reflection']:
        for side,style in [('left','-'),('right','--')]:
            rows=[r for r in h if r['model']==name and r['side']==side];x=[r['height_midpoint'] for r in rows]
            for a,key in [(ax[0,0],'rms_D'),(ax[0,1],'maximum_D')]:a.plot(x,[r['reflection'][key] for r in rows],style+'o',label=name+' '+side,ms=3)
            for a,key in [(ax[1,0],'tangent_mean_px'),(ax[1,1],'normal_mean_px')]:a.plot(x,[r[key]/D if r[key] is not None else np.nan for r in rows],style+'o',label=name+' '+side,ms=3)
    for a,title in zip(ax.ravel(),['RMS/D','Maximum/D','Mean tangent/D','Mean normal/D']):a.set(xlabel='Photographic height y (px)',title=title);a.grid(alpha=.2)
    ax[0,0].legend(fontsize=7);fig.savefig(out/'review/height-errors.png',dpi=130);plt.close(fig)
    trials=[read(f) for f in sorted((out/'trials').glob('*.gz'))]
    from .search import Runner
    shared_rows=[]
    for i,(_,tag) in enumerate(Runner.shared_plan(None)[:len(state['shared'])]):
        row=deepcopy(next(r for r in trials if r['id']==state['shared'][i]));row['requested_tag']=tag;row['tag']=tag;shared_rows.append(row)
    curves=[r for r in shared_rows if r['tag'].startswith(('curve:','count:','height-light:'))];save(out/'parameter-responses.json.gz',curves)
    keys=['phase','s0','turn','count','minor_y','tilt_y','tilt_y2','perspective','light_inverse'];fig,axs=plt.subplots(3,3,figsize=(14,11),layout='constrained')
    for a,key in zip(axs.ravel(),keys):
        for family in ['R306-primary','R306-alternative-2665']:
            rr=[r for r in curves if (':'+family+':') in r['tag'] and ((':'+key+':') in r['tag'] or key=='count' and r['tag'].startswith('count:')) and r['feasible']]
            for kind in OBJECTIVES:
                rr=sorted(rr,key=lambda r:r['parameters'][key] if key!='count' else r['parameters']['count']);a.plot([r['parameters'][key] for r in rr],[r['result']['scores'][kind] for r in rr],'.-' if family=='R306-primary' else '.--',label=kind+' '+family.replace('R306-',''))
        a.set_title(key);a.grid(alpha=.2)
    axs[0,0].legend(fontsize=6);fig.savefig(out/'review/responses.png',dpi=130);plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(12,7),layout='constrained')
    for name in ['R306-primary','R309-balanced']:
        model=read(out/'exports'/f'{name}.json.gz');pos=model['positions'];axes[0].plot([b['photo_arc']/ref.length for b in pos],np.array(model['reference_departure_px'])/D,'.',ms=1,label=name)
        witnesses=model['physical']['witnesses'];axes[1].plot([pos[w['pair'][0]]['photo_arc']/ref.length for w in witnesses],[w['gap_units']/model['parameters']['radius'] for w in witnesses],'.',ms=1,label=name)
    axes[0].set_ylabel('Geometric axis minus photo reference / D');axes[1].set_ylabel('Certified support margin / bead radius');axes[1].set_xlabel('Photographic arclength / circuit');axes[0].legend();axes[1].legend();fig.savefig(out/'review/physical-axis.png',dpi=130);plt.close(fig)


def dashboard(out,summary,D):
    import html,json
    rows=[]
    for r in summary:
        z=r['all'];a=z['reflection'];b=z['boundary'];rows.append('<tr><td>'+html.escape(r['model'])+'</td>'+''.join(f'<td>{v:.3f}</td>' for v in [a['rms_px'],a['rms_D'],a['maximum_px'],a['maximum_D'],a['p95_px'],a['p95_D'],b['rms_px'],b['maximum_px'],z['ownership']['coherent_percent'],z['material']['background_occupation_percent']])+f'<td>{a["missing"]}</td></tr>')
    figures=['circuit-errors','normalized-errors','height-errors','responses','physical-axis','predicted-actual'];atlas=read(out/'atlas.json')
    page=f'''<!doctype html><meta charset="utf-8"><title>R309 common photographic errors</title><style>body{{font:16px system-ui;margin:24px;background:#14232e;color:#edf3f5}}a{{color:#8edfff}}table{{border-collapse:collapse}}td,th{{padding:8px;border:1px solid #567}}img{{max-width:100%;height:auto}}p{{max-width:1000px}}</style><h1>R309: what the errors mean</h1><p><a href="index.html">Interactive necklace: native owner picking and interior overlap</a> · <a href="../analysis-summary.json">Machine-readable summary</a> · <a href="../R309_REPORT.md">Report</a></p><p>D={D:.3f}px is a fixed independent visible-contour major-axis reference, ±6px, not the true largest bead. An orange vector connects the observed reflection (yellow ring) to its predicted centroid (white ring). Its Euclidean length is the positional error; it is not a bead-center error or an intensity error. Cyan lines are modeled visible boundaries. Uncertain orange photographic contours are evidence, not exact truth. Selection yellow does not denote bead color.</p><p>All physical identities are conditional. Missing reflections are counted separately, never assigned zero error. Boundary measurements exist only for16 uncertain digitized contours; other external bead boundaries remain unmeasured. All comparison data have historical exposure.</p><div style="overflow:auto"><table><tr><th>Model</th><th>Reflection RMS px</th><th>RMS/D</th><th>Max px</th><th>Max/D</th><th>P95 px</th><th>P95/D</th><th>Boundary RMS px</th><th>Boundary max px</th><th>Ownership %</th><th>Paper %</th><th>Missing strong</th></tr>{''.join(rows)}</table></div>'''
    page+=''.join(f'<h2>{x.replace("-"," ")}</h2><a href="{x}.png"><img src="{x}.png"></a>' for x in figures)
    page+='<h2>Consecutive-body atlas: identical coordinates and native zoom</h2>'+''.join(f'<p>{html.escape(r["label"])} · {r["body_count"]} bodies</p><a href="{r["image"]}"><img src="{r["image"]}"></a>' for r in atlas)
    (out/'review/science.html').write_text(page)
    js=out/'review/viewer.js';js.write_text(js.read_text()+f'''\nconst R309_D={D};const r309OriginalDetails=details;details=function(){{r309OriginalDetails();let el=document.getElementById('r309Units');if(!el){{el=document.createElement('p');el.id='r309Units';document.getElementById('overlapDetail').before(el);}}const rr=model.correspondences.records.filter(r=>r.index===selected);el.textContent='Fixed photographic D='+R309_D.toFixed(3)+' px. '+(rr.length?rr.map(r=>r.id+': '+(r.error_px===null?'missing predicted centroid':r.error_px.toFixed(2)+' px = '+(r.error_px/R309_D).toFixed(3)+' D')+'; '+(r.strong?'reliable location, conditional owner':'weak/uncertain observation')).join(' | '):'No observed reflection assigned to selected body; visibility is not a positional error.');}};details();\n''')
    index=out/'review/index.html';s=index.read_text().replace('</header>','<p><a href="science.html">R309 common D, error meanings, response curves and 50-bead atlas</a></p>'+('' if read(out/'acceptance.json')['demonstrably_better'] else '<p><strong>No R309 candidate passed all photographic acceptance checks.</strong> “primary” is the balanced comparison candidate; historical models remain available.</p>')+'</header>');index.write_text(s)


def report(out):
    rows=read(out/'comparison.json');state=read(out/'checkpoint.json');accept=read(out/'acceptance.json');D=read(out/'D.json');pre=read(ROOT/'photo2/r309/results/preflight/preflight.json');comp=read(out/'computation.json');lookup={r['model']:r for r in rows};primary=lookup['R309-balanced'];baseline=lookup['R306-primary'];table=[]
    for r in rows:
        if r['model']=='primary':continue
        z=r['all'];a=z['reflection'];b=z['boundary'];table.append(f"| {r['model']} | {a['rms_px']:.2f}/{a['rms_D']:.3f} | {a['maximum_px']:.2f}/{a['maximum_D']:.3f} | {a['p95_px']:.2f}/{a['p95_D']:.3f} | {b['rms_px']:.2f}/{b['rms_D']:.3f} | {b['maximum_px']:.2f}/{b['maximum_D']:.3f} | {b['p95_px']:.2f}/{b['p95_D']:.3f} | {z['ownership']['coherent_percent']:.2f} | {z['material']['background_occupation_percent']:.2f} | {z['material']['foreground_omission_percent']:.2f} | {a['missing']} |")
    outcomes=[]
    for kind in OBJECTIVES:
        a=lookup['R309-'+kind]['all'];b=baseline['all'];improved=dict(reflection=a['reflection']['rms_px']<b['reflection']['rms_px'],boundary=a['boundary']['rms_px']<b['boundary']['rms_px'],ownership=a['ownership']['coherent_percent']>b['ownership']['coherent_percent'],background=a['material']['background_occupation_percent']<b['material']['background_occupation_percent'],foreground=a['material']['foreground_omission_percent']<b['material']['foreground_omission_percent']);outcomes.append(dict(objective=kind,improved=improved,improvements=sum(improved.values()),accepted=next(r for r in accept['models'] if r['model']=='R309-'+kind)['passed']))
    numerical=read(out/'numerical-descent.json.gz');height_controls=read(out/'height-controls.json')
    ranked=sorted(outcomes,key=lambda r:-r['improvements']);best=ranked[0];r=primary['all'];absolute=r['catalog_absolute']['maximum_record'];strong=r['reflection']['maximum_record'];trials=[read(f) for f in sorted((out/'trials').glob('*.gz'))];shared=[r for r in trials if r['id'] in state['shared'] and r['feasible']];height=[r for r in shared if r['tag'].startswith('height-light:')];controls=read(out/'fixed-owner-controls.json.gz');location=read(out/'required-location.json')
    cause=dict(correspondence=dict(tested='Full-cycle phase, registration, turn and count±1/±13 probes for2405 and2733 families; signed circuit residuals, conditional wrapped phase proxies and fixed-owner controls.',finding='No verified connected physical-owner sequence supports unwrapping or an integer indexing diagnosis. Shared response curves and matched/missing controls quantify aliasing, not physical identity recovery.'),numerics=dict(tested='Original/compiled trace and finite-light shadow agreement, exact versus unthresholded intensity, two finite-difference scales, native/half-pixel sampling and threshold0.25/0.5/0.75.',finding='Smooth intensity overlap does not make visibility smooth: phase and height-tilt derivatives disagree across scales. Discontinuous branches use bounded coordinate brackets, rejecting unreliable Jacobian steps.'),height=dict(tested='Same-height left/right photo-half residual bins; global minor-radius gradient, linear/quadratic orientation, camera perspective and one finite shared light.',parameters=r['dimensions'],finding='Global laws are evaluated across both sides and complete physical geometry. Different limbs and conditional owners prevent identifying a unique physical-versus-projection explanation from a slope alone.'),objective=dict(tested='Four globally applied objectives with the same shared pool and equal remaining time; normalized L2 plus fourth-moment tail.',outcomes=outcomes,finding='Individual outcome gains do not constitute whole-photo acceptance; exact maxima, missingness, all components and geography control acceptance.'))
    fixed_rows=[];all_fixed=[]
    for kind in OBJECTIVES:
        name='R309-'+kind;records=sum([x.get('records',[]) for x in controls if x['model']==name],[]);z=distances(records,D['D_px']);fixed_rows.append(f"| {kind} | {z['rms_px']:.2f}/{z['rms_D']:.3f} | {z['maximum_px']:.2f}/{z['maximum_D']:.3f} | {z['p95_px']:.2f}/{z['p95_D']:.3f} | {z['missing']} |" if records else f"| {kind} | unmeasured | unmeasured | unmeasured | distinct count |")
        all_fixed += [dict(x,model=name,control='fixed R306 family owner') for x in records if x['error_px'] is not None]
    absolute_control=max(all_fixed,key=lambda r:r['error_px']) if all_fixed else None
    control_note=(f"The campaign's largest measured fixed-control displacement is {absolute_control['error_px']:.2f}px / {absolute_control['error_px']/D['D_px']:.3f}D, reliable-location observation {absolute_control['id']} at({absolute_control['observed'][0]:.2f},{absolute_control['observed'][1]:.2f}); its physical owner is conditional." if absolute_control else 'No same-count fixed-owner control is available; physical index equivalence was not invented.')
    local_before=next(x for x in location if x['model']=='R306-primary');local_after=next(x for x in location if x['model']=='primary')
    height_text=' '.join(f"{x['model']}: retaining height terms changes reflection RMS by {x['reflection_rms_change_px']:+.3f}px, boundary RMS by {x['boundary_rms_change_px']:+.3f}px, ownership by {x['coherence_change_pp']:+.3f}pp and paper occupation by {x['background_change_pp']:+.3f}pp." for x in height_controls['final_all_circuit_ablations'])
    color_table='\n'.join(f"| {c} | {z['observations']} | {z['rms_px']:.2f}/{z['rms_D']:.3f} | {z['maximum_px']:.2f}/{z['maximum_D']:.3f} | {z['p95_px']:.2f}/{z['p95_D']:.3f} | {z['missing']} |" for c,z in r['by_color'].items())
    family=lookup['R306-alternative-2665']['all'];family_text=f"Most balanced-versus-primary gains come from selecting the already-retained2733 family. Against that R306 alternative, balanced reflection RMS worsens {family['reflection']['rms_px']:.2f}→{r['reflection']['rms_px']:.2f}px and boundary RMS {family['boundary']['rms_px']:.2f}→{r['boundary']['rms_px']:.2f}px; ownership rises {family['ownership']['coherent_percent']:.2f}→{r['ownership']['coherent_percent']:.2f}%."
    cause['correspondence']['fixed_control_absolute_maximum']=absolute_control
    cause['height']['ablation_findings']=height_controls['final_all_circuit_ablations']
    cause['numerics']['GN_proposals']=numerical['actual_GN_proposals']
    save(out/'causes.json',cause)
    summary=dict(schema=309,D=D,demonstrably_better=accept['demonstrably_better'],primary_for_review='R309-balanced',best_component_count=best,objective_outcomes=outcomes,causes=cause,typical_and_worst=r['reflection'],absolute_catalog=r['catalog_absolute'],absolute_fixed_control=absolute_control,physical=primary['physical'],fitting=comp,links={k:v for k,v in [('report','R309_REPORT.md'),('viewer','review/index.html'),('geometric_error_dashboard','review/science.html'),('comparison','comparison.json'),('raw_residuals','metrics/primary.json.gz'),('parameter_responses','parameter-responses.json.gz'),('phase','phase-diagnostics.json.gz'),('predicted_vs_actual','numerical-descent.json.gz'),('objective_predictiveness','objective-predictiveness.json'),('height_controls','height-controls.json'),('height','height-diagnostics.json'),('fixed_owners','fixed-owner-controls.json.gz'),('acceptance','acceptance.json'),('verification','verification.json'),('atlas','atlas.json'),('search','checkpoint.json')]})
    save(out/'analysis-summary.json',summary)
    text=f'''# R309 — competing whole-necklace measurements

**{'Accepted improvement' if accept['demonstrably_better'] else 'No convincing whole-photograph improvement'} under the predeclared component, worst-error and regional checks.** The experiment ran automatically on Python/compiled CPU code for {comp['fitting_seconds']/60:.2f} fitting minutes after a {pre['seconds']:.1f}s preflight. Native reevaluation of already completed finalist settings adds {comp['postfit_native_selection_seconds']:.1f}s, before comparison; no new proposals. It retains the historical alternatives and every failed trial. No Phase3 or color-pattern inference.

[Interactive viewer](review/r309/launch.sh) · [Geometric error dashboard](r309/results/campaign/review/science.html) · [JSON summary](r309/results/campaign/analysis-summary.json) · [Reproduce](R309_REPRODUCE.md).

## One photographic length

**D={D['D_px']:.3f}px**, the longest major-axis/Feret chord among16 independently digitized R298 visible contours, B14 at(550.375,602.75). Each end is uncertain by3px, so the conservative length uncertainty is±6px. This is a fixed reference, **not an established maximum over every photographed bead**. No fitted bead dimensions or pixel areas determine it. The [original-photo/endpoints image](r309/results/preflight/D-reference.png) and all16 measurements are retained. All linear results use this identicalD; area measures are percentages.

## Common outcomes

Each distance cell is **pixels / bead-reference diameters**. Strong-reflection distances are Euclidean observed-coordinate to predicted0.5-peak-centroid distances; smooth fitting intensity is a separate surrogate. Boundary distances cover both directions against16 uncertain external observed contours, using the complete modeled visible silhouette at final evaluation. Internal hole edges lack independent photographic annotations and remain unmeasured; actual holes remain visible in the viewer. Other bead exteriors remain unmeasured. Individual distances, maxima locations/IDs, color groups, uncertainty counts, training/comparison and missing cases remain in the full residual files. Paper/foreground percentages average frozen cue fractions over geographic bands; ownership averages observed regions, not pixel area. Boundary sample counts are correlated points across16 contours. All comparison evidence was exposed historically.

| Model | Reflection RMS | Reflection max | Reflection P95 | Boundary RMS | Boundary max | Boundary P95 | Ownership% | Paper% | Foreground omitted% | Missing strong |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

The balanced candidate's reliable maximum is **{strong['error_px']:.2f}px / {strong['error_px']/D['D_px']:.3f}D**, observation {strong['id']} at({strong['observed'][0]:.2f},{strong['observed'][1]:.2f}). The absolute matched catalog maximum is **{absolute['error_px']:.2f}px / {absolute['error_px']/D['D_px']:.3f}D**, {absolute['id']} at({absolute['observed'][0]:.2f},{absolute['observed'][1]:.2f}), classified {absolute['reliability']}. There are269 reliable observations and{r['catalog_absolute']['missing']} unmatched catalog observations in this model. Missing observations have no measurable positional distance: they remain counted and penalized, never zeroed or silently removed. Physical identities are conditional even for reliable reflection locations. The preflight's old `uncertain_correspondences` field measures close alternative margins only; final tables count all unverified physical identities separately from close alternatives.

Balanced candidate by reliable reflection color (pixels / D; all physical owners conditional):

| Color | N | RMS | Maximum | P95 | Missing |
|---|---:|---:|---:|---:|---:|
{color_table}

## Controlled objective comparison

All objectives use the same starts and shared probes, including2405/hand−/open and2733/hand−/closed;2204/hand+/closed and R307/R308 are also preserved. Remaining allowances are equal; cache reuse and actual branch seconds are in computation.json. Single-emphasis objectives retain a small material/missingness cost; balanced includes all four. Fourth-moment tails emphasize large reliable errors while exact maxima remain independent acceptance quantities. All local spline/phase/spacing fields stay frozen. There are no regional optimization variables or independent bead motions.

Component-improvement counts versus R306: {', '.join(x['objective']+' '+str(x['improvements'])+'/5' for x in outcomes)}. **{best['objective']}** has the largest count (ties and magnitudes remain in the tables), which is descriptive rather than proof of best reconstruction. Combining measurements {'meets the full acceptance gate' if accept['demonstrably_better'] else 'does not establish a globally superior model'}. A low mean with large residual maxima remains incomplete. {family_text}

Fixed R306-family owner controls expose the cost of reassignment (pixels / D):

| Objective | RMS | Maximum | P95 | Missing |
|---|---:|---:|---:|---:|
{chr(10).join(fixed_rows)}

{control_note} These controls do not assert that R306 identities were correct. They show why low rematched errors are not identity recovery.

At the required(1110,336) location, mean positive-interior ownership improves **{local_before['coherence_percent']:.2f}→{local_after['coherence_percent']:.2f}%** and reliable reflection RMS **{local_before['reflection']['rms_D']:.3f}→{local_after['reflection']['rms_D']:.3f}D**. This location was never optimized separately. The50-body before/after atlas still shows overextended lower boundaries; this local gain does not represent the entire circuit.

## Four possible causes

1. **Correspondence / phase drift.** Full-cycle phase and registration response curves, global turn/count alternatives, signed tangent/normal circuit plots and fixed-owner controls were tested. Errors fluctuate; recovery alone is not accumulating index drift. No verified adjacent-owner chain supports unwrapped physical phase, so integer slips remain explicitly unresolved. All periodic trials and alternative assignments survive.
2. **Numerical reflection instability.** Native/original centroids agree exactly, and finite-source shadow intensities agree to machine precision. Changing threshold0.25→0.75 changes baseline strong training RMS only {pre['thresholds'][0]['metrics']['rms_px']:.3f}→{pre['thresholds'][-1]['metrics']['rms_px']:.3f}px. Half-pixel sampling changes it {pre['sampling']['native']['rms_px']:.3f}→{pre['sampling']['half']['rms_px']:.3f}px. But perturbation derivatives can change sign and lose lobes. Unthresholded overlap does **not** eliminate visibility discontinuity. Gradient steps are rejected when local linearity fails; bounded coordinate brackets remain. R308's corrected unknown-ray treatment is used from the beginning.
3. **Top-to-bottom variation.** Left/right photo-half residuals are compared at the same six height bands. Global linear minor-radius, linear/quadratic orientation, perspective and finite-distance shared lighting are tested separately in the shared pool and jointly in small parameter blocks. The balanced fit uses a {100*r['dimensions']['minor_y']:.2f}% minor-radius gradient per normalized image height and {r['dimensions']['tilt_y']:.2f}° linear tilt, with zero quadratic tilt/perspective and directional lighting. These modest whole-photo laws remain conditional; image-height trends cannot uniquely separate physical geometry, camera and ownership. The finite source never becomes per-bead lighting.
4. **Inadequate combined objective.** Four competing objectives are fitted, then all are measured against all outcomes. Their disagreements, ownership conflicts, largest errors and geographic regressions are explicit. Final supported external-boundary distances use whole-body native outlines and exclude unannotated internal holes; fitting's smaller all-visible-edge contour windows remain separately labeled in the residuals, avoiding a hidden claim of complete observed boundary evidence.

Height ablations hold fitted globals fixed. {height_text} These changes do not establish a material photographic gain from height variation. Fixed-owner derivative predictions agree in direction with native bracket outcomes for {100*(numerical['direction_agreement'] or 0):.1f}% of nonzero comparisons; {numerical['actual_GN_proposals']} gradient proposals passed the local numerical gate. The gate required every column of a block to be reliable; therefore this run tests bounded coordinate refinement, not a successful coupled Gauss–Newton method. The saved matrices do not prove that every derivative direction is unusable.

## Physical construction, performance and limits

The balanced full model has {primary['parameters']['count']} physical bodies, hand{primary['parameters']['hand']:+d}, {primary['parameters']['topology']} string, and one periodic geometric centerline distinct from the photograph. All{primary['physical']['pairs']} spatial close pairs certify, minimum support margin{primary['physical']['independent_minimum_gap']:.6f} source units. Full native visibility includes every body; the +1/+6/+7 predictions are conditional, not independently measured bead identities. All811 catalog observations survive.

Executed{state['next_id']} native trials. Peak fitting memory{comp['peak_fit_rss_mib']:.1f}MiB; finalization/independent checks{comp['finalization_seconds']:.1f}s separately from fitting, including the ranking audit above. Browser and subsequent segment/report audits are additional verification, not fitting. The standalone program schedules probes, rejects unstable gradients, checkpoints/resumes, exports and verifies without AI optimization decisions. It deliberately uses one numerical process to keep the20-minute aggregate fitting allowance interpretable.

The principal unresolved obstacle is simultaneous visible-body ownership, complete boundary placement and optical correspondence under a nonsmooth native visibility model. The controlled measurements constrain explanations but do not establish unique physical indexing, projection or lighting. See causes.json for the test/outcome ledger and acceptance.json for each failed gate. Keep historical baselines; no adoption based on weighted loss. Stop after verified commit/push.
'''
    if out.resolve()==(ROOT/'photo2/r309/results/campaign').resolve():(ROOT/'photo2/R309_REPORT.md').write_text(text)
    (out/'R309_REPORT.md').write_text(text.replace('r309/results/campaign/','').replace('review/r309/launch.sh','../../../review/r309/launch.sh').replace('R309_REPRODUCE.md','../../../R309_REPRODUCE.md').replace('r309/results/preflight/','../preflight/'))
