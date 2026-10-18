"""Exact rotated-path controls, frozen post-hoc periods, evidence multiplicity."""
from .common import *
from collections import defaultdict,Counter
import datetime

def fixed_rotated(bank,prep,state,origin,direction,seed):
 t=time.perf_counter();n=len(bank['windows']);period=bank['period_px'];arc=bank['windows'][origin]['arc_px'];s=initial(bank,seed,arc);order=[(origin+direction*j)%n for j in range(n+1)];steps=[]
 for j,wi in enumerate(order):
  if j:
   prev=order[j-1];arc+=direction*((direction*(bank['windows'][wi]['arc_px']-bank['windows'][prev]['arc_px']))%period)
  r=state['path'][wi];p=dict(prep['patches'][wi][r['patch']]);p['assignments']={o:[direction*x for x in ab] for o,ab in p['assignments'].items()}
  s,reason=extend(s,p,lifted(p,arc,bank['stations_px'],period),first=j==0)
  if s is None:return dict(origin=origin,direction=direction,failed_step=j,reason=reason,seconds=time.perf_counter()-t)
  steps.append(dict(step=j,window=wi,nodes=len(s['coords']),shared=len(s['path'][-1]['attached_to'])))
 return dict(origin=origin,direction=direction,seed=seed,completed=bool(s['H'] and len(s['returns'])>=3),normalized_H=[direction*x for x in s['H']],returns=s['returns'],state=serialize(s),steps=steps,seconds=time.perf_counter()-t,policy='Replay of the already selected path; proves feasibility for this start, not independent recovery.')

def periods(state,g,label):
 coords=canonical(state);obs={o['id']:o for o in g['observations']};results=[]
 for family,weights in [('A',(7,6)),('B',(6,7))]:
  N=abs(int(np.dot(state['H'],weights)));rows=[dict(id=o,k=int(np.dot(ab,weights)),color=obs[o]['color'],xy=obs[o]['xy']) for o,ab in coords.items()];periods=sorted(set(range(1,501))|{p for p in range(1,N+1) if N%p==0});checks=[]
  for p in periods:
   groups=defaultdict(list)
   for row in rows:groups[row['k']%p].append(row)
   conflicts=[];pairs=0
   for residue,rr in groups.items():
    pairs+=len(rr)*(len(rr)-1)//2
    for i,a in enumerate(rr):
     b=next((b for b in rr[:i] if a['color']!=b['color']),None)
     if b:conflicts.append(dict(residue=residue,first=b,second=a))
   checks.append(dict(period=p,complete_repeat_divides_N=N%p==0,pair_comparisons=pairs,occupied_residues=len(groups),unknown_residues=p-len(groups),conflict_witnesses=len(conflicts),first_conflicts=conflicts[:4],all_conflicts=conflicts if p==252 else None,excludes_under_fixed_colors=bool(conflicts)))
  results.append(dict(label=label,H=state['H'],family=family,N=N,rows=rows,periods=checks,reversal='All pair-equality/conflict results invariant to global sign and origin; independently tested in verify.'))
 return results

def main():
 g,b,p,ss=inputs();fixed=[]
 for direction in [1,-1]:fixed.append(fixed_rotated(b,p,ss[0],124,direction,'C-1669-1561'))
 save(OUT/'fixed-origin-replays.json.gz',dict(runs=fixed))
 # Snapshot all photographic inference before any color computations.
 files=list((OUT/'traversals').glob('*.json.gz'))+[ROOT/'photo2/r328/results/graph.json.gz',ROOT/'photo2/r328/results/alternatives.json.gz']
 save(OUT/'photographic-freeze.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources={str(f.relative_to(ROOT)):sha(f) for f in files},policy='No color-period input to growth, local scores, count screening or physical registration. Additional source-state replay is diagnostic only.'))
 t=time.perf_counter();results=[]
 for i,s in enumerate(ss):results.extend(periods(s,g,'R328-state-'+str(i)))
 save(OUT/'periods.json.gz',dict(results=results,seconds=time.perf_counter()-t,policy='Post-freeze exact equalities for automatic color cues, including provisional black. A conflict excludes only this fixed identity/color hypothesis. P252 is untrusted. For N not divisible by P, complete repeats fail arithmetic independently of motif resemblance. Far-N arithmetic candidates have no full photo mapping; their periods are not excluded using these incompatible maps. No majority recoloring or identity edits.'))
 print('CLOSED',[(r.get('completed'),r.get('normalized_H')) for r in fixed],len(results),'seconds',time.perf_counter()-t,flush=True)
if __name__=='__main__':main()
