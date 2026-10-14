"""Frozen evaluation, scene-level uncertainty and sensitivity curves."""
import numpy as np
from .common import OUT,read,save
from .evaluate import evaluate,summarize
from .detector import decide

def cluster(rows,rules):
 scenes=sorted(set(r['scene'] for r in rows));rng=np.random.default_rng(281303);draw=[]
 for _ in range(2000):
  sample=[r for s in rng.choice(scenes,len(scenes)) for r in rows if r['scene']==s]
  stats=[]
  for method in ('R280','combined'):
   st=summarize([r for r in sample if r['method']==method],rules);stats.append(st)
  draw.append([stats[1]['recall'],stats[1]['false_rate'],stats[1]['false_rate']-stats[0]['false_rate'],stats[1]['recall']-stats[0]['recall']])
 a=np.array(draw);return dict(unit='scene; all queries from sampled scene retained',populated_scenes=len(scenes),bootstrap_replicates=2000,percentile95={k:np.quantile(a[:,i],[.025,.975]).tolist() for i,k in enumerate(('recall','false_rate','false_rate_difference','recall_difference'))},zero_failure_scene_one_sided95_upper=float(1-.05**(1/len(scenes))))

def main(split):
 rows=evaluate(split);rules=read(OUT/'freeze.json')['rules'];out={}
 for method in ('R280','material','boundary','combined'):
  rr=[r for r in rows if r['method']==method];out[method]={}
  for kind,level,angle in sorted(set((r['kind'],r['level'],r['orientation']) for r in rr)):
   out[method][f'{kind}:d{level}:r{angle}']=summarize([r for r in rr if (r['kind'],r['level'],r['orientation'])==(kind,level,angle)],rules)
  for level in (0.,.05,.1):out[method][f'paired:{level}']=summarize([r for r in rr if r['kind'] in ('present','removed') and r['level']==level],rules)
 save(OUT/(split+'-frozen-summary.json'),out)
 paired=[r for r in rows if r['kind'] in ('present','removed') and r['level']==0]
 groups={color:{method:summarize([r for r in paired if r['color']==color and r['method']==method],rules) for method in out} for color in sorted(set(r['color'] for r in paired))}
 curve={method:[dict(threshold=float(t),**summarize([r for r in paired if r['method']==method],{**rules,'margin':float(t)})) for t in np.linspace(0,.7,36)] for method in ('material','boundary','combined')}
 positive=[r for r in paired if r['method']=='combined' and r['correct'] and decide(r,rules)['status']=='supported'];errors=[r['error_diameter'] for r in positive]
 save(OUT/(split+'-statistics.json'),dict(cluster=cluster(paired,rules),color=groups,curves=curve,localization=dict(n=len(errors),median=float(np.median(errors)) if errors else None,p95=float(np.quantile(errors,.95)) if errors else None,coverage_of_nominal_point15D=float(np.mean(np.array(errors)<=.15)) if errors else None,uncertainty_note='Nominal support-centroid radius, not a calibrated confidence interval or physical-center uncertainty.')))
 print(split,{m:out[m]['paired:0.0'] for m in out})
if __name__=='__main__':
 import sys
 main(sys.argv[1])
