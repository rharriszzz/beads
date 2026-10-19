"""Reversible local screen, then unchanged R328 single-seed connected growth.
A screen fires only if colored-body bridge orientation belongs to exactly one
measured family in every extraction/locality variant, while a candidate assigns
that bridge to a mixture of the two families. No black pixels/positions are used.
This is a local diagnostic experiment, not a replacement historical graph.
"""
from .continuity import *
from photo2.r328.grow import search,save

def estimated_bridge_family(c):
 config=c['config'];votes=[]
 for v in c['variants']:
  pts={o:measure(OBS[o],v['radius'],v['threshold'])[0] for o in c['measurements']};vv=vectors(config,pts);anchor=pts[config['anchor']];bridge=pts[config['target']]-anchor;possible=[]
  for fam in [0,1]:
   vv0=field(vv,anchor,fam,v['bandwidth']);a=angle(vv0);spread=max(angle_diff(angle(r['v']),a) for r in vv if r['family']==fam)
   if angle_diff(angle(bridge),a)<=spread:possible.append(fam)
  votes.append(possible)
 return votes[0][0] if len(votes[0])==1 and all(v==votes[0] for v in votes) else None,votes

def assess(c,coords):
 fam,votes=estimated_bridge_family(c);a,b=c['config']['anchor'],c['config']['target']
 if a not in coords or b not in coords:return dict(status='unassessed_missing_colored_endpoint',family=fam)
 delta=[coords[b][i]-coords[a][i] for i in range(2)]
 if fam is None:return dict(status='direction_uncertain',family=None,delta=delta)
 consistent=delta[1-fam]==0 and delta[fam]!=0
 return dict(status='same_family' if consistent else 'family_mismatch',family=fam,delta=delta,votes=votes)

def main():
 began=time.perf_counter();data=read(OUT/'continuity.json.gz')['cases'];checks={name:{st:assess(c,CO[st]) for st in dict.fromkeys(['working',c['config']['alt']])} for name,c in data.items()}
 prep=read(ROOT/'photo2/r328/development/final256/prepared.json.gz');patches=prep['patches'];changes=[]
 for wi in [124,125,126]:
  keep=[]
  for pi,p in enumerate(patches[wi]):
   ev=assess(data['E'],p['assignments']);changes.append(dict(window=wi,patch=pi,hypothesis=p['hypothesis'],score=p['score'],assessment=ev))
   if ev['status']!='family_mismatch':keep.append(p)
  patches[wi]=keep
 bank=read(ROOT/'photo2/r327/results/graph.json.gz');t=time.perf_counter();result=search(bank,patches,width=32,budget=60);seconds=time.perf_counter()-t
 save(OUT/'screened-growth.json.gz',result)
 # Actual saved primary/alternative histories also replay from their original
 # connected seed; screening does not erase the alternative's reproducibility.
 from photo2.r329.common import replay
 originalprep=read(ROOT/'photo2/r328/development/final256/prepared.json.gz');receipts=[]
 for pp in originalprep['patches']:
  for j,p in enumerate(pp):p['patch']=j
 for st in ['working','closest','early','lower']:
  path=ST[st]['path']
  if st=='early':
   by_window={r['window']:r for r in path[:-1]};path=[by_window[i] for i in range(len(bank['windows']))]+[by_window[0]]
  end,receipt,_=replay(bank,originalprep,path);receipts.append(dict(state=st,receipt=receipt))
 save(OUT/'growth-diagnostic.json',dict(cases=checks,patch_checks=changes,experimental_search=dict(width=32,seconds=seconds,completed=result['completed'],best_H=result['states'][0]['H'] if result['states'] else None,best_score=result['states'][0]['score'] if result['states'] else None),replays=receipts,total_seconds=time.perf_counter()-began,policy='Isolated E same-diagonal screen on three frontier windows. All original patches and complete alternative states remain unchanged. No new numerical score weight; no new abstention rule. G/H orientation uncertainty is retained rather than converted to rejection. Not a new reconstruction adoption.'))
 print(checks);print('Search',seconds,result['completed'],result['states'][0]['H'])
if __name__=='__main__':main()
