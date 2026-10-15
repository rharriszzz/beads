"""Frozen-model native evaluation, full visibility exports and offline review."""
import csv
import html
import time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from photo2.r295.finalize import visibility as native_visibility
from photo2.r282.common import runs
from .common import *
from .geometry import Chain, contact
from .objective import Objective, compact
from .search import merit


def native_observations(scene,data,splits):
    rows=[r for r in data['rows'] if r['split'] in splits];out=[]
    for r in rows:
        xy=pixels(r['pixels']);tr=scene.trace(xy);ids,counts=np.unique(tr['owner'],return_counts=True)
        alts=sorted([dict(index=int(scene.indices[j]),fraction=float(n/len(xy))) for j,n in zip(ids,counts) if j>=0],key=lambda x:(-x['fraction'],x['index']))
        fraction=alts[0]['fraction'] if alts else 0.;rival=alts[1]['fraction'] if len(alts)>1 else 0.
        out.append(dict(id=r['id'],kind=r['kind'],split=r['split'],point=r['point'],stratum=r['stratum'],color=r['color'],
            reflection=r['reflection'],accepted=r['accepted'],provenance=r['provenance'],trust=r['trust'],
            index=alts[0]['index'] if fraction>=.3 else None,containment=fraction,compatible=fraction>=.8 and fraction-rival>=.2,
            alternatives=alts,isolated_candidates=[dict(index=int(scene.indices[j]),fraction=float(v/len(xy)),visible_fraction=next((a['fraction'] for a in alts if a['index']==int(scene.indices[j])),0.)) for j,v in enumerate(tr['isolated_counts']) if v>0],unmatched_fraction=float(np.mean(tr['owner']<0)),unknown_pixels=int(tr['unknown'].sum()),identity_verified=False))
    return out


def summarize(rows):
    return dict(n=len(rows),compatible=sum(r['compatible'] for r in rows),
        mean_containment=float(np.mean([r['containment'] for r in rows])) if rows else None,
        unmatched=sum(r['index'] is None for r in rows))


