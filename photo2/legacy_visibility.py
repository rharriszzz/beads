#!/usr/bin/env python3
"""Measure known repeat-slot visibility in the actual legacy scene; no inversion."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import platform
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version

from practice_legacy import ROOT, digest

HERE = ROOT / 'photo2'
WIDTH, HEIGHT = 2400, 1800
PHASES = [('phase-0', '0'), ('phase-half', '0.0625')]
THRESHOLDS = (1, 12, 100)
BODY = '''  object{ beads[color_pattern[mod(bead_index, pattern_length)]]
          rotate <0, 0, chain_angle>
          translate t1+t2+<0,0,chain_minor+2*bead_radius> }'''


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'Legacy source anchor changed: {old[:80]!r}')
    return source.replace(old, new, 1)


def instrument_source(source):
    """Fail closed if case-1 body assumptions or exact replacement anchors change."""
    for color, index in [('Red', 0), ('Green', 1), ('Blue', 2)]:
        if not re.search(rf'beads\[{index}\] = bead\(shiny_opaque\({color}\),'
                         r'\s+0\.8, 0\.7, 1\.0\);', source):
            raise ValueError('Case-1 bead proportions changed')
    source = replace_once(source, 'light_source { <100, -1000, 1000> White*1.4 }', '')
    source = replace_once(source,
        'plane { z, 0 pigment { White } finish { diffuse 0.90 }}', '')
    source = replace_once(source,
        'material{texture{pigment{bead_color} finish {phong 1.5}}}',
        'material{texture{pigment{bead_color} finish {ambient 0 emission 1 diffuse 0}}}')
    source = replace_once(source, '#declare bead_index = 0;', '''
#if (bead_pattern != 1) #error "Visibility instrumentation requires case 1" #end
#ifdef (VisibilityTable)
  #fopen VisibilityFile VisibilityTable write
#end
#declare bead_index = 0;''')
    source = replace_once(source, BODY, '''
  #ifdef (VisibilityTable)
    #declare VisibilityPosition=t1+t2+<0,0,chain_minor+2*bead_radius>;
    #write (VisibilityFile, bead_index, ",", mod(bead_index,pattern_length), ",",
      str(chain_angle,0,12), ",", str(row_angle,0,12), ",",
      str(VisibilityPosition.x,0,12), ",", str(VisibilityPosition.y,0,12), ",",
      str(VisibilityPosition.z,0,12), "\\n")
  #end
  #if ((VisibilityOnly < 0) | (VisibilityOnly = bead_index))
    #if (VisibilityPalette)
''' + BODY + '''
    #else
      #include "photo2/legacy-visibility-body.inc"
    #end
  #end''')
    return '''#version 3.7;
global_settings { assumed_gamma 1.0 }
background { color rgb 0 }
#ifndef (VisibilityOnly) #declare VisibilityOnly=-1; #end
#ifndef (VisibilityPalette) #declare VisibilityPalette=0; #end
''' + source + '''
#ifdef (VisibilityTable) #fclose VisibilityFile #end
#debug concat("VIS_PARAMS ", str(nbeads,0,0), " ", str(nrows,0,0), " ",
  str(exact_beads_per_row,0,12), " ", str(rclock,0,12), "\\n")
'''


def wrapper(pattern, include, table=None):
    colors, groups = pattern['colors'], pattern['groups']
    if not colors or any(type(c) is not int or c not in range(3) for c in colors):
        raise ValueError('Expected case-1 palette indices 0..2')
    if type(groups) is not int or groups < 1 or len(colors)*groups >= 2**24:
        raise ValueError('Invalid bead count')
    return (f'#declare CustomColorPattern=array[{len(colors)}] {{'
            + ','.join(map(str, colors)) + '};\n'
            + f'#declare CustomPatternGroups={groups};\n'
            + (f'#declare VisibilityTable="{table.as_posix()}";\n' if table else '')
            + f'#include "{include}"\n')


def render(out, name, scene, clock, commands, *, beauty=False, only=-1, palette=False,
           width=WIDTH, height=HEIGHT):
    output = out / f'{name}.png'
    command = ['povray', f'+I{scene}', f'+L{ROOT}', f'+L{out}', f'+O{output}',
               f'+W{width}', f'+H{height}', f'+K{clock}', '+FN8', '-D', '+WT2']
    if beauty:
        command += ['+A0.1']  # Exactly the original practice beauty settings.
    else:
        command += ['-A', '-J', 'File_Gamma=1.0', 'Dither=Off',
                    f'Declare=VisibilityOnly={only}', f'Declare=VisibilityPalette={int(palette)}']
    with (out/f'{name}.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    commands.append({'cwd': str(ROOT), 'argv': command})
    return np.asarray(Image.open(output).convert('RGB'))


def decode(rgb, count):
    rgb = np.asarray(rgb, dtype=np.int32)
    ids = rgb[..., 0] + 256*rgb[..., 1] + 65536*rgb[..., 2]
    if np.any(ids > count):
        raise ValueError('Non-ID color in instrumented image')
    return ids


def measure(ids, length, groups):
    """Keep all original indices; zero-pixel observations stay explicitly missing."""
    n = length*groups
    counts = np.bincount(ids.ravel(), minlength=n+1)[1:]
    ys, xs = np.indices(ids.shape)
    sx = np.bincount(ids.ravel(), weights=xs.ravel(), minlength=n+1)[1:]
    sy = np.bincount(ids.ravel(), weights=ys.ravel(), minlength=n+1)[1:]
    centroids = [[float(sx[i]/c), float(sy[i]/c)] if c else None
                 for i, c in enumerate(counts)]
    by_occurrence = counts.reshape(groups, length)
    coverage = {}
    for threshold in THRESHOLDS:
        visible = by_occurrence >= threshold
        support = visible.sum(axis=0)
        coverage[str(threshold)] = {
            'visible_beads': int(visible.sum()),
            'slots_seen': int(np.count_nonzero(support)),
            'unseen_slots': np.flatnonzero(support == 0).tolist(),
            'occurrences_per_slot': support.tolist(),
        }
    return {'pixels_per_bead': counts.tolist(), 'visible_centroids': centroids,
            'pixels_by_occurrence_and_slot': by_occurrence.tolist(), 'coverage': coverage,
            'zero_pixel_bead_indices': np.flatnonzero(counts == 0).tolist()}


def verify_practice(directory):
    report = json.loads((directory/'report.json').read_text())
    for name, expected in report['sources'].items():
        if digest(ROOT/name) != expected:
            raise ValueError(f'Practice source hash changed: {name}')
    for name, expected in report['artifacts'].items():
        if digest(directory/name) != expected:
            raise ValueError(f'Practice artifact hash changed: {name}')
    return report


def font(size=19):
    # Pillow ships a scalable default font; no external font dependency.
    return ImageFont.load_default(size=size)


def draw_coverage(cases, out):
    panel = Image.new('RGB', (1500, 1090), 'white')
    d = ImageDraw.Draw(panel)
    d.text((20, 12), 'Known repeat-slot visibility in original beads.pov', fill='black', font=font(26))
    d.text((20, 48), 'One cell = one bead. White: 0 pixels; gray: 1-11; light teal: 12-99; dark teal: >=100.',
           fill='black', font=font(19))
    for row, case in enumerate(cases):
        for col, phase in enumerate(case['views']):
            view = case['views'][phase]
            matrix = np.array(view['pixels_by_occurrence_and_slot'])
            x, y = 50+col*740, 128+row*460
            cw, ch = 600//matrix.shape[1], min(15, 360//matrix.shape[0])
            d.text((x, y-49), f'{case["name"]} / {phase}', fill='black', font=font(21))
            cov = view['coverage']['12']
            d.text((x, y-24), f'{cov["slots_seen"]}/{case["length"]} slots; {cov["visible_beads"]} beads with >=12 pixels',
                   fill='black', font=font(17))
            for g in range(matrix.shape[0]):
                for s in range(matrix.shape[1]):
                    c = int(matrix[g, s])
                    color = ('white' if c == 0 else '#9b9b9b' if c < 12
                             else '#86d6cf' if c < 100 else '#007e87')
                    d.rectangle((x+s*cw, y+g*ch, x+(s+1)*cw-1, y+(g+1)*ch-1),
                                fill=color, outline='#cccccc')
            d.text((x, y+matrix.shape[0]*ch+9), 'Columns: repeat slot (0-based); rows: repeat occurrence',
                   fill='black', font=font(15))
    d.text((20, 1028), 'The two phases are separate synthetic observations; their union is not evidence from one photo.',
           fill='black', font=font(19))
    panel.save(out/'coverage.png')


def draw_traces(case, phase, ids, beauty, out):
    """Show visible occurrences of slot 0, with known original bead IDs."""
    rgb = np.asarray(beauty).copy()
    counts = np.array(case['views'][phase]['pixels_per_bead'])
    indices = np.arange(0, case['count'], case['length'])
    visible = indices[counts[indices] >= 12]
    highlight = np.isin(ids, visible+1)
    rgb[highlight] = (0.4*rgb[highlight]+0.6*np.array([255,255,0])).astype(np.uint8)
    im = Image.fromarray(rgb)
    d = ImageDraw.Draw(im)
    # Label six spatially separated occurrences at most; all highlighted IDs are in JSON.
    selected = visible[np.linspace(0, len(visible)-1, min(6,len(visible)), dtype=int)] if len(visible) else []
    if len(visible) <= 6:
        selected = sorted(selected, key=lambda i: case['views'][phase]['visible_centroids'][int(i)][0])
    for j, i in enumerate(selected):
        x, y = case['views'][phase]['visible_centroids'][int(i)]
        label = f'#{i} / slot 0'
        tx, ty = max(0, min(WIDTH-220, x+22)), max(0, min(HEIGHT-40, y-45))
        if len(visible) <= 6:
            tx, ty = 200+j*450, HEIGHT-100
        d.line((x, y, tx, ty+25), fill='black', width=3)
        box = d.textbbox((tx, ty), label, font=font(24))
        d.rectangle((box[0]-5, box[1]-4, box[2]+5, box[3]+4), fill='white', outline='black')
        d.text((tx, ty), label, fill='black', font=font(24))
    title = f'{case["name"]} / {phase}: slot 0 highlighted; {len(visible)}/{case["groups"]} occurrences >=12 px'
    d.rectangle((0,0,WIDTH,55), fill='white')
    d.text((20,12), title, fill='black', font=font(28))
    target = out/f'{case["name"]}-{phase}-trace.png'
    im.save(target)
    # One enlargement per view shows the strongest observed occurrence of slot 0.
    # The mask marks measured visible pixels only; it does not fill the hidden body.
    best = int(indices[np.argmax(counts[indices])])
    x, y = case['views'][phase]['visible_centroids'][best]
    left = max(0, min(WIDTH-180, int(x)-90))
    top = max(0, min(HEIGHT-180, int(y)-90))
    box = (left, top, left+180, top+180)
    detail = Image.new('RGB', (1100,640), 'white')
    detail.paste(beauty.crop(box).resize((540,540), Image.Resampling.NEAREST), (5,80))
    detail.paste(Image.fromarray(rgb).crop(box).resize((540,540), Image.Resampling.NEAREST), (555,80))
    dd = ImageDraw.Draw(detail)
    dd.text((12,12), f'{case["name"]} / {phase}: bead #{best}, slot 0, {counts[best]} visible pixels',
            fill='black', font=font(24))
    dd.text((12,49), 'Original beauty (3x nearest-neighbor)', fill='black', font=font(20))
    dd.text((562,49), 'Same pixels; known slot 0 highlighted', fill='black', font=font(20))
    # A crosshair terminates outside the thin sliver, preserving its actual pixels.
    cx, cy = 555+(x-left)*3, 80+(y-top)*3
    for sign in (-1,1):
        dd.line((cx+sign*12,cy,cx+sign*35,cy),fill='black',width=2)
        dd.line((cx,cy+sign*12,cx,cy+sign*35),fill='black',width=2)
    detail_path = out/f'{case["name"]}-{phase}-detail.png'
    detail.save(detail_path)
    return {'slot': 0, 'highlighted_indices': visible.tolist(),
            'labelled_indices': [int(i) for i in selected], 'image': target.name,
            'detail_image':detail_path.name, 'detail_index':best, 'detail_box':box}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'output/legacy-visibility')
    parser.add_argument('--practice', type=Path, default=HERE/'output/legacy-practice')
    args = parser.parse_args()
    out, practice = args.output.resolve(), args.practice.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not (practice/'report.json').exists():
        raise SystemExit('First run .venv/bin/python photo2/practice_legacy.py')
    practice_report = verify_practice(practice)
    source = (ROOT/'beads.pov').read_text()
    instrument = out/'instrumented-legacy.pov'
    instrument.write_text(instrument_source(source))
    commands, cases = [], []
    sources = [Path(__file__), HERE/'legacy-visibility-body.inc',
               HERE/'test_legacy_visibility.py', ROOT/'beads.pov', ROOT/'bead-shape.inc',
               HERE/'practice-pattern.json', HERE/'visibility-pattern-13.json']
    report = {'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                              'pillow': pillow_version},
              'raster': [WIDTH,HEIGHT], 'thresholds_pixels': THRESHOLDS,
              'sources': {str(p.relative_to(ROOT)): digest(p) for p in sources},
              'practice_report_sha256': digest(practice/'report.json'),
              'practice_sources_and_artifacts_verified': True,
              'practice_artifacts': practice_report['artifacts'],
              'commands': commands, 'cases': cases}
    for name, filename in [('repeat-40','practice-pattern.json'),
                           ('repeat-13','visibility-pattern-13.json')]:
        pattern = json.loads((HERE/filename).read_text())
        length, groups = len(pattern['colors']), pattern['groups']
        count = length*groups
        turns = int(count/6.5+.5)
        drift = Fraction(360*turns, groups) % 360
        case = {'name': name, 'pattern': pattern, 'length': length, 'groups': groups,
                'count': count, 'turns': turns, 'exact_beads_per_turn': count/turns,
                'repeat_phase_advance_degrees': float(drift),
                'total_closure_adjustment_degrees': float(360*(turns-Fraction(2*count,13))),
                'views': {}}
        cases.append(case)
        beauty_scene = out/f'{name}-beauty.pov'
        beauty_scene.write_text(wrapper(pattern, 'beads.pov'))
        id_scene = out/f'{name}-id.pov'
        id_scene.write_text(wrapper(pattern, instrument.name))
        for phase, clock in PHASES:
            prefix = f'{name}-{phase}'
            layout_path = out/f'{prefix}-layout.csv'
            table_scene = out/f'{prefix}-table.pov'
            table_scene.write_text(wrapper(pattern, instrument.name, layout_path))
            ids = decode(render(out, prefix+'-ids', table_scene, clock, commands), count)
            palette = render(out, prefix+'-palette', id_scene, clock, commands, palette=True)
            np.testing.assert_array_equal(ids>0, np.any(palette != 0, axis=2))
            # Original palette shape and placement must match ID body exactly.
            expected_colors = np.array([[255,0,0],[0,255,0],[0,0,255]], dtype=np.uint8)
            foreground = ids > 0
            palette_indices = np.array(pattern['colors'])[(ids[foreground]-1) % length]
            np.testing.assert_array_equal(palette[foreground], expected_colors[palette_indices])
            view = measure(ids, length, groups)
            case['views'][phase] = view
            view['clock'] = clock
            view['palette_mask_and_slot_colors_exact'] = True
            params = re.search(r'VIS_PARAMS (\d+) (\d+) ([\d.]+) ([\d.]+)',
                               (out/f'{prefix}-ids.log').read_text())
            if params is None or tuple(map(int,params.groups()[:2])) != (count, turns):
                raise AssertionError('Scene parameters do not match requested count/closure')
            view['rendered_beads_per_turn'] = float(params[3])
            view['rclock'] = float(params[4])
            layout = np.loadtxt(layout_path, delimiter=',')
            np.testing.assert_array_equal(layout[:,0], np.arange(count))
            np.testing.assert_array_equal(layout[:,1], np.arange(count) % length)
            view['layout_columns'] = ['index','slot','chain_angle_deg','row_angle_deg','x','y','z']
            view['layout_file'] = layout_path.name
            # Local coverage isolates the changing view direction around the ring.
            # These quadrants select bead centers by chain angle, not image crops.
            view['quarter_ring_coverage'] = []
            for quadrant in range(4):
                angles = layout[:,2] % 360
                in_arc = (angles >= quadrant*90) & (angles < (quadrant+1)*90)
                arc_counts = np.where(in_arc, view['pixels_per_bead'], 0).reshape(groups,length)
                arc = {'chain_angle_degrees': [quadrant*90,(quadrant+1)*90], 'coverage':{}}
                for threshold in THRESHOLDS:
                    support = (arc_counts >= threshold).sum(axis=0)
                    arc['coverage'][str(threshold)] = {
                        'slots_seen':int(np.count_nonzero(support)),
                        'unseen_slots':np.flatnonzero(support == 0).tolist(),
                        'occurrences_per_slot':support.tolist()}
                view['quarter_ring_coverage'].append(arc)
            # Check one visible, one sliver, and one missing instance in each view.
            counts = np.array(view['pixels_per_bead'])
            positive = np.flatnonzero(counts)
            chosen = {int(np.argmax(counts)), int(positive[np.argmin(counts[positive])])}
            slot_zero = np.arange(0,count,length)
            chosen.add(int(slot_zero[np.argmax(counts[slot_zero])]))
            zero = np.flatnonzero(counts == 0)
            if len(zero):
                chosen.add(int(zero[0]))
            isolated_checks = []
            for index in sorted(chosen):
                isolated = decode(render(out, f'{prefix}-isolated-{index}', id_scene, clock,
                                         commands, only=index), count)
                if not np.all((isolated == 0) | (isolated == index+1)):
                    raise AssertionError('Isolated pass contains another bead')
                full_mask, solo_mask = ids == index+1, isolated == index+1
                if np.any(full_mask & ~solo_mask):
                    raise AssertionError('Visible body is not a subset of isolated projection')
                area = int(solo_mask.sum())
                if area == 0:
                    raise AssertionError('Selected isolated bead has no raster support')
                isolated_checks.append({'index':index, 'slot':index % length,
                    'visible_pixels':int(full_mask.sum()), 'isolated_pixels':area,
                    'visible_fraction':float(full_mask.sum()/area), 'subset_verified':True})
            view['isolated_checks'] = isolated_checks
            if length == 40:
                beauty_path = practice/f'{phase}.png'
            else:
                render(out, prefix+'-beauty', beauty_scene, clock, commands, beauty=True)
                beauty_path = out/f'{prefix}-beauty.png'
            view['beauty'] = {'path': str(beauty_path), 'sha256':digest(beauty_path)}
            view['trace'] = draw_traces(case, phase, ids, Image.open(beauty_path).convert('RGB'), out)
            print(f'{prefix}: '+json.dumps(view['coverage']), flush=True)
        # A union is explicitly labelled as using two distinct synthetic views.
        case['two_view_union_slots'] = {}
        for threshold in THRESHOLDS:
            support = np.array([v['coverage'][str(threshold)]['occurrences_per_slot']
                                for v in case['views'].values()]).sum(axis=0)
            case['two_view_union_slots'][str(threshold)] = {
                'slots_seen':int(np.count_nonzero(support)),
                'unseen_slots':np.flatnonzero(support == 0).tolist()}
    draw_coverage(cases, out)
    report['artifacts'] = {str(p.relative_to(out)): digest(p)
                           for p in sorted(out.iterdir()) if p.is_file() and p.name != 'report.json'}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'Report: {out/"report.json"}', flush=True)


if __name__ == '__main__':
    main()
