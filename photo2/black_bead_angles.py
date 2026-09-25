#!/usr/bin/env python3
"""Repeat the 26-frame walk at eight major-circle locations; no extra renders."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from black_bead_walk import COUNT, NBEADS, ROOT, digest, font


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--helicity',type=int,choices=(-1,1),default=1)
    parser.add_argument('--analyze-only', action='store_true')
    args = parser.parse_args()
    review = ROOT/'photo2/review/r084'
    output = ROOT/'photo2/output/black-bead-walk'
    if args.helicity == -1:
        review = review/'opposite'
        output = output/'opposite'
    rows = []
    for location in range(8):
        start = NBEADS*location//8
        # Preserve the first walk already requested and rendered before extension.
        directory = review if location == 0 else review/f'angle-{location*45:03d}'
        scratch = output if location == 0 else output/f'angle-{location*45:03d}'
        command = [sys.executable, str(ROOT/'photo2/black_bead_walk.py'),
                   '--helicity',str(args.helicity),'--start-index', str(start), '--output', str(scratch),
                   '--review', str(directory), '--resume']
        if args.analyze_only:
            command.append('--analyze-only')
        output.mkdir(parents=True,exist_ok=True)
        with (output/f'location-{location}.log').open('w') as stream:
            subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
        report = json.loads((directory/'report.json').read_text())
        rows.append(dict(location=location, nominal_angle=location*45,
                         actual_start_angle=360*start/NBEADS,
                         start=start, stop=start+COUNT-1,
                         report=str((directory/'report.json').relative_to(review)),
                         report_sha256=digest(directory/'report.json'),
                         command=command))
        print(f'Completed location {location+1}/8: indices {start}–{start+COUNT-1}',flush=True)
    # Review overview: three consecutive indices around the largest response,
    # at the same scale within each location; every frame remains in linked sheets.
    sheet = Image.new('RGB',(1500,8*260+50),'white')
    draw=ImageDraw.Draw(sheet)
    draw.text((12,10),'Eight positions around the necklace: consecutive visible-shape examples',font=font(24),fill='black')
    html=['<!doctype html><meta charset="utf-8"><title>Eight black-bead walks</title>',
          '<style>body{font:18px system-ui;max-width:1500px;margin:2em auto}img{max-width:100%;height:auto}</style>',
          '<h1>Eight locations × 26 consecutive black-bead indices</h1>',
          '<p>Fixed camera, scene and scale. Each walk contains exactly one black bead and 675 white beads. '
          'The selected starting positions sample the major circle approximately every 45 degrees. '
          'Every sequence spans 13.31 degrees along that circle and four turns around the rope. '
          'Indices here are known render indices, unrelated to the JPEG observation IDs.</p>',
          '<p><a href="angles-overview.png"><img src="angles-overview.png"></a></p>']
    for row in rows:
        directory=(review/row['report']).parent
        report=json.loads((directory/'report.json').read_text())
        counts=[f['response_pixels']['10'] for f in report['frames']]
        peak=counts.index(max(counts))
        first=min(max(peak-1,0),COUNT-3)
        selected=list(range(first,first+3))
        row['overview_indices']=[report['frames'][i]['index'] for i in selected]
        row['response_pixels_10']=counts
        box=report['crop']
        base_y=50+row['location']*260
        draw.text((12,base_y+8),f"{row['nominal_angle']}° start\nindices {row['start']}–{row['stop']}",font=font(20),fill='black')
        scratch=output if row['location']==0 else output/f"angle-{row['nominal_angle']:03d}"
        for column,slot in enumerate(selected):
            index=report['frames'][slot]['index']
            crop=Image.open(scratch/f'black-{index:03d}.png').convert('RGB').crop(box)
            crop.thumbnail((400,210),Image.Resampling.NEAREST)
            x=225+column*420
            sheet.paste(crop,(x,base_y+35))
            draw.text((x,base_y+6),f'Index {index} · {counts[slot]} response px',font=font(17),fill='black')
        prefix='' if row['location']==0 else f"angle-{row['nominal_angle']:03d}/"
        html.append(f"<h2>{row['nominal_angle']}° start: indices {row['start']}–{row['stop']}</h2>"
                    f'<p><a href="{prefix}review.html">All frames and scene context</a></p>'
                    f'<img src="{prefix}walk.gif">')
    sheet.save(review/'angles-overview.png')
    (review/'angles.html').write_text('\n'.join(html))
    summary=dict(render_count=8*COUNT,helicity=args.helicity,locations=rows,
                 scope='Known synthetic calibration; no existing inventory changes',
                 sources={str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},
                 artifacts={name:digest(review/name) for name in ('angles-overview.png','angles.html')})
    (review/'angles-report.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':
    main()
