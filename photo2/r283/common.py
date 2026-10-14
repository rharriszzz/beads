import os
from pathlib import Path
from photo2.r282.common import ROOT, photo, read, save, sha, pixels, support, record, validate

OUT = Path(os.environ.get('R283_OUTPUT', ROOT/'photo2/r283/results'))
OLD = ROOT/'photo2/r282/results'
REVIEW = ROOT/'photo2/review/r283'
