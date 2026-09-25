#!/usr/bin/env python3
"""Check the R085 atlas against its saved single object-label render."""
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

from full_circle_shapes import OUT, REVIEW, ROOT, NBEADS, choose_index
from legacy_visibility import decode


def main():
    report=json.loads((REVIEW/'report.json').read_text())
    shapes=json.loads((REVIEW/'shapes.json').read_text())
    assert report['render_count']==1 and len(report['commands'])==1
    for group,base in [('sources',ROOT),('raw_artifacts',ROOT),('artifacts',REVIEW)]:
        from practice_legacy import digest
        for name,sha in report[group].items():assert digest(base/name)==sha,(group,name)
    labels=decode(np.asarray(Image.open(OUT/'ids.png').convert('RGB')),NBEADS)
    counts=np.bincount(labels.ravel(),minlength=NBEADS+1)[1:]
    assert len(shapes['beads'])==NBEADS
    assert sum(counts)==report['total_visible_pixels']
    assert int((counts>0).sum())==report['nonzero_shapes']
    assert np.flatnonzero(counts==0).tolist()==report['zero_pixel_indices']
    for index,bead in enumerate(shapes['beads']):
        assert bead['index']==index and bead['pixels']==counts[index]
        assert bead['phase_column']==(2*index)%13
        y,x=np.nonzero(labels==index+1)
        if len(x):
            assert bead['bbox']==[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1]
            assert bead['contours']
            for contour in bead['contours']:
                assert contour[0]==contour[-1]
        else:assert bead['bbox'] is None and not bead['contours']
    assert len(shapes['atlas_selection'])==156
    for cell in shapes['atlas_selection']:
        assert cell['index']==choose_index(cell['requested_major_angle'],cell['phase_column'])
        bead=shapes['beads'][cell['index']]
        if bead['pixels']:
            cx,cy=np.rint(bead['projected_center']).astype(int)
            x0,y0,x1,y1=bead['bbox']
            assert cx-30<=x0<x1<=cx+30 and cy-30<=y0<y1<=cy+30
            # Rotation in a 60-pixel square must retain the complete silhouette.
            yy,xx=np.nonzero(labels==bead['index']+1)
            assert np.hypot(xx-cx,yy-cy).max()<29
    assert len(report['response_comparison'])==208
    response=report['response_comparison']
    assert sum(r['response_pixels'] for r in response)==report['response_summary']['response_pixels']
    assert sum(r['outside_one_pixel'] for r in response)==report['response_summary']['response_outside_one_pixel']
    for row in response:assert row['id_pixels']==counts[row['index']]
    for link in re.findall(r'(?:href|src)="([^"]+)"',(REVIEW/'review.html').read_text()):
        assert (REVIEW/link).is_file(),link
    match=re.search(r'VIS_PARAMS (\d+) (\d+) ([\d.]+) ([\d.]+)',(OUT/'ids.log').read_text())
    assert match and tuple(map(int,match.groups()[:2]))==(676,104)
    assert float(match[3])==6.5 and float(match[4])==0
    print('Verified all 676 shapes, 156 unclipped atlas cells, 208 response comparisons, hashes, links and one render.')


if __name__=='__main__':main()
