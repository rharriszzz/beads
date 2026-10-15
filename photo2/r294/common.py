from pathlib import Path
import os
from photo2.r282.common import ROOT, read, save, sha, photo, pixels

BASE = ROOT / 'photo2/r294'
OUT = Path(os.environ.get('R294_OUTPUT', BASE / 'results'))
EVIDENCE = BASE / 'evidence'
REVIEW = Path(os.environ.get('R294_REVIEW', ROOT / 'photo2/review/r294'))
REQUESTED = (-20, 200)
GUARD = (-45, 250)

def source_hashes():
    names = ['photo2/r279/geometry.py', 'photo2/r280/contact.py',
             'photo2/r282/geometry.py', 'photo2/r282/common.py', 'photo2/r293/geometry.py']
    names += [str(p.relative_to(ROOT)) for p in sorted(BASE.glob('*.py'))]
    return {p: sha(ROOT/p) for p in names}
