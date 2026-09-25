#!/usr/bin/env python3
"""Verify R084 provenance, all 208 consecutive color assignments and pixel counts."""
import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image

from black_bead_walk import ROOT, COUNT, NBEADS, SIZE, digest, scene


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comparison',action='store_true')
    parser.add_argument('--helicity',type=int,choices=(-1,1),default=1)
    args=parser.parse_args()
    review=ROOT/'photo2/review/r084'
    output=ROOT/'photo2/output/black-bead-walk'
    if args.comparison:
        report=json.loads((review/'helicity-report.json').read_text())
        assert report['render_count']==416 and report['extra_comparison_renders']==0
        assert len(list(output.rglob('black-*.png')))==416
        for name,sha in report['sources'].items():
            assert digest(ROOT/name)==sha
        for name,sha in {**report['inputs'],**report['artifacts']}.items():
            assert digest(review/name)==sha
        for row in report['locations']:
            index=row['colocated_index']
            assert index%13==0
            assert abs(math.remainder(720*index/6.5,360))<1e-8
            areas=[r['10'] for r in row['response_pixels_at_colocated_index']]
            intersection,union=row['response_intersection_pixels'],row['response_union_pixels']
            assert 0<=intersection<=min(areas) and union==sum(areas)-intersection
            assert abs(row['response_iou']-intersection/union)<1e-12
            assert Image.open(review/row['animation']).n_frames==26
        for link in re.findall(r'(?:href|src)="([^"]+)"',(review/'helicity.html').read_text()):
            assert (review/link).is_file()
        print('Verified comparison hashes, 416-render limit, colocated phases, overlap bookkeeping, eight paired animations and links.')
        return
    if args.helicity == -1:
        review=review/'opposite'
        output=output/'opposite'
    summary=json.loads((review/'angles-report.json').read_text())
    assert summary['render_count']==208 and len(summary['locations'])==8
    seen=set()
    for name,sha in summary['sources'].items():
        assert digest(ROOT/name)==sha
    for name,sha in summary['artifacts'].items():
        assert digest(review/name)==sha
    for location in summary['locations']:
        report_path=review/location['report']
        assert digest(report_path)==location['report_sha256']
        report=json.loads(report_path.read_text())
        start=NBEADS*location['location']//8
        indices=list(range(start,start+COUNT))
        assert report['helicity']==args.helicity
        assert report['indices']==indices and report['render_count']==26
        assert not seen.intersection(indices)
        seen.update(indices)
        for name,sha in report['sources'].items():
            assert digest(ROOT/name)==sha,(report_path,name)
        for name,sha in report['artifacts'].items():
            assert digest(report_path.parent/name)==sha
        for link in re.findall(r'(?:href|src)="([^"]+)"',(report_path.parent/'review.html').read_text()):
            assert (report_path.parent/link).is_file()
        scratch=output if location['location']==0 else output/f"angle-{location['nominal_angle']:03d}"
        arrays=[]
        for index,record in zip(indices,report['frames']):
            assert record['index']==index
            wrapper=scratch/f'black-{index:03d}.pov'
            assert wrapper.read_text()==scene(index,args.helicity)
            colors=re.search(r'array\[676\]\{(.*?)\}',wrapper.read_text())[1].split(',')
            assert colors.count('1')==1 and colors[index]=='1' and colors.count('0')==675
            for suffix,field in [('pov','scene_sha256'),('png','png_sha256'),('log','log_sha256')]:
                assert digest(scratch/f'black-{index:03d}.{suffix}')==record[field]
            image=Image.open(scratch/f'black-{index:03d}.png').convert('RGB')
            assert image.size==SIZE
            arrays.append(np.asarray(image))
        reference=np.maximum.reduce(arrays).astype(np.int16)
        for array,record in zip(arrays,report['frames']):
            response=(reference-array.astype(np.int16)).max(axis=2)
            assert {str(t):int((response>t).sum()) for t in (3,10,25)}==record['response_pixels']
        gif=Image.open(report_path.parent/'walk.gif')
        assert gif.n_frames==26
        print(f"Verified location {location['location']+1}: {indices[0]}–{indices[-1]}")
    for link in re.findall(r'(?:href|src)="([^"]+)"',(review/'angles.html').read_text()):
        assert (review/link).is_file()
    assert len(seen)==208
    rendered=[p for p in output.rglob('black-*.png') if args.helicity == -1 or 'opposite' not in p.relative_to(output).parts]
    assert len(rendered)==208
    print('Verified 208 renders, single-black assignments, source/artifact hashes, response counts, 8 animations and HTML links.')


if __name__=='__main__':
    main()
