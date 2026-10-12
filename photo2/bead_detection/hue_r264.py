"""Controlled R264 hue comparison. Detection is the unchanged bounded R263 code."""
import argparse
import gzip
import json
import subprocess
import sys
import tarfile
from dataclasses import asdict, replace
from .bounded_detect import ROOT, Parameters, save, sha

HUES = (5, 8, 10, 12, 15, 20)
WORK = ROOT / 'photo2/output/hue-r264'
OUT = ROOT / 'photo2/review/r264'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit', action='store_true')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for hue in HUES:
        work = WORK / str(hue)
        params = replace(Parameters(), hue_stop_deg=float(hue))
        if not (work / 'summary.json').exists():
            subprocess.run([sys.executable, '-m', 'photo2.bead_detection.bounded_detect',
                            '--output', str(work), '--hue-stop-deg', str(hue)], check=True)
        data = json.loads((work / 'regions.json').read_text())
        assert data['parameters'] == asdict(params)
        assert data['detector_sha256'] == sha(ROOT / 'photo2/bead_detection/bounded_detect.py')
        target = OUT / str(hue)
        target.mkdir(exist_ok=True)
        with gzip.GzipFile(filename=str(target / 'regions.json.gz'), mode='wb', mtime=0) as f:
            f.write((work / 'regions.json').read_bytes())
        for name in ('summary.json', 'coordinates.csv'):
            (target / name).write_text((work / name).read_text())
        with tarfile.open(target / 'traces.tar', 'w') as tar:
            for path in sorted((work / 'traces').glob('*.gz')):
                info = tar.gettarinfo(str(path), arcname='traces/' + path.name)
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ''
                with path.open('rb') as f:
                    tar.addfile(info, f)
        if args.audit and not (target / 'validation.json').exists():
            subprocess.run([sys.executable, '-m', 'photo2.bead_detection.validate_bounded',
                            '--work', str(work), '--output', str(target / 'validation.json')], check=True)
        print('ARCHIVED', hue, flush=True)


if __name__ == '__main__':
    main()
