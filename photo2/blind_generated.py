#!/usr/bin/env python3
"""Image-only bead candidates in the seven existing generated JPEGs.

No POV-Ray source, layout, saved pattern, ID pass, or old audit is imported.
Candidate masks and highlight locations are observations, not verified beads.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
import skimage
from skimage.color import rgb2hsv
from skimage.feature import peak_local_max
from skimage.filters import sobel
from skimage.morphology import disk
from skimage.segmentation import watershed, find_boundaries

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = dict(dark_channel=190, closing_radius=4, fill_holes_below=300,
                  smooth_sigma=1.25, contrast_sigma=4., min_distance=5,
                  minimum_value=.22, minimum_contrast=.025,
                  interior_margin=2., small_region_pixels=25,
                  watershed_compactness=.002)
# Assistant's palette names from viewing the JPEGs, not renderer definitions.
PALETTES = {
    1: ['red', 'green', 'blue'],
    2: ['orange', 'yellow', 'violet', 'lavender'],
    3: ['red', 'black', 'white'],
    4: ['red', 'yellow', 'green', 'cyan', 'white'],
    5: ['purple', 'gray', 'white'],
    6: ['red', 'blue-gray', 'white'],
    7: ['red', 'green', 'black', 'silver', 'white'],
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def detect(rgb, *, spacing=5, contrast_threshold=.025):
    hsv = rgb2hsv(rgb)
    value = hsv[..., 2]
    dark = rgb.min(axis=2) < PARAMETERS['dark_channel']
    mask = ndi.binary_closing(dark, structure=disk(PARAMETERS['closing_radius']))
    components, _ = ndi.label(mask)
    sizes = np.bincount(components.ravel())
    sizes[0] = 0
    if not sizes.any():
        return np.zeros(mask.shape, np.int32), np.empty((0, 2), int), mask, hsv
    mask = components == sizes.argmax()
    components, _ = ndi.label(~mask)
    sizes = np.bincount(components.ravel())
    small_holes = sizes < PARAMETERS['fill_holes_below']
    # Never fill a background component that reaches the raster boundary.
    boundary = np.unique(np.r_[components[0], components[-1], components[:, 0], components[:, -1]])
    small_holes[boundary] = False
    mask |= small_holes[components]
    smooth = ndi.gaussian_filter(value, PARAMETERS['smooth_sigma'])
    contrast = smooth - ndi.gaussian_filter(value, PARAMETERS['contrast_sigma'])
    peaks = peak_local_max(smooth, min_distance=spacing,
                           threshold_abs=PARAMETERS['minimum_value'],
                           exclude_border=False, labels=mask.astype(np.uint8))
    peaks = peaks[contrast[tuple(peaks.T)] > contrast_threshold]
    peaks = peaks[np.lexsort((peaks[:, 1], peaks[:, 0]))]
    seeds = np.zeros(mask.shape, np.int32)
    if len(peaks):
        seeds[tuple(peaks.T)] = np.arange(1, len(peaks) + 1)
    smooth_rgb = ndi.gaussian_filter(rgb.astype(float)/255., (1., 1., 0.))
    gradient = np.max([sobel(smooth_rgb[..., c]) for c in range(3)], axis=0)
    labels = watershed(-smooth + .3*gradient, seeds, mask=mask,
                       compactness=PARAMETERS['watershed_compactness']).astype(np.int32)
    return labels, peaks[:, ::-1], mask, hsv


def color_name(hsv, case):
    """Conservative image-palette classification; highlights are excluded upstream."""
    if not len(hsv):
        return 'unknown', None
    h, s, v = np.median(hsv, axis=0)
    # Circular red hue: use sine/cosine mean only for sufficiently saturated pixels.
    saturated = hsv[:, 1] > .20
    if saturated.mean() > .50:
        a = hsv[saturated, 0]*2*np.pi
        h = np.arctan2(np.sin(a).mean(), np.cos(a).mean())/(2*np.pi) % 1
    if case == 3:
        name = 'red' if s > .35 and (h < .08 or h > .94) else ('black' if v < .40 else 'white')
    elif case == 5:
        name = 'purple' if s > .13 else ('gray' if v < .62 else 'white')
    elif case == 6:
        name = 'red' if s > .45 and (h < .08 or h > .94) else ('blue-gray' if s > .13 else 'white')
    elif case == 7:
        name = ('black' if v < .30 else 'red' if s > .5 and (h < .07 or h > .94)
                else 'green' if .20 < h < .47 and s > .2
                else 'silver' if .43 < h < .60 and s > .065 else 'white')
    elif case == 2:
        name = ('violet' if .65 < h < .88 and s > .45 else 'orange' if .035 < h < .105 and s > .4
                else 'yellow' if .105 <= h < .22 and s > .3 else 'lavender')
    else:
        if s < .25:
            name = 'white' if case == 4 else 'unknown'
        elif h < .08 or h > .94:
            name = 'red'
        elif h < .22:
            name = 'yellow'
        elif h < .47:
            name = 'green'
        elif h < .59:
            name = 'cyan'
        elif h < .78:
            name = 'blue'
        else:
            name = 'unknown'
    if name not in PALETTES[case]:
        name = 'unknown'
    return name, [float(h), float(s), float(v)]


def observations(rgb, labels, xy, mask, hsv, case):
    margin = ndi.distance_transform_edt(mask)
    boxes = ndi.find_objects(labels)
    rows = []
    for label, (x, y) in enumerate(xy, 1):
        sy, sx = boxes[label-1]
        ys, xs = np.nonzero(labels[sy, sx] == label)
        xs, ys = xs+sx.start, ys+sy.start
        values = hsv[ys, xs]
        # Use pixels near the marker; broad watershed regions may merge beads.
        distance = np.hypot(xs-x, ys-y)
        selected = ((distance >= 2) & (distance <= 7) &
                    ((values[:, 1] > .2) | (values[:, 2] < .92)))
        color, med = color_name(values[selected], case)
        if selected.sum() < 4:
            color, med = 'unknown', None
        flags = []
        if margin[y, x] <= PARAMETERS['interior_margin']:
            flags.append('silhouette_or_shadow_candidate')
        if len(xs) < PARAMETERS['small_region_pixels']:
            flags.append('small_fragment')
        rows.append(dict(observation_id=label, marker_xy=[int(x), int(y)],
                         marker_kind='brightness_peak_not_body_center',
                         bbox_xyxy=[sx.start, sy.start, sx.stop, sy.stop],
                         visible_centroid_xy=[float(xs.mean()), float(ys.mean())],
                         candidate_region_pixels=len(xs), color=color,
                         color_sample_pixels=int(selected.sum()), sample_hsv=med,
                         flags=flags, verified_bead=False, bead_index=None))
    return rows


def font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)


def draw(rgb, labels, rows, output, case):
    image = Image.fromarray(rgb).resize((1600, 1200))
    d = ImageDraw.Draw(image)
    for row in rows:
        x, y = np.asarray(row['marker_xy'])*2
        color = '#ff9900' if row['flags'] else '#e000e0'
        d.ellipse((x-4, y-4, x+4, y+4), outline=color, width=2)
        d.text((x+4, y-9), str(row['observation_id']), font=font(10), fill='black', stroke_width=1, stroke_fill='white')
    d.rectangle((0, 0, 1600, 38), fill='white')
    d.text((12, 7), f'beads{case}.jpg — {len(rows)} candidates; magenta=interior, orange=flagged; IDs are not chain indices', font=font(18), fill='black')
    image.save(output / f'beads{case}-observations.png')
    boundary = find_boundaries(labels, mode='inner')
    overlay = rgb.copy(); overlay[boundary] = [255, 0, 255]
    Image.fromarray(overlay).save(output / f'beads{case}-regions.png')


def gallery(output, reports):
    parts = ['<!doctype html><meta charset="utf-8"><title>Blind generated-image bead observations</title>',
             '<style>body{font:17px system-ui;margin:2em;max-width:1200px}svg{width:100%;border:1px solid #aaa}.mark{fill:none;stroke:#df00df;stroke-width:1}.flag{stroke:#f90} .mark:hover{stroke:#000;stroke-width:3} summary{cursor:pointer} code{white-space:pre-wrap}</style>',
             '<h1>Seven generated images: bead candidates</h1><p>Image-only observations. These are not verified bead counts or recovered patterns. Hover over a marker for its record. Orange marks need extra caution. Turn labels on to locate an observation in the JSON.</p>',
             '<label><input type="checkbox" onchange="document.querySelectorAll(\'.id\').forEach(x=>x.style.display=this.checked?\'block\':\'none\')"> Show observation IDs</label>']
    for report in reports:
        case=report['case']; encoded=base64.b64encode((ROOT/f'beads{case}.jpg').read_bytes()).decode()
        parts += [f'<h2>beads{case}.jpg</h2><p>{report["candidate_count"]} candidates; {report["flagged_count"]} flagged. Pattern: unresolved.</p>',
                  f'<svg viewBox="0 0 800 600"><image href="data:image/jpeg;base64,{encoded}" width="800" height="600"/>']
        for row in report['observations']:
            x,y=row['marker_xy']; title=f'ID {row["observation_id"]}; {row["color"]}; {row["candidate_region_pixels"]} pixels; {", ".join(row["flags"]) or "unverified interior candidate"}'
            parts.append(f'<circle class="mark {"flag" if row["flags"] else ""}" cx="{x}" cy="{y}" r="3"><title>{title}</title></circle><text class="id" style="display:none;font-size:7px;paint-order:stroke;stroke:white;stroke-width:1px" x="{x+3}" y="{y-3}">{row["observation_id"]}</text>')
        parts.append('</svg>')
    (output/'index.html').write_text('\n'.join(parts))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/blind-generated')
    args=parser.parse_args(); output=args.output; output.mkdir(parents=True,exist_ok=True)
    reports=[]
    for case in range(1,8):
        path=ROOT/f'beads{case}.jpg'; rgb=np.array(Image.open(path).convert('RGB'))
        labels, xy, mask, hsv=detect(rgb)
        rows=observations(rgb,labels,xy,mask,hsv,case)
        sensitivity=[]
        for spacing, threshold in [(6,.025),(5,.04)]:
            alternate, peaks, _, _=detect(rgb,spacing=spacing,contrast_threshold=threshold)
            sensitivity.append(dict(spacing=spacing,contrast=threshold,candidates=len(peaks)))
        report=dict(case=case,input=path.name,input_sha256=digest(path),dimensions=list(rgb.shape[1::-1]),
                    candidate_count=len(rows),flagged_count=sum(bool(r['flags']) for r in rows),
                    interior_unflagged_count=sum(not r['flags'] for r in rows),
                    candidate_colors=dict(Counter(r['color'] for r in rows)),
                    sensitivity=sensitivity,observations=rows,
                    all_visible_beads_identified=False,pattern_status='unresolved')
        reports.append(report); write_json(output/f'beads{case}-observations.json',report)
        np.save(output/f'beads{case}-labels.npy',labels)
        draw(rgb,labels,rows,output,case)
        print(f'{path.name}: {len(rows)} candidates, {report["flagged_count"]} flagged',flush=True)
    gallery(output,reports)
    report=dict(command=[sys.executable,*sys.argv],parameters=PARAMETERS,palettes=PALETTES,
                sources={'photo2/blind_generated.py':digest(Path(__file__))},
                input_policy='Only beads1.jpg through beads7.jpg; no POV source/patterns, layouts, truth masks or other reports',
                palette_policy='Names and HSV boxes from assistant visual inspection; not unsupervised palette recovery',
                environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,skimage=skimage.__version__),
                results=[{k:v for k,v in r.items() if k!='observations'} for r in reports],
                artifacts={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file() and p.name!='report.json'},
                limitations=['No independent per-bead truth available under blind protocol.',
                             'Highlights can be missing, duplicated or confused with background.',
                             'Watershed can split beads or join neighbors/shadows.',
                             'Silhouette/sliver completeness and chain indices remain unverified.',
                             'Candidate colors are not a recovered stringing pattern.'])
    write_json(output/'report.json',report)


if __name__=='__main__':
    main()
