"""Fresh bounded scientific replay and process time/peak-memory measurement."""
import argparse,os,sys,time,subprocess
from pathlib import Path
from .common import ROOT,read,save
STAGES=[('corrections','corrections'),('classify','classification'),('export','overlay'),('analyze','analysis')]
def normalized(v):
    if isinstance(v,dict):return {k:normalized(x) for k,x in v.items() if k not in ['seconds','sampling_seconds']}
    if isinstance(v,list):return [normalized(x) for x in v]
    return v

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',R334_RUN_ROOT=str(out));records=[];start=time.perf_counter()
    for module,directory in STAGES:
        elapsed=out/f'{module}-time.txt';t=time.perf_counter();result=subprocess.run(['/usr/bin/time','-f','%e %M','-o',str(elapsed),sys.executable,'-m','photo2.r334.'+module,'--output',str(out/directory)],cwd=ROOT,env=env,capture_output=True,text=True);(out/f'{module}-stdout.txt').write_text(result.stdout);(out/f'{module}-stderr.txt').write_text(result.stderr);assert result.returncode==0,result.stderr;seconds,rss=elapsed.read_text().split();checked=[]
        for file in (out/directory).rglob('*'):
            if file.is_file() and (file.name.endswith('.json') or file.name.endswith('.json.gz')):
                rel=file.relative_to(out);assert normalized(read(file))==normalized(read(ROOT/'photo2/r334'/rel)),str(rel);checked.append(str(rel))
        row=dict(stage=module,wall_seconds=time.perf_counter()-t,process_seconds=float(seconds),peak_rss_MiB=int(rss)/1024,parsed_scientific_equality=checked);records.append(row);save(out/'partial-replay.json',records);print(row,flush=True)
    save(out/'replay.json',dict(passed=True,fresh_output=str(out),stages=records,total_wall_seconds=time.perf_counter()-start,policy='All scientific data compare exactly, excluding measured time fields only. No model, detector or physical renderer.'))
if __name__=='__main__':main()
