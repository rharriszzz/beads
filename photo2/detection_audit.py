#!/usr/bin/env python3
"""Compare RGB-input bead detectors on saved beads.pov renders and paired palettes."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import platform
import sys

import numpy as np
from PIL import Image, ImageDraw, __version__ as pillow_version
import scipy
import skimage
from skimage.segmentation import find_boundaries

from detect_beads import METHODS, PALETTES, PARAMETERS, detect
from detection_metrics import score_instances
from inference_audit import verify_inputs, write_json
from legacy_visibility import decode, font, render, replace_once, wrapper
from practice_legacy import ROOT, digest

HERE = ROOT/'photo2'
PHASES = (('phase-0', '0'), ('phase-half', '0.0625'))
SOURCE_NAMES = ('photo2/detect_beads.py', 'photo2/detection_metrics.py',
                'photo2/detection_audit.py', 'photo2/requirements.txt',
                'photo2/legacy_visibility.py', 'photo2/inference_audit.py',
                'photo2/practice_legacy.py', 'photo2/practice-pattern.json',
                'photo2/visibility-pattern-13.json', 'beads.pov', 'bead-shape.inc')


def source_hashes():
    return {name: digest(ROOT/name) for name in SOURCE_NAMES}


def prepare_fixtures(out, baseline):
    """Appearance-only variants of case 1. No tracked renderer edit."""
    manifest = out/'report.json'
    if manifest.exists():
        saved = json.loads(manifest.read_text())
        for name, sha in saved['sources'].items():
            if digest(ROOT/name) != sha:
                raise ValueError(f'Fixture source changed: {name}; use a fresh fixture directory')
        if saved['baseline_report_sha256'] != digest(baseline/'report.json'):
            raise ValueError('Fixture baseline differs')
        for name, sha in saved['artifacts'].items():
            if digest(out/name) != sha:
                raise ValueError(f'Fixture artifact changed: {name}')
        return saved
    if out.exists() and any(out.iterdir()):
        raise ValueError('Fixture directory must be empty or contain a verified manifest')
    out.mkdir(parents=True, exist_ok=True)
    source = (ROOT/'beads.pov').read_text()
    pattern = json.loads((HERE/'practice-pattern.json').read_text())
    commands, images = [], []
    old = ('#declare beads[0] = bead(shiny_opaque(Red),   0.8, 0.7, 1.0);\n'
           '#declare beads[1] = bead(shiny_opaque(Green), 0.8, 0.7, 1.0);\n'
           '#declare beads[2] = bead(shiny_opaque(Blue),  0.8, 0.7, 1.0);')
    for palette, colors in [('rgb', ('Red', 'Green', 'Blue')),
                            ('ryb', ('Red', 'Yellow', 'Black')),
                            ('gray', ('Gray50',)*3), ('black', ('Black',)*3)]:
        new = '\n'.join(f'#declare beads[{i}] = bead(shiny_opaque({color}), 0.8, 0.7, 1.0);'
                         for i, color in enumerate(colors))
        scene_source = out/f'{palette}.inc'
        scene_source.write_text(replace_once(source, old, new))
        scene = out/f'{palette}.pov'
        scene.write_text(wrapper(pattern, scene_source.as_posix()))
        for phase, clock in PHASES:
            name = f'{palette}-{phase}'
            print(f'Render {name}', flush=True)
            rgb = render(out, name, scene, clock, commands, beauty=True)
            base_name = f'repeat-40-h+1-{phase}'
            if palette == 'rgb':
                original = np.asarray(Image.open(baseline/f'{base_name}-beauty.png').convert('RGB'))
                if not np.array_equal(rgb, original):
                    raise ValueError('Unchanged RGB source does not reproduce the saved beauty pixels')
            images.append(dict(name=name, palette=palette, phase=phase, baseline_view=base_name,
                               image=f'{name}.png', rgb_baseline_pixel_equal=palette == 'rgb'))
    sources = {name: digest(ROOT/name) for name in
               ('photo2/detection_audit.py', 'photo2/practice-pattern.json', 'beads.pov',
                'bead-shape.inc', 'photo2/legacy_visibility.py', 'photo2/practice_legacy.py')}
    saved = dict(sources=sources, baseline_report_sha256=digest(baseline/'report.json'),
                 changes='Only case-1 pigment arguments replaced; dimensions, geometry, lighting and camera retained',
                 commands=commands, images=images,
                 artifacts={p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file()})
    write_json(manifest, saved)
    return saved


def overlay(rgb, labels, color):
    result = rgb.copy()
    result[find_boundaries(labels, mode='inner')] = color
    return Image.fromarray(result)


def panels(out, case, rgb, truth, predictions, scores):
    # Same normalized crop for every view and method; selected before scoring.
    h, w = rgb.shape[:2]
    box = tuple(round(a*b) for a, b in zip((.68, .35, .96, .72), (w, h, w, h)))
    entries = [('Input; fixed crop boxed', Image.fromarray(rgb)),
               ('Evaluator-only visible boundaries', overlay(rgb, truth, (0, 255, 255)))]
    for method in METHODS:
        s = scores[method]['thresholds']['100']
        entries.append((f'{method}: TP {s["tp"]}, FP {s["fp"]}, FN {s["fn"]}',
                        overlay(rgb, predictions[method], (255, 0, 255))))
    for detail in (False, True):
        panel = Image.new('RGB', (1800, 1030), 'white')
        draw = ImageDraw.Draw(panel)
        draw.text((15, 10), f'{case}: '+('fixed detail' if detail else 'whole image')+
                  '; whole-image counts, IoU > 0.5, >=100 truth pixels', fill='black', font=font(22))
        for j, (title, im) in enumerate(entries):
            if detail:
                im = im.crop(box)
            else:
                im = im.copy()
                ImageDraw.Draw(im).rectangle(box, outline='#00aa00', width=5)
            im.thumbnail((588, 440))
            x, y = (j % 3)*600+6, (j//3)*480+65
            panel.paste(im, (x+(588-im.width)//2, y))
            draw.text((x, y-23), title, fill='black', font=font(15))
        panel.save(out/f'{case}-{"detail" if detail else "whole"}.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=HERE/'output/neighbor-audit-final')
    parser.add_argument('--fixtures', type=Path, default=HERE/'output/detection-fixtures-r045')
    parser.add_argument('--output', type=Path, default=HERE/'output/detection-audit-r045')
    args = parser.parse_args()
    baseline, fixtures, out = (p.resolve() for p in (args.input, args.fixtures, args.output))
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output must be new or empty')
    initial_sources = source_hashes()
    baseline_report, revisions = verify_inputs(baseline)
    fixture_report = prepare_fixtures(fixtures, baseline)
    out.mkdir(parents=True, exist_ok=True)
    cases = []
    for view in baseline_report['views']:
        length = int(view.split('-')[1])
        pattern_file = 'practice-pattern.json' if length == 40 else 'visibility-pattern-13.json'
        pattern = json.loads((HERE/pattern_file).read_text())
        colors = [PALETTES['rgb'][i] for i in pattern['colors']]*pattern['groups']
        cases.append(dict(name=view, palette='rgb', image=baseline/f'{view}-beauty.png',
                          truth=baseline/f'{view}-ids.png', colors=colors, variant='original'))
    pattern = json.loads((HERE/'practice-pattern.json').read_text())
    for item in fixture_report['images']:
        palette = item['palette']
        if palette == 'rgb':  # Pixel reproduction control, not a duplicate scored case.
            continue
        colors = ([PALETTES[palette][i] for i in pattern['colors']]*pattern['groups']
                  if palette == 'ryb' else [palette]*800)
        cases.append(dict(name=item['name'], palette=palette, image=fixtures/item['image'],
                          truth=baseline/f'{item["baseline_view"]}-ids.png', colors=colors,
                          variant='palette_control'))
    # One fixed, mild corruption test for RYB only; no extra renderer geometry.
    for case in list(cases):
        if case['palette'] == 'ryb':
            cases.append(dict(case, name=case['name']+'-blur-noise', variant='blur_noise'))
    rows, records = [], []
    for case in cases:
        print(f'Segment {case["name"]}', flush=True)
        rgb = np.asarray(Image.open(case['image']).convert('RGB'))
        if case['variant'] == 'blur_noise':
            from scipy.ndimage import gaussian_filter
            rng = np.random.Generator(np.random.PCG64(45))
            rgb = np.clip(np.rint(gaussian_filter(rgb.astype(float), (1., 1., 0.))+
                                  rng.normal(0, 2., rgb.shape)), 0, 255).astype(np.uint8)
            Image.fromarray(rgb).save(out/f'{case["name"]}-input.png')
        truth = decode(np.asarray(Image.open(case['truth']).convert('RGB')), len(case['colors']))
        predictions, scores = {}, {}
        case_record = dict(name=case['name'], palette=case['palette'], variant=case['variant'],
                           image=str(case['image']), image_sha256=digest(case['image']),
                           truth=str(case['truth']), truth_sha256=digest(case['truth']), methods={})
        for method in METHODS:
            labels, detected = detect(rgb, method, case['palette'])
            evaluation = score_instances(labels, truth, detected['objects'], case['colors'])
            name = f'{case["name"]}-{method}'
            Image.fromarray(labels.astype(np.uint16)).save(out/f'{name}-labels.png')
            write_json(out/f'{name}.json', dict(detection=detected, evaluation=evaluation))
            case_record['methods'][method] = f'{name}.json'
            for threshold, metrics in evaluation['thresholds'].items():
                rows.append(dict(case=case['name'], palette=case['palette'], variant=case['variant'],
                                  method=method, threshold=int(threshold),
                                  **{k: metrics[k] for k in ('tp', 'fp', 'fn', 'ignored',
                                      'precision', 'recall', 'color_correct', 'color_unknown', 'mean_iou')},
                                  merges=evaluation['merged_predictions'], splits=evaluation['split_truth_beads']))
            predictions[method], scores[method] = labels, evaluation
        panels(out, case['name'], rgb, truth, predictions, scores)
        records.append(case_record)
    with (out/'summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    aggregates = {}
    for palette, variant in sorted({(r['palette'], r['variant']) for r in rows}):
        group = f'{palette}/{variant}'
        aggregates[group] = {}
        for method in METHODS:
            selected = [r for r in rows if (r['palette'], r['variant'], r['method'], r['threshold']) ==
                        (palette, variant, method, 100)]
            totals = {k: sum(r[k] for r in selected) for k in
                      ('tp', 'fp', 'fn', 'ignored', 'color_correct', 'color_unknown')}
            tp, fp, fn = (totals[k] for k in ('tp', 'fp', 'fn'))
            totals.update(precision=tp/(tp+fp) if tp+fp else None,
                          recall=tp/(tp+fn) if tp+fn else None)
            aggregates[group][method] = totals
    if source_hashes() != initial_sources:
        raise ValueError('Sources changed during audit')
    report = dict(command=[sys.executable, *sys.argv], sources=initial_sources,
                  environment=dict(python=platform.python_version(), numpy=np.__version__,
                                   scipy=scipy.__version__, skimage=skimage.__version__, pillow=pillow_version),
                  baseline_report_sha256=digest(baseline/'report.json'),
                  baseline_source_revisions=revisions,
                  fixture_report_sha256=digest(fixtures/'report.json'),
                  parameters=PARAMETERS, methods=METHODS, cases=records, aggregates_T100=aggregates,
                  corruption=dict(gaussian_sigma_px=1., rgb_noise_sigma=2., seed=45),
                  claims='Beauty-image detection only; no source indices supplied to detector; all bead_index fields remain null',
                  limitations=['White-floor foreground heuristic, including shadows',
                               'Paired controls reuse exact geometry; not independent scenes',
                               'ID masks un-antialiased, beauty antialiased',
                               'No model-guided correction, manual scribble trial, photo segmentation or index recovery'],
                  artifacts={p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file()})
    write_json(out/'report.json', report)
    print(json.dumps(aggregates, indent=2), flush=True)


if __name__ == '__main__':
    main()
