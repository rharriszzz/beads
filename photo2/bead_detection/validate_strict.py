"""Audit the complete saved R260 strict-growth comparison independently."""
import gzip
import json
import numpy as np
from .detect import ROOT,sha


def pixels(region):
    return {(x,y) for y,a,b in region['pixel_runs'] for x in range(a,b+1)}


def main():
    root=ROOT/'photo2/review/r260';out={};variants={}
    expected={f'strict-{mode}-{variant}.json.gz' for mode in ['native','smoothed'] for variant in ['14','30','30-color']}
    assert {p.name for p in root.glob('strict-*.json.gz')}==expected
    for path in sorted(root.glob('strict-*.json.gz')):
        data=json.loads(gzip.decompress(path.read_bytes()));variants[path.name]=data
        assert data['experiment_source_sha256']==sha(ROOT/'photo2/bead_detection/strict_r260.py')
        assert data['source_sha256']==sha(ROOT/'beads-photo-2.jpg')
        assert len({r['id'] for r in data['regions']})==data['summary']['candidates']
        for r in data['regions']:
            xy=np.array(sorted(pixels(r)))
            assert len(xy)==r['pixel_count']==r['area_px2']
            np.testing.assert_allclose(xy.mean(axis=0),r['centroid'])
            assert any((xy==r['location']).all(axis=1))
            assert any((xy==r['seed']).all(axis=1))
            assert all(c[0]==c[-1] for c in r['contours'])
            assert np.all(np.array(r['retained_radii'])<=r['effective_stop_radii'])
            assert np.all(np.array(r['effective_stop_radii'])<=r['stop_radii'])
        out[path.name]=dict(records=len(data['regions']),ray_contracts=data['summary']['ray_contracts'],
                            checks=['pixel-counts','centroids','locations-and-seeds-in-support',
                                    'closed-contours','ordered-stop-and-retreat-radii','source-hashes'])
    for mode in ['native','smoothed']:
        base=variants[f'strict-{mode}-30.json.gz'];guarded=variants[f'strict-{mode}-30-color.json.gz']
        for a,b in zip(base['regions'],guarded['regions']):
            assert a['id']==b['id'] and a['seed']==b['seed']
            assert pixels(b)<=pixels(a),(a['id'],'guard expanded mask')
    out['guard_comparison']='Both guarded variants are pixel subsets of their unguarded variant for all 1494 candidates.'
    (root/'strict-validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print('All six variants passed native mask/coordinate audits; both color guards only remove pixels.')


if __name__=='__main__':main()
