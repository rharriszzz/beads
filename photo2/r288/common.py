from pathlib import Path
import numpy as np
from photo2.r282.common import ROOT,read,save,photo,pixels,support,sha,record,validate,circular_distance
OUT=ROOT/'photo2/r288/results'
REVIEW=ROOT/'photo2/review/r288'
OLD=ROOT/'photo2/r287/results'
BASE='e46b2c23699332c4668532fc813c35dae24c82e3'
def development():
    d=read(OLD/'development.json.gz')['cases'];c=read(OLD/'confirmation.json.gz')['cases'];out=[]
    for name in ('N07','N11','N06','P2','P5','C05'):
        q=next(q for q in d+c if q['name']==name);out.append(dict(q,stratum='reviewed-development'))
    return out
