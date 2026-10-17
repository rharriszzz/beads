"""Actual trial coverage, indexing alternatives, readiness and fixed bracket review."""
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
from photo2.r297.common import ROOT,read,save,sha
from photo2.r314.run import engine
from .diagnose import OUT
from .measurement import measure_readiness
from .review import FONT,card

def main():
 e=engine();m=e.m;trials=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];narrow=[read(p) for p in sorted((OUT/'narrow-trials').glob('*.gz'))];historical=[read(p) for p in sorted((ROOT/'photo2/r314/results/trials').glob('*.gz'))];coverage=[]
 for name,rs in [('R314',historical),('R315 controls and compact',trials),('R315 narrow',narrow)]:
  ranges={};keys=sorted(set(k for r in rs for k,v in r['parameters'].items() if isinstance(v,(int,float)) and not isinstance(v,bool)))
  for k in keys:
   vv=[r['parameters'][k] for r in rs if k in r['parameters']];ranges[k]=dict(min=min(vv),max=max(vv),unique=len(set(vv)))
  coverage.append(dict(epoch=name,trials=len(rs),classifications=dict(Counter(r['classification'] for r in rs)),discrete=dict(Counter(str((r['parameters']['count'],r['parameters']['hand'],r['parameters']['topology'])) for r in rs)),scalar_ranges=ranges,duplicate_parameters=len(rs)-len({str(sorted(r['parameters'].items())) for r in rs})))
 # Constant owner shifts compared on the SAME fixed cores; identities remain unverified.
 rows=read(OUT/'baseline-summary.json.gz');base={c['id']:c for key in ['development','comparison','buffer'] for c in rows[0]['metrics'][key]['cores']};assignments=[]
 for r in rows[1:]:
  cs=[c for key in ['development','comparison','buffer'] for c in r['metrics'][key]['cores']];differences=[c['index']-base[c['id']]['index'] for c in cs if c['index'] is not None and base[c['id']]['index'] is not None];counts=Counter(differences);shift,num=counts.most_common(1)[0];assignments.append(dict(model=r['name'],compared=len(differences),difference_histogram=dict(counts),best_uniform_shift=shift,explained=num,unexplained=len(differences)-num,minor_revolution_shifts={str(k):counts[k] for k in [-7,-6,6,7]},physical_identity_established=False))
 # First observed failures at several declared thresholds, not a verified chain.
 old=read(ROOT/'photo2/r314/results/geometry-diagnostics.json.gz');arc={r['id']:r['arc'] for r in old['models'][0]['regions']};first=[];ready=[]
 for name in ['baseline','translation','compact','narrow']:
  r=read(OUT/f'{name}-model.json.gz');a=np.load(OUT/f'{name}-raster.npz');tr={k:a[k] for k in ['owner','unknown']};cs=[c for key in ['development','comparison','buffer'] for c in r[key]['cores']]
  for threshold in [.6,.7,.8,.9]:
   for direction in [-1,1]:
    fail=sorted([c for c in cs if c['id']!='C-1497-0271' and direction*arc[c['id']]>0 and c['modal_fraction']<threshold],key=lambda c:abs(arc[c['id']]));first.append(dict(model=name,threshold=threshold,direction=direction,first=None if not fail else dict(id=fail[0]['id'],point=fail[0]['point'],arc=arc[fail[0]['id']],conditional_index=fail[0]['index'],modal_fraction=fail[0]['modal_fraction'])))
  ready.append(dict(name=name,splits={key:measure_readiness(e,tr,r[key],i) for i,key in enumerate(['development','comparison','buffer'])}))
 save(OUT/'search-coverage.json',dict(epochs=coverage,policy='Actual evaluated scalar ranges and discrete families; vector fields retained in every trial. R315 search retains geometry family per parent; no new count/hand census. Duplicate test compares exact serialized parameters.'))
 save(OUT/'indexing-and-readiness.json',dict(uniform_shift_controls=assignments,first_failures=first,readiness=ready,observed_adjacency='No independent verified +1/+6/+7 chain; core labels and optical nearest matches cannot create one.'))
 # Fixed endpoint integrity and missing-bracket raw-photo atlas.
 bs=read(OUT/'baseline-brackets.json.gz');cards=[];endpoint=[]
 for b in bs:
  p=np.array(b['material_endpoint'])-m['origin'];q=np.array(b['paper_endpoint'])-m['origin'];assert m['material'][p[1],p[0]] and m['paper'][q[1],q[0]];endpoint.append(dict(id=b['id'],material=True,paper=True,strength=b['strength']))
  if not b['outside_old_scan']:continue
  x,y=p;lo=np.maximum([0,0],p-30);hi=np.minimum(np.array(e.shape)[::-1],p+31);raw=m['native'][lo[1]:hi[1],lo[0]:hi[0]];im=card(raw,f"bracket {b['id']}: excess {b['displacement']:.0f}px",3);d=ImageDraw.Draw(im);pa=(p-lo)*3;qa=(q-lo)*3;d.line([tuple(pa+[0,38]),tuple(qa+[0,38])],fill='white',width=2)
  for z,col in [(pa,'lime'),(qa,'blue')]:d.ellipse((z[0]-3,z[1]+35,z[0]+3,z[1]+41),fill=col)
  cards.append(im)
 if cards:
  w=max(i.width for i in cards);h=max(i.height for i in cards);canvas=Image.new('RGB',(w*6,h*((len(cards)+5)//6)),'#eeeeee')
  for i,im in enumerate(cards):canvas.paste(im,((i%6)*w,(i//6)*h))
  canvas.save(OUT/'review/bracket-failures.png')
 save(OUT/'bracket-endpoint-audit.json',dict(count=len(bs),all_endpoints_retained=True,rows=endpoint,classification_caveat='Photographic color/erosion criteria are uncalibrated. Endpoints do not prove intervening complete silhouettes, calibrated edge positions, or distinct physical bead identities. No post-fit reclassification.'))
 # Freeze actual source and input provenance after the instrumentation is complete.
 save(OUT/'provenance.json',dict(sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'photo2/r315').glob('*.py'))},inputs={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'beads-photo-2.jpg',ROOT/'photo2/r314/evidence/maps.npz',ROOT/'photo2/r314/evidence/freeze.json',ROOT/'photo2/r314/results/observation-catalog.json.gz']}))
if __name__=='__main__':main()
