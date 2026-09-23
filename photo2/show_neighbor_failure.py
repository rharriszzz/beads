#!/usr/bin/env python3
"""Create an exact SVG evidence diagram of one saved R039 inference failure."""
from __future__ import annotations

import argparse
import base64
import ctypes
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STEM = 'repeat-40-h+1-phase-0-t12-s17'
VIEW = 'repeat-40-h+1-phase-0'


def rasterize(svg, png):
    """Render the vector evidence diagram using installed librsvg and Cairo."""
    rsvg = ctypes.CDLL('librsvg-2.so.2')
    cairo = ctypes.CDLL('libcairo.so.2')
    gobject = ctypes.CDLL('libgobject-2.0.so.0')
    pointer = ctypes.c_void_p
    rsvg.rsvg_handle_new_from_file.argtypes = [ctypes.c_char_p, pointer]
    rsvg.rsvg_handle_new_from_file.restype = pointer
    rsvg.rsvg_handle_render_cairo.argtypes = [pointer, pointer]
    rsvg.rsvg_handle_render_cairo.restype = ctypes.c_int
    cairo.cairo_image_surface_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    cairo.cairo_image_surface_create.restype = pointer
    cairo.cairo_create.argtypes = [pointer]
    cairo.cairo_create.restype = pointer
    cairo.cairo_surface_write_to_png.argtypes = [pointer, ctypes.c_char_p]
    cairo.cairo_surface_write_to_png.restype = ctypes.c_int
    cairo.cairo_destroy.argtypes = [pointer]
    cairo.cairo_surface_destroy.argtypes = [pointer]
    gobject.g_object_unref.argtypes = [pointer]
    handle = rsvg.rsvg_handle_new_from_file(str(svg).encode(), None)
    assert handle, svg
    surface = cairo.cairo_image_surface_create(0, 1600, 1030)
    context = cairo.cairo_create(surface)
    try:
        assert rsvg.rsvg_handle_render_cairo(handle, context)
        assert cairo.cairo_surface_write_to_png(surface, str(png).encode()) == 0
    finally:
        cairo.cairo_destroy(context)
        cairo.cairo_surface_destroy(surface)
        gobject.g_object_unref(handle)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/neighbor-failure')
    args = parser.parse_args()
    audit = ROOT/'photo2/output/inference-audit-verified'
    render = ROOT/'photo2/output/neighbor-audit-final'
    paths = {kind: audit/f'{STEM}-{kind}.json' for kind in ('input', 'truth', 'shape')}
    beauty = render/f'{VIEW}-beauty.png'
    # Verify saved inputs against their recorded manifests before illustrating them.
    for directory, files in ((audit, list(paths.values())), (render, [beauty])):
        manifest = json.loads((directory/'report.json').read_text())['artifacts']
        for path in files:
            assert digest(path) == manifest[path.name], path
    data = {kind: json.loads(path.read_text()) for kind, path in paths.items()}
    truth = data['truth']['source_indices']
    xy = data['input']['centroids']
    lookup = {n: xy[truth.index(n)] for n in (611, 612, 613)}
    evaluation = data['shape']['evaluation'][0]
    failures = [edge for edge in evaluation['edge_truth']
                if [truth[edge[0]], truth[edge[1]]] == [611, 613]]
    assert len(failures) == 1 and failures[0][2:] == [7, 2], failures
    variant = data['shape']['inference']['variants'][0]
    assert variant['convention'] == 1
    assert failures[0][:3] in variant['edges']
    assert Image.open(beauty).size == (2400, 1800)
    args.output.mkdir(parents=True, exist_ok=True)
    encoded = base64.b64encode(beauty.read_bytes()).decode('ascii')
    # Embed the original bytes once. All marks are separate vector elements;
    # the whole render and inset use the same unmodified image and coordinates.
    left, top, width, height = 1000, 1290, 250, 280
    full_box = (20+left*.43, 95+top*.43, width*.43, height*.43)
    a, b, c = (lookup[n] for n in (611, 612, 613))
    markers = ''.join(
        f'<circle cx="{p[0]}" cy="{p[1]}" r="7" fill="none" stroke="#00ffff" stroke-width="2"/>'
        f'<text x="{p[0]+9}" y="{p[1]-8}" font-size="11" fill="white" '
        f'stroke="black" stroke-width="2" paint-order="stroke">{n}</text>'
        for n, p in lookup.items())
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600" height="1030" viewBox="0 0 1600 1030">
<defs><image id="original" width="2400" height="1800" xlink:href="data:image/png;base64,{encoded}"/></defs>
<rect width="1600" height="1030" fill="white"/>
<g font-family="sans-serif" fill="#181818">
<text x="20" y="37" font-size="28">A concrete algorithm failure — synthetic render, not photo 2</text>
<text x="20" y="70" font-size="20">Rectangle locates the detail. The original render is embedded unchanged.</text>
<use xlink:href="#original" transform="translate(20 95) scale(.43)"/>
<rect x="{full_box[0]}" y="{full_box[1]}" width="{full_box[2]}" height="{full_box[3]}" fill="none" stroke="#00aaaa" stroke-width="4"/>
<text x="1100" y="112" font-size="22">Detail: true source indices</text>
<text x="1100" y="138" font-size="17">Circles: visible-mask centroids, not body centers.</text>
<svg x="1100" y="145" width="475" height="532" viewBox="{left} {top} {width} {height}">
<use xlink:href="#original"/>
<polyline points="{a[0]},{a[1]} {b[0]},{b[1]} {c[0]},{c[1]}" fill="none" stroke="#00ffff" stroke-width="2" stroke-dasharray="4 3"/>
<line x1="{a[0]}" y1="{a[1]}" x2="{c[0]}" y2="{c[1]}" stroke="#ff00ff" stroke-width="3"/>
{markers}
</svg>
<text x="1100" y="712" font-size="20" fill="#a000a0">Magenta: inferred 611 → 613 as +7.</text>
<text x="1100" y="745" font-size="20">Actual difference: +2. Wrong pair.</text>
<text x="1100" y="790" font-size="20" fill="#007777">Cyan dashes: 611 → 612 → 613.</text>
<text x="1100" y="823" font-size="20">Each true step is +1.</text>
<text x="20" y="922" font-size="22">The third bead (612) is visible. This is a failure of the local inference rule, not proof of visual ambiguity.</text>
<text x="20" y="957" font-size="19">R039 saved shape rule · T12 · seed 17 · convention +1 · source indices used only to explain the error afterward.</text>
<text x="20" y="990" font-size="19">No new indexing, rendering, segmentation or photo fit. Pixel coordinates and source hashes are in report.json.</text>
</g></svg>'''
    target = args.output/'whole-image-failure.svg'
    target.write_text(svg)
    png = target.with_suffix('.png')
    rasterize(target, png)
    report = dict(
        command='.venv/bin/python photo2/show_neighbor_failure.py',
        source_hashes={str(p.relative_to(ROOT)): digest(p) for p in
                       [Path(__file__), *paths.values(), beauty,
                        audit/'report.json', render/'report.json']},
        view=VIEW, threshold=12, seed=17, convention=1,
        selected_source_indices=[611, 613], predicted_difference=7,
        actual_difference=2, visible_intermediate_source_index=612,
        mask_centroids=lookup, crop_box=[left, top, left+width, top+height],
        selection='Post-hoc illustrative wrong pair with visibly supported endpoints; not an accuracy trial.',
        limitation='Synthetic baseline error; no claim of human ambiguity or photo-2 indexing.',
        artifacts={p.name: digest(p) for p in (target, png)})
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(target)


if __name__ == '__main__':
    main()
