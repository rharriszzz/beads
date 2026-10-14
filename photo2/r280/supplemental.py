"""Additional descriptive metrics; never used for detector selection."""
import numpy as np
from collections import Counter
from .common import OUT,read,save
from .evaluate import summary

def main():
 rows=read(OUT/'heldout-evaluation.json.gz')['records'];out={}
 for test in ('A1','A2','A3','A4'):
  out[test]={}
  for tier in ('easy','moderate','hard'):
   rr=[r for r in rows if r['test']==test and r['tier']==tier and r['method']=='C' and r['status']=='strong'];errs=[r['location_error_diameter'] for r in rr if r['location_error_diameter'] is not None]
   out[test][tier]=dict(strong=len(rr),impure=sum(r['intended_purity']<.9 for r in rr),median_error_diameter=float(np.median(errs)) if errs else None,p90_error_diameter=float(np.percentile(errs,90)) if errs else None,mean_intended_purity=float(np.mean([r['intended_purity'] for r in rr])) if rr else None)
 color={};ps=[]
 for f in sorted((OUT/'heldout').glob('scene-*')):
  a=read(f/'A1-exact.json.gz');truth=read(f/'truth.json');ps.append(read(f/'phase1-associations.json'))
  for r in a['methods']['C']:
   if r['status']!='strong':continue
   c=('red','yellow','black')[truth['classes'][int(r['id'].replace('model-',''))+14]];color.setdefault(c,Counter())[r['color']]+=1
 central=[r for r in rows if r['method']=='C' and r['test']=='A1' and r['tier']=='easy' and abs(int(r['id'].replace('model-','')))<=7]
 save(OUT/'supplemental.json',dict(all_strong_measurements=out,reported_colors=color,central_segment_easy_posthoc=summary(central),phase1_standalone=dict(accepted=sum(r['accepted'] for r in ps),false_or_impure=sum(r['false_or_impure'] for r in ps)),note='Central-segment subset is an explicit post-hoc edge sensitivity, never a threshold selection. Color is measured from pixels, no truth input.'))
if __name__=='__main__':main()
