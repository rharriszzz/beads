from pathlib import Path
import numpy as np
from photo2.r282.common import ROOT, read, save, sha, photo, pixels, runs
OUT=ROOT/'photo2/r289/results'
REVIEW=ROOT/'photo2/review/r289'
BASE='2b9c289'

def stats(v, diameter=30.):
    a=np.asarray(v,float)
    if not len(a):return dict(n=0)
    d=dict(n=len(a),median=float(np.median(a)),rms=float(np.sqrt(np.mean(a*a))),p90=float(np.percentile(a,90)),p95=float(np.percentile(a,95)),maximum=float(a.max()))
    d['diameter_fractions']={k:v/diameter for k,v in d.items() if k!='n'}
    return d
