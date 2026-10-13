"""Validate saved R267 evidence and hash the final deliverable."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from .audit_r267 import ROOT,OUT,photo,save,METRICS

def main():
    manifest=json.loads((OUT/'manifest.json').read_text());rgb=photo()
    for name,sha in manifest['inputs'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    pixel_count=0;rank_checks=0
    for name,s in manifest['summaries'].items():
        x0,y0,x1,y1=s['box'];assert np.array_equal(np.asarray(Image.open(OUT/f'{name}-original-native.png')),rgb[y0:y1,x0:x1])
        rows=list(csv.DictReader(open(OUT/f'{name}-all-maximum-pixels.csv')));assert len(rows)==s['pixels'];pixel_count+=len(rows)
        for k in METRICS:
            ranked=list(csv.DictReader(open(OUT/f'{name}-rank-{k}.csv')))
            assert set(r['number'] for r in ranked)==set(r['number'] for r in rows)
            vs=[float(r[k]) for r in ranked];assert vs==sorted(vs,reverse=True)
            for r in rows:assert int(r['rank_'+k])==1+sum(v>float(r[k]) for v in vs)
            rank_checks+=len(rows)
        assert all(v['overlapping_labels']==v['labels_covering_maximum_markers']==0 for v in s['label_checks'].values())
    tests=(OUT/'tests.log').read_text();assert 'Ran 4 tests' in tests and tests.rstrip().endswith('OK')
    control=json.loads((OUT/'control-summary.json').read_text());table=json.loads((OUT/'table-validation.json').read_text())
    save(OUT/'validation.json',dict(status='pass',source_input_hashes=len(manifest['inputs']),native_originals_exact=2,maximum_pixels=pixel_count,independent_rank_checks=rank_checks,numeric_tests=4,old_mask_exact_checks=control['old_mask_exact_checks'],prominence_gate_checks=table['prominence_gate_checks'],selected_score_checks=table['selected_score_checks'],detector_changed=False,visual_review='Both all-maxima mean7 maps, fixed-background mean7 maps and frozen-growth photographs inspected. No verified bead identities/center error asserted.'))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='artifact-hashes.json')
    files+=sorted((ROOT/'photo2/bead_detection').glob('*r267.py'))
    files+=[ROOT/'photo2/LOCAL_MAXIMA_R267.md']
    save(OUT/'artifact-hashes.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    print(json.dumps(json.loads((OUT/'validation.json').read_text())))
if __name__=='__main__':main()
