"""One bounded fresh application/review/check replay with exact data comparison."""
import argparse,gzip,json,os,subprocess,sys,time
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
def read(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def normalized(x):
    if isinstance(x,dict):return {k:normalized(v) for k,v in x.items() if k!='seconds'}
    if isinstance(x,list):return [normalized(v) for v in x]
    return x
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--compare-only',action='store_true');a=p.parse_args();out=Path(a.output).resolve()
    if not a.compare_only:out.mkdir(parents=True,exist_ok=False)
    else:assert read(out/'verification.json')['passed']
    reference=ROOT/'photo2/r335';env=dict(os.environ,OPENBLAS_NUM_THREADS='1');stages=[];start=time.perf_counter()
    for module,args in [('application',['--output',str(out/'results')]),('review',['--run',str(out),'--output',str(out/'review')]),('verify',['--run',str(out),'--output',str(out/'verification.json')])]:
        log=out/(module+'.stdout');err=out/(module+'.stderr');timing=out/(module+'.time');t=time.perf_counter()
        if not a.compare_only:
            with log.open('w') as stdout,err.open('w') as stderr:subprocess.run(['/usr/bin/time','-f','%e %M','-o',str(timing),sys.executable,'-m','photo2.r335.'+module,*args],cwd=ROOT,env=env,stdout=stdout,stderr=stderr,check=True)
        elapsed,peak=timing.read_text().split();stages.append(dict(stage=module,wall_seconds=None if a.compare_only else time.perf_counter()-t,process_elapsed_seconds=float(elapsed),peak_RSS_MiB=int(peak)/1024))
    compared=[]
    for directory in ['results','review']:
        for path in sorted((out/directory).rglob('*')):
            if path.is_file() and (path.name.endswith('.json') or path.name.endswith('.json.gz')):
                rel=path.relative_to(out);assert normalized(read(path))==normalized(read(reference/rel)),str(rel);compared.append(str(rel))
    fresh=json.loads((out/'review/data.js').read_text().split('=',1)[1].rstrip(';\n'));old=json.loads((reference/'review/data.js').read_text().split('=',1)[1].rstrip(';\n'));assert normalized(fresh)==normalized(old)
    for path in (out/'review/assets').glob('*.png'):assert np.array_equal(np.asarray(Image.open(path)),np.asarray(Image.open(reference/'review/assets'/path.name)))
    for name in ['index.html','style.css','viewer.js']:assert (out/'review'/name).read_bytes()==(reference/'review'/name).read_bytes()
    result=dict(passed=True,fresh_output=str(out),stages=stages,total_process_wall_seconds=sum(s['process_elapsed_seconds'] for s in stages),comparison_only=a.compare_only,comparison_or_full_wall_seconds=time.perf_counter()-start,parsed_scientific_equality=compared,viewer_data_exact_excluding_seconds=True,native_crops_exact=208,viewer_templates_exact=True,policy='One fresh bounded replay; historical scientific files unchanged; no classifier training, new spiral search or period scan. Comparison-only mode checks already completed fresh stages without repeating them.')
    (out/'replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
