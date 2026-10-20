import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r339-mpl')
from pathlib import Path
import json,time,copy,math
from collections import Counter,defaultdict
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from scipy.spatial import cKDTree
from photo2.r337.common import ROOT,read,save,sha,motif,predict,COLORS
from photo2.r338.common import rope_clearance
BASE='f6ed047543c647dd30d7efda97244861a202fbc2'
def artifact(p):return Path(os.environ.get('R339_RUN_ROOT',ROOT/'photo2/r339'))/p
def baseline():
 g=read(ROOT/'photo2/r338/results/graph.json.gz');return g,{r['id']:r for r in g['observations']},{r['id']:r['ab'] for r in g['coordinates']}
def photograph():return np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
def authority():
 g,obs,co=baseline();auth={}
 ledger=read(ROOT/'photo2/r334/corrections/ledger.json')
 for r in ledger['ordinary_color_corrections']+[ledger['location_correction']]:auth[r['id']]=dict(color='black',source='R334 maker correction')
 for r in read(ROOT/'photo2/r335/results/application.json.gz')['records']:
  if r['maker_accepted']:auth[r['id']]=dict(color=r['color'],source='R335 maker review')
 for r in read(ROOT/'photo2/r336/results/maker-decisions.json')['decisions']:
  if r['maker_color']:auth[r['id']]=dict(color=r['maker_color'],source='R336 maker review')
 # R332 maker accepted labels in the specifically displayed R331 sets;
 # R337 accepted the two R336 displayed regions. Protect only those named
 # observations, never infer a whole-photo color certification.
 import ast
 for node in ast.walk(ast.parse((ROOT/'photo2/r331/review.py').read_text())):
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['gids','eids','fids','blackids'] for t in node.targets):
   for o in ast.literal_eval(node.value):
    if o in obs:auth.setdefault(o,dict(color=obs[o]['color'],source='R332 maker accepted specifically displayed R331 labels'))
 for panel in read(ROOT/'photo2/r336/review/panels.json').values():
  for k in panel['key']:
   if k['id'] in obs:auth.setdefault(k['id'],dict(color=obs[k['id']]['color'],source='R337 maker accepted displayed R336 labels/adjacency'))
 for o,r in obs.items():
  if r.get('review_authority') or r.get('reviewed_color') or r.get('maker_color'):auth.setdefault(o,dict(color=r['color'],source='Explicit observation maker provenance'))
 for r in read(artifact('maker/decisions.json'))['decisions']:
  if r.get('color'):auth[r['id']]=dict(color=r['color'],source='R339 own-panel maker review')
 return auth
def seal_inputs():
 import subprocess
 args=['photo2/r331/review.py','beads-photo-2.jpg','beads.pov']+[f'photo2/r{n}' for n in range(332,339)]+[f'photo2/R{n}_{kind}.md' for n in range(332,339) for kind in ['REPORT','REPRODUCE']]
 return {p:sha(ROOT/p) for p in subprocess.check_output(['git','ls-files',*args],cwd=ROOT,text=True).splitlines()}
def content_sha(path):
 import hashlib
 value=read(path)
 if isinstance(value,dict):value={k:v for k,v in value.items() if k!='seconds'}
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
