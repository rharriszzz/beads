"""R334 immutable input adapter and explicit evidence layers."""
import os,copy
os.environ.setdefault('MPLCONFIGDIR','/tmp/r334-mpl')
from pathlib import Path
import numpy as np
from photo2.r332.common import ROOT,read,save,sha,representative
from photo2.r333.common import dataset as raw_dataset,COLORS
BASE='acd51b0bcd586e812e1979258de8b402094fb634'
def artifact(path):return Path(os.environ.get('R334_RUN_ROOT',ROOT/'photo2/r334'))/path

def reviewed_dataset(layer='color'):
    g,obs,co,ids,ab,c,w,b,station=raw_dataset();g=copy.deepcopy(g);obs={o['id']:o for o in g['observations']}
    ledger=read(artifact('corrections/ledger.json'))
    if layer!='raw':
        for row in ledger['ordinary_color_corrections']:obs[row['id']]['color']='black'
    if layer in ['relocated','provisional']:
        row=ledger['location_correction'];obs[row['id']]['xy']=row['corrected_xy'];obs[row['id']]['color']='black'
    if layer=='provisional':
        audit=read(artifact('classification/audit.json.gz'))
        for row in audit['ranked_color_candidates']:
            if row['strong_provisional'] and row['id'] in obs:obs[row['id']]['color']=row['body_prediction']
    c=np.array([COLORS.index(obs[o]['color']) for o in ids])
    # Main before/after comparison freezes R333 observation weights and geography.
    # Equal-weight and reweighted controls are reported separately.
    return g,obs,co,ids,ab,c,w,b,station
