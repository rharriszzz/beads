#!/usr/bin/env python3
"""Illustrated oracle-edge audit of both legacy helicities, not image inference."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import platform
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, __version__ as pillow_version

from legacy_visibility import (HEIGHT, PHASES, THRESHOLDS, WIDTH, decode, font,
                               instrument_source, measure, render, wrapper)
from neighbor_graph import OFFSETS, propagate, reciprocal
from practice_legacy import ROOT, digest

HERE = ROOT / 'photo2'
BASELINE = 'ab7915841577c27cfb03f779cc765e556ffc9dcd'


def projected_centers(layout, width=WIDTH, height=HEIGHT):
    """POV perspective camera: default sky +y, right length 1.33, angle 10.

    Pixel coordinates use integer pixel centers, as do measured ID centroids.
    """
    camera = np.array([50., -600., 500.])
    forward = -camera / np.linalg.norm(camera)
    # POV uses a left-handed camera: default direction +z, right +x, sky +y.
    right = np.cross([0., 1., 0.], forward)
    right /= np.linalg.norm(right)
    up = np.cross(forward, right)
    relative = layout[:, 4:7] - camera
    scale = width / (2*np.tan(np.deg2rad(5))) / (relative @ forward)
    return np.column_stack((width/2-.5 + scale*(relative @ right),
                            height/2-.5 - scale*(1.33*height/width)*(relative @ up)))


def evaluate_graph(indices, count, seed, *, ring):
    """Evaluator supplies topology; solver receives anonymous vertices/offsets only."""
    indices = sorted(map(int, indices))
    anonymous = np.random.Generator(np.random.PCG64(seed)).permutation(len(indices))
    mapping = dict(zip(indices, map(int, anonymous)))
    truth = {v: i for i, v in mapping.items()}
    forward = []
    missing = []
    for i in indices:
        for d in OFFSETS:
            j = (i+d) % count if ring else i+d
            if j not in mapping:
                missing.append([mapping[i], d])
            elif d > 0:
                forward.append((mapping[i], mapping[j], d))
    edges = reciprocal(forward)
    vertices = list(range(len(indices)))
    result = propagate(vertices, edges, modulus=count if ring else None)
    errors = []
    for component in result['components']:
        origin = truth[component['seed']]
        for vertex in component['vertices']:
            error = result['labels'][vertex] - (truth[vertex]-origin)
            if ring:
                error %= count
            if error:
                errors.append([vertex, error])
    assert result['consistent'] and not errors
    # Cycles +1,+6,-7 independently counted in evaluator topology.
    triangles = sum((i+1) % count in mapping and (i+7) % count in mapping
                    for i in indices) if ring else sum(i+1 in mapping and i+7 in mapping
                                                      for i in indices)
    return {'seed': seed, 'ring': ring,
            'input': {'vertices': vertices, 'edges': edges,
                      'modulus': count if ring else None},
            'evaluation_only_source_indices': truth, 'result': result,
            'missing_neighbor_directions': missing,
            'summary': {'vertices': len(vertices), 'undirected_edges': len(forward),
                        'components': len(result['components']),
                        'component_sizes': sorted((len(c['vertices']) for c in result['components']),
                                                  reverse=True),
                        'edges_by_positive_offset': dict(Counter(d for _, _, d in forward)),
                        'independent_cycles': len(forward)-len(vertices)+len(result['components']),
                        'triangles_1_6_7': int(triangles),
                        'winding_directed_edges': len(result['winding_edges']),
                        'relative_index_errors': errors,
                        'missing_directed_neighbors': len(missing)}}


def controls():
    fixtures = {
        'triangle': ([0, 1, 2], [(0, 1, 1), (1, 2, 6), (0, 2, 7)], None, True),
        'contradiction': ([0, 1, 2], [(0, 1, 1), (1, 2, 6), (0, 2, 6)], None, False),
        'missing_edge_alternate_path': ([0, 1, 2], [(0, 1, 1), (1, 2, 6)], None, True),
        'disconnected': ([0, 1, 2, 3], [(0, 1, 1), (2, 3, 7)], None, True),
        'duplicate_constraints': ([0, 1], [(0, 1, 1), (0, 1, 6)], None, False),
        'duplicate_indices': ([0, 1, 2], [(0, 1, 1), (0, 2, 1)], None, False),
        'wrong_bridge': ([0, 1, 2, 3], [(0, 1, 1), (2, 3, 6), (1, 2, 6)], None, True),
        'ring_winding': (list(range(20)), [(i, (i+1) % 20, 1) for i in range(20)], 20, True),
        'ring_lifted_without_cut': (list(range(20)), [(i, (i+1) % 20, 1) for i in range(20)], None, False),
    }
    report = {}
    for name, (vertices, edges, modulus, expected) in fixtures.items():
        result = propagate(vertices, reciprocal(edges), modulus)
        assert result['consistent'] == expected
        report[name] = {'input_edges': reciprocal(edges), 'result': result}
    report['wrong_bridge']['evaluation_only_true_indices'] = [0, 1, 20, 26]
    report['wrong_bridge']['limitation'] = 'Consistent but wrong: inferred 0,1,7,13; true 0,1,20,26.'
    assert list(report['wrong_bridge']['result']['labels'].values()) == [0, 1, 7, 13]
    return report


def draw_styled_line(draw, start, end, color, offset):
    start, end = np.asarray(start), np.asarray(end)
    length = np.linalg.norm(end-start)
    if offset == 1:
        draw.line((*start, *end), fill=color, width=4)
    elif length:
        step, stroke = (18, 11) if offset == 6 else (9, 2)
        for distance in np.arange(0, length, step):
            a = start+(end-start)*distance/length
            b = start+(end-start)*min(distance+stroke, length)/length
            draw.line((*a, *b), fill=color, width=4)
    # Arrow at the destination gives the direction of the signed label.
    if length:
        unit = (end-start)/length
        normal = np.array([-unit[1], unit[0]])
        a, b = end-unit*12+normal*5, end-unit*12-normal*5
        draw.polygon([tuple(end), tuple(a), tuple(b)], fill=color)


def draw_patch(out, name, beauty, layout, view, index, reason, threshold=12):
    xy = projected_centers(layout)
    count = len(layout)
    neighbors = [(d, (index+d) % count) for d in OFFSETS]
    targets = [index] + [j for _, j in neighbors]
    low = np.floor(xy[targets].min(axis=0)-40).astype(int)
    high = np.ceil(xy[targets].max(axis=0)+40).astype(int)
    center = (low+high)/2
    side = int(max(200, *(high-low)))
    left, top = np.floor(center-side/2).astype(int)
    box = (int(left), int(top), int(left+side), int(top+side))
    panel = Image.new('RGB', (1560, 920), 'white')
    crop = Image.open(beauty).convert('RGB').crop(box).resize((700, 700), Image.Resampling.NEAREST)
    panel.paste(crop, (20, 115))
    panel.paste(crop, (790, 115))
    draw = ImageDraw.Draw(panel)
    draw.text((20, 10), f'{name}: {reason}, source bead #{index}', font=font(25), fill='black')
    draw.text((20, 47), 'Known topology only. +/-1: solid red; +/-6: dashed cyan; +/-7: dotted purple.',
              font=font(21), fill='black')
    draw.text((20, 80), 'Beauty / same crop', font=font(21), fill='black')
    draw.text((790, 80), f'Projected centers: circles; visible-mask centroids: crosses; T={threshold} px',
              font=font(17), fill='black')
    scale = 700/side

    def point(p):
        return np.array([790, 115]) + (np.asarray(p)-[left, top])*scale

    counts = view['pixels_per_bead']
    origin = point(xy[index])
    colors = {1: '#d52222', 6: '#007b9d', 7: '#8428ae'}
    details = []
    for d, target in neighbors:
        end = point(xy[target])
        visible = counts[index] >= threshold and counts[target] >= threshold
        color = colors[abs(d)]
        if visible:
            draw_styled_line(draw, origin, end, color, abs(d))
        draw.ellipse((*tuple(end-6), *tuple(end+6)), outline=color, width=3)
        label = f'{d:+d} / #{target}' + ('' if visible else ' missing')
        # Radial label positions keep the six short labels away from their edges.
        unit = (end-origin)/max(1., np.linalg.norm(end-origin))
        position = end+unit*25
        bounds = draw.textbbox((0, 0), label, font=font(18))
        position[0] = np.clip(position[0]-bounds[2]/2, 794, 1488-bounds[2])
        position[1] = np.clip(position[1]-10, 120, 786)
        draw.rectangle((position[0]-3, position[1]-2, position[0]+bounds[2]+3,
                        position[1]+24), fill='white')
        draw.text(tuple(position), label, fill=color, font=font(18))
        details.append({'offset': d, 'target': target, 'edge_drawn': bool(visible),
                        'visible_pixels': counts[target],
                        'projected_center': xy[target].tolist(),
                        'visible_centroid': view['visible_centroids'][target]})
    # Show centroid displacement for every selected bead with visible pixels.
    for target in targets:
        if view['visible_centroids'][target] is not None:
            a, b = point(xy[target]), point(view['visible_centroids'][target])
            draw.line((*a, *b), fill='#555555', width=2)
            draw.line((b[0]-5, b[1], b[0]+5, b[1]), fill='black', width=2)
            draw.line((b[0], b[1]-5, b[0], b[1]+5), fill='black', width=2)
    draw.ellipse((*tuple(origin-8), *tuple(origin+8)), outline='black', width=4)
    draw.text((20, 838), 'Missing edge: no arrow; an outlined endpoint shows its evaluator-known position only.',
              font=font(21), fill='black')
    draw.text((20, 875), 'Center and centroid can differ substantially under occlusion. No image-edge detector was used.',
              font=font(21), fill='black')
    filename = name+'-neighbors.png'
    panel.save(out/filename)
    return {'file': filename, 'seed_index': index, 'reason': reason, 'crop_box': box,
            'threshold': threshold, 'seed_pixels': counts[index], 'neighbors': details}


def regression(out, source, historical, commands):
    old = out/'baseline-legacy.pov'
    old.write_text(historical)
    checks = []
    for case in range(8):
        clock = str((case+.37)/8)
        before = render(out, f'default-case-{case+1}-before', old, clock, commands,
                        beauty=True, width=480, height=360)
        after = render(out, f'default-case-{case+1}-after', ROOT/'beads.pov', clock, commands,
                       beauty=True, width=480, height=360)
        np.testing.assert_array_equal(before, after)
        checks.append({'case': case+1, 'clock': clock, 'raster': [480, 360], 'pixel_equal': True})
    assert source != historical  # A regression must compare different source versions.
    return checks


def check_projection(out, source, layout, commands):
    """Render isolated world-space markers through the actual scene camera."""
    indices = [17, 200, 500]
    scene = out/'projection-markers.pov'
    camera = re.search(r'camera\s*\{[^}]+\}', source).group()
    lines = ['#version 3.7;', 'global_settings { assumed_gamma 1.0 }',
             'background { color rgb 0 }', camera]
    for code, i in enumerate(indices, 1):
        vector = ','.join(format(v, '.12f') for v in layout[i, 4:7])
        lines.append(f'sphere {{ <{vector}>, 0.2 pigment {{ color rgb <{code}/255,0,0> }} '
                     'finish { ambient 0 emission 1 diffuse 0 } }')
    scene.write_text('\n'.join(lines)+'\n')
    ids = decode(render(out, 'projection-markers', scene, '0', commands), 3)
    centroids = np.array(measure(ids, 3, 1)['visible_centroids'])
    centers = projected_centers(layout)[indices]
    error = np.linalg.norm(centroids-centers, axis=1)
    assert np.max(error) < .25, (centroids, centers, error)
    return {'indices': indices, 'projected_centers': centers.tolist(),
            'marker_centroids': centroids.tolist(), 'errors_pixels': error.tolist(),
            'tolerance_pixels': .25}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'output/neighbor-audit')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources = [ROOT/'beads.pov', ROOT/'bead-shape.inc', Path(__file__),
               HERE/'neighbor_graph.py', HERE/'test_neighbor_graph.py',
               HERE/'test_legacy_visibility.py',
               HERE/'legacy_visibility.py', HERE/'legacy-visibility-body.inc',
               HERE/'practice_legacy.py', HERE/'practice-pattern.json',
               HERE/'visibility-pattern-13.json']
    source_hashes = {str(p.relative_to(ROOT)): digest(p) for p in sources}
    source = (ROOT/'beads.pov').read_text()
    historical = subprocess.check_output(['git', 'show', f'{BASELINE}:beads.pov'], cwd=ROOT).decode()
    historical_body = subprocess.check_output(['git', 'show', f'{BASELINE}:bead-shape.inc'], cwd=ROOT)
    assert historical_body == (ROOT/'bead-shape.inc').read_bytes()
    (out/'instrumented.pov').write_text(instrument_source(source))
    (out/'baseline-instrumented.pov').write_text(instrument_source(historical))
    commands = []
    report = {'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                              'pillow': pillow_version},
              'raster': [WIDTH, HEIGHT], 'baseline_commit': BASELINE,
              'commands': commands, 'controls': controls(), 'views': {},
              'claim': 'Exact propagation with evaluator-supplied edges; no automatic edge extraction.'}
    report['default_regression'] = regression(out, source, historical, commands)
    print('Eight default legacy cases: before/after pixel equality passed.', flush=True)
    for case, filename in [('repeat-40', 'practice-pattern.json'),
                           ('repeat-13', 'visibility-pattern-13.json')]:
        pattern = json.loads((HERE/filename).read_text())
        count = len(pattern['colors'])*pattern['groups']
        positive_layouts = {}
        for hand in (1, -1):
            for phase, clock in PHASES:
                name = f'{case}-h{hand:+d}-{phase}'
                layout_path = out/f'{name}-layout.csv'
                scene = out/f'{name}.pov'
                scene.write_text(f'#declare LegacyHelicity={hand};\n'
                                 + wrapper(pattern, 'instrumented.pov', layout_path))
                ids = decode(render(out, name+'-ids', scene, clock, commands), count)
                palette = render(out, name+'-palette', scene, clock, commands, palette=True)
                mask = ids > 0
                np.testing.assert_array_equal(mask, np.any(palette != 0, axis=2))
                colors = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
                expected = colors[np.array(pattern['colors'])[(ids[mask]-1) % len(pattern['colors'])]]
                np.testing.assert_array_equal(palette[mask], expected)
                beauty_scene = out/f'{name}-beauty.pov'
                beauty_scene.write_text(f'#declare LegacyHelicity={hand};\n'+wrapper(pattern, 'beads.pov'))
                beauty = render(out, name+'-beauty', beauty_scene, clock, commands, beauty=True)
                layout = np.loadtxt(layout_path, delimiter=',')
                if 'projection_check' not in report:
                    report['projection_check'] = check_projection(out, source, layout, commands)
                nrows = int(count/6.5+.5)
                rclock = (float(clock)*.99999*8) % 1
                np.testing.assert_allclose(layout[:, 3],
                    360*(hand*np.arange(count)*nrows/count+rclock), rtol=0, atol=1e-9)
                np.testing.assert_allclose(np.diff(layout[:, 3]), hand*360*nrows/count,
                                           rtol=0, atol=1e-9)
                # Verify the exported positions independently from the scene angles.
                # Preserve the legacy expression literally: POV sin takes radians,
                # even though vaxis_rotate takes degrees. Do not correct its geometry.
                bead_radius = 4*.96*np.sin(180/6.5)
                major = .65*(2*bead_radius)*1.05*nrows/(2*np.pi)
                a, b = np.deg2rad(layout[:, 2]), np.deg2rad(layout[:, 3])
                expected_xyz = np.column_stack(((major-4*np.sin(b))*np.cos(a),
                    (major-4*np.sin(b))*np.sin(a), 4*np.cos(b)+4+2*bead_radius))
                np.testing.assert_allclose(layout[:, 4:7], expected_xyz, rtol=0, atol=1e-9)
                if hand == 1:
                    positive_layouts[phase] = layout
                    baseline_scene = out/f'{name}-baseline.pov'
                    baseline_table = out/f'{name}-baseline-layout.csv'
                    baseline_scene.write_text(wrapper(pattern, 'baseline-instrumented.pov', baseline_table))
                    before = decode(render(out, name+'-baseline-ids', baseline_scene, clock, commands), count)
                    np.testing.assert_array_equal(ids, before)
                    np.testing.assert_array_equal(layout, np.loadtxt(baseline_table, delimiter=','))
                    baseline_beauty = out/f'{name}-baseline-beauty.pov'
                    baseline_beauty.write_text(wrapper(pattern, 'baseline-legacy.pov'))
                    before_beauty = render(out, name+'-baseline-beauty', baseline_beauty, clock,
                                           commands, beauty=True)
                    np.testing.assert_array_equal(beauty, before_beauty)
                else:
                    other = positive_layouts[phase]
                    np.testing.assert_array_equal(layout[:, :3], other[:, :3])
                    np.testing.assert_allclose(layout[:, 3]+other[:, 3], 720*rclock,
                                               rtol=0, atol=1e-9)
                    assert not np.allclose(layout[:, 4:7], other[:, 4:7])
                view = measure(ids, len(pattern['colors']), pattern['groups'])
                view.update({'hand': hand, 'count': count, 'turns': nrows, 'clock': clock,
                             'layout': layout_path.name, 'palette_exact': True,
                             'positive_baseline_pixel_and_layout_equal': hand == 1,
                             'graphs': {}, 'panels': []})
                counts = np.array(view['pixels_per_bead'])
                for threshold in THRESHOLDS:
                    selected = np.flatnonzero(counts >= threshold)
                    trials = []
                    for seed in (17, 43):
                        trials.append({'region': 'ring', **evaluate_graph(selected, count, seed, ring=True)})
                        for quadrant in range(4):
                            angle = layout[selected, 2] % 360
                            patch = selected[(angle >= 90*quadrant) & (angle < 90*(quadrant+1))]
                            trials.append({'region': f'quarter-{quadrant}',
                                           **evaluate_graph(patch, count, seed, ring=False)})
                    view['graphs'][str(threshold)] = trials
                    # Relabeling may change tree winding records but never connectivity or accuracy.
                    for a_trial, b_trial in zip(trials[:5], trials[5:]):
                        for key in ('vertices', 'component_sizes', 'relative_index_errors',
                                    'undirected_edges', 'triangles_1_6_7'):
                            assert a_trial['summary'][key] == b_trial['summary'][key]
                xy = projected_centers(layout)
                # A well-visible seed nearest the right-hand screen bend.
                candidates = np.flatnonzero(counts >= 100)
                bend = int(candidates[np.argmax(xy[candidates, 0])])
                view['panels'].append(draw_patch(out, name+'-bend', out/f'{name}-beauty.png',
                                                layout, view, bend, 'right screen bend'))
                if case == 'repeat-13' and phase == 'phase-half':
                    # Preserve the historic weak bead index for comparing the two hands.
                    view['panels'].append(draw_patch(out, name+'-weak', out/f'{name}-beauty.png',
                                                    layout, view, 533, 'R023 weak-slot location'))
                report['views'][name] = view
                print(name, {t: v[0]['summary']['component_sizes'] for t, v in view['graphs'].items()}, flush=True)
    assert source_hashes == {str(p.relative_to(ROOT)): digest(p) for p in sources}, 'Source changed during run'
    report['sources'] = source_hashes
    report['artifacts'] = {p.name: digest(p) for p in sorted(out.iterdir())
                           if p.is_file() and p.name != 'report.json'}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'Report: {out / "report.json"}', flush=True)


if __name__ == '__main__':
    main()
