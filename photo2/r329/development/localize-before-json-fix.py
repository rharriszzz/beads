"""Compare actual saved histories; causal patch splices and prefix checkpoint replay."""
from .common import *
from collections import Counter,defaultdict,deque

def oriented_rows(g,a,b,weights,direction):
 ca,cb=canonical(a),canonical(b);obs={o['id']:o for o in g['observations']};st=g['stations_px'];refst=st[REF];rows=[]
 for oid in sorted(ca.keys()&cb.keys()):
  lift=1 if direction==1 and st[oid]<refst else -1 if direction==-1 and st[oid]>refst else 0
  aa=np.array(ca[oid])+lift*np.array(a['H']);bb=np.array(cb[oid])+lift*np.array(b['H'])
  k=int(direction*np.dot(aa,weights));other=int(direction*np.dot(bb,weights))
  rows.append(dict(id=oid,xy=obs[oid]['xy'],color=obs[oid]['color'],ab_primary=ca[oid],ab_alternative=cb[oid],geographic_lift=lift,k=k,alternative_k=other,delta=other-k,primary_modulo=k%abs(np.dot(a['H'],weights)),alternative_modulo=other%abs(np.dot(b['H'],weights))))
 return sorted(rows,key=lambda r:(r['k'],r['id']))

def evidence(bank,prep,state):
 occurrences=Counter();contexts=Counter();terms=Counter();unique_contexts=set();pred=defaultdict(list)
 for step,r in enumerate(state['path']):
  if r.get('skipped'):continue
  p=prep['patches'][r['window']][r['patch']];h=bank['windows'][r['window']]['hypotheses'][r['hypothesis']]
  unique_contexts.add((r['window'],r['hypothesis']));terms.update(p['score_terms'])
  for oid in p['assignments']:occurrences[oid]+=1
  for z in h['r327_evidence']['rows']:
   if z['observation'] in p['assignments']:
    pred[z['observation']].append(dict(window=r['window'],hypothesis=r['hypothesis'],**z));contexts[(z['observation'],tuple(z['anchor_ids']))]+=1
 return dict(patch_support_occurrences=sum(occurrences.values()),unique_supports=len(occurrences),support_repeat_histogram=dict(Counter(occurrences.values())),unique_selected_contexts=len(unique_contexts),repeated_identical_target_anchor_contexts=sum(n-1 for n in contexts.values()),score_terms=dict(terms),predictions=dict(pred),policy='Overlap, common targets and common anchors are correlated. Counts are not independent confirmations.')

def routes(bank,prep,state,pairs):
 adj=defaultdict(list)
 for r in state['path']:
  if r.get('skipped'):continue
  for a,b,d in prep['patches'][r['window']][r['patch']]['edges']:
   adj[a].append((b,d,r['window']));adj[b].append((a,[-v for v in d],r['window']))
 def bfs(a,b,ban):
  q=deque([a]);parent={a:None}
  while q:
   x=q.popleft()
   for y,d,w in adj[x]:
    if tuple(sorted((x,y))) in ban or y in parent:continue
    parent[y]=(x,d,w)
    if y==b:
     out=[];cur=b
     while parent[cur]:
      z,delta,wi=parent[cur];out.append(dict(source=z,target=cur,delta=delta,window=wi));cur=z
     return out[::-1]
    q.append(y)
  return None
 out=[]
 for a,b in pairs:
  one=bfs(a,b,set());ban={tuple(sorted((z['source'],z['target']))) for z in one or []};two=bfs(a,b,ban)
  out.append(dict(source=a,target=b,first=one,edge_disjoint_second=two,first_delta=np.sum([z['delta'] for z in one],axis=0).tolist() if one else None,second_delta=np.sum([z['delta'] for z in two],axis=0).tolist() if two else None,policy='Each link has selected photographic-patch evidence; alternate routes reuse observations and may share parent fits. This is robustness, not independent truth.'))
 return out

