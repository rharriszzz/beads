"""R343 immutable inputs, explicit new material judgments, and scoped authority."""
import os,sys,copy,json,gzip,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from scipy.spatial import cKDTree
from photo2.r337.common import read,save,sha,COLORS,quotient
OUT=Path(os.environ.get('R343_RUN_ROOT',ROOT/'photo2/r343'));OUT.mkdir(parents=True,exist_ok=True)
BASE='4536b40341ed7151513d61b74c445ce6b6d4a4a8'
Q101='REC266-P100583';C62='R332-Y-0104-0097';P29=['C-1001-2678','C-1226-1539','C-1250-2138','E5-1792-1727','NEW-1519-2976']
def load():
 g=read(ROOT/'photo2/r342/graph.json.gz');obs={r['id']:r for r in g['observations']};co={r['id']:r['ab'] for r in g['coordinates']};rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));auth=read(ROOT/'photo2/r342/corrections.json')['all_authoritative_labels'];legacy={r['id']:r for r in read(ROOT/'photo2/r335/results/graph.json.gz')['observations']};candidate=next(r for r in read(ROOT/'photo2/r342/candidate-checks.json')['records'] if r['id']==C62);extra={C62:dict(id=C62,xy=candidate['source_xy'],color='yellow',provisional=True)};extra.update({o:legacy[o] for o in ['NEW-1927-2829','REC266-P146299','C-1979-2669']});return g,obs,co,rgb,auth,extra

def authority(o,auth):
 if o in [Q101,C62]:return 'explicit_individual_pigment'
 source=auth.get(o,{}).get('source','')
 if 'accepted' in source:return 'illustration_approval'
 if o in auth:return 'explicit_individual_pigment'
 return 'software_native_label'
