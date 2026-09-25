#!/usr/bin/env python3
"""R081: audit frozen active masks by omitting each saved area reference once."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import html
import json
from pathlib import Path
import statistics
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from inventory_selection import select_records

ROOT = Path(__file__).resolve().parents[1]
ROUNDS = [69, 70, 71, 76, 77, 78, 79]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def area_state(ratio, params):
    if ratio < params['minimum_area_ratio']:
        return 'small'
    if ratio > params['large_area_warning_ratio']:
        return 'large'
    return 'ordinary'


def omission_audit(area, reference_ids, reference_areas, params):
    """No replacement neighbors or cascading exclusions; invalid trials stay null."""
    if len(reference_ids) != len(reference_areas) or len(set(reference_ids)) != len(reference_ids):
        raise ValueError('Reference IDs/areas must be paired and unique')
    if area <= 0 or any(a <= 0 for a in reference_areas):
        raise ValueError('Areas must be positive')
    minimum = params['minimum_neighbors']
    median = statistics.median(reference_areas) if len(reference_areas) >= minimum else None
    ratio = area / median if median is not None else None
    nominal = area_state(ratio, params) if ratio is not None else 'insufficient'
    trials = []
    for i, ref in enumerate(reference_ids):
        remaining = reference_areas[:i] + reference_areas[i+1:]
        med = statistics.median(remaining) if len(remaining) >= minimum else None
        r = area / med if med is not None else None
        trials.append(dict(omitted_id=ref, median_area_px=med, ratio=r,
                           state=area_state(r, params) if r is not None else 'insufficient'))
    states = {nominal, *(t['state'] for t in trials)}
    if 'insufficient' in states:
        category = 'insufficient_reference'
    elif len(states) > 1:
        category = 'threshold_sensitive'
    elif nominal != 'ordinary':
        category = 'persistent_' + nominal
    else:
        category = 'stable_ordinary'
    ratios = [t['ratio'] for t in trials if t['ratio'] is not None]
    return dict(nominal_median_area_px=median, nominal_ratio=ratio,
                nominal_state=nominal, category=category,
                omission_ratio_min=min(ratios) if ratios else None,
                omission_ratio_max=max(ratios) if ratios else None,
                omission_state_counts=dict(Counter(t['state'] for t in trials)),
                trials=trials)


def audit_inventory(inventory, params):
    active = inventory['active_observations']
    records = active + inventory['excluded_observations']
    by_id = {r['id']: r for r in records}
    if len(by_id) != len(records):
        raise ValueError('Duplicate image-scoped IDs')
    # Reconstruct selection to catch stale neighbor lists, medians or decisions.
    # Distance-to-silhouette only changes the small-exclusion reason suffix.
    replay_active, replay_excluded = select_records(records, np.zeros((600, 800)), params)
    replay = {r['id']: r for r in replay_active + replay_excluded}
    for row in records:
        saved, computed = row['selection'], replay[row['id']]['selection']
        for key in ['active', 'warnings', 'local_reference_ids', 'local_median_area_px', 'area_ratio']:
            if saved[key] != computed[key]:
                raise ValueError(f'Selection replay mismatch: {row["id"]} / {key}')
    result = []
    for row in active:
        if row['bead_index'] is not None:
            raise ValueError('Audit expects unindexed observations')
        refs = row['selection']['local_reference_ids']
        ref_rows = [by_id[i] for i in refs]
        areas = [r['region_pixels'] for r in ref_rows]
        result.append(dict(id=row['id'], marker_xy=row['marker_xy'], color=row['color'],
                           region_pixels=row['region_pixels'], reference_ids=refs,
                           reference_areas_px=areas,
                           area_excluded_reference_ids=[r['id'] for r in ref_rows if not r['selection']['active']],
                           **omission_audit(row['region_pixels'], refs, areas, params)))
    return result


def figures(queue, output):
    colors = {'threshold_sensitive': '#bc6800', 'persistent_large': '#a52323',
              'persistent_small': '#a52323', 'insufficient_reference': '#666666'}
    fig, ax = plt.subplots(figsize=(10, max(3, .34*len(queue)+1.5)))
    for y, row in enumerate(queue):
        color = colors[row['category']]
        if row['omission_ratio_min'] is not None:
            ax.plot([row['omission_ratio_min'], row['omission_ratio_max']], [y, y], color=color, lw=3)
        if row['nominal_ratio'] is not None:
            ax.plot(row['nominal_ratio'], y, 'o', color=color, ms=5)
    ax.set_yticks(range(len(queue)), [f"{r['image']} / {r['id']}" for r in queue])
    for value in [.5, 2]:
        ax.axvline(value, color='black', ls='--', lw=1)
    ax.invert_yaxis()
    ax.set_xlabel('Mask area / local reference median (dot: original; line: omission range)')
    ax.set_title('Frozen active observations: reference-sensitive or persistent warnings\nOrange: threshold-sensitive; red: persistent large; no selection changes')
    ax.grid(axis='x', alpha=.2)
    fig.tight_layout()
    fig.savefig(output/'ratio-ranges.png', dpi=150)
    plt.close(fig)
    for start in range(0, len(queue), 12):
        group = queue[start:start+12]
        fig, axes = plt.subplots((len(group)+3)//4, 4, figsize=(12, 3*((len(group)+3)//4)), squeeze=False)
        for ax in axes.flat:
            ax.set_axis_off()
        for ax, row in zip(axes.flat, group):
            rgb = np.asarray(Image.open(ROOT/f"{row['image']}.jpg").convert('RGB'))
            x, y = row['marker_xy']
            ax.imshow(rgb)
            ax.set_xlim(x-28, x+28)
            ax.set_ylim(y+28, y-28)
            ax.plot(x, y, '+', color='cyan', ms=12, mew=1)
            for ref in row['reference_markers']:
                rx, ry = ref['xy']
                if abs(rx-x) <= 26 and abs(ry-y) <= 26:
                    ax.text(rx, ry, str(ref['id']), color='yellow', fontsize=7,
                            bbox=dict(facecolor='black', alpha=.5, pad=.5), clip_on=True)
            lo, hi = row['omission_ratio_min'], row['omission_ratio_max']
            interval = f'{lo:.3f}–{hi:.3f}' if lo is not None else 'insufficient'
            ax.set_title(f"{row['image']} / {row['id']}: {row['color']}\n{row['category'].replace('_', ' ')}\nomission ratio {interval}", fontsize=9)
        fig.suptitle('JPEG context only; cyan target, yellow nearby saved references\nMasks and body identities remain provisional', fontsize=12)
        fig.tight_layout(rect=(0, 0, 1, .94))
        fig.savefig(output/f'queue-context-{start//12+1}.png', dpi=150)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sources = [Path(__file__), ROOT/'photo2/test_area_warning_stability.py',
               ROOT/'photo2/inventory_selection.py', ROOT/'photo2/blind_generated.py']
    images, queue = [], []
    for n, round_id in enumerate(ROUNDS, 1):
        image = f'beads{n}'
        folder = ROOT/f'photo2/review/r{round_id:03}'
        inv_path, rep_path = folder/'inventory.json', folder/'report.json'
        report = json.loads(rep_path.read_text())
        if digest(inv_path) != report['artifacts']['inventory.json']:
            raise ValueError(f'{image}: inventory hash mismatch')
        jpeg = ROOT/f'{image}.jpg'
        if digest(jpeg) != report['sources'][jpeg.name]:
            raise ValueError(f'{image}: JPEG hash mismatch')
        inventory = json.loads(inv_path.read_text())
        params = report['parameters'] if n == 1 else report['selection_parameters']
        audited = audit_inventory(inventory, params)
        by_id = {r['id']: r for r in inventory['active_observations'] + inventory['excluded_observations']}
        for row in audited:
            if row['category'] != 'stable_ordinary':
                queue.append(dict(image=image, **row, reference_markers=[
                    dict(id=i, xy=by_id[i]['marker_xy']) for i in row['reference_ids']]))
        images.append(dict(image=image, source_inventory=str(inv_path.relative_to(ROOT)),
                           parameters=params, active_count=len(audited),
                           categories=dict(Counter(r['category'] for r in audited)),
                           observations_with_excluded_references=sum(bool(r['area_excluded_reference_ids']) for r in audited),
                           observations=audited))
        sources.extend([inv_path, rep_path, jpeg])
    summary = [{k: v for k, v in d.items() if k != 'observations'} for d in images]
    write_json(args.output/'audit.json', dict(images=summary, queue=queue))
    with (args.output/'all-observations.csv').open('w', newline='') as f:
        fields = ['image', 'id', 'region_pixels', 'category', 'nominal_state', 'nominal_ratio',
                  'omission_ratio_min', 'omission_ratio_max', 'reference_ids', 'reference_areas_px',
                  'area_excluded_reference_ids', 'omission_state_counts']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        for d in images:
            for row in d['observations']:
                writer.writerow(dict(image=d['image'], **{k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()}))
    with (args.output/'review-queue.csv').open('w', newline='') as f:
        fields = ['image', 'id', 'color', 'region_pixels', 'category', 'nominal_state',
                  'nominal_ratio', 'omission_ratio_min', 'omission_ratio_max']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(queue)
    figures(queue, args.output)
    parts = ['<!doctype html><meta charset="utf-8"><title>Area warning stability</title>',
             '<style>body{font:17px system-ui;max-width:1250px;margin:2em auto}img{max-width:100%}td,th{padding:.4em;text-align:left}table{border-collapse:collapse}tr{border-bottom:1px solid #ddd}</style>',
             '<h1>Seven frozen inventories: area warning stability</h1>',
             '<p>Only active observations are targets. Original reference pools include later area-excluded candidates. Omit one saved reference at a time without replacement; minimum four references, small &lt;0.5, large &gt;2. Equality is ordinary. This is a sensitivity audit, not a confidence interval or completeness test. No mask, selection or body decision changes.</p>',
             '<p><a href="audit.json">Queue omission trials and image summaries</a> · <a href="all-observations.csv">All active observations</a> · <a href="review-queue.csv">Queue CSV</a> · <a href="report.json">Source hashes</a></p>',
             '<img src="ratio-ranges.png" alt="Original and omission area ratios">',
             '<table><tr><th>Image / ID</th><th>Category</th><th>Original ratio</th><th>Omission range</th><th>Trial states</th></tr>']
    def formatted(value):
        return f'{value:.6f}' if value is not None else 'unavailable'
    for r in queue:
        parts.append(f'<tr><td>{r["image"]} / {r["id"]}</td><td>{r["category"]}</td><td>{formatted(r["nominal_ratio"])}</td><td>{formatted(r["omission_ratio_min"])}–{formatted(r["omission_ratio_max"])}</td><td>{html.escape(str(r["omission_state_counts"]))}</td></tr>')
    parts.append('</table>')
    for p in sorted(args.output.glob('queue-context-*.png')):
        parts.append(f'<img src="{p.name}" alt="Image-scoped queue JPEG contexts">')
    parts.append('<p>Beads3 122/405 and beads5 188 remain unresolved even if a numerical warning changes. Same-color borders, pale/shadow separation, colors, beads7 manual glint repairs and inventory completeness remain provisional. No new maker questions; saved R069 sliver exclusions still apply.</p>')
    (args.output/'review.html').write_text('\n'.join(parts)+'\n')
    summary = [dict(image=d['image'], active_count=d['active_count'], categories=d['categories'],
                    observations_with_excluded_references=d['observations_with_excluded_references']) for d in images]
    write_json(args.output/'report.json', dict(command=[sys.executable, *sys.argv],
               summary=summary, checks=dict(inventory_and_jpeg_hashes_verified=True,
               all_original_selection_replayed=True, all_active_chain_indices_null=True),
               environment=dict(python=sys.version, numpy=np.__version__, matplotlib=matplotlib.__version__),
               sources={str(p.relative_to(ROOT)): digest(p) for p in sources},
               artifacts={p.name: digest(p) for p in sorted(args.output.iterdir()) if p.name != 'report.json'}))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