def main():
 began=time.perf_counter();g,bank,prep,states=inputs();op={o['id']:o for o in g['observations']}
 save(OUT/'reference.json',dict(id=REF,xy=op[REF]['xy'],color=op[REF]['color'],evidence='R161 interior association, maker15 in the retrospective established subset',convention='Relative lattice (0,0) at this measured bright support; A=7a+6b, B=6a+7b; reversals negate. Geographic cut through reference station; each direction lifts observations once. Physical model address recorded separately.',original_ab=next(n['relative_ab'] for n in g['intersections'] if n['id']==REF),station_px=g['stations_px'][REF]))
 t=time.perf_counter();primary,receipt,cps=replay(bank,prep,states[0]['path']);assert primary and serialize(primary)['coords']==states[0]['coords'];save(OUT/'primary-replay.json',receipt)
 # Practice local machinery on a small geographic neighborhood before full alternative diagnosis.
 start,end=113,137;patchids={o for r in states[0]['path'][start:end] for o in prep['patches'][r['window']][r['patch']]['assignments']};practice=[]
 for i in [0,1,2]:
  s,z,_=replay(bank,prep,states[i]['path'],checkpoint=cps[start],start=start,until=end);practice.append(dict(alternative=i,observations=len(patchids),start=start,end=end,receipt=z,retained_nodes=len(s['coords']) if s else None))
 save(OUT/'practice.json',dict(runs=practice,policy='Checkpoint retains prior component. Only the stated local windows are attached/replayed; cached photographic features.'))
 cases=[];ledgers=[]
 for ai,alt in enumerate(states[1:],1):
  started=time.perf_counter();diff=[i for i,(a,b) in enumerate(zip(states[0]['path'],alt['path'])) if (a.get('patch'),a.get('skipped'))!=(b.get('patch'),b.get('skipped'))]
  first=diff[0];s,z,_=replay(bank,prep,alt['path'],checkpoint=cps[first],start=first);assert s and s['H']==tuple(alt['H'])
  forward={};reverse={}
  for name,weights in [('A',(7,6)),('B',(6,7))]:
   for direction in [1,-1]:
    rows=oriented_rows(g,states[0],alt,weights,direction);tr=trace_first(rows)
    ledgers.append(dict(alternative=ai,H=alt['H'],family=name,direction=direction,rows=rows,first=tr));(forward if direction==1 else reverse)[name]=tr
  # Isolate the first patch, then the entire smallest contiguous differing bundle.
  onepath=[dict(r) for r in states[0]['path']];onepath[first]=alt['path'][first]
  os,oz,_=replay(bank,prep,onepath,checkpoint=cps[first],start=first)
  bundle=[dict(r) for r in states[0]['path']]
  for j in range(first,diff[-1]+1):bundle[j]=alt['path'][j]
  bs,bz,_=replay(bank,prep,bundle,checkpoint=cps[first],start=first)
  # The last unchanged entering frontier is the relevant predecessor evidence.
  pred=states[0]['path'][first-1];predp=prep['patches'][pred['window']][pred['patch']]
  ca,cb=canonical(states[0]),canonical(alt)
  entering=[dict(id=o,xy=op[o]['xy'],relative_ab=ca[o]) for o in predp['assignments'] if o in ca and o in cb and ca[o]==cb[o]]
  ep=evidence(bank,prep,states[0]);ea=evidence(bank,prep,alt)
  changedids=set(o for j in diff for o in prep['patches'][alt['path'][j]['window']][alt['path'][j]['patch']]['assignments'])
  photo=[dict(id=o,xy=op[o]['xy'],primary=[r for r in ep['predictions'].get(o,[]) if r['window'] in diff],alternative=[r for r in ea['predictions'].get(o,[]) if r['window'] in diff]) for o in sorted(changedids)]
  cases.append(dict(alternative=ai,H=alt['H'],counts={n:abs(int(np.dot(alt['H'],w))) for n,w in WEIGHTS.items()},score_gap=states[0]['score']-alt['score'],changed_steps=diff,earliest_path_decision=first,entering_agreements=entering,forward=forward,reverse=reverse,replay=z,single_patch_counterfactual=oz,bundle_counterfactual=bz,photographic_rows=photo,evidence_reuse={k:v for k,v in ea.items() if k!='predictions'},seconds=time.perf_counter()-started,conclusion='Causal source of the difference demonstrated by replay; which photographic topology is physically correct remains unresolved.'))
 save(OUT/'index-ledger.json.gz',dict(reference=REF,comparisons=ledgers));save(OUT/'backward-cases.json.gz',dict(cases=cases))
 save(OUT/'primary-evidence-reuse.json',{k:v for k,v in evidence(bank,prep,states[0]).items() if k!='predictions'})
 save(OUT/'alternative-routes.json',routes(bank,prep,states[0],[(REF,'K-1341-0309'),('C-1775-1637','C-1669-1561'),('C-1721-1566','K-1740-1575'),('C-1440-3032','E5-1413-3039')]))
 # Return subsets are checked from independently serialized occurrences, not treated as independent measurements.
 closure=[]
 for i,s in enumerate(states):
  ids=s['returns'];groups=[ids,ids[::2],ids[1::2],ids[:3],ids[-3:]]
  for j,group in enumerate(groups):
   values=[]
   for oid in group:
    rr=sorted([r for r in s['coords'] if r['observation']==oid],key=lambda r:r['turn']);a,b=rr[0],rr[-1];values.append([(b['ab'][d]-a['ab'][d])//(b['turn']-a['turn']) for d in range(2)])
   closure.append(dict(alternative=i,subset=j,ids=group,H_values=values,agrees=all(v==s['H'] for v in values)))
 save(OUT/'return-subsets.json',dict(checks=closure,policy='Subsets of the same starting observations; sensitivity check only, not independent evidence.'))
 save(OUT/'localization-performance.json',dict(seconds=time.perf_counter()-began,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,cache='R327 candidate bank and R328 prepared patches; no cold discovery',full_primary_replay=receipt))
 print('LOCALIZE',len(cases),'practice',len(patchids),'first',[(c['H'],c['forward']['B']['first']['id'],c['forward']['B']['first']['k']) for c in cases[:5]],flush=True)
if __name__=='__main__':main()
