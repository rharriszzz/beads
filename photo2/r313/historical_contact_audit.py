"""Revisit selected R312 inconclusive gates using actual hollow solids."""
import time
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,read,save,sha
from photo2.r306.evidence import load
from photo2.r312.fast import Chain
from photo2.r295.contact_fallback import audit_pair
from .objective import Objective

def main():
 began=time.monotonic();data,_,_=load();ev=ROOT/'photo2/r313/evidence';eng=Objective(dict(np.load(ev/'maps.npz')),read(ev/'freeze.json'));out=ROOT/'photo2/r313/continuation';failed=[]
 for path in (ROOT/'photo2/r312/results/campaign/stage1/trials').glob('*.json.gz'):
  r=read(path);p=r.get('physical',r.get('result',{}).get('physical',{}))
  if p and not p.get('certified',True):failed.append((path,r,p))
 print('historical unresolved gates',len(failed),flush=True)
 failed.sort(key=lambda row:(row[2].get('unresolved_pairs',1e6),-row[2].get('minimum_gap_units',-1e6)))
 picked=[];seen=set()
 for path,r,p in failed:
  key=(r['parameters']['count'],r['parameters']['hand'],round(p.get('minimum_gap_units',-1),5))
  if key in seen:continue
  seen.add(key);picked.append((path,r,p))
  if len(picked)==12:break
 rows=[]
 for path,r,old in picked:
  s=Chain(r['parameters'],data);c=s.certify(iterations=220,witnesses=True);checks=[];state='certified-separation' if c['certified'] else 'unresolved';start=time.monotonic()
  for w in sorted([w for w in c['witnesses'] if not w['separated']],key=lambda w:w['gap_units']):
   if time.monotonic()-start>3:break
   a=audit_pair(s,*w['pair'],max_depth=15,max_nodes=200000);checks.append(dict(pair=w['pair'],**a))
   if a['state']=='demonstrated-interpenetration':state='demonstrated-interpenetration';break
  else:
   if all(a['state']=='certified-nonintersection' for a in checks):state='certified-separation'
  tr=s.trace(eng.xy);metric=eng.measure(tr['owner'],tr['unknown'],s.indices,0,True)
  row=dict(path=str(path.relative_to(ROOT)),sha256=sha(path),old_gate=old,reproduced_envelope=c,actual_solid_checks=checks,classification=state,development=metric,parameters=r['parameters'])
  rows.append(row);print(path.name,old.get('unresolved_pairs'),state,metric['score'],flush=True)
 save(out/'historical-contact-audit.json.gz',dict(total_original_inconclusive_gates=len(failed),selection='12 fewest-failed-pair / nearest-positive-margin distinct controls, selected without R313 photographic score. Not exhaustive; all 1301 not rerendered.',rows=rows,seconds=time.monotonic()-began))
if __name__=='__main__':main()
