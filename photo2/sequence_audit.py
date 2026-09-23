#!/usr/bin/env python3
"""Known-index synthetic period validation. No image reading or photo fitting."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version

from partial_word import canonical, completion_summary, fit_period, holdout, primitive, scan

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'ab7915841577c27cfb03f779cc765e556ffc9dcd'
HISTORICAL_REPORT = '12ac2b92948e920b89e7da5a49ae1ecfdfcfb44c102d4c07e53606344489c7c0'
SOURCES = ['photo2/partial_word.py', 'photo2/sequence_audit.py', 'photo2/test_partial_word.py',
           'photo2/staircase-pattern-30.json', 'photo2/practice-pattern.json',
           'photo2/visibility-pattern-13.json']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def verify_history(directory):
    path = directory / 'report.json'
    report = json.loads(path.read_text())
    for name, expected in report['sources'].items():
        data = subprocess.check_output(['git', 'show', f'{BASELINE}:{name}'], cwd=ROOT)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'Historical source hash mismatch: {name}')
    for name, expected in report['artifacts'].items():
        if digest(directory / name) != expected:
            raise ValueError(f'Historical artifact hash mismatch: {name}')
    if report['raster'] != [2400, 1800]:
        raise ValueError('Unexpected visibility raster')
    return report


def bases(history):
    pattern = json.loads((ROOT / 'photo2/staircase-pattern-30.json').read_text())
    yield {'name': 'repeat-30-symbolic', 'pattern': pattern['colors'],
           'truth': pattern['colors'] * pattern['groups'],
           'observations': pattern['colors'] * pattern['groups'],
           'mask': 'Complete symbolic sequence; no visibility rendering'}
    for case in history['cases']:
        source = 'practice-pattern.json' if case['length'] == 40 else 'visibility-pattern-13.json'
        pattern = json.loads((ROOT / 'photo2' / source).read_text())
        if pattern != case['pattern']:
            raise ValueError(f'Current source pattern differs from historical fixture: {source}')
        truth = pattern['colors'] * pattern['groups']
        assert len(truth) == case['count']
        for phase, view in case['views'].items():
            for threshold in (12, 100):
                counts = view['pixels_per_bead']
                assert len(counts) == len(truth)
                observations = [c if counts[i] >= threshold else None for i, c in enumerate(truth)]
                yield {'name': f'{case["name"]}-{phase}-T{threshold}', 'pattern': pattern['colors'],
                       'truth': truth, 'observations': observations,
                       'mask': {'phase': phase, 'threshold_pixels': threshold,
                                'pixels_per_bead': counts, 'raster': history['raster']}}


def variants(base):
    original = base['observations']
    yield 'base', original.copy(), {}
    readable = [i for i, c in enumerate(original) if c is not None]
    for rate in (0.1, 0.3):
        for seed in (17, 43):
            rng = np.random.Generator(np.random.PCG64(seed))
            erased = [i for i, draw in zip(readable, rng.random(len(readable))) if draw < rate]
            obs = original.copy()
            for i in erased:
                obs[i] = None
            yield f'erase-{rate}-seed-{seed}', obs, {'rate': rate, 'seed': seed, 'erased_indices': erased,
                                                   'rule': 'Independent Bernoulli draws in source-index order'}
    yield 'all-unknown', [None] * len(original), {'erased_indices': readable}
    length = len(base['pattern'])
    slot = next(i % length for i in readable)
    erased = [i for i in readable if i % length == slot]
    obs = original.copy()
    for i in erased:
        obs[i] = None
    yield 'missing-slot', obs, {'missing_slot': slot, 'erased_indices': erased}
    index = next(i for i in readable if sum(j % length == i % length for j in readable) >= 2)
    obs = original.copy()
    obs[index] = (obs[index] + 1) % 3
    yield 'wrong-color', obs, {'changed_index': index, 'before': original[index], 'after': obs[index]}


def check_scan(result, obs):
    for fit in result['rejected']:
        a, b = fit['witness_positions']
        assert obs[a] is not None and obs[b] is not None and obs[a] != obs[b]
        assert (a-b) % fit['period'] == 0
    for fit in result['compatible']:
        for slot, ids in enumerate(fit['support_positions']):
            assert (not ids) == (fit['slot_colors'][slot] is None)
            assert all(i % fit['period'] == slot and obs[i] == fit['slot_colors'][slot] for i in ids)
        assert sum(map(len, fit['support_positions'])) == sum(c is not None for c in obs)


def canonical_fast(slots):
    # Uniform partial families arise in the all-unknown control at every length.
    if all(c is None for c in slots):
        return {'key': [-1] * len(slots), 'direction': 1, 'shift': 0,
                'kind': 'partial_family', 'block_length': len(slots)}
    return canonical(slots)


def evaluate(base, variant, obs, changes):
    before = obs.copy()
    n, length = len(obs), len(base['pattern'])
    result = scan(obs, exact_count=n)
    check_scan(result, obs)
    families = {}
    for fit in result['compatible']:
        norm = canonical_fast(fit['slot_colors'])
        fit['presentation'] = norm
        key = (norm['kind'], tuple(norm['key']))
        if key not in families:
            families[key] = {'presentation': norm, 'periods': []}
        families[key]['periods'].append(fit['period'])
    folds = []
    for fold in range(4):
        start, stop = fold*n//4, (fold+1)*n//4
        held = holdout(obs, start, stop, exact_count=n)
        assert all(sum(row[k] for k in ('correct', 'wrong', 'abstained')) ==
                   sum(c is not None for c in obs[start:stop]) for row in held['compatible'])
        if variant != 'wrong-color':
            true_row = next(row for row in held['compatible'] if row['period'] == length)
            assert true_row['wrong'] == 0
        folds.append(held)
    true_fit = fit_period(obs, length)
    assert true_fit['compatible'] == (variant != 'wrong-color')
    if true_fit['compatible']:
        assert all(c is None or c == base['pattern'][i] for i, c in enumerate(true_fit['slot_colors']))
        true_fit['completions'] = completion_summary(true_fit['slot_colors'])
    assert obs == before
    if variant == 'base':
        if length == 40 or length == 30:
            assert true_fit['unsupported_slots'] == []
        if base['name'] == 'repeat-13-phase-half-T100':
            assert true_fit['unsupported_slots'] == [0]
    return {'name': f'{base["name"]}-{variant}', 'base': base['name'], 'variant': variant,
            'input': {'exact_count': n, 'observations': obs, 'changes': changes,
                      'unknown_indices': [i for i, c in enumerate(obs) if c is None]},
            'scan': result, 'presentation_families': list(families.values()), 'folds': folds,
            'evaluation_only': {'true_period': length, 'true_period_fit': true_fit}}


def table(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def illustration(path, examples):
    image = Image.new('RGB', (1320, 590), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=19)
    small = ImageFont.load_default(size=13)
    palette = ['#ce303b', '#f0c82f', '#222222']
    draw.text((20, 12), 'Indexed color evidence: observations remain unchanged', fill='black', font=font)
    draw.text((20, 40), 'Conditional on the stated period. Colored cells = supported; ? = unsupported; dash = no new inference.', fill='black', font=font)
    for panel, example in enumerate(examples):
        y = 88 + panel*240
        obs = example['input']['observations']
        fit = example['evaluation_only']['true_period_fit']
        length = fit['period']
        draw.text((20, y), f'{example["name"]}   |   evaluate L={length}', fill='black', font=font)
        draw.text((20, y+27), 'Two consecutive repeats shown; each column keeps its original bead index.', fill='black', font=small)
        shown = min(2*length, 60)
        for row, label in enumerate(('Observed', 'Inferred only', 'Supported slots')):
            yy = y + 70 + row*40
            draw.text((20, yy+5), label, fill='black', font=font)
            for i in range(shown if row < 2 else length):
                x = 200 + i*18
                observed, predicted = obs[i], fit['slot_colors'][i % length]
                c = observed if row == 0 else predicted
                blank = row == 1 and observed is not None
                if blank:
                    c = None
                draw.rectangle((x, yy, x+16, yy+28), fill='white' if c is None else palette[c], outline='#999999')
                if c is None:
                    draw.text((x+3, yy+6), '-' if blank else '?', fill='black', font=small)
                if row == 0 and i % 5 == 0:
                    draw.text((x, yy-17), str(i), fill='black', font=small)
    draw.text((20, 563), '30-bead example: artificial erasures. 13-bead example: historical T=100 mask; slot 0 has no support.', fill='black', font=font)
    image.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--visibility', type=Path, default=ROOT/'photo2/output/legacy-visibility-verified')
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/sequence-audit')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output directory to preserve earlier evidence')
    history = verify_history(args.visibility.resolve())
    hashes = {name: digest(ROOT/name) for name in SOURCES}
    out.mkdir(parents=True, exist_ok=True)
    (out/'cases').mkdir()
    summaries, candidates, folds, examples, inputs = [], [], [], [], []
    for base in bases(history):
        assert len(primitive(base['pattern'])) == len(base['pattern'])
        inputs.append(base)
        for variant, obs, changes in variants(base):
            result = evaluate(base, variant, obs, changes)
            path = out/'cases'/f'{result["name"]}.json'
            write_json(path, result)
            fits = result['scan']['compatible']
            true = result['evaluation_only']['true_period_fit']
            summaries.append({'case': result['name'], 'N': len(obs), 'true_L': len(base['pattern']),
                              'readable': sum(c is not None for c in obs), 'compatible_count': len(fits),
                              'periods': ' '.join(str(f['period']) for f in fits),
                              'closure_periods': ' '.join(str(f['period']) for f in fits if f['whole_repeat_closure']),
                              'true_L_compatible': true['compatible'],
                              'true_L_unsupported': ' '.join(map(str, true.get('unsupported_slots', []))),
                              'canonical_families': len(result['presentation_families'])})
            for fit in fits:
                candidates.append({'case': result['name'], 'period': fit['period'],
                                   'closure': fit['whole_repeat_closure'],
                                   'supported_slots': fit['period'] - len(fit['unsupported_slots']),
                                   'unsupported_slots': ' '.join(map(str, fit['unsupported_slots']))})
            for j, fold in enumerate(result['folds']):
                for row in fold['compatible']:
                    folds.append({'case': result['name'], 'fold': j,
                                  **{k: v for k, v in row.items() if k != 'slot_colors'}})
            if result['name'] in ('repeat-30-symbolic-erase-0.3-seed-17', 'repeat-13-phase-half-T100-base'):
                examples.append(result)
        print(f'Checked {base["name"]}: 8 variants, four holdouts each', flush=True)
    table(out/'summary.csv', summaries)
    table(out/'candidates.csv', candidates)
    table(out/'holdouts.csv', folds)
    write_json(out/'indexed-inputs.json', inputs)
    illustration(out/'evidence.png', examples)
    assert hashes == {name: digest(ROOT/name) for name in SOURCES}
    report = {'scope': 'Known synthetic indices and oracle colors; no image extraction or photo recovery',
              'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'pillow': pillow_version},
              'command': {'cwd': str(ROOT), 'argv': [sys.executable, *sys.argv]},
              'sources': hashes, 'historical_report_sha256': digest(args.visibility.resolve()/'report.json'),
              'original_R023_report': digest(args.visibility.resolve()/'report.json') == HISTORICAL_REPORT,
              'historical_source_revision': BASELINE,
              'historical_sources_verified': len(history['sources']),
              'historical_artifacts_verified': len(history['artifacts']),
              'palette_mapping': {'0': 'red', '1': 'yellow', '2': 'black', 'null': 'unknown, not a color'},
              'policy': {'candidate_domain': '1..floor(N/2), at least two repeats in benchmark',
                         'closure': 'Independent exact synthetic N mod L flag; never use provisional photo count',
                         'holdouts': 'Four contiguous quarters, training candidates frozen before evaluation',
                         'completion_enumeration': 'At most four unknown slots; larger families retained symbolically',
                         'photo_guidance': 'R035 shortest repeat <400; not applied to synthetic domain'},
              'case_count': len(summaries), 'holdout_count': len(summaries)*4,
              'summary': summaries,
              'artifacts': {str(p.relative_to(out)): digest(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    write_json(out/'report.json', report)
    (out/'report.sha256').write_text(digest(out/'report.json') + '  report.json\n')
    print(f'Report: {out}/report.json; sha256 {digest(out/"report.json")}', flush=True)


if __name__ == '__main__':
    main()