def evaluate_model(identifier,p,data,splits,out,native,other_scenes):
    scene=Chain(p,data);cert=contact(scene,exact=True)
    if not cert['certified']:raise ArithmeticError(f'Final independent physical check failed: {identifier}')
    if scene.closed:
        closure=scene.closure()
        if max(closure[k] for k in ('axis_endpoint_gap','radial_endpoint_gap','tangent_endpoint_gap'))>1e-7:
            raise ArithmeticError('Periodic closure check failed')
    obs=native_observations(scene,data,splits)
    xy,_,d=native_visibility(scene,native.shape[:2]);owners=d['owner']
    signed=np.full(len(xy),np.iinfo(np.int32).min,np.int32);ok=owners>=0;signed[ok]=scene.indices[owners[ok]]
    np.savez_compressed(out/f'model-{identifier}-visibility.npz',xy=xy,owner=signed,unknown=d['unknown'],background_sentinel=np.iinfo(np.int32).min)
    visible=np.bincount(owners[ok],minlength=scene.n);isolated=d['isolated_counts'];fractions=visible/np.maximum(isolated,1)
    rows=[];all_surface=scene.surface_points();surface=all_surface[:,np.linspace(0,all_surface.shape[1]-1,64).astype(int)];projected=scene.project(surface.reshape(-1,3)).reshape(scene.n,-1,2)
    assignments={int(k):[] for k in scene.indices}
    for r in obs:
        if r['index'] is not None:assignments[r['index']].append(r)
    order=np.argsort(owners,kind='stable');sorted_owner=owners[order]
    for j,k in enumerate(scene.indices):
        links=assignments[int(k)];supported=any(r['compatible'] for r in links)
        alternatives=[s.pc[int(k-s.indices[0])] for s in other_scenes if s.indices[0]<=k<=s.indices[-1]]
        alternative_xy=np.asarray([scene.pc[j]]+alternatives)
        a,b=np.searchsorted(sorted_owner,[j,j+1]);pts=xy[order[a:b]]
        rows.append(dict(index=int(k),historical_index=int(k) if -20<=k<=200 else None,
            center_xyz=scene.centers[j].tolist(),projected_center=scene.pc[j].tolist(),axis_xyz=scene.line[j].tolist(),
            station_px=float(scene.station_px[j]),phase=float(scene.phase[j]),
            visible_pixels=int(visible[j]),isolated_pixels=int(isolated[j]),visible_fraction=float(fractions[j]),
            visible_runs=runs(pts),projected_surface_samples=projected[j].tolist(),
            compatible_support=supported,correspondences=[dict(id=r['id'],kind=r['kind'],split=r['split'],containment=r['containment'],compatible=r['compatible']) for r in links],
            support_status='photographic compatibility; owner unverified' if supported else 'geometry-only prediction',
            conditional_alternative_spread_px=float(np.linalg.norm(alternative_xy-scene.pc[j],axis=1).max()),
            uncertainty='Retained-family spread at same conditional index, not confidence interval or correspondence truth',
            physical_status=cert['state'],physical_identity_verified=False,model_color=None))
    for r in obs:
        r['modeled_visibility']=float(fractions[r['index']-scene.indices[0]]) if r['index'] is not None else None
    result=dict(id=identifier,parameters=p,closure=scene.closure(),contact=cert,observations=obs,
        summary={s:{kind:summarize([r for r in obs if r['split']==s and r['kind']==kind]) for kind in ('patch','region')} for s in splits},
        strata={s:summarize([r for r in obs if r['stratum']==s]) for s in ('central','peripheral')},
        low_modeled_visibility=summarize([r for r in obs if r['modeled_visibility'] is not None and r['modeled_visibility']<.1]),
        visibility=dict(native_rays=len(xy),unknown=int(d['unknown'].sum()),sites=scene.n,
            below_point_one=int(np.sum(fractions<.1)),supported=sum(r['compatible_support'] for r in rows),
            unsupported=sum(not r['compatible_support'] for r in rows)),
        diagnostics={s:compact(Objective(data,s,allow_reserved=s=='reserved').assess(scene)) for s in splits},
        limits='Native first-hit geometric compatibility is not verified photographic occlusion or physical ownership. Floating-point support/volume certificates, not interval arithmetic.')
    save(out/f'model-{identifier}.json.gz',dict(parameters=p,records=rows,photo=data['photo']))
    save(out/f'evaluation-{identifier}.json.gz',result)
    with (out/f'positions-{identifier}.csv').open('w') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['index','historical_index','x','y','visible_fraction','compatible_support','alternative_spread_px','physical_state'])
        for r in rows:writer.writerow([r['index'],r['historical_index'],*r['projected_center'],r['visible_fraction'],r['compatible_support'],r['conditional_alternative_spread_px'],r['physical_status']])
    return result,rows


def overlay(native,positions,observations):
    im=Image.fromarray(native).convert('RGBA');layer=Image.new('RGBA',im.size);draw=ImageDraw.Draw(layer)
    # Observations in cyan; geometry in orange/gray. No inferred pattern colors.
    for r in observations:
        x,y=r['point'];draw.ellipse((x-2,y-2,x+2,y+2),outline=(0,235,245,230),width=1)
    for r in positions:
        x,y=r['projected_center'];color=(255,165,35,220) if r['compatible_support'] else (175,175,175,165)
        for yy,a,b in r['visible_runs']:
            # Draw only the two ends of each visible native scanline: exact first-hit
            # edges also include annulus holes and occlusion boundaries.
            draw.point((a,yy),fill=color);draw.point((b,yy),fill=color)
        if r['index']%25==0 or r['index'] in (0,33,65,195,200):
            draw.text((x+3,y+2),str(r['index']),fill=(255,255,255,255),stroke_width=1,stroke_fill=(0,0,0,255))
        if r['index']==0:draw.ellipse((x-8,y-8,x+8,y+8),outline=(255,255,255,255),width=3)
    return Image.alpha_composite(im,layer).convert('RGB')


def progress_plot(history,path):
    import os
    os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r297-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,1,figsize=(10,5),sharex=True)
    x=[r['id'] for r in history]
    for key,label in [('best','Selected train/validation score'),('best_train','Selected training score'),('best_validation','Best validation score seen')]:
        axes[0].plot(x,[np.nan if r[key] is None else r[key] for r in history],label=label)
    axes[0].legend(fontsize=8);axes[0].set_ylabel('Sampled objective')
    axes[1].plot(x,np.cumsum([r['seconds'] for r in history]));axes[1].set(xlabel='Completed proposal',ylabel='Evaluation seconds')
    fig.tight_layout();fig.savefig(path,dpi=140);plt.close(fig)


