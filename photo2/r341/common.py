"""Frozen photographic inputs; no pattern-derived pigment or identity changes."""
import os,sys,copy,time,json,gzip,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from scipy.spatial import cKDTree
from photo2.r337.common import read,save,sha,COLORS,quotient
OUT=Path(os.environ.get('R341_RUN_ROOT',ROOT/'photo2/r341'));OUT.mkdir(parents=True,exist_ok=True)
BASE='6484b9dacb8c4ab322cb26dcba8aab275d4f5cbe'
def load():
 g=read(ROOT/'photo2/r340/autoregion/graph.json.gz');obs={r['id']:r for r in g['observations']};co={r['id']:r['ab'] for r in g['coordinates']};rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));auth=read(ROOT/'photo2/r340/autoregion/freeze.json')['authoritative_labels'];old={r['id']:r for r in read(ROOT/'photo2/r340/autoregion/classification.json')['records']};return g,obs,co,rgb,auth,old

def local_geometry(g,obs):
 mids=np.array([(np.array(obs[e['source']]['xy'])+obs[e['target']]['xy'])/2 for e in g['edges']]);native=np.array([np.array(obs[e['target']]['xy'])-obs[e['source']]['xy'] for e in g['edges']]);ab=np.array([e['delta_ab'] for e in g['edges']]);tree=cKDTree(mids);rows={}
 for o,r in obs.items():
  ii=tree.query_ball_point(r['xy'],80);J=np.linalg.lstsq(ab[ii],native[ii],rcond=None)[0].T;spacing=float(np.median(np.linalg.norm(native[ii],axis=1)));axis=J@np.array([6.,-7.]);axis/=np.linalg.norm(axis);other=np.array([-axis[1],axis[0]]);rows[o]=dict(J=J.tolist(),spacing=spacing,cross_axis=axis.tolist(),long_axis=other.tolist(),local_edges=len(ii))
 return rows
if __name__=='__main__':
 g,obs,co,rgb,auth,old=load();geo=local_geometry(g,obs);save(OUT/'geometry.json',geo)
 for o in ['K-1740-1575','RF70T-K-2172-1154','K-2183-1053','C-1253-2928','C-1302-0316','C-0412-1572']:print(o,geo[o])
 print('Active colors',Counter(r['color'] for r in obs.values()))
