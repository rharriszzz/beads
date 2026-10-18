"""Fresh-process cold, rebuilt-geometry, and exact geometry-cache timings."""
import argparse,time,platform,os,resource,json
from pathlib import Path
import numpy as np
from photo2.r297.common import ROOT,save,read,utc
from photo2.r306.evidence import load
from .model import parameters,derive,corrected
from .evaluate import Evidence,evaluate
OUT=ROOT/'photo2/r320/results'
CASES=[(2200,1.65,1.25),(2600,1.65,1.05),(2800,1.35,1.25)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case',type=int,required=True);ap.add_argument('--scope',required=True);args=ap.parse_args();scope='all' if args.scope=='all' else int(args.scope)
 start=time.perf_counter();data=load()[0];ev=Evidence(data);setup=time.perf_counter()-start
 n,r,a=CASES[args.case];s,physical=derive(parameters(n,r,a),data);obs=ev.cohort(scope)
 t=time.perf_counter();ep=OUT/f'benchmark-{args.case}-{scope}-epoch.json.gz'
 if ep.exists():epoch=read(ep);assignment=0.;assignment_reused=True
 else:epoch=ev.assignment(s,obs);assignment_reused=False
 assignment=time.perf_counter()-t
 save(OUT/f'benchmark-{args.case}-{scope}-epoch.json.gz',dict(epoch,observations=obs))
 rows=[]
 for j in range(2):
  p=dict(s.p)
  if j:
   p['radius']*=.998;p['minor']*=.998;p=corrected(p,[.25,0,0,0])
  else:
   from photo2.r306.geometry import axis
   axis.cache_clear()
  # The second rebuilt geometry is a timing control only; no fitted result.
  z,cache,_=evaluate(p,data,ev,scope,obs,epoch['mapping']);z['mode']='process-cold' if j==0 else 'geometry-invalidated';z['parameters']=p;rows.append(z)
  for rep in range(2):
   q=dict(p);q['light_az']+=.1*(rep+1)
   zz,_,_=evaluate(q,data,ev,scope,obs,epoch['mapping'],cached=cache);zz['mode']='exact-geometry-cached-light-change';zz['repeat']=rep;rows.append(zz)
  del cache
 assert len(rows)==6 and {r['mode'] for r in rows}=={'process-cold','geometry-invalidated','exact-geometry-cached-light-change'}
 save(OUT/f'benchmark-{args.case}-{scope}.json.gz',dict(case=args.case,scope=scope,setup_seconds=setup,assignment_seconds=assignment,assignment_reused=assignment_reused,packing=physical,rows=rows,utc=utc(),hardware=dict(platform=platform.platform(),cpu_model=next((l.split(':',1)[1].strip() for l in Path('/proc/cpuinfo').read_text().splitlines() if l.startswith('model name')),'unknown'),logical_cpus=os.cpu_count(),threads={k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)))
 print('BENCHMARK',args.case,scope,[round(x['total_seconds'],4) for x in rows],flush=True)
if __name__=='__main__':main()
