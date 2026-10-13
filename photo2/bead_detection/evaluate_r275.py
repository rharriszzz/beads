"""Known-identity stress tests; detector sees pixels and a reference line only."""
from collections import Counter
from dataclasses import replace
import time
import numpy as np
from .centerline_r275 import Band,save,write_rows
from .recover_r275 import Recovery,resolve
from .ownership_r275 import contract
from .connected_r275 import connected
from .dominance_r275 import suppress
from .reclassify_r275 import correct
from .core_r275 import core
from .dim_r275 import proposals as dim_proposals
from .homogeneous_r275 import guard_ownership
from .reflection_r275 import reflection_region
from scipy.spatial import cKDTree
from .interiors_r273 import pixels
from .coverage_r272 import detect,Parameters,black_region
from .hue_r274 import refine
from .synthetic_r274 import scenes
from .evaluate_coverage_r272 import scenes as other_scenes,metric,add_metrics,finish

def main():
 start=time.time();total={c:Counter() for c in ('black','red','yellow')};results=[];records=[]
 items=list(scenes())+[(n,r,t,c) for n,r,t,c,_ in other_scenes()]
 for name,rgb,truth,colors in items:
  base=detect(rgb)[0];b,l,*_=refine(rgb,rgb,base);old=dict(beads=b,locations=l);band=Band(np.array([[rgb.shape[1]/2,0],[rgb.shape[1]/2,rgb.shape[0]-1]]));engine=Recovery(rgb,rgb,base,band);rows=[];frozen={r['id'] for r in b}
  for r in base:
   if r['id'] not in frozen and r['color']!='black':rows.append(engine.interior(r))
  for peak in engine.peaks():
   r=engine.new_colored(peak['anchor'],'E'+str(peak['window']),True)
   if r.get('region'):r=engine.interior(r,layered=True)
   rows.append(r)
  for peak in engine.peaks(black=True):
   r=dict(id='N-'+peak['id'],anchor=peak['anchor'],accepted=False,reasons=[],confidence={});black_region(r,rgb,rgb,engine.hsv,engine.nhsv,engine.lum,engine.paper,replace(Parameters(),black_peak_value=.18,black_contrast=.10));rows.append(r)
  beads,loc,decisions=resolve(rows,old,band)
  extra=[]
  for peak in engine.peaks(black=True):
   r=dict(id='D40-'+peak['id'],anchor=peak['anchor'],accepted=False,reasons=[],confidence={});black_region(r,rgb,rgb,engine.hsv,engine.nhsv,engine.lum,engine.paper,replace(Parameters(),black_maximum_value=.40));extra.append(r)
  beads,loc,more=resolve(extra,dict(beads=beads,locations=loc),band);decisions+=more
  engine.pale=True;extra=[]
  for peak in engine.peaks():
   r=engine.new_colored(peak['anchor'],'P'+str(peak['window']),True)
   if not r.get('color_evidence',{}).get('pale_highlight_evidence',{}).get('accepted'):continue
   if r.get('region'):r=engine.interior(r,layered=True)
   extra.append(r)
  beads,loc,more=resolve(extra,dict(beads=beads,locations=loc),band);decisions+=more
  owned=set().union(*(pixels(r) for r in beads));extra=[contract(r,owned,rgb,rgb,engine.hsv,engine.lum) for r in decisions if r.get('color') in ('red','yellow') and r.get('region') and r['reasons']==['ownership-conflict']]
  beads,loc,more=resolve(extra,dict(beads=beads,locations=loc),band);decisions+=more
  extra=[]
  for peak in engine.peaks(black=True):
   r=dict(id='MAT25-'+peak['id'],anchor=peak['anchor'],accepted=False,reasons=[],confidence={});black_region(r,rgb,rgb,engine.hsv,engine.nhsv,engine.lum,engine.paper,replace(Parameters(),black_maximum_value=.40,black_surround_fraction=.25));extra.append(r)
  beads,loc,more=resolve(extra,dict(beads=beads,locations=loc),band);material_decisions=more;decisions+=more;owned=set().union(*(pixels(r) for r in beads));known=np.array([[l['point']['x'],l['point']['y']] for l in loc]);extra=[]
  for peak in engine.peaks():
   if peak['score']<.025 or (len(known) and np.linalg.norm(known-peak['anchor'],axis=1).min()<7):continue
   x,y=peak['anchor'];color,ev=engine.classify(x,y,True)
   if color is None:continue
   r=dict(id=f'CON{peak["window"]}-{x:04d}-{y:04d}',anchor=peak['anchor'],color=color,color_evidence=ev,confidence={},accepted=False,reasons=[]);extra.append(connected(engine,r,owned))
  beads,loc,more=resolve(extra,dict(beads=beads,locations=loc),band);decisions+=more;owned=set().union(*(pixels(r) for r in beads));known=np.array([[l['point']['x'],l['point']['y']] for l in loc]);peaks=engine.peaks();trees={n:cKDTree([p['anchor'] for p in peaks if p['window']==n]) for n in (5,7,9)} if peaks and all(any(p['window']==n for p in peaks) for n in (5,7,9)) else {};extra=[]
  for peak in peaks:
   if peak['window']!=7 or peak['score']<.04 or not trees or (len(known) and np.linalg.norm(known-peak['anchor'],axis=1).min()<7):continue
   if max(trees[n].query(peak['anchor'])[0] for n in (5,7,9))>3:continue
   r=engine.new_colored(peak['anchor'],'CORE',True)
   if r.get('region'):extra.append(core(engine,r,owned))
  beads,loc,more=resolve(extra,dict(beads=beads,locations=loc),band);decisions+=more;active,dominance=suppress(dict(beads=beads,locations=loc),rgb,rgb,band);active,corrections=correct(active,material_decisions,rgb,rgb,band);engine.homogeneous=True;known=np.array([[l['point']['x'],l['point']['y']] for l in active['locations']]);owned=set().union(*(pixels(r) for r in active['beads']));extra=[]
  for peak in peaks:
   if peak['score']<.08 or (len(known) and np.linalg.norm(known-peak['anchor'],axis=1).min()<8):continue
   r=engine.new_colored(peak['anchor'],'H'+str(peak['window']),True)
   if not r.get('region') or r['color_evidence']['required_prototype_margin']!=4:continue
   result=engine.interior(r,layered=True)
   if not result.get('accepted'):result=core(engine,r,owned)
   extra.append(guard_ownership(result,active,engine))
  beads,loc,more=resolve(extra,active,band);decisions+=more;extra=[]
  for peak in engine.peaks(black=True):
   r=dict(id='RF70-'+peak['id'],anchor=peak['anchor'],accepted=False,reasons=[],confidence={});reflection_region(r,rgb,rgb,engine.hsv,engine.nhsv,engine.lum,engine.paper,replace(Parameters(),black_maximum_value=.40,black_surround_fraction=.25),.70,list(engine.palette.values()),True);extra.append(r)
  beads,loc,more=resolve(extra,{**active,'beads':beads,'locations':loc},band);decisions+=more;final,_=suppress({**active,'beads':beads,'locations':loc},rgb,rgb,band);engine.homogeneous=False;beads,loc,more=resolve(dim_proposals(engine,peaks,final),final,band);decisions+=more;m,a=metric(beads,truth,colors);add_metrics(total,m);results.append(dict(scene=name,baseline=len(b),accepted=len(beads),metrics=m,associations=a));records.extend(dict(scene=name,**r) for r in decisions)
  if len(results)%10==0:print('scenes',len(results),flush=True)
 save('synthetic-evaluation.json',dict(scenes=len(results),metrics=finish(total),results=results,elapsed_seconds=time.time()-start,scope='End-to-end R272/R274 baseline plus consistent R275 recovery. Truth is evaluation-only; no 100% photographic conclusion.'));write_rows('synthetic-decisions.jsonl.gz',records);print(finish(total),flush=True)
if __name__=='__main__':main()
