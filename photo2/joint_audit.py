#!/usr/bin/env python3
"""Compare fixed R039 and joint lattice rules on exactly the same saved inputs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import platform
import sys

import numpy as np
from PIL import Image, ImageDraw, __version__ as pillow_version

from infer_neighbors import infer
from inference_audit import evaluate, panel, verify_inputs, write_json
from inference_controls import brick_ring
from joint_neighbors import infer_joint, PARAMETERS
from legacy_visibility import font
from neighbor_graph import propagate, reciprocal
from practice_legacy import ROOT, digest

HERE = ROOT/'photo2'


def verify_baseline(directory):
    report = json.loads((directory/'report.json').read_text())
    for filename, expected in report['sources'].items():
        if digest(ROOT/filename) != expected:
            raise ValueError(f'Baseline source changed: {filename}')
    for filename, expected in report['artifacts'].items():
        if digest(directory/filename) != expected:
            raise ValueError(f'Baseline artifact changed: {filename}')
    return report


def canonical(edges, truth):
    return sorted((min(truth[u], truth[v]), max(truth[u], truth[v]),
                   d if truth[u] < truth[v] else -d) for u, v, d in edges)


def score(truth, count, result):
    evaluations = []
    for variant in result['variants']:
        value = evaluate(truth, count, variant)
        value['local_integer_propagation'] = propagate(range(len(truth)), reciprocal(variant['edges']))
        trace_scores = []
        for trace in variant.get('traces', []):
            actual = [int((truth[v]-truth[u]+count//2) % count-count//2)
                      for u, v in zip(trace['vertices'], trace['vertices'][1:])]
            trace_scores.append(dict(family=trace['family'], length=len(actual),
                                     all_true_neighbor_pairs=all(abs(d) in (1, 6, 7) for d in actual),
                                     signed_correct_by_reversal={s: sum(d == s*trace['family'] for d in actual)
                                                                for s in (1, -1)},
                                     actual_differences=actual))
        value['traces'] = trace_scores
        evaluations.append(value)
    return evaluations


def row(view, threshold, mode, algorithm, summaries):
    a, b = summaries
    assert a['proposed_edges'] == b['proposed_edges']
    assert a['true_neighbor_pairs'] == b['true_neighbor_pairs']
    best = max(max(s['signed_correct_by_global_reversal'].values()) for s in summaries)
    best_summary = max(summaries, key=lambda s: max(s['signed_correct_by_global_reversal'].values()))
    return dict(view=view, threshold=threshold, mode=mode, algorithm=algorithm,
                proposed=a['proposed_edges'], true_pairs=a['true_neighbor_pairs'],
                available=a['available_true_edges'], best_signed=best,
                precision=a['pair_precision'], recall=a['pair_recall'],
                best_signed_precision=best/a['proposed_edges'] if a['proposed_edges'] else None,
                evaluator_best_convention_wrong_consistent_nonseed=best_summary['consistent_wrong_nonseed_up_to_reversal'],
                # Convention +1 only here; all conventions retained in trial files.
                consistent_components=a['consistent_nontrivial_components'],
                consistent_nonseed=a['consistent_nonseed'],
                wrong_consistent_nonseed=a['consistent_wrong_nonseed_up_to_reversal'],
                inconsistent_components=a['inconsistent_nontrivial_components'], isolated=a['isolated'])


def stage_diagnostics(result, truth, count):
    """Truth-based loss attribution after inference; never used for selection."""
    triangle = {e for tri in result['triangles'] for e in tri}
    trace = {e for a, b, _ in result['continuations'] for e in (a, b)}
    stages = {'reciprocal_candidates': range(len(result['candidates'])),
              'motif_supported': sorted(triangle & trace),
              'reciprocal_selected': result['selected_before_pruning'],
              'final': result['selected_candidate_ids']}
    values = {}
    for name, ids in stages.items():
        pairs = {(u, v) for e in ids for u, v, _ in [result['candidates'][e]]}
        true_pairs = sum(abs((truth[v]-truth[u]+count//2) % count-count//2) in (1, 6, 7)
                         for u, v in pairs)
        values[name] = dict(unique_pairs=len(pairs), true_pairs=true_pairs)
    return values


def whole_context(out, beauty, xy, result, evaluation):
    """Whole-ring plot of accepted edges, with the prior example located."""
    image = Image.new('RGB', (1300, 1120), 'white')
    image.paste(beauty.resize((1200, 900), Image.Resampling.LANCZOS), (50, 100))
    draw = ImageDraw.Draw(image)
    draw.text((25, 15), 'Whole synthetic ring: retained joint edges, shape T12', font=font(27), fill='black')
    draw.text((25, 58), 'Green: correct signed edge. Orange: wrong label. Red: wrong pair. Convention +1.', font=font(21), fill='black')
    for u, v, d, actual in evaluation['edge_truth']:
        color = '#188040' if d == actual else '#dc8c00' if abs(actual) in (1, 6, 7) else '#e22222'
        a, b = xy[u]*.5+[50, 100], xy[v]*.5+[50, 100]
        draw.line((*a, *b), fill=color, width=2)
    draw.rectangle((550, 745, 690, 885), outline='#00aaaa', width=4)
    draw.text((25, 1020), 'Box: R041 example. Its false 611-613 edge is rejected, but the correct path is also untraced.', font=font(23), fill='black')
    draw.text((25, 1065), 'Sparse retained patches do not establish correct component indices or photo recovery.', font=font(23), fill='black')
    image.save(out/'whole-ring-joint.png')


def controls(out):
    xy, cov, truth, count = brick_ring()
    keep = np.ones(len(xy), bool)
    keep[[47, 52, 57]] = False
    fixtures = {'ideal': (xy, cov, truth), 'missing': (xy[keep], cov[keep], truth[keep])}
    report = {}
    for name, (points, moments, indices) in fixtures.items():
        results = {}
        for mode in ('centers', 'shape'):
            for algorithm, function in (('baseline', infer), ('joint', infer_joint)):
                result = function(points, moments if mode == 'shape' else None)
                evaluation = score(indices, count, result)
                results[f'{mode}-{algorithm}'] = dict(inference=result, evaluation=evaluation)
                if name == 'ideal':
                    s = evaluation[0]['summary']
                    assert s['true_neighbor_pairs'] == s['proposed_edges'] == 520
                    assert s['signed_correct_by_global_reversal'][1] == 520
                    assert s['consistent_wrong_nonseed_up_to_reversal'] == 0
        write_json(out/f'control-{name}.json', dict(centroids=points.tolist(), covariance=moments.tolist(),
                   evaluation_only_indices=indices.tolist(), count=count, results=results))
        report[name] = {key: [e['summary'] for e in r['evaluation']] for key, r in results.items()}
    points = np.vstack([xy, xy+[1.1*np.max(xy[:, 0]), 13.]])
    moments = np.concatenate([cov, cov])
    sheets = np.repeat([0, 1], len(xy))
    indices = np.tile(truth, 2)
    crossing = {}
    for mode in ('centers', 'shape'):
        for algorithm, function in (('baseline', infer), ('joint', infer_joint)):
            result = function(points, moments if mode == 'shape' else None)
            wrong = [[[u, v, d] for u, v, d in variant['edges'] if sheets[u] != sheets[v]]
                     for variant in result['variants']]
            true_pairs = [int(sum(sheets[u] == sheets[v] and
                              abs((indices[v]-indices[u]+count//2) % count-count//2) in (1, 6, 7)
                              for u, v, _ in variant['edges'])) for variant in result['variants']]
            crossing[f'{mode}-{algorithm}'] = dict(inference=result, cross_sheet_edges=wrong,
                                                   true_pairs=true_pairs, available_true_pairs=1040)
    write_json(out/'control-crossing.json', dict(centroids=points.tolist(), covariance=moments.tolist(),
               evaluation_only_sheets=sheets.tolist(), evaluation_only_indices=indices.tolist(), results=crossing,
               limitation='Two superposed point clouds, no physical occlusion or depth evidence.'))
    report['crossing'] = {key: dict(proposed=[len(v['edges']) for v in r['inference']['variants']],
                                   cross_sheet=[len(e) for e in r['cross_sheet_edges']],
                                   true_pairs=r['true_pairs'], available_true_pairs=1040)
                          for key, r in crossing.items()}
    image = Image.new('RGB', (1600, 740), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((20, 12), 'Crossing stress: red edges join different sheets; gray does not guarantee correctness.', font=font(23), fill='black')
    scale = min(740/np.ptp(points[:, 0]), 550/np.ptp(points[:, 1]))
    for column, algorithm in enumerate(('baseline', 'joint')):
        data = crossing[f'shape-{algorithm}']
        display = (points-points.min(axis=0))*scale+[20+800*column, 120]
        draw.text((20+800*column, 60), f'{algorithm}: {len(data["cross_sheet_edges"][0])} cross-sheet false links', font=font(22), fill='black')
        for u, v, d in data['inference']['variants'][0]['edges']:
            draw.line((*display[u], *display[v]), fill='#df2020' if sheets[u] != sheets[v] else '#cccccc', width=2)
        for p, sheet in zip(display, sheets):
            draw.ellipse((p[0]-2, p[1]-2, p[0]+2, p[1]+2), fill=('#2855b2', '#bd7500')[sheet])
    draw.text((20, 698), 'Shape, convention +1. 2-D superposition without rendered occlusion; single-ring frame remains a limitation.', font=font(21), fill='black')
    image.save(out/'crossing-comparison.png')
    return report


def chart(out, rows):
    selected = [r for r in rows if r['threshold'] == 12 and r['mode'] == 'shape']
    views = list(dict.fromkeys(r['view'] for r in selected))
    image = Image.new('RGB', (1600, 920), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((20, 15), 'Joint triangle and three-family trace constraints - T12, shape, one shuffle per view', font=font(25), fill='black')
    draw.text((20, 60), 'Blue: fixed baseline. Orange: joint rule. Same anonymous oracle-mask features.', font=font(23), fill='black')
    for x, label in ((470, 'Pair precision'), (1040, 'Pair recall')):
        draw.text((x, 105), label, font=font(24), fill='black')
    for i, view in enumerate(views):
        y = 155+80*i
        draw.text((20, y+10), view, font=font(20), fill='black')
        for a, algorithm in enumerate(('baseline', 'joint')):
            r = next(r for r in selected if r['view'] == view and r['algorithm'] == algorithm)
            for x, key in ((470, 'precision'), (1040, 'recall')):
                value = r[key]
                draw.rectangle((x, y+a*27, x+380*(value or 0), y+a*27+18), fill=('#286bb0', '#d68515')[a])
                draw.text((x+390, y+a*27-3), 'none' if value is None else f'{100*value:.1f}%', font=font(19), fill='black')
    draw.text((20, 840), 'Signed labels, component errors, rejected alternatives and missing indices are retained separately.', font=font(22), fill='black')
    draw.text((20, 878), 'Local consistency is not proof of correct indexing. No photo recovery claim.', font=font(22), fill='black')
    image.save(out/'comparison.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=HERE/'output/inference-audit-verified')
    parser.add_argument('--render-input', type=Path, default=HERE/'output/neighbor-audit-final')
    parser.add_argument('--output', type=Path, default=HERE/'output/joint-audit')
    args = parser.parse_args()
    out, source, render = args.output.resolve(), args.input.resolve(), args.render_input.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output must be new or empty')
    baseline = verify_baseline(source)
    old, revisions = verify_inputs(render)
    if baseline['input_report_sha256'] != digest(render/'report.json'):
        raise ValueError('Baseline and render reports must be the matching input/output pair')
    out.mkdir(parents=True, exist_ok=True)
    sources = [Path(__file__), HERE/'joint_neighbors.py', HERE/'test_joint_neighbors.py',
               *[ROOT/p for p in baseline['sources']], HERE/'inference_audit.py']
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in sources}
    report = dict(command=[sys.executable, *sys.argv], parameters=PARAMETERS, sources=hashes,
                  environment=dict(python=platform.python_version(), numpy=np.__version__, pillow=pillow_version),
                  baseline_report_sha256=digest(source/'report.json'), render_report_sha256=digest(render/'report.json'),
                  baseline_directory=str(source), render_directory=str(render),
                  verified_baseline_sources=len(baseline['sources']), verified_baseline_artifacts=len(baseline['artifacts']),
                  verified_render_sources=revisions, verified_render_artifacts=len(old['artifacts']), trials=[])
    rows, invariance = [], {}
    for trial in baseline['trials']:
        name, threshold, seed, mode = (trial[k] for k in ('view', 'threshold', 'seed', 'mode'))
        stem = f'{name}-t{threshold}-s{seed}'
        features = json.loads((source/f'{stem}-input.json').read_text())
        truth = json.loads((source/f'{stem}-truth.json').read_text())
        xy = np.asarray(features['centroids'])
        moments = np.asarray(features['mask_covariance']) if mode == 'shape' else None
        result = infer_joint(xy, moments)
        evaluations = score(truth['source_indices'], truth['count'], result)
        stages = stage_diagnostics(result, truth['source_indices'], truth['count'])
        filename = f'{stem}-{mode}.json'
        write_json(out/filename, dict(inference=result, evaluation=evaluations, evaluation_only_stages=stages,
                   input_file=str(source/f'{stem}-input.json'), evaluation_truth_file=str(source/f'{stem}-truth.json')))
        summaries = [e['summary'] for e in evaluations]
        report['trials'].append(dict(view=name, threshold=threshold, seed=seed, mode=mode,
                                   file=filename, summaries=summaries,
                                   candidate_count=len(result['candidates']), triangle_count=len(result['triangles']),
                                   continuation_count=len(result['continuations']), evaluation_only_stages=stages))
        key = (name, threshold, mode)
        canonical_edges = [canonical(v['edges'], truth['source_indices']) for v in result['variants']]
        if key in invariance:
            assert invariance[key] == canonical_edges, key
        else:
            invariance[key] = canonical_edges
        if seed == 17:
            rows.append(row(name, threshold, mode, 'baseline', trial['summaries']))
            rows.append(row(name, threshold, mode, 'joint', summaries))
        if threshold == 12 and seed == 17 and mode == 'shape':
            beauty = Image.open(render/f'{name}-beauty.png').convert('RGB')
            for oldpanel in old['views'][name]['panels']:
                panel(out, f'{name}-{oldpanel["reason"].split()[0].lower()}-joint.png', xy, result,
                      evaluations[0], beauty, oldpanel['crop_box'], f'{name} / joint shape T12 / {oldpanel["reason"]}')
            if name == 'repeat-40-h+1-phase-0':
                selected = [e for e in evaluations[0]['edge_truth']
                            if set((truth['source_indices'][e[0]], truth['source_indices'][e[1]])) == {611, 613}]
                report['r041_case'] = dict(retained_edges=selected, source_pair=[611, 613],
                                          retained_true_path_edges=[e for e in evaluations[0]['edge_truth']
                                              if set((truth['source_indices'][e[0]], truth['source_indices'][e[1]]))
                                              in ({611, 612}, {612, 613})],
                                          note='Post-hoc diagnostic only; the rule has no source indices.')
                assert not report['r041_case']['retained_true_path_edges']
                whole_context(out, beauty, xy, result, evaluations[0])
                panel(out, 'r041-location-joint.png', xy, result, evaluations[0], beauty,
                      [1000, 1290, 1280, 1570], 'R041 failure location / joint shape T12 / convention +1')
        if threshold == 100 and seed == 43 and mode == 'shape':
            print(name, 'done', flush=True)
    report['relabeling_invariance'] = f'All {len(invariance)} paired shuffle comparisons agree on signed source-pair sets.'
    report['controls'] = controls(out)
    report['summary_rows'] = rows
    with (out/'summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    chart(out, rows)
    assert hashes == {str(p.relative_to(ROOT)): digest(p) for p in sources}
    report['artifacts'] = {p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file()}
    write_json(out/'report.json', report)
    print(out/'report.json', flush=True)


if __name__ == '__main__':
    main()
