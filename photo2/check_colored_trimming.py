"""R220: trimming comparisons on existing known-ID development scenes.

All variants finish image-only extraction before known owner pixels are read.
These examples are development/regression controls, not independent holdouts.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from auto_label_beads import ROOT, sha
from refine_colored_masks import refine
from trim_colored_masks import trim, METHODS
from check_mask_refinement import FIXTURES, ownership_measurements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'photo2/output/r220/calibration')
    parser.add_argument('--stable-rim-rule', choices=('rank','inset'), default='rank')
    parser.add_argument('--no-stable-raw-floor', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    fixture_dir = ROOT/'photo2/output/r167/calibration'
    pending = []
    for name in FIXTURES:
        path = fixture_dir/(name+'.png')
        image = np.asarray(Image.open(path).convert('RGB'))
        base = refine(image, sha(path))
        for method in ('baseline', *METHODS):
            report, arrays = base if method == 'baseline' else trim(image, sha(path), method, base,
                args.stable_rim_rule, not args.no_stable_raw_floor)
            prefix = args.output/(name+'-'+method)
            prefix.with_suffix('.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
            np.savez_compressed(str(prefix)+'.npz', **arrays)
            pending.append((name, method, report, arrays))
        print(json.dumps(dict(fixture=name, extraction_completed=True)), flush=True)
    results = []
    for name, method, report, arrays in pending:
        id_path = fixture_dir/(name+'-ids.png')
        rgb = np.asarray(Image.open(id_path).convert('RGB'), int)
        labels = rgb[...,0]+256*rgb[...,1]-1
        evaluation_report = dict(report, records=[r for r in report['records'] if r['retained_pixels']>0])
        measured = ownership_measurements(evaluation_report, arrays, labels)
        measured['empty_region_numbers'] = [r['region_number'] for r in report['records'] if not r['retained_pixels']]
        before = pending[FIXTURES.index(name)*5][3]
        assert np.array_equal(arrays['reflections'], before['reflections'])
        assert not np.any((arrays['retained']>0)&(arrays['retained']!=before['retained']))
        # Preserve body/owner ledgers, including failed or under-covered bodies.
        results.append(dict(fixture=name, method=method, appearance_sha256=sha(fixture_dir/(name+'.png')),
                            ids_sha256=sha(id_path), result=measured, reflection_masks_unchanged=True))
        print(json.dumps(dict(fixture=name, method=method,
            **{k:v for k,v in measured.items() if k not in ('bodies','regions','reflections')})), flush=True)
    (args.output/'report.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
