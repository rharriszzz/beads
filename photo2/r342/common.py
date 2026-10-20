"""R342 fixed photographic inputs and explicit maker authority."""
import os,sys,copy,json,gzip,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from scipy.spatial import cKDTree
from photo2.r337.common import read,save,sha,COLORS,quotient
OUT=Path(os.environ.get('R342_RUN_ROOT',ROOT/'photo2/r342'));OUT.mkdir(parents=True,exist_ok=True)
BASE='ef3a8137c6f2e0777eb81f87784f35bb0a4a1292'
MAKER={'R332-R-0077-0077':'black','NEW-1681-1498':'black','R332-R-0147-0142':'yellow','REC266-P074746':'yellow'}
def load():
 g=read(ROOT/'photo2/r341/graph.json.gz');obs={r['id']:r for r in g['observations']};co={r['id']:r['ab'] for r in g['coordinates']};rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));auth=read(ROOT/'photo2/r340/autoregion/freeze.json')['authoritative_labels'];auth.update({o:dict(color=c,source='R342 maker review of R341 own-photograph feature1',active_color_authority=True) for o,c in MAKER.items()});return g,obs,co,rgb,auth