def finalize(out,seal=False):
    out=Path(out);state=read(out/'checkpoint.json');data,_=load_evidence(state)
    if state['environment']!=environment():raise ValueError('Numerical environment changed since checkpoint')
    if state['sources']!=fingerprints():raise ValueError('Source changed: refuse to re-evaluate a saved run with different algorithms')
    if not state['pool']:
        review=out/'review';review.mkdir(parents=True,exist_ok=True)
        (review/'index.html').write_text('<!doctype html><title>No feasible model</title><h1>No certified model found</h1><p>Inspect checkpoint.json and candidate rejection records. No reconstruction is accepted.</p>')
        return
    pool=[read(out/'candidates'/f'{i:06d}.json.gz') for i in state['pool']]
    pool.sort(key=lambda r:(-merit(r),r['id']))
    # Export champion plus best distinct hand/topology families; no held-out choice.
    selected=[pool[0]];families={(pool[0]['parameters']['hand'],pool[0]['parameters']['topology'])}
    for r in pool[1:]:
        key=(r['parameters']['hand'],r['parameters']['topology'])
        if key not in families:selected.append(r);families.add(key)
    for r in pool:
        if len(selected)>=4:break
        if r not in selected:selected.append(r)
    frozen=dict(evaluation_protocol=read(BASE/'evidence/protocol.json'),ids=[r['id'] for r in selected],parameters={str(r['id']):r['parameters'] for r in selected},
        evidence=state['evidence'],photographic_cues=state['photographic_cues'],sources=state['sources'],selection='0.65 training + 0.35 validation; hand/topology alternatives retained; no reserved selection')
    if seal and not state['sealed']:
        # Freeze and latch are written before reading any reserved outcome. A crash
        # after sealing can rebuild exports but cannot resume optimization.
        save(out/'final-freeze.json',dict(utc=utc(),**frozen));state['sealed']=True;save(out/'checkpoint.json',state)
    if state['sealed']:
        old=read(out/'final-freeze.json')
        if any(old[k]!=frozen[k] for k in frozen):raise ValueError('Sealed models or sources changed')
    splits=['train','validation']+(['reserved','buffer'] if state['sealed'] else [])
    signature=digest(dict(frozen=frozen,splits=splits))
    review=out/'review';review.mkdir(parents=True,exist_ok=True);export=out/'exports';export.mkdir(exist_ok=True)
    native,_,_=photo();Image.fromarray(native).save(review/'original.png')
    scenes=[Chain(r['parameters'],data) for r in selected];evaluations=[];position_sets=[];images=[]
    cached=read(export/'manifest.json') if (export/'manifest.json').exists() else {}
    for r,scene in zip(selected,scenes):
        identifier=r['id'];print('Native evaluation/export',identifier,flush=True)
        if cached.get('signature')==signature and (export/f'evaluation-{identifier}.json.gz').exists():
            result=read(export/f'evaluation-{identifier}.json.gz');positions=read(export/f'model-{identifier}.json.gz')['records']
        else:result,positions=evaluate_model(identifier,r['parameters'],data,splits,export,native,scenes)
        evaluations.append(result);position_sets.append(positions)
        im=overlay(native,positions,result['observations']);im.save(review/f'model-{identifier}.png');images.append(im)
    save(export/'manifest.json',dict(signature=signature,ids=[r['id'] for r in selected],splits=splits))
    best=evaluations[0];obs=best['observations'];best_positions=position_sets[0]
    # Historical comparison uses identical archived native R295 rows, with explicit
    # conditional index changes. No whole-chain metric is compared to a local fit.
    old=read(ROOT/'photo2/r295/results/R295-evaluation.json')['observations'];new_by={r['id']:r for r in obs};changes=[]
    for r in old:
        q=new_by.get(r['id'])
        if q:changes.append(dict(id=r['id'],kind=r['kind'],point=r['point'],old_index=r['index'],new_index=q['index'],old_containment=r['containment'],new_containment=q['containment'],delta=q['containment']-r['containment'],index_changed=r['index']!=q['index']))
    save(export/'r295-comparison.json',dict(changes=changes,stable=sum(not r['index_changed'] for r in changes),total=len(changes),
        limits='Same native archived supports, retrospective. Original R295 local guard geometry differs from full-chain occlusion. Conditional labels are not certified identities.'))
    failures=sorted([r for r in obs if r['kind']=='region'],key=lambda r:(r['containment'],r['id']))
    strong=sorted([r for r in obs if r['kind']=='region'],key=lambda r:(-r['containment'],r['id']))
    crops=[];chosen=[]
    for label,items in [('Mismatch',failures),('Strong',strong)]:
        for r in items:
            if any(np.linalg.norm(np.asarray(r['point'])-q['point'])<150 for q in chosen):continue
            chosen.append(r);crops.append((label,r))
            if sum(x[0]==label for x in crops)>=3:break
    historical=[r for r in changes if r['kind']=='region' and r['old_index'] in (33,65,195)]
    for r in historical[:3]:crops.append(('Historical',new_by[r['id']]))
    # Eight geographic sectors cover the complete path, including both bends,
    # lower arc, left return and the approach to bead zero. Worst large support
    # in each sector is selected by a declared rule, not attractive appearance.
    stations={r['id']:r['station'] for r in data['rows']}
    for sector in range(8):
        candidates=[r for r in obs if r['kind']=='region' and int(stations[r['id']]/data['length']*8)%8==sector]
        if candidates:crops.append((f'Full circuit sector {sector}',min(candidates,key=lambda r:(r['containment'],r['id']))))
    crop_html=[]
    for j,(label,r) in enumerate(crops):
        x,y=map(int,r['point']);box=(max(0,x-95),max(0,y-80),min(native.shape[1],x+95),min(native.shape[0],y+80))
        raw=Image.fromarray(native).crop(box);model=images[0].crop(box);pair=Image.new('RGB',(raw.width*2,raw.height));pair.paste(raw,(0,0));pair.paste(model,(raw.width,0));pair.save(review/f'crop-{j}.png')
        crop_html.append(f'<figure><a href="crop-{j}.png"><img src="crop-{j}.png" alt="Original and geometric overlay for {html.escape(r["id"])}"></a><figcaption>{label}: {html.escape(r["id"])} · {r["containment"]:.1%} native containment · {r["split"]} · owner unverified</figcaption></figure>')
    progress_plot(state['history'],review/'progress.png')
    summary=dict(evaluation_protocol=frozen['evaluation_protocol'],stop_reason=state['stop_reason'],proposals=state['next_id'],search_seconds=state['elapsed_seconds'],sealed=state['sealed'],
        models=[dict(id=r['id'],parameters=r['parameters'],summary=r['summary'],strata=r['strata'],visibility=r['visibility'],closure=r['closure'],
                     physical={k:v for k,v in r['contact'].items() if k not in ('witnesses','index_pairs')}) for r in evaluations],
        failures=[dict(id=r['id'],point=r['point'],containment=r['containment'],index=r['index'],split=r['split']) for r in failures[:40]],
        r295_summary={kind:dict(n=sum(r['kind']==kind for r in changes),old_mean=float(np.mean([r['old_containment'] for r in changes if r['kind']==kind])),new_mean=float(np.mean([r['new_containment'] for r in changes if r['kind']==kind]))) for kind in ('patch','region')})
    save(out/'summary.json',summary)
    options='<option value="original.png">Original photograph</option>'+''.join(f'<option value="model-{r["id"]}.png" {"selected" if i==0 else ""}>Model {r["id"]}: {r["parameters"]["count"]} sites, hand {r["parameters"]["hand"]:+d}, {r["parameters"]["topology"]}</option>' for i,r in enumerate(selected))
    table=[]
    for r in evaluations:
        for split in splits:
            a=r['summary'][split]['region'];b=r['summary'][split]['patch']
            table.append(f'<tr><td>{r["id"]}</td><td>{split}</td><td>{a["compatible"]}/{a["n"]}</td><td>{a["mean_containment"]:.1%}</td><td>{b["compatible"]}/{b["n"]}</td><td>{r["visibility"]["unsupported"]}</td><td>{r["contact"]["minimum_gap_units"]:.5f}</td></tr>')
    links=''.join(f'<li>Model {r["id"]}: <a href="../exports/model-{r["id"]}.json.gz">all positions and native visible runs</a> · <a href="../exports/positions-{r["id"]}.csv">CSV</a> · <a href="../exports/evaluation-{r["id"]}.json.gz">assignments / contact / metrics</a> · <a href="../exports/model-{r["id"]}-visibility.npz">native visibility</a></li>' for r in evaluations)
    text=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R297 full-necklace Phase 2 review</title>
