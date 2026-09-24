#!/usr/bin/env python3
"""Fixed shared-cavity comparison; R052 fits and R055 conservative parity."""
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
from shared_highlights import PARAMETERS, METHODS, assign_shared
from highlight_region_audit import SOURCES as HIGHLIGHT_SOURCES, pixel_metrics
from inference_audit import verify_inputs, write_json
from legacy_visibility import decode, font
from local_patch import retained_hypotheses, warp
from local_patch_audit import WARPS, baseline_assessment, evaluate, verify_manifest
from practice_legacy import ROOT, digest
from region_anchor_audit import anchor_diagnostics, summarize
from region_anchors import clicked_labels, correspondence, region_gate

HERE = ROOT/'photo2'
SOURCES = (*HIGHLIGHT_SOURCES, 'photo2/shared_highlights.py',
           'photo2/shared_highlight_audit.py', 'photo2/test_shared_highlights.py')


def hashes():
    return {name: digest(ROOT/name) for name in SOURCES}


def panel(path, trial, rgb, regions, truth, anchors, diagnostics, baselines, nominal):
    image = Image.new('RGB', (2050, 830), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((8, 8), trial+' | fixed fits and clicks; conditional indices', fill='black', font=font(21))
    arrays = [rgb.copy() for _ in range(5)]
    for j, method in enumerate(METHODS, 1):
        arrays[j][find_boundaries(regions[method], mode='inner')] = (0, 220, 255)
        arrays[j][regions[method] != regions['old']] = (255, 0, 255)
        for owner in baselines[method]['records']:
            added = ((regions[method] != regions['old']) &
                     (regions[method] == owner['model_label']))
            if owner['matched']:
                arrays[j][added & (truth != owner['truth_label'])] = (255, 130, 0)
            else:
                arrays[j][added] = (70, 110, 255)
    arrays[4][find_boundaries(truth, mode='inner')] = (255, 220, 0)
    titles = ('Beauty; frozen clicks', 'Conservative; magenta = added',
              'Distance; magenta = added', 'Gradient; magenta = added', 'Evaluator-only truth boundaries')
    for j, (arr, title) in enumerate(zip(arrays, titles)):
        x = 410*j
        image.paste(Image.fromarray(arr), (x, 65))
        draw.text((x+5, 44), title, fill='black', font=font(15))
        for i, (ax, ay) in enumerate(anchors):
            draw.ellipse((x+ax-4, 65+ay-4, x+ax+4, 65+ay+4), outline='white', width=2)
            draw.text((x+ax+5, 65+ay), str(i), fill='white', font=font(13))
    for j, method in enumerate(METHODS):
        x = 8+680*j
        b = baselines[method]['supported']
        d = diagnostics[method]
        draw.text((x, 493), f"{method}: {d['shared_added_pixels']} shared pixels; {d['tie_pixels']} ties", fill='black', font=font(18))
        draw.text((x, 522), f"{b['matched']}/{b['eligible_truth']} regions; {b['false_predictions']} false", fill='black', font=font(16))
        selected = nominal['selected'][method]
        if not selected:
            draw.text((x, 550), 'Nominal four anchors: no retained candidate', fill='black', font=font(15))
        for k, (name, score) in enumerate(selected.items()):
            draw.text((x, 550+k*45), f"{name}: {score['correct_index']}/{score['matched']} indices; {score['false_predictions']} false", fill='black', font=font(15))
            draw.text((x, 570+k*45), f"All seed bodies correct: {score['all_model_anchors_correct']}", fill='black', font=font(15))
    draw.text((8, 768), 'Evaluator overlay on added pixels: magenta = correct, orange = wrong owner, blue = unresolved owner.', fill='black', font=font(17))
    draw.text((8, 803), 'All alternatives, unknowns, misses and controls in JSON. No automatic geometry, helicity or photo recovery claim.', fill='black', font=font(17))
    image.save(path)


def ownership(added, labels, truth, baseline):
    owners = {r['model_label']: r for r in baseline['records']}
    records = []
    for label in np.unique(labels[added]):
        mask = added & (labels == label)
        owner = owners.get(int(label), {})
        matched = bool(owner.get('matched'))
        correct = int(np.count_nonzero(mask & (truth == owner['truth_label']))) if matched else 0
        records.append(dict(label=int(label), added_pixels=int(mask.sum()), owner_matched=matched,
            owner_truth_index=owner.get('truth_label', 0)-1, correct_pixels=correct,
            wrong_pixels=int(mask.sum())-correct if matched else 0,
            unresolved_pixels=0 if matched else int(mask.sum())))
    return dict(total=int(added.sum()), true_foreground=int(np.count_nonzero(added & (truth > 0))),
                true_background=int(np.count_nonzero(added & (truth == 0))), ownership=records)


def aggregate(trials):
    result = {}
    controls = ('false_background', 'duplicate', 'exclude_true_phase')
    for method in METHODS:
        totals = dict(added_pixels=0, shared_added_pixels=0, tie_pixels=0,
                      correct_pixels=0, wrong_pixels=0, unresolved_pixels=0,
                      added_background_pixels=0, shared_cavities=0)
        for trial in trials:
            diagnostics, pixels = trial['diagnostics'][method], trial['added_pixels'][method]
            for key in ('added_pixels', 'shared_added_pixels', 'tie_pixels'):
                totals[key] += diagnostics[key]
            totals['shared_cavities'] += len(diagnostics['shared_cavities'])
            totals['added_background_pixels'] += pixels['true_background']
            for owner in pixels['ownership']:
                for key in ('correct_pixels', 'wrong_pixels', 'unresolved_pixels'):
                    totals[key] += owner[key]
        groups = {}
        for count in (3, 4):
            counts = dict(trials=0, accepted=0, accepted_with_wrong_index=0,
                          accepted_with_all_seeds_correct=0, gains=0, losses=0)
            control_counts = {key: dict(trials=0, accepted=0) for key in controls}
            for trial in trials:
                for variant in trial['variants']:
                    if variant['count'] != count:
                        continue
                    selected = variant['selected'][method]
                    if variant['variant'] in controls:
                        c = control_counts[variant['variant']]
                        c['trials'] += 1
                        c['accepted'] += bool(selected)
                        continue
                    baseline = variant['selected']['conservative']
                    counts['trials'] += 1
                    counts['accepted'] += bool(selected)
                    counts['accepted_with_wrong_index'] += any(s['wrong_index'] for s in selected.values())
                    counts['accepted_with_all_seeds_correct'] += bool(selected) and all(
                        s['all_model_anchors_correct'] for s in selected.values())
                    counts['gains'] += bool(selected) and not baseline
                    counts['losses'] += bool(baseline) and not selected
            groups[count] = dict(**counts, controls=control_counts)
        result[method] = dict(pixels=totals, anchors=groups)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, default=HERE/'output/region-anchors-r052-final')
    parser.add_argument('--conservative', type=Path, default=HERE/'output/highlight-regions-r055-final')
    parser.add_argument('--output', type=Path, default=HERE/'output/shared-highlights-r057')
    args = parser.parse_args()
    args.previous, args.output = args.previous.resolve(), args.output.resolve()
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError('Output must be new or empty')
    before = hashes()
    previous = verify_manifest(args.previous/'report.json')
    args.conservative = args.conservative.resolve()
    conservative_report = verify_manifest(args.conservative/'report.json')
    if conservative_report['previous_report_sha256'] != digest(args.previous/'report.json'):
        raise ValueError('Conservative baseline uses another input')
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
        regions, diagnostics = dict(old=observed), {}
        for method in METHODS:
            regions[method], diagnostics[method] = assign_shared(rgb, observed, method)
        with np.load(args.conservative/(name+'-masks.npz')) as prior_masks:
            if not np.array_equal(regions['conservative'], prior_masks['repaired']):
                raise AssertionError('Conservative masks changed')
        conservative_prediction = json.loads((args.conservative/(name+'-prediction.json')).read_text())
        entries, anchors = saved['entries'], saved['nominal_anchors']
        missing_control = observed.copy()
        seed_label = clicked_labels(observed, anchors[:1])[0]
        if seed_label:
            missing_control[missing_control == seed_label] = 0
        # Image-only ablation: choose the deleted label before truth is loaded.
        missing = {}
        for method in METHODS:
            missing_repaired, missing_diagnostics = assign_shared(rgb, missing_control, method)
            missing[method] = dict(deleted_label=seed_label, applied=bool(seed_label),
                deleted_pixels=int(np.count_nonzero(observed != missing_control)),
                restored_deleted_pixels=int(np.count_nonzero((observed != missing_control) & (missing_repaired > 0))),
                seed_after=clicked_labels(missing_repaired, anchors[:1])[0], diagnostics=missing_diagnostics)
        old_missing = conservative_prediction['missing_region_control']
        if any(missing['conservative'][k] != v for k, v in old_missing.items() if k != 'diagnostics'):
            raise AssertionError('Conservative deletion control changed')
        tables = {method: {c['name']: correspondence(labels, masks[c['name']], c['objects'])
                          for c in entries} for method, labels in regions.items()}
        predictions = []
        for prior, cp in zip(saved['variants'], conservative_prediction['variants'], strict=True):
            gates = {method: {c['name']: region_gate(labels, prior['anchors'], tables[method][c['name']])
                             for c in entries} for method, labels in regions.items()}
            retained = {}
            for method in regions:
                options = [dict(c, assessment=gates[method][c['name']]) for c in entries
                           if prior['variant'] != 'exclude_true_phase' or c['phase'] != 0]
                retained[method] = retained_hypotheses(options)
            if gates['old'] != prior['gates']['region'] or retained['old'] != prior['retained']['region']:
                raise AssertionError('Old gates changed')
            if gates['conservative'] != cp['gates']['repaired'] or retained['conservative'] != cp['retained']['repaired']:
                raise AssertionError('Conservative gates changed')
            predictions.append(dict(count=prior['count'], variant=prior['variant'],
                anchors=prior['anchors'], gates=gates, retained=retained))
        # No evaluator truth or evaluator scores have been loaded for this trial.
        write_json(args.output/(name+'-prediction.json'), dict(trial=name,
            source_prediction_sha256=digest(args.previous/(name+'-prediction.json')),
            conservative_prediction_sha256=digest(args.conservative/(name+'-prediction.json')),
            input_sha256=digest(args.previous/(name+'-input.png')),
            entries=entries, nominal_anchors=anchors, diagnostics=diagnostics,
            correspondences=tables, variants=predictions, missing_region_control=missing))
        np.savez_compressed(args.output/(name+'-masks.npz'), **regions)
        Image.fromarray(rgb).save(args.output/(name+'-input.png'))
        saved_eval = json.loads((args.previous/(name+'-evaluation.json')).read_text())
        conservative_eval = json.loads((args.conservative/(name+'-evaluation.json')).read_text())
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
        if baselines['conservative'] != conservative_eval['baseline']['repaired']:
            raise AssertionError('Conservative baseline changed')
        evaluations = saved_eval['candidate_evaluations']
        nominal_truth = [i+1 for i in saved_eval['nominal_anchor_truth_indices']]
        scores = []
        for p, prior_score, cs in zip(predictions, saved_eval['variants'], conservative_eval['variants'], strict=True):
            selected = {method: {n: dict(summarize(evaluations[n], p['gates'][method][n]),
                       **anchor_diagnostics(evaluations[n], baselines[method], p['gates'][method][n],
                                            nominal_truth[:p['count']]))
                       for n in p['retained'][method]} for method in regions}
            if selected['old'] != prior_score['selected']['region']:
                raise AssertionError('Old scores changed')
            if selected['conservative'] != cs['selected']['repaired']:
                raise AssertionError('Conservative scores changed')
            scores.append(dict(count=p['count'], variant=p['variant'], selected=selected,
                clicked_truth_indices=prior_score['clicked_truth_indices']))
        changed_pixels = {method: ownership(labels != observed, labels, truth, baselines[method])
                          for method, labels in regions.items() if method != 'old'}
        shared_pixels = {method: ownership(labels != regions['conservative'], labels, truth, baselines[method])
                         for method, labels in regions.items() if method in ('distance', 'gradient')}
        # Also bind ownership to the pre-extension region match; region growth must
        # not silently change the meaning of "correctly owned" added pixels.
        fixed_owners = {method: ownership(labels != regions['conservative'], labels, truth, baselines['conservative'])
                        for method, labels in regions.items() if method in ('distance', 'gradient')}
        if changed_pixels['conservative'] != conservative_eval['added_pixels']:
            raise AssertionError('Conservative pixel ownership changed')
        metrics = {method: pixel_metrics(labels, truth) for method, labels in regions.items()}
        write_json(args.output/(name+'-evaluation.json'), dict(truth_sha256=digest(truth_path),
            previous_evaluation_sha256=digest(args.previous/(name+'-evaluation.json')),
            nominal_anchor_truth_indices=saved_eval['nominal_anchor_truth_indices'],
            baseline=baselines, variants=scores, pixels=metrics, added_pixels=changed_pixels,
            shared_pixels=shared_pixels, fixed_owner_shared_pixels=fixed_owners, missing_region_control=missing))
        nominal = next(p for p in scores if p['count'] == 4 and p['variant'] == 'nominal')
        panel(args.output/(name+'-panel.png'), name, rgb, regions, truth,
              anchors, diagnostics, baselines, nominal)
        trials.append(dict(name=name, patch=trial['patch'], palette=palette,
            hand=trial['hand'], condition=trial['condition'], diagnostics=diagnostics,
            baseline={k: v['supported'] for k, v in baselines.items()}, pixels=metrics,
            added_pixels=changed_pixels, shared_pixels=shared_pixels, fixed_owner_shared_pixels=fixed_owners,
            missing_region_control=missing, variants=scores))
    if hashes() != before:
        raise ValueError('Sources changed during run')
    write_json(args.output/'report.json', dict(sources=before, parameters=PARAMETERS,
        command=[sys.executable, *sys.argv], python=platform.python_version(),
        packages={n: version(n) for n in ('numpy', 'scipy', 'Pillow', 'scikit-image')},
        previous_report=str(args.previous/'report.json'),
        previous_report_sha256=digest(args.previous/'report.json'), verified_inputs=verified,
        scope='Fixed R052 calibrated geometry, masks, fits, clicks and colors; no new renders or fits',
        old_gate_score_parity=True, conservative_parity=True,
        conservative_report=str(args.conservative/'report.json'),
        conservative_report_sha256=digest(args.conservative/'report.json'), trials=trials,
        summary=aggregate(trials),
        artifacts={p.name: digest(p) for p in sorted(args.output.iterdir()) if p.is_file()}))
    print('Saved '+str(args.output/'report.json'), flush=True)


if __name__ == '__main__':
    main()
