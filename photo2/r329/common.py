import time, resource, subprocess, hashlib
from pathlib import Path
import numpy as np
from photo2.r328.grow import read,save,sha,ROOT,extend,lifted,plus,minus
OUT=ROOT/'photo2/r329/results'
REF='C-1302-0316'
WEIGHTS={'A':(7,6),'B':(6,7),'reverse_A':(-7,-6),'reverse_B':(-6,-7)}
def inputs():
 g=read(ROOT/'photo2/r328/results/graph.json.gz')
 bank=read(ROOT/'photo2/r327/results/graph.json.gz')
 prep=read(ROOT/'photo2/r328/development/final256/prepared.json.gz')
 states=read(ROOT/'photo2/r328/development/final256/search.json.gz')['states']
 for pp in prep['patches']:
  for j,p in enumerate(pp):p['patch']=j
 return g,bank,prep,states

def canonical(state,frame=1):
 H=state['H'];out={}
 for r in state['coords']:
  v=tuple(frame*(r['ab'][d]-r['turn']*H[d]) for d in range(2))
  if r['observation'] in out:assert out[r['observation']]==v
  out[r['observation']]=v
 origin=out[REF]
 return {o:minus(v,origin) for o,v in out.items()}

def initial(bank,seed,arc,frame=1):
 turn=int(round((arc-bank['stations_px'][seed])/bank['period_px']))
 return dict(coords={(seed,turn):(0,0)},H=None,returns=[],score=0.,path=[],skips=0)

def serialize(s):
 return dict(s,coords=[dict(observation=o,turn=t,ab=list(v)) for (o,t),v in sorted(s['coords'].items())])

def replay(bank,prep,path,seed='C-0986-0371',until=None,checkpoint=None,start=0):
 t=time.perf_counter();s=checkpoint or initial(bank,seed,bank['windows'][0]['arc_px']);checkpoints={start:s};n=len(bank['windows'])
 for step in range(start,len(path) if until is None else until):
  r=path[step];wi=r['window'];arc=bank['windows'][wi]['arc_px']+(bank['period_px'] if step==n else 0)
  if r.get('skipped'):
   s=dict(s,path=s['path']+[r],skips=s['skips']+1);continue
  p=prep['patches'][wi][r['patch']];s,why=extend(s,p,lifted(p,arc,bank['stations_px'],bank['period_px']),first=step==0)
  if s is None:return None,dict(failed_step=step,reason=why,seconds=time.perf_counter()-t),checkpoints
  checkpoints[step+1]=s
 return s,dict(seconds=time.perf_counter()-t,completed=bool(s['H'] and len(s['returns'])>=3),H=s['H'],returns=len(s['returns']),steps=len(s['path'])-start),checkpoints

def trace_first(rows,key='delta',direction=1):
 ordered=sorted((r for r in rows if direction*r['k']>=0),key=lambda r:(direction*r['k'],r['id']))
 last=None
 for r in ordered:
  if r.get(key) is None:continue
  if r[key]!=0:return dict(first=r,last_agreement=last,interval=[last['k'] if last else 0,r['k']],certainty='first observed disagreement, not proved physical error')
  last=r
 return dict(first=None,last_agreement=last,interval=None)