<style>body{{font:16px system-ui;max-width:1200px;margin:24px auto;padding:0 16px;background:#15191e;color:#e8edf2}}a{{color:#8ad9ff}}h1{{font-size:1.7rem}}p{{line-height:1.5}}img{{max-width:100%}}.scroll{{overflow:auto;max-height:80vh;background:#080a0c}}#whole{{max-width:none;width:100%}}select{{max-width:100%}}table{{border-collapse:collapse;font-size:14px}}td,th{{padding:7px;border:1px solid #566}}.table{{overflow:auto}}figure{{margin:18px 0}}figcaption{{font-size:14px}}button,input,select{{margin:5px;padding:5px}}li{{margin:9px 0}}</style>
<h1>R297 · conditional whole-necklace reconstruction</h1>
<p>{state['next_id']} proposals; {state['elapsed_seconds']:.1f}s cumulative search; stopped at {state['stop_reason']}. <strong>{'SEALED: reserved outcomes evaluated after freeze; this run cannot resume.' if state['sealed'] else 'RESUMABLE: development review only; retrospective reserved outcomes not re-evaluated.'}</strong></p>
<p>Orange geometry has compatible photographic support; gray geometry has no compatible support. Cyan dots are observed patch/region representatives. White numbers are conditional indices, with historical −20…200 retained and bead 0 circled. No repeating color pattern is used. Geometric centers are not measured patch centers.</p>
<p>Counts, helicity, topology and ownership remain competing hypotheses. The reference centerline is periodic by construction; its closure does not establish a physical joint. Bright-patch containment alone does not certify ownership. Native first-hit visibility is a model prediction.</p>
<label>View <select id="model">{options}</select></label><button id="toggle">Toggle original</button><label>Width <input id="zoom" type="range" min="500" max="3000" value="1100"></label>
<div class="scroll"><img id="whole" src="model-{selected[0]['id']}.png" alt="Whole original necklace with conditional reconstruction"></div>
<h2>Frozen photographic evidence</h2><p>Validation is development selection evidence. Previously revealed R296 reserved cases are retrospective final checks, excluded from this run's optimization; no fresh independent holdout remains. Central/peripheral and low modeled visibility statistics are in each evaluation export.</p>
<div class="table"><table><tr><th>Model</th><th>Split</th><th>Large compatible</th><th>Large containment</th><th>Patches compatible</th><th>Unsupported sites</th><th>Min plane gap</th></tr>{''.join(table)}</table></div>
<h2>Progress</h2><img src="progress.png" alt="Objective and computational progress">
<h2>Strong matches and failures · raw photograph on the left</h2>{''.join(crop_html)}
<h2>Auditable exports</h2><ul>{links}<li><a href="../exports/r295-comparison.json">R295 native-support and explicit index changes</a></li><li><a href="../summary.json">Summary and failure locations</a></li><li><a href="../checkpoint.json">Checkpoint, source hashes and search history</a></li></ul>
<script>const model=document.querySelector('#model'),whole=document.querySelector('#whole');let selected=model.value;model.onchange=()=>{{selected=model.value;whole.src=selected;}};document.querySelector('#toggle').onclick=()=>{{whole.src=whole.getAttribute('src')==='original.png'?selected:'original.png';}};document.querySelector('#zoom').oninput=e=>{{whole.style.width=e.target.value+'px';}};</script></html>'''
    (review/'index.html').write_text(text)
    from .debugger import build
    build(out,data,evaluations,position_sets)
    print('Final native review complete; reserved '+('evaluated after freeze' if state['sealed'] else 'not evaluated'),flush=True)
