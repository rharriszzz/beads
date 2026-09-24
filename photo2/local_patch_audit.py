#!/usr/bin/env python3
"""Frozen, geometry-calibrated local contour test; no full photo recovery claim."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import platform
import sys

import numpy as np
from PIL import Image, ImageDraw
from skimage.segmentation import find_boundaries

from local_patch import (PARAMETERS, assess, displace, fit, image_evidence,
                         retained_hypotheses, warp)
from inference_audit import verify_inputs, write_json
from legacy_visibility import decode, font, instrument_source, render, replace_once, wrapper
from practice_legacy import ROOT, digest

HERE = ROOT/'photo2'
BOX = (1900, 650, 2310, 1060)
CLICKS = {1: [(2160,830), (2190,850), (2225,815), (2225,885)],
          -1: [(2160,850), (2190,870), (2225,820), (2240,880)]}
WARPS = {'identity': [0.]*6, 'translation': [8.,-6.,0.,0.,0.,0.],
         'smooth': [0.,0.,0.,-4.,8.,0.]}
SOURCE_NAMES = ('photo2/local_patch.py', 'photo2/local_patch_audit.py',
                'photo2/test_local_patch.py',
                'photo2/detect_beads.py', 'photo2/legacy_visibility.py',
                'photo2/legacy-visibility-body.inc', 'photo2/practice_legacy.py',
                'photo2/inference_audit.py', 'photo2/practice-pattern.json',
                'beads.pov', 'bead-shape.inc')


def hashes():
    return {n: digest(ROOT/n) for n in SOURCE_NAMES}


def verify_manifest(path):
    report = json.loads(path.read_text())
    for name, sha in report['artifacts'].items():
        if digest(path.parent/name) != sha:
            raise ValueError(f'Stale artifact: {path.parent/name}')
    for name, sha in report['sources'].items():
        if digest(ROOT/name) != sha:
            raise ValueError(f'Stale source: {name}')
    return report


def templates(directory):
    manifest = directory/'report.json'
    if manifest.exists():
        return verify_manifest(manifest)
    if directory.exists() and any(directory.iterdir()):
        raise ValueError('Template directory must be empty or verified')
    directory.mkdir(parents=True, exist_ok=True)
    (directory/'generator.py').write_bytes(Path(__file__).read_bytes())
    source = instrument_source((ROOT/'beads.pov').read_text())
    source = replace_once(source,
        '360*(Helicity*bead_index/exact_beads_per_row + rclock*1.00)',
        '360*(Helicity*bead_index/exact_beads_per_row + rclock*1.00 + PatchPhase)')
    inc = directory/'model.inc'; inc.write_text(source)
    pattern = json.loads((HERE/'practice-pattern.json').read_text())
    commands, cases = [], []
    for hand in (1, -1):
        for phase in (0., .25, .5, .75):
            name = f'h{hand:+d}-phase{phase:g}'
            scene = directory/(name+'.pov')
            scene.write_text(f'#declare Helicity={hand};\n#declare PatchPhase={phase};\n'+wrapper(pattern, str(inc)))
            print('Render candidate '+name, flush=True)
            rgb = render(directory, name, scene, '0', commands)
            labels = decode(rgb, 800)[BOX[1]:BOX[3], BOX[0]:BOX[2]]
            Image.fromarray(labels.astype(np.uint16)).save(directory/(name+'-patch.png'))
            cases.append(dict(name=name, hand=hand, phase=phase, image=name+'-patch.png'))
    sources = {n: digest(ROOT/n) for n in ('beads.pov', 'bead-shape.inc',
                'photo2/legacy_visibility.py', 'photo2/legacy-visibility-body.inc',
                'photo2/practice_legacy.py', 'photo2/practice-pattern.json')}
    report = dict(sources=sources, generator_sha256=digest(Path(__file__)),
                  box=BOX, candidates=cases, commands=commands,
                  artifacts={p.name: digest(p) for p in sorted(directory.iterdir()) if p.is_file()})
    write_json(manifest, report)
    return report


def crop(path):
    return np.asarray(Image.open(path).convert('RGB').crop(BOX))


def evaluate(labels, truth, assessment, anchors, colors):
    """Evaluate after predictions. No feedback or truth-based hypothesis choice."""
    def interior(mask):
        yy, xx = np.nonzero(mask)
        b = PARAMETERS['border']
        return (len(xx) >= 100 and xx.min() >= b and yy.min() >= b and
                xx.max() < labels.shape[1]-b and yy.max() < labels.shape[0]-b)
    visible = [int(t) for t in np.unique(truth) if t and interior(truth == t)]
    seed_xy = np.rint(anchors[0]).astype(int)
    seed_truth = int(truth[seed_xy[1], seed_xy[0]])
    records = []
    for obj in assessment['objects']:
        label = obj['model_label']
        pred = labels == label
        values, counts = np.unique(truth[pred], return_counts=True)
        candidates = []
        for t, intersection in zip(values, counts):
            if t:
                union = int(pred.sum())+int(np.count_nonzero(truth == t))-int(intersection)
                candidates.append((float(intersection/union), int(t)))
        iou, t = max(candidates, default=(0., 0))
        matched = iou > .5
        delta = (t-seed_truth+400) % 800-400 if t and seed_truth else None
        relative = obj['relative_index']
        correct_index = bool(matched and relative is not None and delta == relative)
        records.append(dict(model_label=label, truth_label=t, iou=iou,
            eligible_truth=t in visible, matched=matched, supported=obj['supported'],
            index_claimed=relative is not None, correct_relative_index=correct_index,
            actual_relative_index=delta,
            candidate_index_correct=bool(matched and delta == obj['candidate_relative_index']),
            correct_color=bool(matched and obj['color'] == colors[t-1]), color=obj['color']))
    def summarize(which):
        selected = [r for r in records if which(r)]
        matches = [r for r in selected if r['matched'] and r['eligible_truth']]
        ignored = [r for r in selected if r['matched'] and not r['eligible_truth']]
        return dict(predictions=len(selected), matched=len(matches),
            false_predictions=sum(not r['matched'] for r in selected), ignored=len(ignored),
            eligible_truth=len(visible), missing_truth=[t-1 for t in visible if t not in {r['truth_label'] for r in matches}],
            correct_color=sum(r['correct_color'] for r in matches),
            unknown_color=sum(r['color']=='unknown' for r in matches),
            correct_index=sum(r['correct_relative_index'] for r in matches),
            wrong_claimed_index=sum(r['index_claimed'] and not r['correct_relative_index'] for r in matches),
            candidate_index_correct=sum(r['candidate_index_correct'] for r in matches))
    return dict(seed_truth_index=seed_truth-1 if seed_truth else None,
                anchor_truth_indices=[int(truth[round(y),round(x)])-1 for x,y in anchors],
                all_model=summarize(lambda r: True),
                supported=summarize(lambda r: r['supported']),
                claimed=summarize(lambda r: r['index_claimed']), records=records)


def baseline_assessment(labels, rgb, palette):
    # Same color rule/support bookkeeping, but segmentation alone supplies no indices.
    _, distance = image_evidence(rgb)
    result = assess(labels, distance, [(0.,0.)]*4, palette, rgb)
    for o in result['objects']:
        o['supported'] = not o['touches_crop']
        o['relative_index'] = None
        o['candidate_relative_index'] = None
    return result


def panel(out, name, full, rgb, truth, anchors, candidate_labels, chosen, edge, indexed_objects):
    im = Image.new('RGB', (1640, 970), 'white')
    d = ImageDraw.Draw(im)
    d.text((15,10), name+'; calibrated geometry, conditional indices', font=font(24), fill='black')
    context = full.copy(); ImageDraw.Draw(context).rectangle(BOX, outline='#ff00ff', width=5)
    context.thumbnail((395,350)); im.paste(context,(5,70))
    d.text((5,45), 'Whole input; fixed patch boxed', font=font(17), fill='black')
    tiles = [('Beauty; four supplied clicks', rgb.copy()), ('Observed image edges', np.repeat(edge[...,None]*255,3,axis=2).astype('uint8')),
             ('Evaluator-only truth contours', rgb.copy())]
    tiles[-1][1][find_boundaries(truth,mode='inner')] = (0,255,255)
    for title, labels in candidate_labels:
        overlay = rgb.copy(); overlay[find_boundaries(labels,mode='inner')] = (255,0,255)
        tiles.append((title,overlay))
    for j,(title, arr) in enumerate(tiles):
        x,y = ((j%3)*410+410, 70+(j//3)*440)
        im.paste(Image.fromarray(arr), (x,y))
        d.text((x,y-23),title,font=font(15),fill='black')
        if j == 0:
            for k,(ax,ay) in enumerate(anchors):
                d.ellipse((x+ax-5,y+ay-5,x+ax+5,y+ay+5),outline='white',width=2)
                d.text((x+ax+6,y+ay),str(k),fill='white',font=font(16))
        if j == 5:
            labels = candidate_labels[-1][1]
            for obj in indexed_objects:
                index = obj['relative_index']
                if index is None:
                    continue
                yy, xx = np.nonzero(labels == obj['model_label'])
                tx, ty = x+int(xx.mean()), y+int(yy.mean())
                text = f'{index:+d}'
                bounds = d.textbbox((tx,ty), text, font=font(12))
                d.rectangle(bounds, fill='black')
                d.text((tx,ty),text,fill='white',font=font(12))
    d.text((8,440),'Retained smooth hypotheses:',font=font(17),fill='black')
    for i,n in enumerate(chosen):
        d.text((8,470+i*25),n,font=font(17),fill='black')
    if not chosen:
        d.text((8,470),'None passes anchor gate',font=font(17),fill='black')
    d.text((8,920),'Magenta: model prediction, not automatically accepted. All candidates and unsupported bodies remain in JSON.',font=font(19),fill='black')
    im.save(out/(name+'-panel.png'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,default=HERE/'output/neighbor-audit-final')
    parser.add_argument('--fixtures',type=Path,default=HERE/'output/detection-fixtures-r045-final')
    parser.add_argument('--detection',type=Path,default=HERE/'output/detection-audit-r045-final')
    parser.add_argument('--templates',type=Path,default=HERE/'output/local-patch-templates-r047')
    parser.add_argument('--output',type=Path,default=HERE/'output/local-patch-r047')
    args=parser.parse_args()
    for key,value in vars(args).items(): setattr(args,key,value.resolve())
    if args.output.exists() and any(args.output.iterdir()): raise ValueError('Output must be new or empty')
    source_before=hashes()
    _, revisions=verify_inputs(args.baseline)
    verify_manifest(args.fixtures/'report.json')
    verify_manifest(args.detection/'report.json')
    bank=templates(args.templates)
    args.output.mkdir(parents=True,exist_ok=True)
    candidates=[dict(c,labels=np.asarray(Image.open(args.templates/c['image']),dtype=np.int32)) for c in bank['candidates']]
    pattern=json.loads((HERE/'practice-pattern.json').read_text())['colors']*20
    cases=[('ryb-phase-0','ryb',1),('gray-phase-0','gray',1),('black-phase-0','black',1),
           ('repeat-40-h-1-phase-0','rgb',-1)]
    trials=[]
    from detect_beads import PALETTES, detect
    for name,palette,hand in cases:
        source_path=(args.baseline/(name+'-beauty.png') if palette=='rgb' else args.fixtures/(name+'.png'))
        rgb0=crop(source_path)
        anchors0=np.asarray(CLICKS[hand],float)-BOX[:2]
        source_labels=np.asarray(Image.open(args.detection/(name+'-gray_boundary-labels.png')).crop(BOX),dtype=np.int32)
        colors=[PALETTES[palette][i] for i in pattern] if palette in ('rgb','ryb') else [palette]*800
        for condition, coefficients in WARPS.items():
            rgb=warp(rgb0,coefficients,order=1,background=255)
            anchors=displace(anchors0,coefficients,rgb.shape[0])
            for evidence in ('sv','gray') if condition=='identity' and palette in ('ryb','black') else ('sv',):
                trial_name=f'{name}-{condition}-{evidence}'
                print('Fit '+trial_name,flush=True)
                edge,distance=image_evidence(rgb,evidence)
                results, masks, kept={}, {}, {}
                for method in ('fixed','translation','smooth'):
                    options=[]
                    for candidate in candidates:
                        alignment=fit(candidate['labels'],distance,method)
                        labels=warp(candidate['labels'],alignment['coefficients'])
                        observation=assess(labels,distance,anchors,palette,rgb)
                        entry=dict(name=candidate['name'],hand=candidate['hand'],phase=candidate['phase'],
                                   fit=alignment,assessment=observation)
                        options.append(entry)
                        masks[(method,candidate['name'])]=labels
                    kept[method]=retained_hypotheses(options)
                    results[method]=options
                # Re-segment the actual perturbed beauty image. Warping earlier
                # detector output would give this baseline the oracle correction.
                if condition == 'identity':
                    baseline_mask = source_labels
                else:
                    full_rgb = np.array(Image.open(source_path).convert('RGB'))
                    full_rgb[BOX[1]:BOX[3], BOX[0]:BOX[2]] = rgb
                    full_labels, _ = detect(full_rgb, 'gray_boundary', palette)
                    baseline_mask = full_labels[BOX[1]:BOX[3], BOX[0]:BOX[2]]
                # Freeze inference output BEFORE observed truth is read.
                prediction=dict(name=trial_name,anchors=anchors.tolist(),image=str(source_path),
                    image_sha256=digest(source_path),condition=condition,evidence=evidence,
                    retained=kept,methods=results)
                write_json(args.output/(trial_name+'-prediction.json'),prediction)
                np.savez_compressed(args.output/(trial_name+'-predicted-masks.npz'),
                    no_model=baseline_mask,
                    **{method+'_'+candidate: labels for (method,candidate),labels in masks.items()})
                truth_path=args.baseline/(f'repeat-40-h{hand:+d}-phase-0-ids.png')
                truth0=decode(crop(truth_path),800)
                truth=warp(truth0,coefficients)
                evaluations={}
                for method,options in results.items():
                    evaluations[method]={c['name']:evaluate(masks[(method,c['name'])],truth,c['assessment'],anchors,colors) for c in options}
                oracle=next(c for c in candidates if c['hand']==hand and c['phase']==0)
                oracle_mask=warp(oracle['labels'],coefficients)
                if not np.array_equal(oracle_mask,truth): raise ValueError('Independent zero-phase candidate differs from oracle geometry')
                oracle_assess=assess(oracle_mask,distance,anchors,palette,rgb)
                baseline=evaluate(baseline_mask,truth,baseline_assessment(baseline_mask,rgb,palette),anchors,colors)
                controls={}
                if palette=='ryb' and evidence=='sv':
                    for control, clicks in [('false_background',np.vstack([[70.,200.],anchors[1:]])),
                                           ('one_click_slip',np.vstack([anchors[1],anchors[1:]]))]:
                        alternatives=[]
                        for c in results['smooth']:
                            assessment=assess(masks[('smooth',c['name'])],distance,clicks,palette,rgb)
                            alternatives.append(dict(c,assessment=assessment))
                        controls[control]=dict(anchors=clicks.tolist(),retained=retained_hypotheses(alternatives),candidates=alternatives)
                    wrong_phase=[c for c in results['smooth'] if c['phase']!=0]
                    controls['exclude_true_phase']=dict(retained=retained_hypotheses(wrong_phase))
                record=dict(prediction=trial_name+'-prediction.json',truth_sha256=digest(truth_path),
                    evaluations=evaluations,oracle=evaluate(oracle_mask,truth,oracle_assess,anchors,colors),
                    no_model=baseline,controls=controls)
                write_json(args.output/(trial_name+'-evaluation.json'),record)
                # Display the lowest TRAIN score even if rejected, explicitly labeled.
                best={m:min(results[m],key=lambda c:c['fit']['train_mean']) for m in results}
                tiles=[(m+': '+best[m]['name'],masks[(m,best[m]['name'])]) for m in ('fixed','translation','smooth')]
                indexed = (best['smooth']['assessment']['objects']
                           if best['smooth']['name'] in kept['smooth'] else [])
                panel(args.output,trial_name,Image.open(source_path).convert('RGB'),rgb,truth,anchors,tiles,kept['smooth'],edge,indexed)
                Image.fromarray(rgb).save(args.output/(trial_name+'-input.png'))
                selected={m:{n:evaluations[m][n]['claimed'] for n in kept[m]} for m in results}
                trials.append(dict(name=trial_name,palette=palette,hand=hand,condition=condition,evidence=evidence,
                    retained=kept,selected=selected,baseline=baseline['supported'],oracle=record['oracle'],
                    best_train={m:dict(name=c['name'],fit=c['fit'],anchor_ok=c['assessment']['anchor_ok'],
                       supported=evaluations[m][c['name']]['supported'],all_model=evaluations[m][c['name']]['all_model']) for m,c in best.items()},
                    controls={k:v['retained'] for k,v in controls.items()}))
    if hashes()!=source_before: raise ValueError('Sources changed during run')
    report=dict(sources=source_before,parameters=PARAMETERS,box=BOX,clicks=CLICKS,warps=WARPS,
        scope='Known legacy camera/rope/scale; recorded visual clicks; no image-derived geometry or automatic seed',
        command=[sys.executable,*sys.argv],python=platform.python_version(),baseline_source_revisions=revisions,
        input_reports={str(p):digest(p) for p in (args.baseline/'report.json',args.fixtures/'report.json',args.detection/'report.json',args.templates/'report.json')},
        trials=trials,artifacts={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    write_json(args.output/'report.json',report)
    print('Saved '+str(args.output/'report.json'),flush=True)

if __name__=='__main__':main()
