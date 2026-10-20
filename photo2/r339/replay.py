"""Fresh bounded replay; manual native judgments explicit, only timing ignored."""
import argparse,subprocess,resource
from .common import *
def clean(v):
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if k!='seconds'}
 if isinstance(v,list):return [clean(x) for x in v]
 return v
def run(out):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();env=dict(os.environ,OPENBLAS_NUM_THREADS='1',R339_RUN_ROOT=str(out));stages=[]
 for module,folder in [('maker','maker'),('classify','classification'),('compare','comparison'),('apply','results'),('analyze','analysis'),('review','review'),('verify',None)]:
  before=time.perf_counter();args=['--root',str(out)] if folder is None else ['--output',str(out/folder)];p=subprocess.run([str(ROOT/'.venv/bin/python'),'-m','photo2.r339.'+module,*args],cwd=ROOT,env=env,capture_output=True,text=True);(out/(module+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,(module,p.stdout,p.stderr);stages.append(dict(module=module,seconds=time.perf_counter()-before));print('REPLAY',module,stages[-1]['seconds'],flush=True)
 compared=[];selected=ROOT/'photo2/r339'
 for folder in ['maker','classification','comparison','results','analysis','review']:
  for p in sorted((out/folder).rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(out);old=selected/rel;assert old.is_file(),str(rel)
   if p.suffix=='.json' or p.name.endswith('.json.gz'):assert clean(read(p))==clean(read(old)),str(rel)
   else:assert p.read_bytes()==old.read_bytes(),str(rel)
   compared.append(str(rel))
 assert clean(read(out/'verification.json'))==clean(read(selected/'verification.json'))
 result=dict(passed=True,stages=stages,exact_artifacts=compared,seconds=time.perf_counter()-start,peak_child_rss_mib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024,ignored_fields=['seconds'],manual_input_scope='Exact maker decisions and documented fixed-support native ownership judgments are replay inputs, not independently rediscovered human truth.');save(out/'replay-receipt.json',result);save(selected/'performance.json',result);print('PASS R339 replay',result['seconds'],result['peak_child_rss_mib'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
