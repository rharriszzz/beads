from pathlib import Path
import numpy as np
from photo2.r282.common import ROOT,read,save,photo,pixels,support,sha,record,validate,circular_distance
OUT=ROOT/'photo2/r287/results'
REVIEW=ROOT/'photo2/review/r287'
OLD=ROOT/'photo2/r286/results'
BASE='f676c850d569aaddcb3735e480080094b6a56399'

def development():
    d=read(OLD/'development.json.gz')['cases'];c=read(OLD/'confirmation.json.gz')['cases'];out=[]
    for name in ('P5','P2','P1','P3'):
        q=next(q for q in d if q['name']==name);out.append(dict(name=name,seed=q['seed'],stratum='reviewed-development',observations=q['observations']))
    for name in ('C05','C02','C04','C07'):
        q=next(q for q in c if q['name']==name);out.append(dict(q,stratum='peripheral-review-no-tuning' if name=='C02' else 'development-failure-and-neighbors'))
    return out
