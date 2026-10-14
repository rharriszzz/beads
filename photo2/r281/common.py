from pathlib import Path
from photo2.r280.common import ROOT,read,save,sha,runs,mask_from_runs
import os
OUT=Path(os.environ.get('R281_OUTPUT',ROOT/'photo2/r281/results'))
