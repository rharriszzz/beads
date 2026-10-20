"""Freeze geometry from manual material annotations; no color-score optimization."""
import sys,json,gzip,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image,ImageOps
from photo2.r337.common import read
OUT=Path(os.environ.get('R340_MATERIAL_RUN_ROOT',Path(__file__).parent))
OUT.mkdir(parents=True,exist_ok=True)

def setup():
 g=read(ROOT/'photo2/r339/results/graph.json.gz');obs={o['id']:o for o in g['observations']};co={o['id']:o['ab'] for o in g['coordinates']};photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
 geom={r['id']:{k:r[k] for k in ['spacing','physical_interior','clearance','indexed']} for r in read(ROOT/'photo2/r339/classification/classification.json.gz')['records']}
 auth=read(ROOT/'photo2/r339/results/freeze.json')['authoritative_labels']
 for o in ['E5-2272-1815','NEW-2156-1135','MAT25-K-2142-2497','K-1663-3006','NEW-1247-2991','NEW-2235-1476']:auth[o]=dict(color='black',source='R340 direct maker confirmation')
 return g,obs,co,photo,geom,auth

def calibrate(manual,geom):
 training=[r for r in manual if r['number']%2==1];offset=[];radius=[]
 for r in training:
  x,y,u,v=r['absolute_material_box'];s=geom[r['id']]['spacing'];offset.append(((x+u-1)/2-np.array(r['xy'])[0],(y+v-1)/2-np.array(r['xy'])[1]));offset[-1]=np.array(offset[-1])/s;radius.append((min(u-x,v-y)-1)/2/s)
 return dict(offset_fraction=np.median(offset,axis=0).tolist(),radius_fraction=float(np.median(radius)),training_ids=[r['id'] for r in training],heldout_ids=[r['id'] for r in manual if r['number']%2==0],policy='Geometry fit only: median normalized manual glass-interior center offset and median inscribed radius; odd-numbered24 train, even-numbered24 reserved. No brightness or color optimizes geometry. Single fixed disk per bead.')

def region(photo,xy,spacing,model):
 center=np.array(xy)+spacing*np.array(model['offset_fraction']);radius=spacing*model['radius_fraction'];x0,y0=np.floor(center-radius).astype(int);x1,y1=np.ceil(center+radius).astype(int)+1
 if x0<0 or y0<0 or x1>photo.shape[1] or y1>photo.shape[0]:return None
 yy,xx=np.mgrid[y0:y1,x0:x1];mask=(xx-center[0])**2+(yy-center[1])**2<=radius**2
 win=np.lib.stride_tricks.sliding_window_view(mask,(3,3)).all(axis=(-2,-1));v=photo[y0:y1,x0:x1].max(2);patches=np.lib.stride_tricks.sliding_window_view(v,(3,3)).max(axis=(-2,-1)).astype(int);patches[~win]=256
 if not win.any():return None
 y,x=np.unravel_index(patches.argmin(),patches.shape);ax=int(x0+x);ay=int(y0+y)
 return dict(center=center.tolist(),radius=radius,region_pixels=np.c_[xx[mask],yy[mask]].tolist(),patch_box=[ax,ay,ax+3,ay+3],score=int(patches[y,x]),patch_RGB=photo[ay:ay+3,ax:ax+3].tolist(),decision='black' if patches[y,x]<73.5 else 'not-black')

def main():
 g,obs,co,photo,geom,auth=setup();manual=read(ROOT/'photo2/r340/material-diagnostic/measurements.json')['records'];model=calibrate(manual,geom);(OUT/'geometry-model.json').write_text(json.dumps(model,indent=2)+'\n');rows=[]
 for o in sorted(obs):
  r=region(photo,obs[o]['xy'],geom[o]['spacing'],model);rows.append(dict(id=o,xy=obs[o]['xy'],recorded_color=obs[o]['color'],geometry=geom[o],authority=auth.get(o),measurement=r))
 (OUT/'trial-1.json').write_text(json.dumps(dict(model=model,records=rows),indent=2)+'\n')
 for name,ids in [('manual48',[r['id'] for r in manual]),('heldout24',model['heldout_ids']),('additional_authoritative',[o for o in auth if o in obs and o not in {r['id'] for r in manual}]),('darkred_controls',['C-0309-0966','C-0313-1445','C-1899-0420'])]:
  rr=[r for r in rows if r['id'] in ids];wrong=[r for r in rr if r['measurement'] and (r['measurement']['decision']=='black')!=((r['authority'] or dict(color='red'))['color']=='black')];print(name,len(rr),'wrong',[(r['id'],r['recorded_color'],r['measurement']['score'],r['geometry']['physical_interior']) for r in wrong])
 print('model',model)
 print('raw nonblack->black',[(r['id'],r['recorded_color'],r['measurement']['score']) for r in rows if r['recorded_color']!='black' and r['measurement'] and r['measurement']['decision']=='black'])
if __name__=='__main__':main()
