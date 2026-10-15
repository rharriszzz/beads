from pathlib import Path
import os
from photo2.r282.common import ROOT, read, save, sha, photo, pixels, runs
BASE = ROOT/'photo2/r295'
OUT = Path(os.environ.get('R295_OUTPUT', BASE/'results'))
EVIDENCE = BASE/'evidence'
REVIEW = Path(os.environ.get('R295_REVIEW', ROOT/'photo2/review/r295'))
def source_hashes():
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(BASE.glob('*.py'))}
