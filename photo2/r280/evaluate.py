"""Evaluation only. This module may read independent truth; detector cannot."""
import argparse,collections
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from .common import OUT,read,save,mask_from_runs
from .detector import classify,DEFAULT

def truth_rows(folder):
 truth=np.load(folder/'truth.npz')['owner'];g=read(folder/'geometry.json');t=read(folder/'truth.json');rgb=np.asarray(Image.open(folder/'photo.png'))/255.;lum=rgb@np.array([.2126,.7152,.0722]);p=g['parameters'];ang=np.radians(p['roll']);normal=np.array([-np.sin(ang),np.cos(ang)])
 rows=[]
 for j,pred in enumerate(g['predictions']):
  mask=truth==j;xy=np.argwhere(mask)[:,::-1];area=len(xy);isolated=mask_from_runs(pred['silhouette'],truth.shape).sum();frac=area/max(1,isolated);light=float(np.percentile(lum[mask],75)) if area else 0.;value75=float(np.percentile(rgb[mask].max(1),75)) if area else 0.
  central=abs((np.array(pred['center'])-g['parameters']['translation'])@normal)<4*g['parameters']['scale']*.65
  others=(truth>=0)&(truth!=j);distance=ndi.distance_transform_edt(~others);gap=float(distance[mask].min()) if area else 0.
  sufficient=area>=30 and frac>=.1
  centroids=[np.argwhere(truth==k)[:,::-1].mean(0) for k in range(29) if k!=j and np.sum(truth==k)>=30]
  center_gap=min((np.linalg.norm(xy.mean(0)-c) for c in centroids),default=0.)/pred['diameter'] if area else 0.
  tier='easy' if area>=150 and frac>=.65 and central and value75>=.25 and light>=.05 and center_gap>=.55 else ('moderate' if sufficient and light>=.08 else 'hard')
  rows.append(dict(index=j,model_index=j-14,area=area,visible_fraction=float(frac),luminance75=light,value75=value75,centroid_gap_diameter=float(center_gap),central=bool(central),gap_px=gap,sufficient=bool(sufficient),tier=tier,color=('red','yellow','black')[t['classes'][j]],centroid=xy.mean(0).tolist() if area else None,diameter=pred['diameter']))
 return truth,rows

def association(r,truth,target):
 mask=mask_from_runs(r['support'],truth.shape);values=truth[mask];n=len(values);ids,cnt=np.unique(values[values>=0],return_counts=True);owner=int(ids[cnt.argmax()]) if len(ids) else -1;purity=float(cnt.max()/n) if len(ids) else 0.
 intended=float(np.mean(values==target['index'])) if n else 0.;intersection=int(np.sum(values==target['index']));union=n+target['area']-intersection
 error=float(np.linalg.norm(np.array(r['location'])-target['centroid'])) if r['location'] is not None and target['centroid'] is not None else None
 return dict(owner=owner,purity=purity,intended_purity=intended,correct=bool(intended>=.9 and intersection>=8 and target['sufficient']),wrong_owner=bool(owner!=target['index'] and owner>=0 and purity>=.5),support_iou=float(intersection/max(1,union)),support_recall=float(intersection/max(1,target['area'])),location_error_px=error,location_error_diameter=error/target['diameter'] if error is not None else None,covered=bool(error is not None and r['uncertainty_radius_px'] is not None and error<=r['uncertainty_radius_px']))

def collect(split):
 records=[];tiers=[];phase1=[]
 for folder in sorted((OUT/split).glob('scene-*')):
  truth,targets=truth_rows(folder);tiers.extend(dict(scene=folder.name,**t) for t in targets)
  for path in sorted(folder.glob('A*.json.gz')):
   data=read(path)
   for method,results in data['methods'].items():
    for r in results:
     idx=int(r['id'].split('-false')[0].replace('model-',''))+14;target=targets[idx]
     records.append(dict(scene=folder.name,case=path.name[:-8],**data['metadata'],method=method,id=r['id'],false='-false' in r['id'],tier=target['tier'],color=target['color'],sufficient=target['sufficient'],visible_fraction=target['visible_fraction'],score=r['score'],status=r['status'],metrics=r['metrics'],positive_pixels=r['positive_pixels'],competing_ids=r['competing_ids'],**association(r,truth,target)))
  path=folder/'phase1.json.gz'
  if path.exists():
   b=read(path);results=[];by={r['id']:r for r in b['beads']}
   for loc in b['locations']:
    bead=by.get(loc['id']);runs=bead['region']['runs'] if bead else []
    mask=mask_from_runs(runs,truth.shape);vals=truth[mask];ids,cnt=np.unique(vals[vals>=0],return_counts=True);owner=int(ids[cnt.argmax()]) if len(ids) else -1
    results.append(dict(id=loc['id'],owner=owner,purity=float(cnt.max()/max(1,len(vals))) if len(ids) else 0.))
   for target in targets:
    matches=[r for r in results if r['owner']==target['index'] and r['purity']>=.9];phase1.append(dict(scene=folder.name,**target,found=bool(matches),duplicates=max(0,len(matches)-1)))
   save(folder/'phase1-associations.json',dict(associations=results,false_or_impure=sum(r['purity']<.9 for r in results),accepted=len(results)))
 save(OUT/(split+'-evaluation.json.gz'),dict(records=records,targets=tiers,phase1=phase1))
 return records,tiers,phase1

def summary(rows,threshold=None):
 statuses=[]
 for row in rows:
  r=dict(row)
  if threshold is not None:classify(r,{'strong':threshold})
  statuses.append(r)
 strong=[r for r in statuses if r['status']=='strong'];positive=[r for r in statuses if not r['false'] and r['sufficient']];correct=[r for r in strong if r['correct'] and not r['false']];false=[r for r in statuses if r['false']]
 errors=[r['location_error_diameter'] for r in correct if r['location_error_diameter'] is not None]
 return dict(predictions=len(rows),eligible=len(positive),strong=len(strong),correct=len(correct),precision=len(correct)/len(strong) if strong else None,recall=len(correct)/len(positive) if positive else None,wrong_owners=sum(r['wrong_owner'] for r in strong),false_predictions=len(false),false_confirmations=sum(r['false'] for r in strong),false_confirmation_rate=sum(r['false'] for r in strong)/len(false) if false else None,ambiguity=sum(r['status']=='ambiguous' for r in statuses)/max(1,len(rows)),abstention=sum(r['status'] in ('ambiguous','insufficient','partial') for r in statuses)/max(1,len(rows)),median_error_diameter=float(np.median(errors)) if errors else None,uncertainty_coverage=float(np.mean([r['covered'] for r in correct])) if correct else None,mean_support_iou=float(np.mean([r['support_iou'] for r in correct])) if correct else None,mean_support_purity=float(np.mean([r['intended_purity'] for r in correct])) if correct else None,statuses=dict(collections.Counter(r['status'] for r in statuses)))

def report(split):
 records,targets,baseline=collect(split);out={}
 for method in sorted(set(r['method'] for r in records)):
  out[method]={}
  for test in sorted(set(r['case'] for r in records)):
   out[method][test]={tier:summary([r for r in records if r['method']==method and r['case']==test and (tier=='all' or r['tier']==tier)]) for tier in ('easy','moderate','hard','all')}
 save(OUT/(split+'-summary.json'),out)
 print('tiers',dict(collections.Counter(t['tier'] for t in targets)))
 for m in out:print(m,out[m].get('A1-exact'))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('split');report(p.parse_args().split)
