"""Fresh bounded replay; exact artifacts except measured time and peak memory."""
import argparse,json,gzip,subprocess,time,os,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k not in ['seconds','peak_rss_mib']}
    if isinstance(x,list):return [clean(v) for v in x]
    return x
def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();env=dict(os.environ,OPENBLAS_NUM_THREADS='1',R337_EXTRA_STATES=str(out/'bounded/states.json.gz'));stages=[]
    for module,args in [('analyze',['--output',str(out/'results')]),('bounded',['--output',str(out/'bounded')]),('search',['--output',str(out/'search-results')]),('consequences',['--output',str(out/'results'),'--results',str(out/'results'),'--search',str(out/'search-results')]),('pattern',['--output',str(out/'results')]),('review',['--output',str(out/'review'),'--results',str(out/'results'),'--search',str(out/'search-results')]),('verify',['--root',str(out)])]:
        before=time.perf_counter();result=subprocess.run([str(ROOT/'.venv/bin/python'),'-m','photo2.r337.'+module,*args],cwd=ROOT,env=env,capture_output=True,text=True);(out/(module+'.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,(module,result.stderr);stages.append(dict(module=module,seconds=time.perf_counter()-before));print('replay',module,stages[-1]['seconds'],flush=True)
    selected=ROOT/'photo2/r337';comparisons=[]
    for folder in ['results','bounded','search-results','review']:
        for p in sorted((out/folder).rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(out);old=selected/rel;assert old.is_file(),str(rel)
            if p.suffix=='.json' or p.name.endswith('.json.gz'):assert clean(read(p))==clean(read(old)),str(rel)
            else:assert p.read_bytes()==old.read_bytes(),str(rel)
            comparisons.append(str(rel))
    assert clean(read(out/'verification.json'))==clean(read(selected/'verification.json'))
    result=dict(passed=True,output=str(out),stages=stages,exact_artifacts=comparisons,seconds=time.perf_counter()-start,children_peak_rss_mib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss/1024,ignored_fields=['seconds','peak_rss_mib']);(out/'replay-receipt.json').write_text(json.dumps(result,indent=2)+'\n');(selected/'performance.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS R337 exact replay',result['seconds'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
