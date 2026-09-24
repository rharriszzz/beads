#!/usr/bin/env python3
"""Reproducible image-only transect review; annotations are assistant estimates."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from skimage.color import rgb2hsv
import width_correction as wc

ROOT = Path(__file__).resolve().parents[1]
# Locations selected to cover heights, both sides, bends and the return loop.
TARGETS = [('A', 'top left', (1150, 310)), ('B', 'top right', (1620, 295)),
           ('C', 'upper left slope', (575, 600)), ('D', 'left upper bend', (240, 1050)),
           ('E', 'left lower bend', (260, 1350)), ('F', 'middle return', (1120, 1510)),
           ('G', 'lower loop left', (945, 2480)), ('H', 'lower loop shadow', (1010, 2710)),
           ('I', 'bottom left', (1370, 2990)), ('J', 'bottom right', (1700, 2970)),
           ('K', 'right middle', (2280, 1800)), ('L', 'upper right', (2060, 860))]


def interval_distance(value, interval):
    """Distance outside an inclusive visual interval, not error against truth."""
    lo, hi = interval
    if not np.isfinite([value, lo, hi]).all() or lo > hi:
        raise ValueError('Expected finite value and ordered interval')
    return float(max(lo-value, value-hi, 0.))


def assess(items):
    edge_scores = {'original': [], 'corrected': []}
    center_scores = {'original': [], 'corrected': []}
    anchors = []
    for item in items:
        review = item['review']
        outer, inner = review['outer_interval_px'], review['inner_interval_px']
        review['width_interval_px'] = [inner[0]-outer[1], inner[1]-outer[0]]
        review['midpoint_interval_px'] = [(inner[0]+outer[0])/2, (inner[1]+outer[1])/2]
        item['outside_visual_interval_px'] = {}
        for kind in edge_scores:
            scores = {side: interval_distance(item[kind][side], review[side+'_interval_px'])
                      for side in ['inner', 'outer']}
            scores['center'] = interval_distance(item[kind]['center'], review['midpoint_interval_px'])
            item['outside_visual_interval_px'][kind] = scores
            edge_scores[kind].extend([scores['inner'], scores['outer']])
            center_scores[kind].append(scores['center'])
        for side in ['inner', 'outer']:
            if item['clear'][side]:
                anchors.append(dict(id=item['id'], side=side,
                                    outside_px=item['outside_visual_interval_px']['original'][side]))
    summary = {}
    for kind in edge_scores:
        edge = np.array(edge_scores[kind]); center = np.array(center_scores[kind])
        summary[kind] = dict(edge_count=len(edge), edges_inside=int((edge == 0).sum()),
                             edges_within_2px=int((edge <= 2).sum()),
                             mean_edge_distance_outside_px=float(edge.mean()),
                             max_edge_distance_outside_px=float(edge.max()),
                             centers_inside=int((center == 0).sum()),
                             mean_center_distance_outside_px=float(center.mean()))
    summary['clear_anchors'] = anchors
    summary['interpretation'] = ('Compatibility with subjective assistant intervals at 12 selected transects; '
                                 'not true error, a random sample, or statistical validation. '
                                 'Midpoints are silhouette midpoints, not calibrated physical axes.')
    return summary


def geometry():
    source = json.loads((ROOT/'photo2/boundary-splines-source.json').read_text())
    binding = json.loads((ROOT/'photo2/centerline.json').read_text())
    if (wc.digest(ROOT/'beads-photo-2.jpg') != binding['image_sha256'] or
            wc.digest(ROOT/'photo2/boundary-splines-source.json') != binding['source_sha256']):
        raise ValueError('Image or source geometry does not match provenance')
    rgb = np.asarray(Image.open(ROOT/'beads-photo-2.jpg').convert('RGB'))
    xy, n, _, _ = wc.resample(source['centerline_spline'], 600)
    hits = {k: wc.normal_hits(xy, n, source[k+'_spline']) for k in ['inner', 'outer']}
    edges = {k: xy+n*hits[k][:, None] for k in hits}
    width = np.linalg.norm(edges['inner']-edges['outer'], axis=1)
    direction = (edges['inner']-edges['outer'])/width[:, None]
    tangent = np.column_stack([direction[:, 1], -direction[:, 0]])
    hsv = rgb2hsv(rgb)
    q = {k: wc.edge_quality(hsv, edges[k], n*np.sign(hits[k])[:, None], tangent) for k in hits}
    clear = {k: (q[k]['ratio'] >= wc.PARAMETERS['clear_ratio']) & q[k]['paper_ok'] for k in hits}
    shadow = {k: (q[k]['ratio'] < wc.PARAMETERS['deep_shadow_ratio']) & q[k]['paper_ok'] for k in hits}
    expected, fit = wc.fit_width(xy[:, 1], width, clear['inner'] & clear['outer'], rgb.shape[0])
    ni, no, nc, *_ = wc.constrain(xy, edges['inner'], edges['outer'], width, expected,
                                 fit['residual_band_px'][1], clear['inner'], clear['outer'], shadow['inner'], shadow['outer'])
    return rgb, xy, direction, tangent, edges, {'inner': ni, 'outer': no, 'center': nc}, clear, fit


def strip_image(rgb, center, direction, tangent):
    # Pixel centers span -90..90 normal and -28..28 tangent, 4x bilinear display.
    u = np.arange(-360, 361)/4
    v = np.arange(-112, 113)/4
    points = center+u[None, :, None]*direction+v[:, None, None]*tangent
    values = np.stack([map_coordinates(rgb[..., c].astype(float), points.reshape(-1, 2).T[::-1],
                                      order=1, mode='constant', cval=255) for c in range(3)], axis=1)
    return Image.fromarray(np.clip(np.rint(values.reshape(len(v), len(u), 3)), 0, 255).astype('uint8'))


def draw_sheet(items, rgb, annotated=False):
    canvas = Image.new('RGB', (805, 335*len(items)+60), 'white')
    draw = ImageDraw.Draw(canvas)
    draw.text((15, 10), 'Outer side at left; inner side at right. Offsets in original pixels.', font=wc.font(17), fill='black')
    subtitle = ('White: visual bounds; orange: original; cyan: corrected. Read at side ticks.' if annotated
                else 'Read the horizontal midpoint; side ticks mark it. No geometry on raw panels.')
    draw.text((15, 33), subtitle, font=wc.font(16), fill='black')
    for row, item in enumerate(items):
        y = 65+row*335
        draw.text((15, y), f"{item['id']}: {item['location']}  image ({item['center_xy'][0]:.0f}, {item['center_xy'][1]:.0f})", font=wc.font(18), fill='black')
        top = y+55
        canvas.paste(strip_image(rgb, np.array(item['center_xy']), np.array(item['direction']), np.array(item['tangent'])), (42, top))
        for u in range(-80, 81, 10):
            x = 42+360+4*u
            draw.line((x, top-7, x, top), fill='black')
            draw.text((x-13, top-27), str(u), font=wc.font(14), fill='black')
        draw.line((25, top+112, 41, top+112), fill='black', width=2)
        draw.line((764, top+112, 780, top+112), fill='black', width=2)
        if annotated and 'review' in item:
            for side in ['outer', 'inner']:
                lo, hi = item['review'][side+'_interval_px']
                for off in [lo, hi]:
                    x = 402+4*off
                    draw.line((x, top+94, x, top+130), fill='white', width=2)
                for kind, color in [('original', '#ffb000'), ('corrected', '#00ffff')]:
                    x = 402+4*item[kind][side]
                    draw.line((x, top+83, x, top+141), fill='black', width=5)
                    draw.line((x, top+83, x, top+141), fill=color, width=2)
            draw.text((42, top+232), 'White: visual interval; orange: original; cyan: width correction', font=wc.font(16), fill='black')
    return canvas


def review_html(output, items):
    parts = ['<!doctype html><meta charset="utf-8"><title>Transect boundary review</title>',
             '<style>body{font:17px system-ui;max-width:1100px;margin:2em auto;padding:0 1em}img{max-width:100%;height:auto}td,th{border:1px solid #ccc;padding:.4em}table{border-collapse:collapse}</style>',
             '<h1>Photo 2: direct boundary review</h1>',
             '<p>Twelve preselected locations. White brackets show assistant visual estimates from raw image strips, recorded before reading predicted offsets. The reviewer knew earlier whole-image results; these are not blind human ground truth. Original-photo pixels are used throughout.</p>',
             '<p>Orange: saved edge. Cyan: width-constrained edge. Coincident lines appear cyan. Examine the horizontal midpoint, marked by side ticks; bead scallops above and below it can differ.</p>',
             '<img src="locations.png" alt="Twelve labeled transect locations">']
    for i in range(1, 4):
        parts.append(f'<h2>Transects {"ABCD EFGH IJKL".split()[i-1]}</h2><details open><summary>Raw image: no predicted boundary</summary><img src="raw-{i}.png" alt="Raw transects group {i}"></details><details><summary>Compare with original and corrected edges</summary><img src="comparison-{i}.png" alt="Compared transects group {i}"></details>')
    parts.append('<h2>Distances outside visual intervals</h2><p>Zero means compatible with the marked interval, not a proven exact fit. These brackets describe local visible bead edges, while the saved curves are smooth outlines.</p><table><tr><th>Location</th><th>Visual width range</th><th>Original outer / inner</th><th>Corrected outer / inner</th><th>Visual observation</th></tr>')
    for item in items:
        scores = item['outside_visual_interval_px']; width = item['review']['width_interval_px']
        pairs = [f'{scores[k]["outer"]:.1f} / {scores[k]["inner"]:.1f}' for k in ['original', 'corrected']]
        parts.append(f'<tr><td>{item["id"]}: {html.escape(item["location"])}</td><td>{width[0]:.0f}–{width[1]:.0f}</td><td>{pairs[0]}</td><td>{pairs[1]}</td><td>{html.escape(item["review"]["note"])}</td></tr>')
    parts.append('</table><p>The width correction improves several shadow-side edges but does not establish that every clear anchor is accurate. The original geometry remains the default. A direct edge-evidence term with uncertainty on both sides is needed before adoption.</p>')
    (output/'review.html').write_text('\n'.join(parts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--annotations', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rgb, xy, direction, tangent, edges, corrected, clear, fit = geometry()
    items = []
    for label, location, target in TARGETS:
        j = int(np.argmin(np.linalg.norm(xy-np.array(target), axis=1)))
        project = lambda p: float(np.dot(p-xy[j], direction[j]))
        items.append(dict(id=label, location=location, sample=j, center_xy=xy[j].tolist(),
                          direction=direction[j].tolist(), tangent=tangent[j].tolist(),
                          original={k: project(edges[k][j]) for k in edges} | {'center': 0.},
                          corrected={k: project(corrected[k][j]) for k in corrected},
                          clear={k: bool(clear[k][j]) for k in clear}))
    annotations = json.loads(args.annotations.read_text()) if args.annotations else None
    if annotations:
        if annotations['photo_sha256'] != wc.digest(ROOT/'beads-photo-2.jpg'):
            raise ValueError('Annotations refer to a different photograph')
        if set(annotations['transects']) != {item['id'] for item in items}:
            raise ValueError('Annotation and transect IDs differ')
        for item in items:
            item['review'] = annotations['transects'][item['id']]
        summary = assess(items)
    for start in range(0, len(items), 4):
        draw_sheet(items[start:start+4], rgb).save(args.output/f'raw-{start//4+1}.png')
        if annotations:
            draw_sheet(items[start:start+4], rgb, True).save(args.output/f'comparison-{start//4+1}.png')
    overview = Image.fromarray(rgb)
    d = ImageDraw.Draw(overview)
    for item in items:
        c = np.array(item['center_xy']); n = np.array(item['direction'])
        d.line([tuple(c-90*n), tuple(c+90*n)], fill='white', width=3)
        x, y = c+115*n
        d.ellipse((x-24,y-24,x+24,y+24), fill='white', outline='black', width=2)
        d.text((x-12, y-18), item['id'], font=wc.font(29), fill='black')
    overview.thumbnail((800, 1100)); overview.save(args.output/'locations.png')
    if annotations:
        for name, expected in annotations['raw_artifact_sha256'].items():
            if wc.digest(args.output/name) != expected:
                raise ValueError('Raw transects changed since visual annotation: '+name)
        review_html(args.output, items)
    sources = [Path(__file__).resolve(), ROOT/'photo2/test_transect_review.py', ROOT/'photo2/width_correction.py', ROOT/'photo2/boundary-splines-source.json', ROOT/'photo2/centerline.json', ROOT/'beads-photo-2.jpg']
    if args.annotations: sources.append(args.annotations.resolve())
    report = dict(command=[sys.executable, *sys.argv], sources={str(p.relative_to(ROOT)): wc.digest(p) for p in sources},
                  sampling='12 preselected locations; normal offsets -90..90, tangent -28..28; 4x bilinear display; visual review at tangent 0',
                  fit=fit, transects=items)
    if annotations:
        report['summary'] = summary
    report['artifacts'] = {p.name: wc.digest(p) for p in sorted(args.output.iterdir())
                           if p.suffix in ['.png', '.html']}
    wc.write_json(args.output/'report.json', report)

if __name__ == '__main__':
    main()
