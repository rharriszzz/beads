"""Fresh bounded replay; exact results except measured runtime and peak memory."""
import argparse,os,subprocess,time,resource
from .common import ROOT,Path,read,save

def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k not in ['seconds','peak_rss_mib']}
    if isinstance(x,list):return [clean(v) for v in x]
    return x

def run(out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);selected=ROOT/'photo2/r338';env=dict(os.environ,OPENBLAS_NUM_THREADS='1',R338_RUN_ROOT=str(out),R338_FREEZE_UTC=read(selected/'results/body-freeze.json')['utc']);stages=[];start=time.perf_counter()
    for module,folder in [('audit','audit'),('inspect','inspection'),('conflicts','conflicts'),('measure','measurement'),('revise','results'),('analyze','analysis'),('review','review'),('verify',None)]:
        args=['--root',str(out)] if folder is None else ['--output',str(out/folder)];before=time.perf_counter();result=subprocess.run([str(ROOT/'.venv/bin/python'),'-m','photo2.r338.'+module,*args],cwd=ROOT,env=env,capture_output=True,text=True);(out/(module+'.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,(module,result.stdout,result.stderr);stages.append(dict(module=module,seconds=time.perf_counter()-before));print('replay',module,stages[-1]['seconds'],flush=True)
    comparisons=[]
    for folder in ['audit','inspection','conflicts','measurement','results','analysis','review']:
        for p in sorted((out/folder).rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(out);old=selected/rel;assert old.is_file(),str(rel)
            if p.suffix=='.json' or p.name.endswith('.json.gz'):assert clean(read(p))==clean(read(old)),str(rel)
            else:assert p.read_bytes()==old.read_bytes(),str(rel)
            comparisons.append(str(rel))
    assert clean(read(out/'verification.json'))==clean(read(selected/'verification.json'))
    receipt=dict(passed=True,stages=stages,exact_artifacts=comparisons,seconds=time.perf_counter()-start,children_peak_rss_mib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024,ignored_fields=['seconds','peak_rss_mib'],manual_inputs='Existing maker decision, frozen native inspection plan and documented visual judgments; replay checks computations, not independent truth of those judgments.',freeze_utc=env['R338_FREEZE_UTC']);save(out/'replay-receipt.json',receipt);save(selected/'performance.json',receipt);print('PASS R338 exact replay',receipt['seconds'],receipt['children_peak_rss_mib'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
