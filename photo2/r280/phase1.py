"""Frozen R275 synthetic chain; only evaluation I/O/domain wrapper changed.
Copied from evaluate_r275.py, with all thresholds and measurement calls retained.
R278 recovery uses the same existing functions, with FullDomain instead of old
photograph-specific Band. No historical geometric data are read.
"""
"""Known-identity stress tests; detector sees pixels and a reference line only."""
from collections import Counter
from dataclasses import replace
import time
import numpy as np
from photo2.bead_detection.centerline_r275 import Band,save,write_rows
from photo2.bead_detection.recover_r275 import Recovery,resolve
from photo2.bead_detection.ownership_r275 import contract
from photo2.bead_detection.connected_r275 import connected
from photo2.bead_detection.dominance_r275 import suppress
from photo2.bead_detection.reclassify_r275 import correct
from photo2.bead_detection.core_r275 import core
from photo2.bead_detection.dim_r275 import proposals as dim_proposals
from photo2.bead_detection.homogeneous_r275 import guard_ownership
from photo2.bead_detection.reflection_r275 import reflection_region
from scipy.spatial import cKDTree
from photo2.bead_detection.interiors_r273 import pixels
from photo2.bead_detection.coverage_r272 import detect,Parameters,black_region
from photo2.bead_detection.hue_r274 import refine
from photo2.bead_detection.synthetic_r274 import scenes
from photo2.bead_detection.evaluate_coverage_r272 import scenes as other_scenes,metric,add_metrics,finish


class FullDomain:
 def distance(self,points):return np.zeros(np.asarray(points).shape[:-1])
 def qualifies(self,point,region=None):return dict(in_band=True)

def detect_phase1(rgb):
 base=detect(rgb)[0];b,l,*_=refine(rgb,rgb,base);old=dict(beads=b,locations=l);band=FullDomain();engine=Recovery(rgb,rgb,base,band);rows=[];frozen={r['id'] for r in b}
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
 beads,loc,more=resolve(extra,{**active,'beads':beads,'locations':loc},band);decisions+=more;final,_=suppress({**active,'beads':beads,'locations':loc},rgb,rgb,band);engine.homogeneous=False;beads,loc,more=resolve(dim_proposals(engine,peaks,final),final,band);decisions+=more
 from .recovery_adapter import recover
 from photo2.bead_detection.phase1_r278 import confidence_gate
 old=dict(beads=beads,locations=loc)
 _,fs,proposals=recover(rgb,rgb,old,base)
 for r in proposals:confidence_gate(r)
 beads,loc,more=resolve(proposals,old,band);decisions+=more
 return dict(beads=beads,locations=loc,decisions=decisions)
