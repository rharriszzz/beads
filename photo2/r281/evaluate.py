"""Truth access confined to evaluation. All predictions were saved first."""
import argparse
from collections import Counter
import numpy as np
from PIL import Image
from .common import OUT,read,save,mask_from_runs
from .detector import decide

def evaluate(split):
 rows=[]
 for f in sorted((OUT/split).glob('scene-*')):
  path=f/'inference.json.gz'
  if not path.exists():continue
  targets={r['model_index']:r for r in read(f/'evaluation-targets.json')['targets']};truth=np.load(f/'truth.npz')['owner']
  for record in read(path):
   target=targets[record['query_target']];rgb=np.asarray(Image.open(OUT/record['photo']));image_truth=truth if not record['kind'].startswith('removed') else np.asarray(Image.open((OUT/record['photo']).with_name('identity.png')))[:,:,0].astype(int)-1
   for method,result in [('R280',record['baseline']),('combined',record['result']),*record['controls'].items()]:
    support=mask_from_runs(result['support'],truth.shape);values=image_truth[support];intended=target['index'];purity=float(np.mean(values==intended)) if len(values) else 0.;ids,n=np.unique(values[values>=0],return_counts=True);owner=int(ids[n.argmax()]) if len(ids) else -1
    loc=result['location'];error=float(np.linalg.norm(np.array(loc)-target['centroid'])/target['diameter']) if loc is not None else None
    rows.append(dict(scene=f.name,target=record['query_target'],kind=record['kind'],level=record['level'],orientation=record['orientation'],negative=record['negative'],method=method,status=result['status'],accepted=result['status'] in ('strong','supported'),correct=bool(not record['negative'] and purity>=.90 and support.sum()>=8),purity=purity,owner=owner,wrong_owner=bool(owner>=0 and owner!=intended),error_diameter=error,color=target['color'],**({k:record['result'][k] for k in ('margin','material_margin','boundary_margin','metrics','support_pixels','competing_ids')} if method!='R280' else {})))
 save(OUT/(split+'-evaluation.json.gz'),rows);return rows

def summarize(rows,rules=None):
 if rules is not None:
  rows=[{**r,'accepted':decide(r,rules,r['method'])['status']=='supported','status':decide(r,rules,r['method'])['status']} if r['method']!='R280' else r for r in rows]
 pos=[r for r in rows if not r['negative']];neg=[r for r in rows if r['negative']];accept=[r for r in rows if r['accepted']];tp=[r for r in accept if r['correct']];false=[r for r in accept if r['negative']];impure=[r for r in accept if not r['negative'] and not r['correct']]
 return dict(n=len(rows),positive=len(pos),negative=len(neg),true_positives=len(tp),false_confirmations=len(false),impure_positives=len(impure),accepted=len(accept),precision=len(tp)/len(accept) if accept else None,recall=len(tp)/len(pos) if pos else None,false_rate=len(false)/len(neg) if neg else None,ambiguous=sum(r['status']=='ambiguous' for r in rows),contradicted=sum(r['status']=='contradicted' for r in rows),insufficient=sum(r['status']=='insufficient' for r in rows),wrong_owners=sum(r['wrong_owner'] for r in accept),median_error_diameter=float(np.median([r['error_diameter'] for r in tp])) if tp else None,mean_purity=float(np.mean([r['purity'] for r in accept])) if accept else None)

def main(split):
 rows=evaluate(split);out={}
 for method in ('R280','material','boundary','combined'):
  out[method]={}
  for kind,level,angle in sorted(set((r['kind'],r['level'],r['orientation']) for r in rows)):
   rr=[r for r in rows if (r['method'],r['kind'],r['level'],r['orientation'])==(method,kind,level,angle)];out[method][f'{kind}:d{level}:r{angle}']=summarize(rr)
 save(OUT/(split+'-summary.json'),out)
 for m in out:
  print(m,{k:v for k,v in out[m].items() if k in ('present:d0.0:r0.0','removed:d0.0:r0.0')})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('split');main(p.parse_args().split)
