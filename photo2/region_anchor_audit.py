#!/usr/bin/env python3
"""Frozen observed-region anchor audit on two calibrated synthetic patches."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import sys

import numpy as np
from PIL import Image, ImageDraw
from skimage.segmentation import find_boundaries

from detect_beads import PALETTES
from inference_audit import verify_inputs, write_json
from legacy_visibility import decode, font
from local_patch import PARAMETERS, assess, fit, image_evidence, retained_hypotheses, warp
from local_patch_audit import (BOX, CLICKS, WARPS, baseline_assessment, evaluate,
                               verify_manifest)
from practice_legacy import ROOT, digest
from region_anchors import (REGION_PARAMETERS, apply_gate, correspondence,
                            interior_distances, legacy_gate, region_gate)

HERE = ROOT/'photo2'
NEW_BOX = (80, 650, 490, 1060)
NEW_CLICKS = {1: [(165,810), (220,835), (220,775), (280,810)],
             -1: [(170,770), (225,800), (225,740), (280,775)]}
SOURCES = ('photo2/region_anchors.py', 'photo2/region_anchor_audit.py',
           'photo2/test_region_anchors.py', 'photo2/local_patch.py',
           'photo2/local_patch_audit.py', 'photo2/detect_beads.py',
           'photo2/inference_audit.py', 'photo2/legacy_visibility.py',
           'photo2/practice_legacy.py', 'photo2/practice-pattern.json')


def source_hashes():
    return {name: digest(ROOT/name) for name in SOURCES}


def variants(anchors):
    result = [('nominal', anchors)]
    for radius in (3, 6):
        for dx, dy in ((radius,0),(-radius,0),(0,radius),(0,-radius)):
            result.append((f'shift-{dx:+d}-{dy:+d}', anchors+[dx,dy]))
    # Generate four slots even for three-anchor condition: paired first three.
    rng = np.random.default_rng(5201)
    for i in range(8):
        result.append((f'independent-{i}', anchors+rng.integers(-6,7,(4,2))[:len(anchors)]))
    return result


def summarize(evaluation, gate):
    """Nominal seed truth defines origin for every jitter, including wrong seeds."""
    seed = gate['anchor_labels'][0]
    records = evaluation['records'] if gate['anchor_ok'] else []
    claimed = [r for r in records if r['supported']]
    matches = [r for r in claimed if r['matched'] and r['eligible_truth']]
    correct = [r for r in matches if r['model_label']-seed == r['actual_relative_index']]
    visible = evaluation['all_model']['missing_truth'] + [r['truth_label']-1
               for r in evaluation['records'] if r['matched'] and r['eligible_truth']]
    matched_ids = {r['truth_label']-1 for r in matches}
    return dict(predictions=len(claimed), matched=len(matches),
                false_predictions=sum(not r['matched'] for r in claimed),
                ignored=sum(r['matched'] and not r['eligible_truth'] for r in claimed),
                eligible_truth=evaluation['all_model']['eligible_truth'],
                correct_index=len(correct), wrong_index=len(matches)-len(correct),
                correct_color=sum(r['correct_color'] for r in matches),
                correct_region_color_index=sum(r['correct_color'] for r in correct),
                unknown_color=sum(r['color']=='unknown' for r in matches),
                missing_truth=sorted(set(visible)-matched_ids))


def anchor_diagnostics(evaluation, observed_evaluation, gate, nominal_truth_labels):
    """Detect a click selecting a different observed/model bead than intended."""
    model = {r['model_label']:r for r in evaluation['records']}
    observed = {r['model_label']:r for r in observed_evaluation['records']}
    records = []
    for i,(label,expected) in enumerate(zip(gate['anchor_labels'],nominal_truth_labels)):
        m=model.get(label,{})
        o=observed.get(gate.get('observed_labels',[0]*len(nominal_truth_labels))[i],{})
        records.append(dict(expected_truth_index=int(expected)-1,
            model_truth_index=m.get('truth_label',0)-1,
            model_correct=bool(m.get('matched') and m.get('truth_label')==expected),
            observed_truth_index=o.get('truth_label',0)-1,
            observed_correct=bool(o.get('matched') and o.get('truth_label')==expected)))
    return dict(anchors=records, all_model_anchors_correct=all(r['model_correct'] for r in records),
                all_observed_anchors_correct=(all(r['observed_correct'] for r in records)
                                              if 'observed_labels' in gate else None))


def draw_panel(path, full, box, rgb, observed, anchors, entries, masks, nominal, rows, title):
    im = Image.new('RGB', (1640, 760), 'white')
    d = ImageDraw.Draw(im)
    d.text((8,8), title+' | calibrated geometry; indices conditional', fill='black', font=font(21))
    context = full.copy()
    ImageDraw.Draw(context).rectangle(box, outline='magenta', width=6)
    context.thumbnail((400,255)); im.paste(context,(5,480))
    arrays = [rgb.copy(), rgb.copy()]
    arrays[1][find_boundaries(observed,mode='inner')] = (0,220,255)
    titles = ['Beauty; assistant-marked clicks', 'Observed watershed regions']
    selected = []
    for method in ('legacy','region'):
        kept = nominal['retained'][method]
        candidates = [c for c in entries if c['name'] in kept] or entries
        best = min(candidates,key=lambda c:c['fit']['train_mean'])
        selected.append(best)
        arr = rgb.copy(); arr[find_boundaries(masks[best['name']],mode='inner')] = (255,0,255)
        arrays.append(arr)
        titles.append(method+': '+best['name']+(' ACCEPTED' if kept else ' rejected'))
    for j,arr in enumerate(arrays):
        x=410*j
        im.paste(Image.fromarray(arr),(x,65))
        d.text((x+4,43),titles[j],fill='black',font=font(14))
        for i,(ax,ay) in enumerate(anchors):
            d.ellipse((x+ax-4,65+ay-4,x+ax+4,65+ay+4),outline='white',width=2)
            d.text((x+ax+5,65+ay),str(i),fill='white',font=font(13))
        if j >= 2:
            method=('legacy','region')[j-2]; best=selected[j-2]
            if best['name'] in nominal['retained'][method]:
                gate=nominal['gates'][method][best['name']]
                for obj in apply_gate(best['objects'],gate)['objects']:
                    if obj['relative_index'] is None: continue
                    yy,xx=np.nonzero(masks[best['name']]==obj['model_label'])
                    tx,ty=x+int(xx.mean()),65+int(yy.mean())
                    text=f"{obj['relative_index']:+d}"
                    d.rectangle(d.textbbox((tx,ty),text,font=font(10)),fill='black')
                    d.text((tx,ty),text,fill='white',font=font(10))
    for k,method in enumerate(('legacy','region')):
        x=430+590*k
        kept=nominal['retained'][method]
        d.text((x,495),method+' retained: '+(', '.join(kept) or 'none'),fill='black',font=font(15))
        for n,row in enumerate(rows[method].items()):
            name,s=row
            line=f"{name}: {s['matched']}/{s['eligible_truth']} regions, {s['correct_index']} correct indices, {s['false_predictions']} false"
            d.text((x,523+23*n),line,fill='black',font=font(14))
    d.text((430,700),'Cyan: image segmentation. Magenta: predicted contours, including unsupported bodies.',fill='black',font=font(16))
    d.text((430,725),'All jitter variants, competing hands and failures remain in JSON. No photo recovery claim.',fill='black',font=font(16))
    im.save(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,default=HERE/'output/neighbor-audit-final')
    parser.add_argument('--fixtures',type=Path,default=HERE/'output/detection-fixtures-r045-final')
    parser.add_argument('--detection',type=Path,default=HERE/'output/detection-audit-r045-final')
    parser.add_argument('--templates',type=Path,default=HERE/'output/local-patch-templates-r047-final')
    parser.add_argument('--previous',type=Path,default=HERE/'output/local-patch-r047-verified')
    parser.add_argument('--output',type=Path,default=HERE/'output/region-anchors-r052')
    args=parser.parse_args()
    for key,value in vars(args).items():setattr(args,key,value.resolve())
    if args.output.exists() and any(args.output.iterdir()):raise ValueError('Output must be empty')
    before=source_hashes()
    _,revisions=verify_inputs(args.baseline)
    reports={name:verify_manifest(getattr(args,name)/'report.json')
             for name in ('fixtures','detection','templates','previous')}
    args.output.mkdir(parents=True,exist_ok=True)
    bank=reports['templates']['candidates']
    pattern=json.loads((HERE/'practice-pattern.json').read_text())['colors']*20
    cases=[('ryb-phase-0','ryb',1),('gray-phase-0','gray',1),('black-phase-0','black',1),
           ('repeat-40-h-1-phase-0','rgb',-1)]
    trials=[]
    for patch,box,clicks in [('old',BOX,CLICKS),('new',NEW_BOX,NEW_CLICKS)]:
        for name,palette,hand in cases:
            image_path=(args.baseline/(name+'-beauty.png') if palette=='rgb' else args.fixtures/(name+'.png'))
            full=Image.open(image_path).convert('RGB')
            for condition in (WARPS if patch=='old' else ['identity']):
                trial=f'{patch}-{name}-{condition}'
                print('Assess '+trial,flush=True)
                if patch=='old':
                    stem=f'{name}-{condition}-sv'
                    saved=json.loads((args.previous/(stem+'-prediction.json')).read_text())
                    rgb=np.asarray(Image.open(args.previous/(stem+'-input.png')).convert('RGB'))
                    anchors=np.asarray(saved['anchors'])
                    with np.load(args.previous/(stem+'-predicted-masks.npz')) as arrays:
                        observed=arrays['no_model'].copy()
                        masks={c['name']:arrays['smooth_'+c['name']].copy() for c in bank}
                    entries=[dict(name=c['name'],hand=c['hand'],phase=c['phase'],fit=c['fit'],
                                  objects=c['assessment']['objects']) for c in saved['methods']['smooth']]
                else:
                    rgb=np.asarray(full.crop(box)); anchors=np.asarray(clicks[hand],float)-box[:2]
                    observed=np.asarray(Image.open(args.detection/(name+'-gray_boundary-labels.png')).crop(box),dtype=np.int32)
                    _,distance=image_evidence(rgb)
                    entries=[]; masks={}
                    for c in bank:
                        # Full forward-model render, not observed ID truth.
                        template=decode(np.asarray(Image.open(args.templates/(c['name']+'.png')).convert('RGB').crop(box)),800)
                        alignment=fit(template,distance,'smooth')
                        labels=warp(template,alignment['coefficients']); masks[c['name']]=labels
                        assessment=assess(labels,distance,anchors,palette,rgb)
                        entries.append(dict(name=c['name'],hand=c['hand'],phase=c['phase'],fit=alignment,
                                            objects=assessment['objects']))
                tables={c['name']:correspondence(observed,masks[c['name']],c['objects']) for c in entries}
                interiors={c['name']:interior_distances(masks[c['name']]) for c in entries}
                predictions=[]
                for count in (3,4):
                    group=anchors[:count]
                    conditions=variants(group)+[
                        ('false_background',np.vstack([[20.,20.],group[1:]])),
                        ('duplicate',np.vstack([group[1],group[1:]])),
                        ('exclude_true_phase',group)]
                    for variant,points in conditions:
                        gates={'legacy':{},'region':{}}; kept={}
                        for c in entries:
                            key=c['name']
                            gates['legacy'][key]=legacy_gate(masks[key],points,interiors[key])
                            gates['region'][key]=region_gate(observed,points,tables[key])
                        for method in gates:
                            options=[dict(c,assessment=gates[method][c['name']]) for c in entries
                                     if variant!='exclude_true_phase' or c['phase']!=0]
                            kept[method]=retained_hypotheses(options)
                        predictions.append(dict(count=count,variant=variant,anchors=points.tolist(),
                                                retained=kept,gates=gates))
                prediction=dict(trial=trial,box=box,palette=palette,source=str(image_path),
                    source_sha256=digest(image_path),nominal_anchors=anchors.tolist(),
                    entries=entries,correspondences=tables,variants=predictions)
                # All inference, including negative controls, serialized before evaluation.
                write_json(args.output/(trial+'-prediction.json'),prediction)
                np.savez_compressed(args.output/(trial+'-masks.npz'),observed=observed,**masks)
                Image.fromarray(rgb).save(args.output/(trial+'-input.png'))
                truth_path=args.baseline/(f'repeat-40-h{hand:+d}-phase-0-ids.png')
                truth=decode(np.asarray(Image.open(truth_path).convert('RGB').crop(box)),800)
                if patch=='old':truth=warp(truth,WARPS[condition])
                colors=[PALETTES[palette][i] for i in pattern] if palette in ('rgb','ryb') else [palette]*800
                evaluations={c['name']:evaluate(masks[c['name']],truth,
                    dict(objects=c['objects']),anchors,colors) for c in entries}
                baseline=evaluate(observed,truth,baseline_assessment(observed,rgb,palette),anchors,colors)
                nominal_truth_labels=[int(truth[round(y),round(x)]) for x,y in anchors]
                scores=[]
                for p in predictions:
                    selected={method:{n:dict(summarize(evaluations[n],p['gates'][method][n]),
                              **anchor_diagnostics(evaluations[n],baseline,p['gates'][method][n],
                                                   nominal_truth_labels[:p['count']]))
                              for n in p['retained'][method]} for method in p['retained']}
                    scores.append(dict(count=p['count'],variant=p['variant'],selected=selected,
                        clicked_truth_indices=[int(truth[round(y),round(x)])-1
                           if 0<=round(y)<truth.shape[0] and 0<=round(x)<truth.shape[1] else None
                           for x,y in p['anchors']]))
                write_json(args.output/(trial+'-evaluation.json'),dict(truth_sha256=digest(truth_path),
                    nominal_anchor_truth_indices=[t-1 for t in nominal_truth_labels],
                    candidate_evaluations=evaluations,baseline=baseline,variants=scores))
                nominal=next(p for p in predictions if p['count']==4 and p['variant']=='nominal')
                nominal_score=next(p for p in scores if p['count']==4 and p['variant']=='nominal')
                draw_panel(args.output/(trial+'-panel.png'),full,box,rgb,observed,anchors,entries,
                           masks,nominal,nominal_score['selected'],trial)
                trials.append(dict(name=trial,patch=patch,palette=palette,hand=hand,condition=condition,
                    baseline=baseline['supported'],variants=scores,
                    fits={c['name']:c['fit'] for c in entries}))
    if source_hashes()!=before:raise ValueError('Sources changed during run')
    write_json(args.output/'report.json',dict(sources=before,parameters=REGION_PARAMETERS,
        fit_parameters=PARAMETERS,boxes=dict(old=BOX,new=NEW_BOX),clicks=dict(old=CLICKS,new=NEW_CLICKS),
        jitter_seed=5201,command=[sys.executable,*sys.argv],python=platform.python_version(),
        scope='Supplied geometry; assistant visual seeds; second spatial patch of same scenes',
        baseline_source_revisions=revisions,
        input_reports={str(getattr(args,n)/'report.json'):digest(getattr(args,n)/'report.json')
                       for n in ('baseline','fixtures','detection','templates','previous')},
        trials=trials,artifacts={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.is_file()}))
    print('Saved '+str(args.output/'report.json'),flush=True)


if __name__=='__main__':main()
