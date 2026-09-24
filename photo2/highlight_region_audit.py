#!/usr/bin/env python3
"""Paired fixed highlight repair on R052 masks, fits, anchors and controls."""
from __future__ import annotations

import argparse
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys

import numpy as np
from PIL import Image, ImageDraw
from skimage.segmentation import find_boundaries

from detect_beads import PALETTES
from highlight_regions import PARAMETERS, fill_highlights
from inference_audit import verify_inputs, write_json
from legacy_visibility import decode, font
from local_patch import retained_hypotheses, warp
from local_patch_audit import WARPS, baseline_assessment, evaluate, verify_manifest
from practice_legacy import ROOT, digest
from region_anchor_audit import SOURCES as PREVIOUS_SOURCES, anchor_diagnostics, summarize
from region_anchors import clicked_labels, correspondence, region_gate

HERE = ROOT/'photo2'
SOURCES = (*PREVIOUS_SOURCES, 'photo2/highlight_regions.py',
           'photo2/highlight_region_audit.py', 'photo2/test_highlight_regions.py')


def hashes():
    return {name: digest(ROOT/name) for name in SOURCES}


def pixel_metrics(labels, truth):
    """All crop pixels; split/merge counts include border regions and slivers."""
    _, inverse = np.unique(labels, return_inverse=True)
    # Reserve row zero for background even when a crop contains no zero label.
    values = np.unique(labels)
    if values[0] != 0:
        inverse = inverse+1
    width = int(truth.max())+1
    table = np.bincount(inverse.ravel()*width+truth.ravel(),
                        minlength=(int(inverse.max())+1)*width).reshape(-1, width)
    areas = table.sum(axis=0)
    substantial = (table[1:, 1:] >= 12) & (table[1:, 1:] >= .10*areas[None, 1:])
    tp = int(table[1:, 1:].sum())
    fp = int(table[1:, 0].sum())
    fn = int(table[0, 1:].sum())
    return dict(tp_pixels=tp, fp_pixels=fp, fn_pixels=fn,
        foreground_iou=tp/(tp+fp+fn) if tp+fp+fn else None,
        merged_predictions=int(np.count_nonzero(substantial.sum(axis=1) > 1)),
        split_truth_beads=int(np.count_nonzero(substantial.sum(axis=0) > 1)))


