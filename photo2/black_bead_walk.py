#!/usr/bin/env python3
"""R084: 26 fixed-scene beauty renders, advancing one black bead per frame."""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version

from practice_legacy import ROOT, digest

COUNT = 26
NBEADS = 676  # 104 turns, exactly 6.5 beads per turn.
SIZE = (1200, 900)
CLOCK = '0.2500025001'  # Legacy case 3 (white/black), phase approximately zero.


def font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)


def scene(index, helicity=1):
    assert helicity in (-1, 1)
    colors = [int(i == index) for i in range(NBEADS)]
    assert sum(colors) == 1
    return (f'#declare CustomColorPattern=array[{NBEADS}]{{'
            + ','.join(map(str, colors)) + '};\n'
            '#declare CustomPatternGroups=1;\n'
            f'#declare Helicity={helicity};\n#include "beads.pov"\n'
            '#debug concat("WALK ",str(bead_pattern,0,0)," ",str(nbeads,0,0),'
            '" ",str(nrows,0,0)," ",str(exact_beads_per_row,0,9),'
            '" ",str(rclock,0,9),"\\n")\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/black-bead-walk')
    parser.add_argument('--review', type=Path, default=ROOT/'photo2/review/r084')
    parser.add_argument('--helicity',type=int,choices=(-1,1),default=1)
    parser.add_argument('--start-index', type=int, default=0)
    parser.add_argument('--resume', action='store_true', help='Reuse verified existing frames without rerendering.')
    parser.add_argument('--analyze-only', action='store_true', help='Reuse the same 26 renders; render none.')
    args = parser.parse_args()
    out, review = args.output.resolve(), args.review.resolve()
    out.mkdir(parents=True, exist_ok=True)
    review.mkdir(parents=True, exist_ok=True)
    records, arrays = [], []
    assert 0 <= args.start_index <= NBEADS-COUNT
    for index in range(args.start_index, args.start_index+COUNT):
        stem = f'black-{index:03d}'
        wrapper, png, log = (out/f'{stem}.{ext}' for ext in ('pov', 'png', 'log'))
        content = scene(index,args.helicity)
        command = ['povray', f'+I{wrapper}', f'+L{ROOT}', f'+O{png}',
                   f'+W{SIZE[0]}', f'+H{SIZE[1]}', f'+K{CLOCK}',
                   '+FN8', '-D', '+Q9', '+A0.1', '-J', '+WT2']
        if not args.analyze_only and not (args.resume and png.exists()):
            if png.exists():
                raise FileExistsError(f'{png}: use --analyze-only to avoid extra renders')
            wrapper.write_text(content)
            with log.open('w') as stream:
                subprocess.run(command, cwd=ROOT, stdout=stream,
                               stderr=subprocess.STDOUT, check=True)
        assert wrapper.read_text() == content
        match = re.search(r'WALK (\d+) (\d+) (\d+) ([\d.]+) ([\d.]+)', log.read_text())
        assert match and tuple(map(int, match.groups()[:3])) == (3, NBEADS, 104)
        assert float(match[4]) == 6.5 and abs(float(match[5])) < 1e-6
        im = Image.open(png).convert('RGB')
        assert im.size == SIZE
        arrays.append(np.asarray(im))
        records.append(dict(index=index, command=command, png_sha256=digest(png),
                            scene_sha256=digest(wrapper), log_sha256=digest(log),
                            rendered_phase=float(match[5])))
        print(f'Checked index {index}', flush=True)

    # Every pixel has white-bead observations in other frames. With these opaque,
    # nonreflecting materials and no radiosity, changing pigment is local.
    # This is a response reference, not an additional all-white render or ID mask.
    stack = np.stack(arrays)
    reference = stack.max(axis=0)
    response = (reference[None].astype(np.int16)-stack.astype(np.int16)).max(axis=3)
    union = (response > 10).any(axis=0)
    yy, xx = np.nonzero(union)
    assert len(xx)
    box = (max(0, int(xx.min())-25), max(0, int(yy.min())-25),
           min(SIZE[0], int(xx.max())+26), min(SIZE[1], int(yy.max())+26))
    for record, delta in zip(records, response):
        record['response_pixels'] = {str(t): int((delta > t).sum()) for t in (3, 10, 25)}
        y, x = np.nonzero(delta > 10)
        record['response_bbox'] = [int(x.min()), int(y.min()), int(x.max())+1, int(y.max())+1] if len(x) else None
    # Same crop and scale for every frame; hidden indices remain in sequence.
    crop_w, crop_h = box[2]-box[0], box[3]-box[1]
    scale = 2
    tile_w, tile_h = crop_w*scale+12, crop_h*scale+52
    for start in (0, 13):
        sheet = Image.new('RGB', (tile_w*7, tile_h*2+48), 'white')
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 10), f'One black bead: indices {args.start_index+start}–{args.start_index+start+12} | fixed crop, fixed scale', font=font(22), fill='black')
        for slot, index in enumerate(range(start, start+13)):
            x, y = (slot % 7)*tile_w, 48+(slot//7)*tile_h
            crop = Image.fromarray(arrays[index]).crop(box)
            sheet.paste(crop.resize((crop_w*scale, crop_h*scale), Image.Resampling.NEAREST), (x+6,y+44))
            pixels = records[index]['response_pixels']['10']
            draw.text((x+6,y+2), f'Index {args.start_index+index}: {pixels} response px', font=font(16), fill='black')
        sheet.save(review/f'indices-{start:02d}-{start+12:02d}.png')
    context = Image.fromarray(arrays[0])
    ImageDraw.Draw(context).rectangle(box, outline='#e00070', width=3)
    context.save(review/'context.png')
    Image.fromarray(reference).crop(box).resize((crop_w*4,crop_h*4), Image.Resampling.NEAREST).save(review/'white-reference.png')
    # A compact looping view preserves chronological index progression.
    frames = []
    for index, array in enumerate(arrays):
        im = Image.new('RGB', (crop_w*3,crop_h*3+38), 'white')
        im.paste(Image.fromarray(array).crop(box).resize((crop_w*3,crop_h*3), Image.Resampling.NEAREST),(0,38))
        ImageDraw.Draw(im).text((8,8),f'Black bead index {args.start_index+index}',font=font(20),fill='black')
        frames.append(im)
    frames[0].save(review/'walk.gif', save_all=True, append_images=frames[1:], duration=650, loop=0, disposal=2)
    (review/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>One black bead walk</title>'
        '<style>body{font:18px system-ui;margin:2em}img{max-width:100%;height:auto}</style>'
        '<h1>26 renders: one black bead advancing by one index</h1>'
        '<p>Original beads.pov geometry, camera, light and shiny opaque finish; 676 beads, 6.5 per turn. '
        'Response pixel counts compare each frame to the pixelwise maximum of the same 26 frames '
        '(threshold 10/255); these are not complete object silhouettes. Zero response means no measurable '
        'pigment change at this resolution. No additional render passes.</p>'
        + ''.join(f'<p><a href="{name}"><img src="{name}"></a></p>' for name in
                  ('walk.gif','context.png','indices-00-12.png','indices-13-25.png','white-reference.png')))
    report = dict(render_count=COUNT, helicity=args.helicity, indices=list(range(args.start_index,args.start_index+COUNT)), nbeads=NBEADS,
                  beads_per_turn=6.5, turns=104, clock=CLOCK, size=SIZE, crop=box,
                  sources={str(p.relative_to(ROOT)):digest(p) for p in
                           (Path(__file__),ROOT/'photo2/practice_legacy.py',ROOT/'beads.pov',ROOT/'bead-shape.inc')},
                  python=platform.python_version(), numpy=np.__version__, pillow=pillow_version,
                  font_sha256=digest(Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')),
                  colors_include_sha256=digest(Path('/usr/local/share/povray-3.7/include/colors.inc')),
                  renderer=subprocess.run(['povray','--version'],capture_output=True,text=True).stdout,
                  frames=records,
                  artifacts={name:digest(review/name) for name in ('indices-00-12.png','indices-13-25.png','context.png','white-reference.png','walk.gif','review.html')})
    (review/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(crop=box, response_pixels=[r['response_pixels'] for r in records]),indent=2))


if __name__ == '__main__':
    main()
