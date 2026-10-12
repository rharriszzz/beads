"""Copy the complete frozen run and compact review evidence into tracked files."""
import gzip
import argparse
import json
import shutil
from pathlib import Path
from .detect import ROOT,sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'photo2/review/r260');args=ap.parse_args()
    source=ROOT/'photo2/output/detection-r259';out=args.output;out.mkdir(exist_ok=True)
    for name in ['summary.json','validation.json','labels.npz','rank-size.csv','coordinates.csv','size-distribution.png',
                 'whole-regions.jpg','example-1.png','example-2.png','example-3.png']:
        shutil.copy2(source/name,out/name)
    (out/'regions.json.gz').write_bytes(gzip.compress((source/'regions.json').read_bytes(),mtime=0))
    for name in ['whole.png','detail.png','checks.json']:
        shutil.copy2(source/'browser'/name,out/('browser-'+name))
    files={str(p.relative_to(ROOT)):sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='provenance.json'}
    files.update({str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/bead_detection').rglob('*')) if p.is_file() and '__pycache__' not in str(p)})
    files['beads-photo-2.jpg']=sha(ROOT/'beads-photo-2.jpg')
    legacy=ROOT/'photo2/output/debugger/reviews/latest.json'
    result=dict(files=files,uncompressed_regions_sha256=sha(source/'regions.json'),
                preserved_local_review_sha256=sha(legacy),
                notes='No production review writes. Legacy immutable-input snapshot has a pre-existing hash mismatch; do not restore or replace user reviews.')
    (out/'provenance.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
