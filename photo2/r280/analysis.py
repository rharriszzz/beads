"""Post-freeze summaries/figures; no detector changes or operating-point tuning."""
import collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import OUT,read,save
from .evaluate import summary

def cluster_interval(rows,metric):
 scenes=sorted(set(r['scene'] for r in rows));rng=np.random.default_rng(280404);values=[]
 per={s:[r for r in rows if r['scene']==s] for s in scenes}
 for _ in range(1000):
  sample=[r for s in rng.choice(scenes,len(scenes),replace=True) for r in per[s]]
  v=summary(sample)[metric]
  if v is not None:values.append(v)
 return np.percentile(values,[2.5,97.5]).tolist() if values else None

def main():
 a=read(OUT/'heldout-evaluation.json.gz');rows=a['records'];targets=a['targets'];p1={(r['scene'],r['model_index']):r for r in a['phase1']};out=dict(scene_count=8,tiers=dict(collections.Counter(r['tier'] for r in targets)),metrics={},by_color={},cluster_intervals={},phase1={},incremental={},tradeoffs={})
 for method in 'PABC':
  out['metrics'][method]={};out['by_color'][method]={}
  for tier in ('easy','moderate','hard','all'):
   rr=[r for r in rows if r['method']==method and r['test']=='A1' and (tier=='all' or r['tier']==tier)]
   out['metrics'][method][tier]=summary(rr)
  for color in ('red','yellow','black'):
   rr=[r for r in rows if r['method']==method and r['test']=='A1' and r['color']==color]
   out['by_color'][method][color]=summary(rr)
  easy=[r for r in rows if r['method']==method and r['test']=='A1' and r['tier']=='easy']
  out['cluster_intervals'][method]={m:cluster_interval(easy,m) for m in ('precision','recall')}
  out['tradeoffs'][method]=[]
  if method!='P':
   for t in read(OUT/'freeze.json')['curves'][method]:
    out['tradeoffs'][method].append(dict(threshold=t['threshold'],**summary(easy,t['threshold'])))
 for tier in ('easy','moderate','hard'):
  rr=[r for r in p1.values() if r['tier']==tier and r['sufficient']]
  out['phase1'][tier]=dict(eligible=len(rr),distinct_found=sum(r['found'] for r in rr),duplicates=sum(r['duplicates'] for r in rr))
  rr=[r for r in rows if r['method']=='C' and r['test']=='A1' and r['tier']==tier and r['status']=='strong' and r['correct']]
  out['incremental'][tier]=[dict(scene=r['scene'],id=r['id']) for r in rr if not p1[(r['scene'],int(r['id'].replace('model-','')))]['found']]
 out['per_scene']={s:{m:summary([r for r in rows if r['scene']==s and r['method']==m and r['test']=='A1' and r['tier']=='easy']) for m in 'PABC'} for s in sorted(set(r['scene'] for r in rows))}
 save(OUT/'analysis.json',out)
 plt.rcParams.update({'font.size':10,'figure.dpi':140})
 fig,ax=plt.subplots(1,2,figsize=(10,4))
 for m,color in zip('ABC',['#777777','#df8800','#16804c']):
  rr=out['tradeoffs'][m];ax[0].plot([r['recall'] for r in rr],[r['precision'] for r in rr],'.-',label=m,color=color)
  for tier,style in [('easy','-'),('moderate','--')]:
   points=[]
   for kind,level in [('correct',0.),('position',.1),('position',.25),('position',.5)]:
    s=summary([r for r in rows if r['method']==m and r['kind']==kind and r['tier']==tier and r['test'] in ('A1','A2')]);points.append(s['recall'])
   ax[1].plot([0,.1,.25,.5],points,style,marker='.',label=m+' '+tier,color=color)
 p=out['metrics']['P']['easy'];ax[0].scatter([p['recall']],[p['precision']],marker='x',s=80,label='Frozen Phase1 + nearest query',color='#1875ab')
 ax[0].set(xlabel='Easy-bead recall',ylabel='Strong precision',title='A1 held-out tradeoff (fixed threshold grid)',xlim=(0,1.03),ylim=(0,1.03));ax[1].set(xlabel='Input shift / projected diameter',ylabel='Correct strong recall',title='A2 sensitivity, tiers kept separate',ylim=(0,1.03));[a.legend(fontsize=8) for a in ax];fig.tight_layout();fig.savefig(OUT/'accuracy-sensitivity.png');plt.close(fig)
 fig,axes=plt.subplots(1,3,figsize=(12,4))
 for ax,tier in zip(axes,('easy','moderate','hard')):
  cases=['A1-exact','A3-scale-0.75','A3-scale-1.25','A3-roll--20.0','A3-roll-20.0','A3-camera-15']
  for m in 'BC':
   vals=[summary([r for r in rows if r['case']==c and r['method']==m and r['tier']==tier]) for c in cases]
   ax.plot(range(len(cases)),[v['recall'] for v in vals],'.-',label=m+' recall');ax.plot(range(len(cases)),[v['precision'] for v in vals],':',label=m+' precision')
  ax.set_xticks(range(len(cases)),['Exact','s .75','s 1.25','r -20','r +20','cam+15'],rotation=45);ax.set_title('A3 '+tier);ax.set_ylim(0,1.03);ax.legend(fontsize=7)
 fig.tight_layout();fig.savefig(OUT/'scale-orientation.png');plt.close(fig)
 fig,ax=plt.subplots(figsize=(10,4));kinds=sorted(set(r['kind'] for r in rows if r['test']=='A4'))
 for i,m in enumerate('PABC'):
  vals=[summary([r for r in rows if r['method']==m and r['test']=='A4' and r['kind']==k and r['tier']=='easy'])['false_confirmation_rate'] for k in kinds]
  ax.bar(np.arange(len(kinds))+(i-1.5)*.2,vals,.2,label=m)
 ax.set_xticks(range(len(kinds)),kinds,rotation=25,ha='right');ax.set(ylabel='False strong confirmation rate',title='A4 easy-target adversarial predictions');ax.legend();fig.tight_layout();fig.savefig(OUT/'false-confirmations.png');plt.close(fig)
 print(out['metrics']['C']['easy']);print('incremental', {k:len(v) for k,v in out['incremental'].items()})
if __name__=='__main__':main()
