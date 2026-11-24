"""Score the recorded sites against the committed forecasts and draw both photo sheets."""
import csv
import hashlib
import json
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from photo2.alternate_views.analyze import ROOT, VIEWS, normals, unwrap, write_csv
from photo2.alternate_views.registration import WEAK, candidates
from .forecast import HORIZON, ORIENTATION, OUT, WORD, readings

FROZEN = 'ed9224f65d73f5abe7a4f6db5eb0bad2ed904b477572d3e2f56028553f8d8f2c'


def prior_positions():
    positions = set()
    for file, field in [('path-results.csv', 'observed'), ('neighbor-results.csv', 'color')]:
        with (OUT.parent / file).open() as stream:
            positions.update(int(r['residue']) for r in csv.DictReader(stream) if r[field] != '?')
    return positions


def classify(role, observed, colors):
    if role != 'test':
        return role
    if observed == '?':
        return 'unreadable'
    if not colors:
        return 'no alignment'
    if len(colors) > 1:
        return 'ambiguous'
    return 'correct' if colors == observed else 'contrary'


def draw_window(sheet, strip, start, eighth, points, prefix_count):
    top = ((eighth - 1) // 2) * 270
    panel = Image.fromarray(strip[:, start:start + 555]).resize((888, 213))
    draw = ImageDraw.Draw(panel)
    draw.line((512, 0, 512, 213), fill='white')
    for j, (x, y, color) in enumerate(points):
        px, py = round(x * 1.6), round(y * 1.6)
        ink = 'cyan' if j < prefix_count else 'white' if x < 320 else '#ffe066'
        draw.ellipse((px-5, py-5, px+5, py+5), outline=ink, width=2)
        draw.text((px-4, py-21), color, fill=ink, stroke_width=1, stroke_fill='black')
        draw.text((px-5, 194), str(j+1), fill=ink, stroke_width=1, stroke_fill='black')
    sheet.paste(panel, (8, top+28))
    ImageDraw.Draw(sheet).text((8, top+7), f'{eighth}/8 clockwise   |   cyan: prefix    white: bridge    yellow: test',
                               fill='black')


def main():
    frozen = OUT / 'forecast.csv'
    if hashlib.sha256(frozen.read_bytes()).hexdigest() != FROZEN:
        raise ValueError('Prediction table differs from the pre-reveal commit')
    with frozen.open() as stream:
        forecast = {(r['view'], int(r['eighth']), int(r['step']), int(r['inward'])): r
                    for r in csv.DictReader(stream)}
    prefix = dict(readings(OUT / 'prefix.csv'))
    suffix = dict(readings(OUT / 'suffix.csv'))
    earlier = prior_positions()
    word = WORD.read_text().strip()
    added = {role: set() for role in ('prefix', 'bridge', 'test')}
    records = []
    summary = {'previous_coverage': len(earlier), 'windows': [], 'half_repeat_witnesses': []}
    for view, (filename, knots) in VIEWS.items():
        with Image.open(ROOT / filename) as im:
            axis, strip = unwrap(np.array(ImageOps.exif_transpose(im).convert('RGB')), knots)
        normal = normals(axis)
        sheet = Image.new('RGB', (904, 1080), 'white')
        for eighth in (1, 3, 5, 7):
            key = (view, eighth)
            head, tail = prefix[key], suffix[key]
            points = head + tail
            if len(tail) > HORIZON or any(x2 <= x1 or y1 == y2 for (x1,y1,_),(x2,y2,_) in zip(points,points[1:])):
                raise ValueError(f'Invalid path geometry for {key}')
            origin = eighth * len(axis) // 8
            possible = forecast[view, eighth, 1, 0]['phases'].split()
            phases = list(map(int, possible))
            # Can the new addresses be recovered without using a black observation
            # or imposing any color at the seven historically sparse positions?
            colored_only = [
                fit['phase'] for fit in candidates(head, word)
                if fit['orientation'] == ORIENTATION[view] and all(
                    obs not in 'RY' or k in WEAK or word[k] == obs
                    for (_, _, obs), k in zip(head, fit['positions'], strict=True))
            ]
            down, up = ORIENTATION[view]
            counts = Counter()
            prefix_offset = inward = 0
            for j, (x, y, obs) in enumerate(points):
                if j < len(head):
                    if j:
                        prefix_offset += down if y > points[j-1][1] else up
                    residues = sorted((phase + prefix_offset) % 208 for phase in phases)
                    colors = ''.join(sorted({word[k] for k in residues}))
                    role = 'prefix'
                else:
                    step = j - len(head) + 1
                    inward += int(y > points[j-1][1])
                    row = forecast[view, eighth, step, inward]
                    residues = list(map(int, row['residues'].split()))
                    colors = row['colors']
                    role = 'bridge' if x < 320 else 'test'
                outcome = classify(role, obs, colors)
                counts[outcome] += 1
                if len(residues) == 1 and obs != '?' and residues[0] not in earlier:
                    added[role].add(residues[0])
                station = origin+x
                native = axis[station] + normal[station]*(y-66)
                records.append(dict(view=view, eighth=eighth, site=j+1, role=role, strip_x=x, strip_y=y,
                                    native_x=round(float(native[0]),2), native_y=round(float(native[1]),2),
                                    observed=obs, chart_colors=colors, residues=' '.join(map(str,residues)),
                                    outcome=outcome))
            summary['windows'].append(dict(view=view, eighth=eighth, phases=phases,
                                           colored_only_phases=colored_only, counts=dict(counts)))
            for j in range(len(points)-16):
                run = points[j:j+17]
                if sum(b[1]>a[1] for a,b in zip(run,run[1:])) == 8:
                    first, last = run[0][2], run[-1][2]
                    if first != last and '?' not in (first, last):
                        summary['half_repeat_witnesses'].append(dict(view=view, eighth=eighth,
                            first_site=j+1, last_site=j+17, first_color=first,last_color=last))
            draw_window(sheet, strip, origin, eighth, points, len(head))
        sheet.save(OUT / f'{view}-paths.jpg', quality=95)
    write_csv(OUT / 'results.csv', records)
    summary['new_positions_by_role'] = {role:sorted(values) for role,values in added.items()}
    summary['new_positions'] = sorted(set.union(*added.values()))
    summary['combined_coverage'] = len(earlier | set(summary['new_positions']))
    (OUT / 'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__ == '__main__':
    main()
