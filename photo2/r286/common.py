from pathlib import Path
import numpy as np
from photo2.r282.common import ROOT,read,save,photo,pixels,support,sha,record,validate
OUT=ROOT/'photo2/r286/results'
REVIEW=ROOT/'photo2/review/r286'
OLD=ROOT/'photo2/r285/results'

def reviewed():
    selection=read(OLD/'selection.json')['development'];d={o['id']:o for o in read(OLD/'development.json.gz')['observations']};v=read(OLD/'confirmation.json.gz')['observations'];rows=[]
    for name,example in [('P1','e01'),('P2','e02'),('P3','e04'),('P4','e07')]:
        q=next(q for q in selection if q['example']==example);rows.append(dict(name=name,old_example=example,observation=d[q['observation_id']]))
    rows.append(dict(name='P5',old_example='v04',observation=v[3]));return rows
