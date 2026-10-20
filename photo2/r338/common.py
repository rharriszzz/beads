import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/r338-mpl')
import math,json,gzip,hashlib
from pathlib import Path
from collections import Counter,defaultdict,deque
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image,ImageOps
from photo2.r337.common import ROOT,read,save,sha,quotient,COLORS,motif,predict
BASE='4ddb0c34a567aa1b0778619c16aa3b69d542f2bd'
DIRECTIONS=((1,0),(0,1),(1,-1),(-1,0),(0,-1),(-1,1))
EXCLUDED={'E5-1499-3037','E7-2235-1306','E5-0948-2669','E5-0986-2754','R332-B-0196-0183','R332-B-0138-0130','C-1979-2669','REC266-P146299','NEW-1927-2829'}
def baseline():
    g=read(ROOT/'photo2/r336/results/graph.json.gz');obs={r['id']:r for r in g['observations']};co={r['id']:tuple(r['ab']) for r in g['coordinates']};return g,obs,co

def geometry(g,obs,co):
    # Reuse ONLY the robust local coordinate regression, never historical
    # material response/recentering/admission/classifier routines.
    from photo2.r332.recover import Completion
    obj=Completion.__new__(Completion);obj.g=g;obj.obs=obs;obj.co=co;obj.H=np.array(g['H']);obj.rebuild();return obj

def photograph():return np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))

def rope_clearance(photo):
    """Physical outline eligibility only; never pigment/body-identity proof."""
    from scipy import ndimage as ndi
    rgb=photo.astype(np.float32)/255.;red,green,blue=rgb.transpose(2,0,1);value=rgb.max(2);distances=[]
    for threshold in [.25,.35,.45]:
        paper=(blue-green>threshold*(red-green))&(blue>1.1*green)&(red>1.2*green)&(value>.06)
        fg=ndi.binary_closing(~paper,iterations=5);labels,_=ndi.label(fg);sizes=np.bincount(labels.ravel());keep=sizes>=60;keep[0]=False;fg=keep[labels];holes,_=ndi.label(~fg);sizes=np.bincount(holes.ravel());small=sizes<1000;small[0]=False;fg|=small[holes];distances.append(ndi.distance_transform_edt(fg).astype(np.float32))
    return np.minimum.reduce(distances),distances

def artifact(path):return Path(os.environ.get('R338_RUN_ROOT',ROOT/'photo2/r338'))/path
