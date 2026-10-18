"""R328 connected beam with rotated starts and exactly reversed local frames."""
from .common import *
from collections import Counter,defaultdict
import copy

def run(bank,prep,origin=0,direction=1,width=32,budget=80,rescore=False,forbidden=None):
 began=time.perf_counter();n=len(bank['windows']);period=bank['period_px'];stations=bank['stations_px'];patches=prep['patches'];order=[(origin+direction*j)%n for j in range(n+1)]
 arcs=[bank['windows'][origin]['arc_px']]
 for prev,wi in zip(order,order[1:]):
  d=direction*((direction*(bank['windows'][wi]['arc_px']-bank['windows'][prev]['arc_px']))%period);arcs.append(arcs[-1]+d)
 # Reverse traversal negates both local lattice axes; normalization restores them.
 frame=direction;transformed=[];checks=[]
 for wi,pp in enumerate(patches):
  ll=[]
  for old in pp:
   p=dict(old,assignments={o:[frame*v for v in ab] for o,ab in old['assignments'].items()})
   p['edges']=[(a,b,[frame*v for v in d]) for a,b,d in old['edges']]
   if forbidden:
    a,b,delta=forbidden
    if a in old['assignments'] and b in old['assignments'] and list(minus(old['assignments'][b],old['assignments'][a]))==delta:continue
   h=bank['windows'][wi]['hypotheses'][p['hypothesis']];rr={r['observation']:r for r in h['r327_evidence']['rows']};counts=Counter();qualities=defaultdict(list)
   for a,b,d in old['edges']:
    counts[tuple(d)]+=1;qualities[tuple(d)].append(float(np.sqrt(rr[a]['utility']*rr[b]['utility'])))
   continuity=min([sum(qualities[d]) for d in [(1,0),(0,1)]] or [0])/len(p['assignments'])
   bonus=.5*continuity if rescore else 0.;p['score']=old['score']+bonus
   checks.append(dict(window=wi,patch=p['patch'],primitive_edge_counts={str(k):v for k,v in counts.items()},continuity_bonus=bonus,shared_shape_penalty=p['score_terms']['shape_penalty'],native_mean_utility=float(np.mean([rr[o]['utility'] for o in p['assignments']])),policy='Existing native foreground/intervening-support and shared-pigment geometry retained; soft both-family endpoint continuity bonus, no new hard gate.'))
   ll.append(p)
  transformed.append(ll)
 first=transformed[origin][0];rows=bank['windows'][origin]['hypotheses'][first['hypothesis']]['r327_evidence']['rows'];colors={o['id']:o['color'] for o in bank['observations']}
 seed=max((r for r in rows if r['observation'] in first['assignments'] and colors[r['observation']]!='black'),key=lambda r:r['utility'])['observation']
 if origin==0 and not forbidden:seed='C-0986-0371'
 states=[initial(bank,seed,arcs[0])];trace=[];cps={};retry=set();rollbacks=[];step=0;active_width=width
 future=[set() for _ in range(n+2)]
 for j in range(n,-1,-1):future[j]=future[j+1]|{o for p in transformed[order[j]] for o in p['assignments']}
 while step<=n:
  cps[step]=states;wi=order[step];batch=[];reasons=Counter()
  for s in states:
   for p in transformed[wi]:
    z,reason=extend(s,p,lifted(p,arcs[step],stations,period),first=step==0)
    if step==n and z and (z['H'] is None or len(z['returns'])<3):z=None;reason='insufficient photographed return'
    reasons[reason]+=1
    if z is not None:batch.append(z)
   if step not in (0,n) and s['skips']<3:batch.append(dict(s,path=s['path']+[dict(window=wi,skipped=True)],skips=s['skips']+1))
  if not batch:
   if step>0 and step not in retry and time.perf_counter()-began<budget:
    retry.add(step);back=max(0,step-5);active_width=min(4*active_width,128);rollbacks.append(dict(failed=step,reopen=back,width=active_width));states=cps[back];step=back;continue
   break
  unique={}
  for s in sorted(batch,key=lambda s:-s['score']):
   sig=(tuple(sorted((k,v) for k,v in s['coords'].items() if k[0] in future[step+1])),s['H'],s['skips'])
   if sig not in unique:unique[sig]=s
   if len(unique)>=active_width:break
  states=list(unique.values());trace.append(dict(step=step,window=wi,arc=arcs[step],states=len(states),score=states[0]['score'],nodes=len(states[0]['coords']),reasons=dict(reasons),seconds=time.perf_counter()-began))
  if time.perf_counter()-began>budget:break
  step+=1
 distinct={}
 for s in states:distinct.setdefault(s['H'],s)
 saved=[serialize(s) for s in distinct.values()]
 return dict(origin=origin,direction=direction,local_frame_multiplier=frame,seed=seed,seconds=time.perf_counter()-began,completed=step>n,trace=trace,rollbacks=rollbacks,states=saved,normalized_H=[frame*v for v in states[0]['H']] if states[0]['H'] else None,rescore=rescore,forbidden=forbidden,frontier_checks=checks,cache='R328 prepared patches; no candidate rediscovery')

def main():
 began=time.perf_counter();g,bank,prep,states=inputs();summary=[];base=canonical(states[0]);configs=[('upper-forward',0,1,False,None),('lower-forward',75,1,False,None),('bend-forward',124,1,False,None),('upper-reverse',0,-1,False,None),('lower-reverse',75,-1,False,None),('bend-reverse',124,-1,False,None),('continuity-rescore',0,1,True,None),('withdraw-primary-black-direction',0,1,False,('C-1721-1566','K-1740-1575',[0,-1]))]
 for label,origin,direction,rescore,forbidden in configs:
  result=run(bank,prep,origin,direction,rescore=rescore,forbidden=forbidden);out=OUT/'traversals'/f'{label}.json.gz';save(out,result)
  best=result['states'][0];changed=[]
  if result['completed'] and best['H'] and REF in {c['observation'] for c in best['coords']}:
   other=canonical(best,direction);changed=[o for o in base.keys()&other.keys() if base[o]!=other[o]]
  summary.append(dict(label=label,origin=origin,direction=direction,seed=result['seed'],seconds=result['seconds'],completed=result['completed'],normalized_H=result['normalized_H'],windings=[[direction*v for v in s['H']] for s in result['states'] if s['H']],skips=[r['window'] for r in best['path'] if r.get('skipped')],changed_coordinates=len(changed),changed_ids=changed,returns=len(best['returns']),score=best['score'],file=str(out.relative_to(ROOT))))
  save(OUT/'traversal-summary.json',dict(runs=summary,seconds=time.perf_counter()-began,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,policy='Same cached candidate bank, independent greedy/beam starts; no new independent photograph. Reverse transforms both axes and traverses decreasing lifted station.'))
  print('TRAVERSE',label,summary[-1]['normalized_H'],result['completed'],len(changed),round(result['seconds'],3),flush=True)
if __name__=='__main__':main()
