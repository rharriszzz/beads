#!/usr/bin/env python3
"""Frozen JPEG-only boundary/scale diagnostic for beads5 observation 188."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import beads5_inventory as b5
import blind_generated as bg

ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / 'photo2/beads5-188-r080.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def partition(mask, seam_xy, lower_y, shift=0):
    """Divide existing pixels only; no identity or sliver ownership implied."""
    yy, xx = np.indices(mask.shape)
    seam = np.asarray(seam_xy)
    boundary = np.interp(yy, seam[:, 1], seam[:, 0]) + shift
    lower = mask & (yy >= lower_y)
    side = mask & ~lower & (xx < boundary)
    central = mask & ~lower & ~side
    return central, side, lower


def sample_profile(rgb, center, axis, t, offsets):
    axis = np.asarray(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    normal = np.array([-axis[1], axis[0]])
    xy = (np.asarray(center)[None, None, :] + t[None, :, None] * axis
          + np.asarray(offsets)[:, None, None] * normal)
    return np.stack([ndi.map_coordinates(rgb[:, :, k].astype(float),
                    [xy[:, :, 1], xy[:, :, 0]], order=1, mode='nearest')
                     for k in range(3)], axis=-1)


def trough_measure(t, value):
    """Descriptive local trough depth, not a boundary acceptance score."""
    window = np.flatnonzero(np.abs(t) <= 2)
    index = window[np.argmin(value[window])]
    left, right = np.interp([-5, 5], t, value)
    return dict(trough_offset_px=float(t[index]), trough_v=float(value[index]),
                left_shoulder_v=float(left), right_shoulder_v=float(right),
                depth_below_lower_shoulder=float(min(left, right) - value[index]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(ANNOTATION.read_text())
    inventory = json.loads((ROOT / cfg['inventory']).read_text())
    baseline = json.loads((ROOT / cfg['baseline_report']).read_text())
    for name, expected in baseline['sources'].items():
        assert digest(ROOT / name) == expected, name
    rgb = np.asarray(Image.open(ROOT / cfg['image']).convert('RGB'))
    records = copy.deepcopy(inventory['active_observations'] + inventory['excluded_observations'])
    _, _, old_mask, _ = bg.detect(rgb)
    envelope = b5.envelope_mask(old_mask)
    _, _, channels = b5.color_support(rgb, envelope)
    labels = b5.segment(rgb, channels, records)
    encoded = io.BytesIO()
    np.save(encoded, labels)
    assert hashlib.sha256(encoded.getvalue()).hexdigest() == baseline['bulk_artifacts']['labels.npy']
    target = next(r for r in records if r['id'] == cfg['target_id'])
    mask = labels == target['id']
    assert int(mask.sum()) == target['region_pixels'] == 534
    references = [next(r for r in records if r['id'] == i)
                  for i in target['selection']['local_reference_ids']]
    median = float(np.median([r['region_pixels'] for r in references]))
    reference_sensitivity = []
    for omitted in references:
        reduced_median = float(np.median([r['region_pixels'] for r in references
                                          if r['id'] != omitted['id']]))
        reference_sensitivity.append(dict(omitted_id=omitted['id'], median_area_px=reduced_median,
                                          target_ratio=int(mask.sum()) / reduced_median))
    nominal = partition(mask, cfg['side_seam_xy'], cfg['lower_cut_y'])
    variants = []
    for dx in cfg['seam_shift_px']:
        for dy in cfg['lower_cut_shift_px']:
            parts = partition(mask, cfg['side_seam_xy'], cfg['lower_cut_y'] + dy, dx)
            assert np.array_equal(sum(p.astype(int) for p in parts), mask.astype(int))
            areas = {name: int(p.sum()) for name, p in zip(['central', 'side', 'lower'], parts)}
            variants.append(dict(side_shift_px=dx, lower_shift_px=dy, areas=areas,
                                 area_ratios={k: v / median for k, v in areas.items()}))
    t = np.arange(-cfg['profile_half_length_px'], cfg['profile_half_length_px'] + .01,
                  cfg['sample_step_px'])
    profile_rows, metrics, plot_data = [], [], {}
    for sigma in cfg['gaussian_sigmas_px']:
        source = ndi.gaussian_filter(rgb.astype(float), (sigma, sigma, 0)) if sigma else rgb
        for profile in cfg['profiles']:
            sampled = sample_profile(source, profile['center_xy'], profile['axis_xy'], t,
                                     cfg['parallel_offsets_px'])
            values = sampled.max(axis=2)
            med = np.median(values, axis=0)
            individual = [trough_measure(t, row) for row in values]
            metrics.append(dict(name=profile['name'], sigma_px=sigma,
                                median_trace=trough_measure(t, med),
                                parallel_trace_depths=[r['depth_below_lower_shoulder'] for r in individual]))
            plot_data[profile['name'], sigma] = (values, med)
            for j, offset in enumerate(cfg['parallel_offsets_px']):
                for i, position in enumerate(t):
                    profile_rows.append([profile['name'], sigma, offset, float(position),
                                         *sampled[j, i].tolist(), float(values[j, i]), float(med[i])])
    with (args.output / 'profiles.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['profile', 'sigma_px', 'parallel_offset_px', 'distance_px',
                         'R', 'G', 'B', 'V_max_RGB', 'parallel_median_V'])
        writer.writerows(profile_rows)

    box = cfg['crop_xyxy']
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax in axes:
        ax.imshow(rgb, interpolation='nearest')
        ax.set(xlim=(box[0], box[2]), ylim=(box[3], box[1]), xlabel='JPEG x', ylabel='JPEG y')
    axes[0].set_title('JPEG: unmodified pixels')
    axes[1].contour(mask, levels=[.5], colors=['cyan'], linewidths=1)
    for r in [target, *references]:
        x, y = r['marker_xy']
        axes[1].plot(x, y, '+', color='yellow', markersize=5)
        axes[1].text(x+1, y, str(r['id']), color='yellow', fontsize=8, clip_on=True)
    axes[1].set_title('R077 mask: 534 pixels; ratio 2.008')
    overlay = np.zeros((*mask.shape, 4))
    for part, color in zip(nominal, [(0, 1, 1), (1, .6, 0), (1, 0, 1)]):
        overlay[part] = [*color, .5]
    axes[2].imshow(overlay, interpolation='nearest')
    seam = np.asarray(cfg['side_seam_xy'])
    axes[2].plot(seam[:, 0], seam[:, 1], '--', color='yellow', linewidth=1)
    axes[2].plot([661, 679], [cfg['lower_cut_y']]*2, '--', color='yellow', linewidth=1)
    axes[2].set_title('Diagnostic cuts only; no bead identities\n' +
                      ' / '.join(f'{color} {int(part.sum())}' for color, part in
                                 zip(['cyan', 'orange', 'magenta'], nominal)) + ' pixels')
    fig.suptitle('beads5 188: retain uncertainty; neither cut is a recovered boundary')
    fig.tight_layout()
    fig.savefig(args.output / 'boundary-comparison.png', dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    ax = axes[0, 0]
    ax.imshow(rgb, interpolation='nearest')
    ax.set(xlim=(650, 687), ylim=(255, 209), title='Fixed JPEG-selected transects')
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    for profile, color in zip(cfg['profiles'], colors):
        center, axis = np.asarray(profile['center_xy']), np.asarray(profile['axis_xy'])
        endpoints = center + np.array([-7, 7])[:, None] * axis
        ax.plot(endpoints[:, 0], endpoints[:, 1], color=color, label=profile['name'])
    ax.legend(fontsize=7)
    for ax, profile, color in zip(axes.flat[1:5], cfg['profiles'], colors):
        values, med = plot_data[profile['name'], 0]
        ax.fill_between(t, values.min(axis=0), values.max(axis=0), alpha=.2, color=color,
                        label='five-trace range, raw JPEG')
        ax.plot(t, med, color=color, label='raw median')
        for sigma, style in [(.8, '--'), (1.2, ':')]:
            ax.plot(t, plot_data[profile['name'], sigma][1], style, label=f'sigma {sigma} median')
        ax.axvspan(-2, 2, alpha=.08, color='black')
        ax.set(title=profile['name'], xlabel='distance from proposed seam (px)', ylabel='V = max RGB (0–255)')
        ax.legend(fontsize=7)
        ax.grid(alpha=.2)
    axes[1, 2].axis('off')
    axes[1, 2].text(0, .95, 'Bilinear samples every 0.25 px\nParallel offsets: -2, -1, 0, 1, 2 px\n\nShaded strip: trough search ±2 px\nShoulder samples: -5 and +5 px\nDepth = lower shoulder minus trough\n\nBrightness valleys can be surface shading.\nThey do not establish body counts.\nNo new resolution is created by sampling.', va='top')
    fig.tight_layout()
    fig.savefig(args.output / 'profiles.png', dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].bar([str(r['id']) for r in references] + ['188'],
                [r['region_pixels'] for r in references] + [534], color=['gray']*8 + ['purple'])
    axes[0].axhline(median, color='black', label=f'local median {median:g}')
    axes[0].axhline(2*median, color='red', linestyle='--', label='twice median')
    axes[0].set(xlabel='R077 reference observation IDs and target', ylabel='mask pixels', title='Frozen neighborhood scale')
    axes[0].legend(fontsize=8)
    for i, (name, part, color) in enumerate(zip(['central', 'side', 'lower'], nominal,
                                              ['cyan', 'orange', 'magenta'])):
        values = [v['areas'][name] for v in variants]
        axes[1].bar(i, int(part.sum()), color=color)
        axes[1].errorbar(i, int(part.sum()), yerr=[[int(part.sum())-min(values)],
                                                [max(values)-int(part.sum())]], color='black', capsize=5)
    axes[1].axhline(.5*median, color='red', linestyle='--', label='half median (comparison only)')
    axes[1].axhline(median, color='black', label='local median')
    axes[1].set(xticks=[0, 1, 2], xticklabels=['central', 'side', 'lower'], ylabel='mask pixels',
                title='25 cuts: side and lower shifts ±2 px')
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(args.output / 'area-sensitivity.png', dpi=150)
    plt.close(fig)

    measurements = dict(target=target, references=references, local_median_area_px=median,
                        leave_one_reference_out=reference_sensitivity,
                        nominal_areas={k: int(p.sum()) for k, p in zip(['central', 'side', 'lower'], nominal)},
                        partition_sensitivity=variants, profile_measurements=metrics,
                        decision='retain_unresolved_mask_without_inventory_change',
                        hypotheses=[
                            'One substantial central body with uncertain narrow visible portions included in its mask.',
                            'Two adjacent upper body portions separated by the side seam; lower extension remains uncertain.'],
                        limitations=['Not an exhaustive hypothesis set or a calibrated bead-count test.',
                                     'Cuts are visual annotations; no physical centers, ownership or chain indices inferred.',
                                     'Brightness seams can be caused by shading; nearby masks are provisional.',
                                     'No active region is split, removed or expanded. R069 remains unchanged.'])
    (args.output / 'diagnostics.json').write_text(json.dumps(measurements, indent=2)+'\n')
    (args.output / 'review.html').write_text('''<!doctype html><meta charset="utf-8">
<title>beads5 188 boundary diagnostic</title>
<style>body{font:17px system-ui;max-width:1400px;margin:2em auto;padding:0 1em}img{max-width:100%}</style>
<h1>beads5 188: retain the unresolved mask</h1>
<p>The side seam supports adjacent visible portions, but their count and usable body boundaries remain uncertain.
The 328-observation active inventory is unchanged. Cuts below are measurements only.</p>
<img src="boundary-comparison.png" alt="Raw JPEG, saved mask and diagnostic cuts">
<img src="profiles.png" alt="Brightness transects and placement/smoothing sensitivity">
<img src="area-sensitivity.png" alt="Nearby mask areas and diagnostic cut sensitivity">
<p><a href="../../BEADS5_188_DIAGNOSTIC.md">Method and decision</a> ·
<a href="diagnostics.json">Measurements</a> · <a href="profiles.csv">Profile samples</a> ·
<a href="report.json">Hashes and parameters</a></p>
<p>No new maker question. Saved sliver guidance remains applied; older photo questions remain pending.</p>
''')
    sources = set(baseline['sources']) | {str(ANNOTATION.relative_to(ROOT)), cfg['inventory'],
                                       cfg['baseline_report'], str(Path(__file__).resolve().relative_to(ROOT)),
                                       'photo2/test_beads5_188_diagnostic.py'}
    report = dict(command=[sys.executable, *sys.argv], parameters=cfg,
                  sources={p: digest(ROOT / p) for p in sorted(sources)},
                  checks=dict(baseline_sources_verified=True, regenerated_labels_match_R077=True,
                              partition_conserves_pixels_all_25_cuts=True, active_inventory_unchanged=True),
                  environment=dict(python=sys.version, numpy=np.__version__, scipy=bg.scipy.__version__,
                                   matplotlib=matplotlib.__version__),
                  artifacts={p.name: digest(p) for p in sorted(args.output.iterdir()) if p.name != 'report.json'})
    (args.output / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(nominal=measurements['nominal_areas'], profiles=metrics), indent=2))


if __name__ == '__main__':
    main()
