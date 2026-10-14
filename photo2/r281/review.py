"""Curated raw/annotated review and quantitative plots; evaluation only."""
import json,shutil
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import OUT,ROOT,read,save
from .detector import decide

REVIEW=ROOT/'photo2/review/r281'
def main():
 REVIEW.mkdir(parents=True,exist_ok=True);rules=read(OUT/'freeze.json')['rules'];data=[];real=read(OUT/'real/measurements.json');freeze=read(OUT/'real/prediction-freeze.json');pred={x['id']:x for x in freeze['predictions']};evidence=read(OUT/'real/photo-evidence.json')
 for name in ('raw','enlarged','phase1'):shutil.copyfile(OUT/'real'/(name+'.png'),REVIEW/('real-'+name+'.png'))
 for r in real['rows']:
  h=pred[r['id']]['hypothesis'];m=next(m for m in freeze['models'] if m['id']==r['model']);data.append(dict(id=r['id'],image='real-raw.png',hypothesis=h,result=r['result'],baseline=r['baseline'],phase1=[dict(id=o['id'],point=o['point'],anchor=o['id'] in evidence['anchor_ids']) for o in evidence['observations']],description=f"Real photo; {r['kind']}; hand {m['parameters']['hand']}; local labels {m['assignments']}. Physical identity unresolved.",details=dict(phase1_overlap=r['phase1_overlap'],anchor_ownership=m['anchor_ownership'],parameters=m['parameters'])))
 # Deterministic first examples of successes and important failures, no curation by prettiness.
 wanted=['present-supported','present-ambiguous','removed-repaired','removed-false','neighbor-false','phase-false','duplicate-ambiguous'];chosen={}
 for folder in sorted((OUT/'heldout').glob('scene-*')):
  for item in read(folder/'inference.json.gz'):
   if item['level']!=0 or item['orientation']!=0:continue
   r=item['result'];key=item['kind']+'-'+r['status']
   if item['kind']=='removed':key='removed-false' if r['status']=='supported' else 'removed-repaired' if item['baseline']['status']=='strong' else 'ignore'
   if item['kind'] in ('neighbor','phase') and r['status']=='supported':key=item['kind']+'-false'
   if key in wanted and key not in chosen:chosen[key]=(folder,item)
 for key,(folder,item) in chosen.items():
  name=key+'.png';shutil.copyfile(OUT/item['photo'],REVIEW/name);data.append(dict(id=f'{key}-{folder.name}-{item["query_target"]}',image=name,hypothesis=item['hypothesis'],result=item['result'],baseline=item['baseline'],phase1=[],description=f"Synthetic {key}; expected target {item['query_target']}; evaluation says negative={item['negative']}.",details=dict(scene=folder.name,kind=item['kind'],query_target=item['query_target'])))
 # Fresh confirmation examples are evaluation-only and never change selection rules.
 fresh={}
 if (OUT/'confirmation-frozen-summary.json').exists():
  for folder in sorted((OUT/'confirmation').glob('scene-*')):
   for item in read(folder/'inference.json.gz'):
    material=item['controls']['material'];combined=item['result'];key=None
    if item['kind']=='present' and item['level']==0:
     if material['status']=='supported' and combined['status']!='supported':key='material-extra-present'
     elif combined['status']=='supported' and material['status']!='supported':key='combined-extra-present'
    elif item['kind']=='removed' and material['status']=='supported':key='material-false-absent'
    elif item['kind']=='neighbor' and material['status']=='supported':key='material-false-neighbor'
    if key and key not in fresh:fresh[key]=(folder,item,'material')
    if item['kind']=='removed' and item['level']==0 and combined['status']=='supported':
     key='combined-false-absent-exact'
     if key not in fresh:fresh[key]=(folder,item,'combined')
    if item['kind']=='paper' and combined['status']=='supported':
     key='nominal-paper-shift-false'
     if key not in fresh:fresh[key]=(folder,item,'combined')
  for key,(folder,item,method) in fresh.items():
   name='confirmation-'+key+'.png';shutil.copyfile(OUT/item['photo'],REVIEW/name)
   result=item['result'] if method=='combined' else item['controls'][method]
   data.append(dict(id='confirmation-'+key,image=name,hypothesis=item['hypothesis'],result=result,baseline=item['baseline'],phase1=[],description=f"Fresh seed281403; {method}; {key}; shift {item['level']}D. Combined status: {item['result']['status']}. Physical identity is not established by material continuity.",details=dict(scene=folder.name,kind=item['kind'],query_target=item['query_target'],combined_result=item['result'])))
 (REVIEW/'data.js').write_text('window.REVIEW='+json.dumps(data,separators=(',',':'))+';\n')
 # Static panels for Markdown and convenient side-by-side review.
 from .common import mask_from_runs
 from .detector import boundary
 for i,r in enumerate(data):
  raw=np.asarray(Image.open(REVIEW/r['image']).convert('RGB'));ann=raw.copy();h=r['hypothesis'];target=mask_from_runs(h['h1_surfaces'].get(str(h['target']),[]),raw.shape[:2]);edge=boundary(target.astype(int));ann[edge]=[255,155,0]
  for key,col in [('support',[40,220,255]),('positive',[40,255,60]),('negative',[255,40,180])]:
   mask=mask_from_runs(r['result'][key],raw.shape[:2]);ann[mask]=(ann[mask]*.35+np.array(col)*.65).astype(np.uint8)
  Image.fromarray(np.concatenate([raw,ann],axis=1)).resize((raw.shape[1]*6,raw.shape[0]*3),Image.Resampling.NEAREST).save(REVIEW/(r['id']+'-panel.png'))
 stats=read(OUT/'heldout-statistics.json');summary=read(OUT/'heldout-frozen-summary.json');fig,axs=plt.subplots(1,3,figsize=(13,3.7))
 for method in ('material','boundary','combined'):
  c=stats['curves'][method];axs[0].plot([x['recall'] for x in c],[x['precision'] if x['precision'] is not None else np.nan for x in c],'.-',label=method)
 base=summary['R280']['paired:0.0'];axs[0].plot(base['recall'],base['precision'],'kx',ms=10,label='R280 fixed');axs[0].set(xlabel='Recall, easy present beads',ylabel='Precision, paired present/absent',xlim=(0,1.02),ylim=(0,1.02));axs[0].legend(fontsize=8)
 for method in ('R280','combined'):
  s=[summary[method][f'paired:{level}'] for level in (0.,.05,.1)];axs[1].plot([0,.05,.1],[x['recall'] for x in s],'o-',label=method+' recall');axs[1].plot([0,.05,.1],[x['false_rate'] for x in s],'s--',label=method+' false absent');axs[1].set(xlabel='Position error / diameter',ylabel='Fraction',ylim=(0,1.02));axs[1].legend(fontsize=8)
 kinds=['paper','neighbor','identity','phase','duplicate'];x=np.arange(len(kinds))
 for j,method in enumerate(('R280','combined')):
  axs[2].bar(x+(j-.5)*.35,[summary[method][f'{k}:d0.0:r0.0']['false_rate'] for k in kinds],.35,label=method)
 axs[2].set(xticks=x,xticklabels=kinds,ylabel='False confirmation fraction',ylim=(0,1.02));axs[2].tick_params(axis='x',rotation=25);axs[2].legend(fontsize=8)
 fig.tight_layout();fig.savefig(REVIEW/'sensitivity.png',dpi=170);plt.close(fig)
 save(REVIEW/'manifest.json',dict(examples=len(data),synthetic_categories=list(chosen),missing_categories=[k for k in wanted if k not in chosen],confirmation_categories=list(fresh),real_prediction_hash=real['prediction_freeze_sha256']))
 print('review examples',len(data))
if __name__=='__main__':main()