def panel(path, trial, rgb, old, repaired, truth, anchors, diagnostics, baselines, nominal):
    image = Image.new('RGB', (1640, 750), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((8, 8), trial+' | fixed fits; conditional indices', fill='black', font=font(21))
    arrays = [rgb.copy() for _ in range(4)]
    arrays[1][find_boundaries(old, mode='inner')] = (0, 220, 255)
    arrays[2][find_boundaries(repaired, mode='inner')] = (0, 220, 255)
    arrays[2][old != repaired] = (255, 0, 255)
    arrays[3][find_boundaries(truth, mode='inner')] = (255, 220, 0)
    titles = ('Beauty; frozen assistant clicks', 'Old observed regions',
              'Repaired; magenta = added pixels', 'Evaluator-only true boundaries')
    for j, (arr, title) in enumerate(zip(arrays, titles)):
        x = 410*j
        image.paste(Image.fromarray(arr), (x, 65))
        draw.text((x+5, 44), title, fill='black', font=font(15))
        for i, (ax, ay) in enumerate(anchors):
            draw.ellipse((x+ax-4, 65+ay-4, x+ax+4, 65+ay+4), outline='white', width=2)
            draw.text((x+ax+5, 65+ay), str(i), fill='white', font=font(13))
    draw.text((8, 490), f"Filled {diagnostics['filled_cavities']} cavities / {diagnostics['added_pixels']} pixels; all existing labels preserved.",
              fill='black', font=font(18))
    for j, method in enumerate(('old', 'repaired')):
        x = 8+820*j
        b = baselines[method]['supported']
        draw.text((x, 523), f"{method}: {b['matched']}/{b['eligible_truth']} observed regions, {b['false_predictions']} false; nominal four anchors:",
                  fill='black', font=font(16))
        selected = nominal['selected'][method]
        if not selected:
            draw.text((x, 550), 'No retained candidate', fill='black', font=font(15))
        for k, (name, s) in enumerate(selected.items()):
            line = (f"{name}: {s['correct_index']}/{s['matched']} matched indices correct, "
                    f"{s['false_predictions']} false; seeds correct={s['all_model_anchors_correct']}")
            draw.text((x, 550+k*20), line, fill='black', font=font(14))
    draw.text((8, 725), 'All alternatives, misses and controls remain in JSON. No automatic geometry, helicity or photo recovery claim.',
              fill='black', font=font(16))
    image.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, default=HERE/'output/region-anchors-r052-final')
    parser.add_argument('--output', type=Path, default=HERE/'output/highlight-regions-r055')
    args = parser.parse_args()
    args.previous, args.output = args.previous.resolve(), args.output.resolve()
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError('Output must be new or empty')
    before = hashes()
    previous = verify_manifest(args.previous/'report.json')
    verified = {}
    for name, sha in previous['input_reports'].items():
        source = Path(name)
        if digest(source) != sha:
            raise ValueError('Changed bound input report: '+name)
        if 'neighbor-audit' in source.parent.name:
            _, revisions = verify_inputs(source.parent)
            verified[name] = dict(report_sha256=sha, historical_revisions=revisions)
        else:
            report = verify_manifest(source)
            verified[name] = dict(report_sha256=sha, sources=len(report['sources']),
                                  artifacts=len(report['artifacts']))
    args.output.mkdir(parents=True, exist_ok=True)
    pattern = json.loads((HERE/'practice-pattern.json').read_text())['colors']*20
    trials = []
    for trial in previous['trials']:
        name = trial['name']
        print('Compare '+name, flush=True)
        saved = json.loads((args.previous/(name+'-prediction.json')).read_text())
        rgb = np.asarray(Image.open(args.previous/(name+'-input.png')).convert('RGB'))
        with np.load(args.previous/(name+'-masks.npz')) as arrays:
            observed = arrays['observed'].copy()
            masks = {c['name']: arrays[c['name']].copy() for c in saved['entries']}
        repaired, diagnostics = fill_highlights(rgb, observed)
        regions = dict(old=observed, repaired=repaired)
        entries, anchors = saved['entries'], saved['nominal_anchors']
        missing_control = observed.copy()
        seed_label = clicked_labels(observed, anchors[:1])[0]
        if seed_label:
            missing_control[missing_control == seed_label] = 0
        # Image-only ablation: choose the deleted label before truth is loaded.
        missing_repaired, missing_diagnostics = fill_highlights(rgb, missing_control)
        missing = dict(deleted_label=seed_label, applied=bool(seed_label),
            deleted_pixels=int(np.count_nonzero(observed != missing_control)),
            restored_deleted_pixels=int(np.count_nonzero((observed != missing_control) & (missing_repaired > 0))),
            seed_after=clicked_labels(missing_repaired, anchors[:1])[0], diagnostics=missing_diagnostics)
        tables = {method: {c['name']: correspondence(labels, masks[c['name']], c['objects'])
                          for c in entries} for method, labels in regions.items()}
        predictions = []
        for prior in saved['variants']:
            gates = {method: {c['name']: region_gate(labels, prior['anchors'], tables[method][c['name']])
                             for c in entries} for method, labels in regions.items()}
            retained = {}
            for method in regions:
                options = [dict(c, assessment=gates[method][c['name']]) for c in entries
                           if prior['variant'] != 'exclude_true_phase' or c['phase'] != 0]
                retained[method] = retained_hypotheses(options)
            if gates['old'] != prior['gates']['region'] or retained['old'] != prior['retained']['region']:
                raise AssertionError('Old gates changed')
            predictions.append(dict(count=prior['count'], variant=prior['variant'],
                anchors=prior['anchors'], gates=gates, retained=retained))
        # No evaluator truth or evaluator scores have been loaded for this trial.
        write_json(args.output/(name+'-prediction.json'), dict(trial=name,
            source_prediction_sha256=digest(args.previous/(name+'-prediction.json')),
            input_sha256=digest(args.previous/(name+'-input.png')),
            entries=entries, nominal_anchors=anchors, diagnostics=diagnostics,
            correspondences=tables, variants=predictions, missing_region_control=missing))
        np.savez_compressed(args.output/(name+'-masks.npz'), **regions)
        Image.fromarray(rgb).save(args.output/(name+'-input.png'))
        saved_eval = json.loads((args.previous/(name+'-evaluation.json')).read_text())
        # R052 binds the exact original truth image; validate before decoding it.
        baseline_report = next(Path(p) for p in previous['input_reports'] if 'neighbor-audit' in Path(p).parent.name)
        truth_path = baseline_report.parent/f"repeat-40-h{trial['hand']:+d}-phase-0-ids.png"
        if digest(truth_path) != saved_eval['truth_sha256']:
            raise ValueError('Truth image changed')
        truth = decode(np.asarray(Image.open(truth_path).convert('RGB').crop(saved['box'])), 800)
        if trial['patch'] == 'old':
            truth = warp(truth, WARPS[trial['condition']])
        palette = trial['palette']
        colors = [PALETTES[palette][i] for i in pattern] if palette in ('rgb', 'ryb') else [palette]*800
        baselines = {method: evaluate(labels, truth, baseline_assessment(labels, rgb, palette), anchors, colors)
                     for method, labels in regions.items()}
        if baselines['old'] != saved_eval['baseline']:
            raise AssertionError('Old baseline changed')
        evaluations = saved_eval['candidate_evaluations']
        nominal_truth = [i+1 for i in saved_eval['nominal_anchor_truth_indices']]
        scores = []
        for p, prior_score in zip(predictions, saved_eval['variants'], strict=True):
            selected = {method: {n: dict(summarize(evaluations[n], p['gates'][method][n]),
                       **anchor_diagnostics(evaluations[n], baselines[method], p['gates'][method][n],
                                            nominal_truth[:p['count']]))
                       for n in p['retained'][method]} for method in regions}
            if selected['old'] != prior_score['selected']['region']:
                raise AssertionError('Old scores changed')
            scores.append(dict(count=p['count'], variant=p['variant'], selected=selected,
                clicked_truth_indices=prior_score['clicked_truth_indices']))
        added = repaired != observed
        changed_pixels = dict(total=int(added.sum()),
            true_foreground=int(np.count_nonzero(added & (truth > 0))),
            true_background=int(np.count_nonzero(added & (truth == 0))))
        owners = {r['model_label']: r for r in baselines['repaired']['records']}
        ownership = []
        for label in np.unique(repaired[added]):
            mask = added & (repaired == label)
            owner = owners.get(int(label), {})
            matched = bool(owner.get('matched'))
            correct = int(np.count_nonzero(mask & (truth == owner['truth_label']))) if matched else 0
            ownership.append(dict(label=int(label), added_pixels=int(mask.sum()),
                owner_matched=matched, owner_truth_index=owner.get('truth_label', 0)-1,
                correct_pixels=correct,
                wrong_pixels=int(mask.sum())-correct if matched else 0,
                unresolved_pixels=0 if matched else int(mask.sum())))
        changed_pixels['ownership'] = ownership
        metrics = {method: pixel_metrics(labels, truth) for method, labels in regions.items()}
        write_json(args.output/(name+'-evaluation.json'), dict(truth_sha256=digest(truth_path),
            previous_evaluation_sha256=digest(args.previous/(name+'-evaluation.json')),
            nominal_anchor_truth_indices=saved_eval['nominal_anchor_truth_indices'],
            baseline=baselines, variants=scores, pixels=metrics, added_pixels=changed_pixels,
            missing_region_control=missing))
        nominal = next(p for p in scores if p['count'] == 4 and p['variant'] == 'nominal')
        panel(args.output/(name+'-panel.png'), name, rgb, observed, repaired, truth,
              anchors, diagnostics, baselines, nominal)
        trials.append(dict(name=name, patch=trial['patch'], palette=palette,
            hand=trial['hand'], condition=trial['condition'], diagnostics=diagnostics,
            baseline={k: v['supported'] for k, v in baselines.items()}, pixels=metrics,
            added_pixels=changed_pixels, missing_region_control=missing, variants=scores))
    if hashes() != before:
        raise ValueError('Sources changed during run')
    write_json(args.output/'report.json', dict(sources=before, parameters=PARAMETERS,
        command=[sys.executable, *sys.argv], python=platform.python_version(),
        packages={n: version(n) for n in ('numpy', 'scipy', 'Pillow', 'scikit-image')},
        previous_report=str(args.previous/'report.json'),
        previous_report_sha256=digest(args.previous/'report.json'), verified_inputs=verified,
        scope='Fixed R052 calibrated geometry, masks, fits, clicks and colors; no new renders or fits',
        old_gate_score_parity=True, trials=trials,
        artifacts={p.name: digest(p) for p in sorted(args.output.iterdir()) if p.is_file()}))
    print('Saved '+str(args.output/'report.json'), flush=True)


if __name__ == '__main__':
    main()
