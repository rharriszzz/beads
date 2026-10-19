"""Fresh exact pipeline replay with measured process time and peak RSS."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
from .common import ROOT,read,save,sha
STAGES=[('spirals','spirals'),('staircases','staircases'),('periods','periods-selected'),('diagnose','diagnosis'),('followup','followup')]
def normalize(v):
    if isinstance(v,dict):return {k:normalize(x) for k,x in v.items() if k!='seconds'}
    if isinstance(v,list):return [normalize(x) for x in v]
    return v

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',R333_RUN_ROOT=str(out));records=[];started=time.perf_counter()
    for module,directory in STAGES:
        metrics=out/f'{module}-time.txt';cmd=['/usr/bin/time','-f','%e %M','-o',str(metrics),sys.executable,'-m',f'photo2.r333.{module}','--output',str(out/directory)];t=time.perf_counter();result=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True);(out/f'{module}-stdout.txt').write_text(result.stdout);(out/f'{module}-stderr.txt').write_text(result.stderr);assert result.returncode==0,result.stderr
        seconds,rss=metrics.read_text().split();files=[]
        for path in (out/directory).rglob('*'):
            if path.is_file() and (path.name.endswith('.json') or path.name.endswith('.json.gz')):
                rel=path.relative_to(out);assert normalize(read(path))==normalize(read(ROOT/'photo2/r333'/rel)),str(rel);files.append(str(rel))
        record=dict(stage=module,wall_seconds=time.perf_counter()-t,process_elapsed_seconds=float(seconds),peak_rss_MiB=int(rss)/1024,scientific_files_equal=files);records.append(record);print(record,flush=True)
    receipt=dict(passed=True,fresh_output=str(out),stages=records,total_wall_seconds=time.perf_counter()-started,policy='Parsed scientific equality excludes measured seconds only; independent fresh pipeline, frozen seeds, full controls.')
    save(out/'replay.json',receipt)
if __name__=='__main__':main()
