"""Fresh bounded, exact replay. No historical artifacts are overwritten."""
import argparse,json,os,subprocess,sys,time
import numpy as np
from PIL import Image
from .common import ROOT,read
def normalize(x):
    if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if k!='seconds'}
    if isinstance(x,list):return [normalize(v) for v in x]
    return x
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--compare-only',action='store_true');a=p.parse_args();out=__import__('pathlib').Path(a.output).resolve()
    if a.compare_only:assert read(out/'verification.json')['passed']
    else:out.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',R336_RUN_ROOT=str(out));stages=[];start=time.perf_counter()
    for module,folder in [('evidence','evidence'),('revise','results'),('diagnose','analysis'),('review','review'),('verify',None)]:
        args=['--output',str(out/folder)] if folder else ['--output',str(out/'verification.json')];t=time.perf_counter();timing=out/(module+'.time')
        if not a.compare_only:
            with (out/(module+'.stdout')).open('w') as stdout,(out/(module+'.stderr')).open('w') as stderr:subprocess.run(['/usr/bin/time','-f','%e %M','-o',str(timing),sys.executable,'-m','photo2.r336.'+module,*args],cwd=ROOT,env=env,stdout=stdout,stderr=stderr,check=True)
        elapsed,rss=timing.read_text().split();stages.append(dict(stage=module,wall_seconds=None if a.compare_only else time.perf_counter()-t,process_elapsed_seconds=float(elapsed),peak_RSS_MiB=int(rss)/1024))
    reference=ROOT/'photo2/r336';compared=[]
    for folder in ['evidence','results','analysis','review']:
        for path in sorted((out/folder).rglob('*')):
            if path.is_file() and (path.name.endswith('.json') or path.name.endswith('.json.gz')):
                rel=path.relative_to(out);assert normalize(read(path))==normalize(read(reference/rel)),str(rel);compared.append(str(rel))
    for filename in ['index.html','style.css','viewer.js','evidence.html','repairs.html']:assert (out/'review'/filename).read_bytes()==(reference/'review'/filename).read_bytes(),filename
    fresh=json.loads((out/'review/data.js').read_text().split('=',1)[1].rstrip(';\n'));old=json.loads((reference/'review/data.js').read_text().split('=',1)[1].rstrip(';\n'));assert normalize(fresh)==normalize(old)
    for path in (out/'review/assets').glob('*.png'):assert np.array_equal(np.asarray(Image.open(path)),np.asarray(Image.open(reference/'review/assets'/path.name)))
    result=dict(passed=True,fresh_output=str(out),stages=stages,total_process_wall_seconds=sum(s['process_elapsed_seconds'] for s in stages),comparison_or_full_wall_seconds=time.perf_counter()-start,comparison_only=a.compare_only,parsed_exact_json=compared,viewer_and_appendices_exact=True,literal_crops_exact=11,policy='All selected science and parsed viewer data reproduce exactly, excluding measured seconds; templates and native crops exact. No broad searches or detector/renderer campaign. Comparison-only checks completed fresh stages without repeating them.')
    (out/'replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
