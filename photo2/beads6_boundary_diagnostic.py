#!/usr/bin/env python3
"""JPEG-only diagnostic of frozen beads6 masks 144 and 189 (R082)."""
from __future__ import annotations
import argparse
import copy
import csv
import io
import json
from pathlib import Path
import sys
import hashlib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import beads6_inventory as b6
import blind_generated as bg
from beads5_188_diagnostic import digest, sample_profile, trough_measure

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'photo2/beads6-boundaries-r082.json'


def partition(mask, side_xy, lower_xy, side_shift=0, lower_shift=0):
    """Partition saved pixels for scale diagnostics only; never alter labels."""
    yy, xx = np.indices(mask.shape)
    lower_xy = np.asarray(lower_xy)
    lower = mask & (yy >= np.interp(xx, lower_xy[:, 0], lower_xy[:, 1]) + lower_shift)
    parts = {'upper': mask & ~lower, 'lower': lower}
    if side_xy is not None:
        side_xy = np.asarray(side_xy)
        side = parts['upper'] & (xx < np.interp(yy, side_xy[:, 1], side_xy[:, 0]) + side_shift)
        parts = {'central': parts['upper'] & ~side, 'side': side, 'lower': lower}
    assert np.array_equal(sum(p.astype(int) for p in parts.values()), mask.astype(int))
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(CONFIG.read_text())
    baseline = json.loads((ROOT / cfg['baseline_report']).read_text())
    inventory = json.loads((ROOT / cfg['inventory']).read_text())
    for path, expected in baseline['sources'].items():
        assert digest(ROOT / path) == expected, path
    assert digest(ROOT / cfg['inventory']) == baseline['artifacts']['inventory.json']
    rgb = np.asarray(Image.open(ROOT / cfg['image']).convert('RGB'))
    records = copy.deepcopy(inventory['active_observations'] + inventory['excluded_observations'])
    saved = {r['id']: r for r in records}
    _, _, base, _ = bg.detect(rgb)
    _, _, channels = b6.color_support(rgb, b6.envelope_mask(base))
    labels = b6.segment(rgb, channels, records)
    buf = io.BytesIO()
    np.save(buf, labels)
    label_hash = hashlib.sha256(buf.getvalue()).hexdigest()
    assert label_hash == baseline['bulk_artifacts']['labels.npy']
    assert len(inventory['active_observations']) == 310
    assert all(r['bead_index'] is None for r in records)
    t = np.arange(-cfg['profile_half_length_px'], cfg['profile_half_length_px'] + .01,
                  cfg['sample_step_px'])
    smoothed = {s: ndi.gaussian_filter(rgb.astype(float), (s, s, 0)) if s else rgb.astype(float)
                for s in cfg['gaussian_sigmas_px']}
    measurements, samples = [], []
    fig, axes = plt.subplots(2, 3, figsize=(13, 10))
    profile_fig, profile_axes = plt.subplots(2, 3, figsize=(15, 8))
    area_fig, area_axes = plt.subplots(2, 2, figsize=(12, 8))
    for row, target_cfg in enumerate(cfg['targets']):
        id = target_cfg['id']
        target = saved[id]
        mask = labels == id
        assert int(mask.sum()) == target['region_pixels']
        refs = [saved[i] for i in target['selection']['local_reference_ids']]
        areas = [r['region_pixels'] for r in refs]
        median = float(np.median(areas))
        assert median == target['selection']['local_median_area_px']
        trials = []
        for i, ref in enumerate(refs):
            local = float(np.median(areas[:i] + areas[i+1:]))
            trials.append(dict(omitted_id=ref['id'], median_px=local, ratio=target['region_pixels']/local))
        nominal = partition(mask, target_cfg['side_seam_xy'], target_cfg['lower_seam_xy'])
        variants = []
        for side_shift in cfg['shifts_px'] if target_cfg['side_seam_xy'] else [0]:
            for lower_shift in cfg['shifts_px']:
                parts = partition(mask, target_cfg['side_seam_xy'], target_cfg['lower_seam_xy'], side_shift, lower_shift)
                variants.append(dict(side_shift_px=side_shift, lower_shift_px=lower_shift,
                                     areas={name: int(p.sum()) for name, p in parts.items()}))
        box = target_cfg['crop_xyxy']
        for col, title in enumerate(['Raw JPEG', 'Frozen R078 mask', 'Exploratory cuts and profiles']):
            ax = axes[row, col]
            ax.imshow(rgb, interpolation='nearest')
            ax.set(xlim=(box[0],box[2]), ylim=(box[3],box[1]), title=f'{id}: {title}')
            if col:
                ax.contour(mask, levels=[.5], colors=['cyan'], linewidths=.8)
                x, y = target['marker_xy']
                ax.plot(x, y, '+', color='cyan')
            if col == 2:
                for seam in ('side_seam_xy', 'lower_seam_xy'):
                    if target_cfg[seam] is not None:
                        xy = np.asarray(target_cfg[seam])
                        ax.plot(xy[:,0], xy[:,1], '--', color='yellow', lw=1)
                for k, profile in enumerate(target_cfg['profiles']):
                    center, axis = np.asarray(profile['center_xy']), np.asarray(profile['axis_xy'])
                    ends = center[None,:] + np.array([-7,7])[:,None]*axis
                    ax.plot(ends[:,0], ends[:,1], color=f'C{k+1}', lw=.8)
                    ax.text(*ends[0], str(k+1), color='white', fontsize=8)
        metrics = []
        for col, profile in enumerate(target_cfg['profiles']):
            ax = profile_axes[row, col]
            for sigma in cfg['gaussian_sigmas_px']:
                sampled = sample_profile(smoothed[sigma], profile['center_xy'], profile['axis_xy'], t, cfg['parallel_offsets_px'])
                value = sampled.max(axis=2)
                trace = np.median(value, axis=0)
                offsets_metrics = [trough_measure(t, v) for v in value]
                metrics.append(dict(name=profile['name'], sigma_px=sigma,
                                    median_trace=trough_measure(t, trace), parallel_traces=offsets_metrics))
                for offset, rgb_trace in zip(cfg['parallel_offsets_px'], sampled):
                    for distance, pixel in zip(t, rgb_trace):
                        samples.append([id, profile['name'], sigma, offset, distance, *pixel, max(pixel)])
                if sigma == 0:
                    ax.fill_between(t, value.min(axis=0), value.max(axis=0), color='gray', alpha=.2, label='raw offset range')
                ax.plot(t, trace, label=f'sigma {sigma:g}')
            ax.axvspan(-2, 2, alpha=.06, color='black')
            ax.set(title=f'{id} / {col+1}: {profile["name"]}', xlabel='distance from annotated seam (px)', ylabel='V = max RGB (0–255)')
            ax.grid(alpha=.2)
            ax.legend(fontsize=7)
        ax = area_axes[row, 0]
        ax.bar([str(r['id']) for r in refs]+[str(id)], areas+[target['region_pixels']], color=['gray']*8+['teal'])
        ax.axhline(median, color='black', label=f'median {median:g}')
        ax.axhline(2*median, color='red', linestyle='--', label='twice median')
        ax.set(title=f'{id}: original reference masks', ylabel='pixels', xlabel='image-scoped observation IDs')
        ax.legend(fontsize=8)
        ax = area_axes[row, 1]
        for k, (name, part) in enumerate(nominal.items()):
            n = int(part.sum())
            values = [v['areas'][name] for v in variants]
            ax.bar(k, n, color=['teal','orange','purple'][k])
            ax.errorbar(k, n, yerr=[[n-min(values)],[max(values)-n]], color='black', capsize=5)
        ax.axhline(.5*median, color='red', linestyle='--', label='half median (comparison only)')
        ax.axhline(median, color='black', label='local median')
        ax.set(title=f'{id}: {len(variants)} cuts shifted ±2 px', ylabel='saved pixels', xticks=range(len(nominal)), xticklabels=list(nominal))
        ax.legend(fontsize=8)
        measurements.append(dict(target=target, references=refs, local_median_area_px=median,
                                 leave_one_reference_out=trials,
                                 nominal_areas={name:int(p.sum()) for name,p in nominal.items()},
                                 partition_sensitivity=variants, profile_measurements=metrics,
                                 hypotheses=target_cfg['hypotheses'], decision='retain_unresolved_without_inventory_change'))
    for figure, name in [(fig,'boundary-comparison.png'),(profile_fig,'profiles.png'),(area_fig,'area-sensitivity.png')]:
        figure.tight_layout()
        figure.savefig(args.output/name, dpi=150)
        plt.close(figure)
    with (args.output/'profiles.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['target_id','profile','sigma_px','parallel_offset_px','distance_px','red','green','blue','value'])
        writer.writerows(samples)
    (args.output/'diagnostics.json').write_text(json.dumps(dict(targets=measurements, limitations=[
        'Cuts are exploratory JPEG annotations, not validated boundaries or body counts.',
        'Reference masks are provisional; leave-one-out ranges are not confidence intervals.',
        'Valleys can reflect shading; sampling does not add resolution.',
        'No mask, selection, ID, sliver ownership or chain index changed.']), indent=2)+'\n')
    (args.output/'review.html').write_text('''<!doctype html><meta charset="utf-8">
<title>beads6 144/189 boundary diagnostic</title>
<style>body{font:17px system-ui;max-width:1500px;margin:2em auto;padding:0 1em}img{max-width:100%}</style>
<h1>beads6 144/189: retain unresolved mask extents</h1>
<p>310 active observations remain unchanged. Cyan is the frozen mask; yellow cuts and numbered profiles are exploratory measurements. No portion receives a new identity.</p>
<img src="boundary-comparison.png" alt="Raw JPEG, frozen masks, cuts and numbered profiles">
<img src="profiles.png" alt="Boundary profiles with placement and smoothing sensitivity">
<img src="area-sensitivity.png" alt="Frozen references and diagnostic portion area ranges">
<p><a href="../../BEADS6_BOUNDARY_DIAGNOSTIC.md">Assessment and reproduction</a> ·
<a href="diagnostics.json">Measurements</a> · <a href="profiles.csv">RGB samples</a> · <a href="report.json">Hashes and parameters</a></p>
<p>No new maker questions; saved sliver guidance remains applied. Older photo questions remain pending.</p>
''')
    sources = set(baseline['sources']) | {cfg['inventory'], cfg['baseline_report'],
        str(CONFIG.relative_to(ROOT)), 'photo2/beads6_boundary_diagnostic.py',
        'photo2/test_beads6_boundary_diagnostic.py', 'photo2/beads5_188_diagnostic.py',
        'photo2/beads5_inventory.py', 'photo2/test_beads5_188_diagnostic.py'}
    report = dict(command=[sys.executable,*sys.argv], parameters=cfg,
                  sources={p:digest(ROOT/p) for p in sorted(sources)},
                  checks=dict(baseline_sources_verified=True, inventory_hash_verified=True,
                              regenerated_labels_match_R078=label_hash, all_partitions_conserve_pixels=True,
                              active_count=310, chain_indices_null=True, profile_sample_rows=len(samples)),
                  environment=dict(python=sys.version, numpy=np.__version__, scipy=bg.scipy.__version__, matplotlib=matplotlib.__version__),
                  artifacts={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.name!='report.json'})
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    for m in measurements:
        print(m['target']['id'], m['nominal_areas'])
        print({name:[min(v['areas'][name] for v in m['partition_sensitivity']),max(v['areas'][name] for v in m['partition_sensitivity'])] for name in m['nominal_areas']})
        print([(p['name'],p['sigma_px'],round(p['median_trace']['depth_below_lower_shoulder'],2),p['median_trace']['trough_offset_px']) for p in m['profile_measurements']])


if __name__ == '__main__':
    main()
