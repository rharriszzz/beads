#!/usr/bin/env python3
"""Image-space neighbor inference on anonymous oracle masks; no photo claims."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, __version__ as pillow_version

from infer_neighbors import infer, PARAMETERS
from inference_controls import brick_ring
from legacy_visibility import decode, font
from neighbor_graph import propagate, reciprocal
from practice_legacy import ROOT, digest

HERE = ROOT / 'photo2'
HISTORICAL = '08ba3bb'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def verify_inputs(directory):
    report = json.loads((directory/'report.json').read_text())
    revisions = {}
    for name, expected in report['sources'].items():
        if (ROOT/name).is_file() and digest(ROOT/name) == expected:
            revisions[name] = 'current'
        else:
            data = subprocess.check_output(['git', 'show', f'{HISTORICAL}:{name}'], cwd=ROOT)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f'Historical source mismatch: {name}')
            revisions[name] = HISTORICAL
    for name, expected in report['artifacts'].items():
        if digest(directory/name) != expected:
            raise ValueError(f'Input artifact mismatch: {name}')
    return report, revisions


def mask_features(ids, count):
    """Evaluator splits masks, then discards encoded indices before inference."""
    ys, xs = np.nonzero(ids)
    labels = ids[ys, xs] - 1
    size = np.bincount(labels, minlength=count)
    sums = [np.bincount(labels, weights=w, minlength=count)
            for w in (xs, ys, xs.astype(float)**2, xs*ys, ys.astype(float)**2)]
    denom = np.maximum(size, 1)
    cx, cy, xx, xy, yy = [s/denom for s in sums]
    covariance = np.empty((count, 2, 2))
    covariance[:, 0, 0] = np.maximum(0., xx-cx*cx)
    covariance[:, 1, 1] = np.maximum(0., yy-cy*cy)
    covariance[:, 0, 1] = covariance[:, 1, 0] = xy-cx*cy
    return size, np.column_stack((cx, cy)), covariance


def anonymize(selected, xy, cov, seed):
    selected = np.asarray(selected, int)
    order = np.random.Generator(np.random.PCG64(seed)).permutation(len(selected))
    truth = selected[order]
    return xy[truth], cov[truth], truth


def evaluate(truth, count, variant):
    """Truth enters only here; retain both global sign scores, never fix outputs."""
    vertices = list(range(len(truth)))
    truth = np.asarray(truth)
    edges = variant['edges']
    observed = set(map(int, truth))
    available = sum((i+d) % count in observed for i in observed for d in (1, 6, 7))
    correct_pair = 0
    signed = {1: 0, -1: 0}
    confusion = Counter()
    edge_truth = []
    for u, v, d in edges:
        actual = int((truth[v]-truth[u]+count//2) % count-count//2)
        correct_pair += abs(actual) in (1, 6, 7)
        for sign in signed:
            signed[sign] += actual == sign*d
        confusion[f'{abs(d)}->{abs(actual) if abs(actual) in (1,6,7) else "other"}'] += 1
        edge_truth.append([u, v, d, actual])
    result = propagate(vertices, reciprocal(edges), modulus=count)
    component_details = []
    for component in result['components']:
        members = component['vertices']
        members_set = set(members)
        seed = component['seed']
        errors = {}
        for sign in (1, -1):
            errors[str(sign)] = sum((sign*result['labels'][v]-(int(truth[v])-int(truth[seed]))) % count != 0
                                    for v in members if v != seed)
        conflicts = sum(u in members_set for u, _, _, _ in result['conflicts'])
        duplicates = sum(group[0] in members_set for group in result['duplicate_indices'])
        component_details.append(dict(seed=seed, size=len(members), nonseed=len(members)-1,
                                      errors_by_global_reversal=errors,
                                      consistent=not(conflicts or duplicates),
                                      conflicts=conflicts, duplicate_groups=duplicates))
    nontrivial = [c for c in component_details if c['size'] > 1]
    certified = [c for c in nontrivial if c['consistent']]
    return dict(summary=dict(vertices=len(truth), available_true_edges=available,
                proposed_edges=len(edges), true_neighbor_pairs=int(correct_pair),
                pair_precision=correct_pair/len(edges) if edges else None,
                pair_recall=correct_pair/available if available else None,
                signed_correct_by_global_reversal=signed,
                component_count=len(component_details), isolated=sum(c['size']==1 for c in component_details),
                consistent_nontrivial_components=len(certified),
                consistent_nonseed=sum(c['nonseed'] for c in certified),
                consistent_wrong_nonseed_up_to_reversal=sum(min(c['errors_by_global_reversal'].values()) for c in certified),
                inconsistent_nontrivial_components=len(nontrivial)-len(certified),
                ambiguous_sectors=len(variant['ambiguous']),
                boundary_ambiguous_pairs=len(variant['boundary_ambiguous']),
                nonreciprocal_proposals=len(variant['nonreciprocal']),
                confusion=dict(sorted(confusion.items()))),
                edge_truth=edge_truth, components=component_details, propagation=result,
                index_status='diagnostic_only_unvalidated_edges')


def controls(out):
    """Clean/missing lattice and crossing clouds; no physical occlusion claim."""
    xy, cov, truth, count = brick_ring()
    keep = np.ones(len(xy), bool)
    keep[[47, 52, 57]] = False
    fixtures = {'clean_brick_ring': (xy, cov, truth),
                'missing_interior': (xy[keep], cov[keep], truth[keep])}
    report = {}
    for name, (points, moments, indices) in fixtures.items():
        modes = {}
        for mode in ('centers', 'shape'):
            result = infer(points, moments if mode == 'shape' else None)
            evaluations = [evaluate(indices, count, v) for v in result['variants']]
            if name == 'clean_brick_ring':
                s = evaluations[0]['summary']
                assert s['true_neighbor_pairs'] == s['proposed_edges'] > len(points)
                assert s['signed_correct_by_global_reversal'][1] == s['proposed_edges']
                assert s['consistent_wrong_nonseed_up_to_reversal'] == 0
                assert s['inconsistent_nontrivial_components'] == 0
            modes[mode] = dict(inference=result, evaluation=evaluations)
        write_json(out/f'control-{name}.json', dict(centroids=points.tolist(), covariance=moments.tolist(),
                   evaluation_only_indices=indices.tolist(), count=count, modes=modes))
        report[name] = {mode: [e['summary'] for e in data['evaluation']] for mode, data in modes.items()}
    shift = np.array([1.1*np.max(xy[:, 0]), 13.])
    points = np.vstack([xy, xy+shift])
    moments = np.concatenate([cov, cov])
    sheets = np.repeat([0, 1], len(xy))
    crossing = {}
    for mode in ('centers', 'shape'):
        result = infer(points, moments if mode == 'shape' else None)
        wrong = [[[u, v, d] for u, v, d in variant['edges'] if sheets[u] != sheets[v]]
                 for variant in result['variants']]
        crossing[mode] = dict(inference=result, cross_sheet_edges=wrong)
    write_json(out/'control-crossing.json', dict(centroids=points.tolist(), covariance=moments.tolist(),
               evaluation_only_sheets=sheets.tolist(), shift=shift.tolist(), modes=crossing,
               limitation='2-D superposition, no occlusion simulation; outside single-ring frame assumption'))
    report['crossing'] = {mode: dict(proposed=[len(v['edges']) for v in data['inference']['variants']],
                                   wrong_cross_sheet=[len(e) for e in data['cross_sheet_edges']])
                          for mode, data in crossing.items()}
    im = Image.new('RGB', (1500, 900), 'white')
    draw = ImageDraw.Draw(im)
    draw.text((20, 12), 'Crossing stress: two superposed 2-D brick rings (no rendered occlusion)', font=font(25), fill='black')
    draw.text((20, 50), 'Gray: same sheet, not necessarily correct. Red: false link across sheets. Shape convention +1.', font=font(21), fill='black')
    low = points.min(axis=0)
    extent = np.ptp(points, axis=0)
    scale = min(1440/extent[0], 720/extent[1])
    display = (points-low)*scale+[30, 110]
    for u, v, d in crossing['shape']['inference']['variants'][0]['edges']:
        draw.line((*display[u], *display[v]), fill='#d51919' if sheets[u] != sheets[v] else '#cccccc', width=2)
    for p, sheet in zip(display, sheets):
        draw.ellipse((p[0]-3, p[1]-3, p[0]+3, p[1]+3), fill=('#2855b2', '#bd7500')[sheet])
    draw.text((20, 850), f'Cross-sheet false links: {report["crossing"]["shape"]["wrong_cross_sheet"][0]}; no depth/sheet information supplied.', font=font(24), fill='black')
    im.save(out/'crossing-stress.png')
    return report


def summary_outputs(out, trials):
    """No duplicated shuffle trials in displayed aggregates. Keep both conventions."""
    rows = []
    for trial in trials:
        if trial['seed'] != 17:
            continue
        a, b = trial['summaries']
        assert a['proposed_edges'] == b['proposed_edges']
        assert a['true_neighbor_pairs'] == b['true_neighbor_pairs']
        best = max(max(s['signed_correct_by_global_reversal'].values()) for s in (a, b))
        rows.append(dict(view=trial['view'], threshold=trial['threshold'], mode=trial['mode'],
                         proposed=a['proposed_edges'], true_pairs=a['true_neighbor_pairs'],
                         available=a['available_true_edges'], precision=a['pair_precision'], recall=a['pair_recall'],
                         best_signed_correct=best, best_signed_precision=best/a['proposed_edges'] if a['proposed_edges'] else None,
                         shape_steered=trial['shape_steered']))
    with (out/'summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    im = Image.new('RGB', (1560, 880), 'white')
    draw = ImageDraw.Draw(im)
    draw.text((20, 12), 'T12: outline orientation improves pair precision but does not validate indexing', font=font(26), fill='black')
    draw.text((20, 53), 'One shuffle per view. Blue: centers; orange: shape. Same oracle detections in each comparison.', font=font(22), fill='black')
    draw.text((490, 100), 'Pair precision', font=font(22), fill='black')
    draw.text((1010, 100), 'Pair recall', font=font(22), fill='black')
    names = list(dict.fromkeys(r['view'] for r in rows))
    for k, name in enumerate(names):
        y = 155+75*k
        draw.text((20, y+8), name, font=font(21), fill='black')
        for m, mode in enumerate(('centers', 'shape')):
            row = next(r for r in rows if r['view'] == name and r['threshold'] == 12 and r['mode'] == mode)
            for start, key in ((490, 'precision'), (1010, 'recall')):
                value = row[key]
                draw.rectangle((start, y+24*m, start+380*value, y+24*m+18), fill=('#286bb0', '#d68515')[m])
                draw.text((start+385, y+24*m-2), f'{100*value:.1f}%', font=font(18), fill='black')
    draw.text((20, 800), 'Pair correctness ignores ±1/±6/±7 labels. Labels, graph contradictions and disconnected offsets are reported separately.', font=font(20), fill='black')
    draw.text((20, 839), 'No parameter search or truth-based edge repair. This is a baseline diagnostic, not a photo recovery result.', font=font(21), fill='black')
    im.save(out/'precision-recall.png')
    return rows


def panel(out, name, xy, result, evaluation, beauty, box, title):
    """Diagnostic plot only: green true pair, orange wrong label, red nonneighbor."""
    w, h = 1560, 960
    image = Image.new('RGB', (w, h), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((18, 12), title, font=font(24), fill='black')
    draw.text((18, 47), 'Oracle masks; both sign conventions retained. Arrows use convention +1.', font=font(20), fill='black')
    draw.text((18, 78), 'Green: correct signed edge up to ONE view reversal; orange: wrong label; red: wrong neighbor.', font=font(19), fill='black')
    left, top, right, bottom = box
    side = max(right-left, bottom-top)
    box = (left, top, left+side, top+side)
    crop = beauty.crop(box).resize((710, 710), Image.Resampling.NEAREST)
    image.paste(crop, (20, 125)); image.paste(crop, (820, 125))
    scale = 710/side
    selected = ((xy[:,0]>=left)&(xy[:,0]<left+side)&(xy[:,1]>=top)&(xy[:,1]<top+side))
    def point(i):
        return (xy[i]-[left, top])*scale+[820,125]
    score = evaluation['summary']['signed_correct_by_global_reversal']
    sign = max((1,-1), key=lambda s: score[s])
    for u,v,d,actual in evaluation['edge_truth']:
        if not(selected[u] and selected[v]):
            continue
        a,b=point(u),point(v)
        color = '#188040' if actual == sign*d else '#dc8c00' if abs(actual) in (1,6,7) else '#e22222'
        draw.line((*a,*b), fill=color, width=3)
        unit=(b-a)/max(1.,np.linalg.norm(b-a)); norm=np.array([-unit[1],unit[0]])
        draw.polygon([tuple(b),tuple(b-8*unit+3*norm),tuple(b-8*unit-3*norm)],fill=color)
        p=(a+b)/2
        draw.text(tuple(p),f'{d:+d}',font=font(12),fill='black',stroke_width=1,stroke_fill='white')
    for i in np.flatnonzero(selected):
        p=point(i); t=np.asarray(result['tangent'][i])*9
        draw.line((*tuple(p-t),*tuple(p+t)),fill='#235cd0',width=2)
        draw.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2),fill='black')
    s=evaluation['summary']
    draw.text((20,855),f'Whole-view pairs: {s["true_neighbor_pairs"]}/{s["proposed_edges"]}; available truth edges: {s["available_true_edges"]}.',font=font(23),fill='black')
    draw.text((20,890),'Blue strokes: inferred tangent; black dots: mask centroids. Missing edges remain missing.',font=font(22),fill='black')
    draw.text((20,927),f'Evaluator reversal {sign:+d} colors this panel only; it never changes inference. Crop {box}.',font=font(17),fill='black')
    image.save(out/name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=HERE/'output/neighbor-audit-final')
    parser.add_argument('--output',type=Path,default=HERE/'output/inference-audit')
    args=parser.parse_args()
    out=args.output.resolve(); source=args.input.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output must be new or empty')
    out.mkdir(parents=True,exist_ok=True)
    sources=[Path(__file__),HERE/'infer_neighbors.py',HERE/'neighbor_graph.py',
             HERE/'legacy_visibility.py',HERE/'practice_legacy.py',HERE/'test_infer_neighbors.py',
             HERE/'inference_controls.py']
    hashes={str(p.relative_to(ROOT)):digest(p) for p in sources}
    old,revisions=verify_inputs(source)
    report=dict(environment=dict(python=platform.python_version(),numpy=np.__version__,pillow=pillow_version),
                command=[sys.executable,*sys.argv], input_directory=str(source),
                input_report_sha256=digest(source/'report.json'), verified_input_sources=revisions,
                verified_input_artifacts=len(old['artifacts']), sources=hashes, parameters=PARAMETERS,
                claim='Experimental neighbor proposals from oracle mask features; no photo recovery.', trials=[])
    for name,view in old['views'].items():
        count=view['count']
        ids=decode(np.asarray(Image.open(source/f'{name}-ids.png').convert('RGB')),count)
        size,xy,cov=mask_features(ids,count)
        np.testing.assert_array_equal(size,view['pixels_per_bead'])
        np.testing.assert_allclose(xy[size>0],np.array([p for p in view['visible_centroids'] if p is not None]))
        for threshold in (1,12,100):
            selected=np.flatnonzero(size>=threshold)
            for seed in (17,43):
                points,moments,truth=anonymize(selected,xy,cov,seed)
                stem=f'{name}-t{threshold}-s{seed}'
                write_json(out/f'{stem}-input.json',dict(centroids=points.tolist(),mask_covariance=moments.tolist()))
                write_json(out/f'{stem}-truth.json',dict(source_indices=truth.tolist(),count=count,
                           missing_source_indices=np.flatnonzero(size<threshold).tolist()))
                for mode in ('centers','shape'):
                    result=infer(points,moments if mode=='shape' else None)
                    evaluations=[evaluate(truth,count,v) for v in result['variants']]
                    for evaluation in evaluations:
                        bend=np.abs(points[:,0]-points[:,0].mean())>.8*np.ptp(points[:,0])/2
                        regions={}
                        for region,flags in [('bend',bend),('small_mask',size[truth]<100)]:
                            subset=[e for e in evaluation['edge_truth'] if flags[e[0]] or flags[e[1]]]
                            regions[region]=dict(proposed=len(subset),true_pairs=sum(abs(e[3]) in (1,6,7) for e in subset))
                        evaluation['summary']['regions']=regions
                    filename=f'{stem}-{mode}.json'
                    write_json(out/filename,dict(inference=result,evaluation=evaluations))
                    trial=dict(view=name,threshold=threshold,seed=seed,mode=mode,file=filename,
                               shape_steered=sum(result['shape_steered']),
                               summaries=[e['summary'] for e in evaluations])
                    report['trials'].append(trial)
                    if threshold==12 and seed==17 and mode=='shape':
                        beauty=Image.open(source/f'{name}-beauty.png').convert('RGB')
                        for oldpanel in view['panels']:
                            box=oldpanel['crop_box']
                            filename=f'{name}-{oldpanel["reason"].split()[0].lower()}-inferred.png'
                            panel(out,filename,points,result,evaluations[0],beauty,box,
                                  f'{name} / {oldpanel["reason"]} / shape T12')
        print(name,'done',flush=True)
    # Relabeling invariance checked on geometry-edge identities, not just counts.
    for name in old['views']:
        for threshold in (1,12,100):
            for mode in ('centers','shape'):
                canonical=[]
                for seed in (17,43):
                    stem=f'{name}-t{threshold}-s{seed}'
                    truth=json.loads((out/f'{stem}-truth.json').read_text())['source_indices']
                    result=json.loads((out/f'{stem}-{mode}.json').read_text())['inference']
                    canonical.append([sorted((min(truth[u],truth[v]),max(truth[u],truth[v]),
                                               d if truth[u]<truth[v] else -d) for u,v,d in v['edges'])
                                      for v in result['variants']])
                assert canonical[0]==canonical[1], (name,threshold,mode)
    report['relabeling_invariance']='all 48 paired trials agree on signed source-pair sets'
    report['controls']=controls(out)
    report['summary_rows']=summary_outputs(out,report['trials'])
    assert hashes=={str(p.relative_to(ROOT)):digest(p) for p in sources},'Sources changed during run'
    report['artifacts']={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()}
    write_json(out/'report.json',report)
    print('Report:',out/'report.json',flush=True)


if __name__=='__main__':
    main()
