"""Fresh bounded replay, preserving native judgments as explicit scientific inputs."""
from pathlib import Path
import os,sys,json,gzip,subprocess,tempfile,time
HERE=Path(__file__).resolve().parent

def read(p):
 with (gzip.open(p,'rt') if p.suffix=='.gz' else open(p)) as f:return json.load(f)
def normalize(v):
 if isinstance(v,dict):return {k:normalize(x) for k,x in v.items() if k not in ['seconds','utc'] and not k.endswith('_sha256')}
 if isinstance(v,list):return [normalize(x) for x in v]
 return v

def main():
 start=time.perf_counter();out=Path(tempfile.mkdtemp(prefix='beads-r341-',dir='/tmp'));env=dict(os.environ,R341_RUN_ROOT=str(out),OPENBLAS_NUM_THREADS='1');timings={}
 for stage in ['experiment','audit_panels','native_audit','audit_uncertain','excluded_controls','freeze','pattern','evaluate','review','verify']:
  t=time.perf_counter();r=subprocess.run([sys.executable,str(HERE/f'{stage}.py')],env=env,capture_output=True,text=True);(out/f'{stage}.log').write_text(r.stdout+r.stderr);assert r.returncode==0,(stage,r.stderr);timings[stage]=time.perf_counter()-t
 files=['geometry.json','selection.json','experiment.json','alternatives.json.gz','classification.json.gz','native-audit.json.gz','native-judgments.json','excluded-maker-controls.json','graph.json.gz','corrections.json','freeze.json','input-seal.json','pattern208.json','pattern-analysis.json','evaluation.json','review/panels.json','review/questions.json'];checked=[]
 for f in files:assert normalize(read(HERE/f))==normalize(read(out/f)),f;checked.append(f)
 images=[p.relative_to(HERE) for p in HERE.glob('audit-*.png')]+[p.relative_to(HERE) for p in HERE.glob('disagreement-*.png')]+[p.relative_to(HERE) for p in HERE.glob('uncertain-ownership-*.png')]+[Path('review')/r['filename'] for r in read(HERE/'review/panels.json')]+[Path('excluded-maker-controls.png')]
 for f in images:assert (HERE/f).read_bytes()==(out/f).read_bytes(),str(f)
 assert (HERE/'review/index.html').read_bytes()==(out/'review/index.html').read_bytes()
 receipt=dict(passed=True,output=str(out),science_files=checked,native_images=len(images),offline_HTML_exact=True,stages_seconds=timings,total_seconds=time.perf_counter()-start,comparison_exclusions='Measured seconds/UTC and dependent *_sha256 fields only. Fresh verify independently validates every current producer hash. Native judgments are frozen explicit inputs; replay is not a second independent human inspection.');(HERE/'replay-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
