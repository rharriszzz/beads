"""Final numerical summaries and photographic comparisons, not detector inputs."""
import json,csv
from collections import Counter
import numpy as np
from PIL import Image,ImageDraw
from .centerline_r275 import ROOT,OUT,Band,save,load_rows
from .review_r275 import panel,textfont

def main():
 data=json.loads((OUT/'inventory.json').read_text());old=json.loads((ROOT/'photo2/review/r274/inventory.json').read_text());im=Image.open(ROOT/'photo2/review/r272/photo-srgb.png');new={l['id']:l for l in data['locations']};groups=json.loads((OUT/'stations.json').read_text())['groups'];rows=[]
 for degree in range(0,360,30):
  gg=[g for g in groups if degree<=g['angle_degrees']<degree+30];steps=np.array([g['step_degrees'] for g in gg]);rows.append(dict(start_degrees=degree,end_degrees=degree+30,groups=len(gg),single=sum(g['members']==1 for g in gg),double=sum(g['members']==2 for g in gg),median_step_degrees=float(np.median(steps)),mean_step_degrees=float(steps.mean()),step_cv=float(steps.std()/steps.mean()),long_flags=sum(g['gap_flag'] for g in gg),short_flags=sum(g['short_flag'] for g in gg)))
 with (OUT/'angular-sectors.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 # Explicit observed run sequence, including circular transition at 360 degrees.
 runs=[]
 for g in groups:
  if not runs or runs[-1]['members']!=g['members']:runs.append(dict(members=g['members'],start_degrees=g['angle_degrees'],end_degrees=g['angle_degrees'],groups=1))
  else:runs[-1]['groups']+=1;runs[-1]['end_degrees']=g['angle_degrees']
 steps=np.array([g['step_degrees'] for g in groups]);save('angular-summary.json',dict(groups=len(groups),single=sum(g['members']==1 for g in groups),double=sum(g['members']==2 for g in groups),sum_degrees=float(steps.sum()),median_step_degrees=float(np.median(steps)),minimum_step_degrees=float(steps.min()),maximum_step_degrees=float(steps.max()),cv=float(steps.std()/steps.mean()),long_flags=sum(g['gap_flag'] for g in groups),short_flags=sum(g['short_flag'] for g in groups),sectors=rows,runs=runs,warning='Groups are diagnostic associations of observed points, not known bead centers, helical phases or physical string indices. Uniformity is not enforced.'))
 # Valid-looking reflections just outside the frozen point-reach rule are kept
 # separately; do not shrink the target around failures or silently expand it.
 edges=[];taken=[]
 for r in load_rows(OUT/'reflection-0.70-tinted-decisions.jsonl.gz')+load_rows(OUT/'dim-decisions.jsonl.gz'):
  if r.get('status')!='outside target' or r.get('reasons') or not r.get('brightest'):continue
  q=r['brightest'];point=np.array([q['x'],q['y']]);distance=r['band']['point_distance']
  if not 26<distance<=30 or any(np.linalg.norm(point-z)<8 for z in taken):continue
  taken.append(point);edges.append(dict(id=r['id'],point=q,color=r['color'],band=r['band'],reason='Photographic support passes checks but final native peak and support are outside the fixed target rule; membership proxy is uncertain near this boundary.'))
 save('band-edge-candidates.json',edges)
 comparisons=[]
 def comparison(name,point,before,after,explanation,excluded=False):
  x,y=map(int,point);box=[x-55,y-55,x+55,y+55];sheet=Image.new('RGB',(1010,370),'white');draw=ImageDraw.Draw(sheet)
  for j,(label,pic) in enumerate([('Original photograph',im.crop(box).resize((330,330),Image.Resampling.NEAREST)),('Before',panel(im,box,before['locations'],before['beads'],labels=False)),('Final R275',panel(im,box,after['locations'],after['beads'],labels=False))]):sheet.paste(pic,(j*340,30));draw.text((j*340+5,5),label,fill='black',font=textfont())
  if excluded:
   draw.ellipse((340*2+160,30+160,340*2+169,30+169),fill='#ffb14e');draw.rectangle((680,0,1010,27),fill='white');draw.text((685,5),'Orange: excluded candidate',fill='black',font=textfont())
  file=name+'.png';sheet.save(OUT/file);comparisons.append(dict(image=file,box=box,explanation=explanation))
 for i,c in enumerate(data.get('color_corrections',[]),1):
  id=c['id'];l=new[id];before=dict(locations=[z for z in data.get('superseded_locations',[]) if z['id']==id],beads=[z for z in data.get('superseded_beads',[]) if z['id']==id]);comparison(f'final-color-correction-{i}',[l['point']['x'],l['point']['y']],before,dict(locations=[l],beads=[b for b in data['beads'] if b['id']==id]),'Weak colored spill reclassified to a stronger neutral reflection on the same supported dark material; previous coordinates and region archived.')
 for i,l in enumerate(data.get('suppressed_locations',[]),1):
  before=dict(locations=data['locations']+[l],beads=data['beads']+[b for b in data['suppressed_beads'] if b['id']==l['id']]);comparison(f'final-duplicate-{i}',[l['point']['x'],l['point']['y']],before,data,'Weaker close black reflection removed by peak/contrast dominance and a continuous dark material bridge.')
 for i,id in enumerate(json.loads((OUT/'reflection-controls.json').read_text())['controls']['0.7-tinted']['new_ids'],1):

  if id not in new:continue
  l=new[id];comparison(f'final-reflection-{i}',[l['point']['x'],l['point']['y']],old,data,'Tighter native reflection component; dark surround with at most 25% confidently colored boundary permitted. Full shell evidence retained.')
 # Largest original angular gaps, separated for review. Points are display only.
 band=Band();curve=band.points;arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))];spacing=json.loads((OUT/'spacing.json').read_text());gg=spacing['summary']['r274']['whole-target']['large_gaps'];chosen=[]
 for g in sorted(gg,key=lambda r:-r['step_pixels']):
  s=(g['arc_px']+.5*g['step_pixels'])%spacing['summary']['r274']['whole-target']['total_length'];point=curve[min(len(curve)-1,np.searchsorted(arc,s))]
  if any(np.linalg.norm(point-p)<180 for p in chosen):continue
  chosen.append(point);comparison(f'final-gap-recovery-{len(chosen)}',point,old,data,f"Original {g['step_pixels']:.2f}px / {g['step_degrees']:.3f} degree gap; full-band recovery, not insertion at a predicted position.")
  if len(chosen)==4:break
 for i,r in enumerate(edges[:3],1):
  comparison(f'band-edge-{i}',[r['point']['x'],r['point']['y']],old,data,r['reason'],excluded=True)
 dim_rows=load_rows(OUT/'dim-decisions.jsonl.gz')
 for i,r in enumerate([r for r in dim_rows if r.get('band',{}).get('point_distance',99)<=30],1):
  q=r['brightest'];comparison(f'dim-edge-{i}',[q['x'],q['y']],old,data,'Dim hue-stable support passes photographic checks, but its final point is outside the fixed target band.',excluded=True)
 # Preserve the rejected homogeneous double-patch control photograph.
 import gzip
 prior=json.loads(gzip.decompress((OUT/'before-final-reflection-inventory.json.gz').read_bytes()))
 for pair in json.loads(gzip.decompress((OUT/'before-final-reflection-ownership-doubts.json.gz').read_bytes())):
  a=next(l for l in prior['locations'] if l['id']==pair['a']);comparison('final-colored-secondary',[a['point']['x'],a['point']['y']],prior,data,'Two disjoint patches on one red body are not two beads. A continuous same-color bridge to the stronger accepted point defers the weaker proposal.')
 save('comparisons.json',comparisons)
 atlas=json.loads((OUT/'atlas.json').read_text());save('final-artifacts.json',dict(atlas=[f"atlas-{r['tile']:02d}.jpg" for r in atlas],unresolved=[f"unresolved-{i+1:02d}.png" for i in range(len(json.loads((OUT/'unresolved-candidates.json').read_text())))],comparisons=[r['image'] for r in comparisons],group_flags=[r['image'] for r in json.loads((OUT/'group-flags.json').read_text())],note='Other gap/group/unresolved files are preserved intermediate experiments; use this manifest for the final set.'))
 print(dict(groups=len(groups),comparisons=len(comparisons)))
if __name__=='__main__':main()
