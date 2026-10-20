"""Fresh bounded replay of selected geometry/classification/overlay/pattern only."""
from pathlib import Path
import os,sys,subprocess,tempfile,json,gzip,time
HERE=Path(__file__).resolve().parent

def decoded(p):
 with (gzip.open(p,'rt') if p.suffix=='.gz' else open(p)) as f:return json.load(f)
def normalize(x):
 if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if k not in ['seconds','utc','classification_sha256','freeze_sha256']}
 if isinstance(x,list):return [normalize(v) for v in x]
 return x

def main():
 start=time.perf_counter();out=Path(tempfile.mkdtemp(prefix='beads-r340-material-',dir='/tmp'));env=dict(os.environ,R340_MATERIAL_RUN_ROOT=str(out),OPENBLAS_NUM_THREADS='1');stages={}
 for name in ['run','evaluate','freeze','pattern']:
  t=time.perf_counter();r=subprocess.run([sys.executable,str(HERE/f'{name}.py')],env=env,capture_output=True,text=True);(out/f'{name}.log').write_text(r.stdout+r.stderr);assert r.returncode==0,(name,r.stderr);stages[name]=time.perf_counter()-t
 files=['rectangle-model.json','classification.json','evaluation.json','maker-graph.json.gz','graph.json.gz','freeze.json','pattern208.json','pattern-analysis.json'];checks=[]
 for name in files:assert normalize(decoded(HERE/name))==normalize(decoded(out/name)),name;checks.append(name)
 receipt=dict(passed=True,fresh_output=str(out),stages_seconds=stages,exact_scientific_files=checks,excluded_fields=['seconds','utc','classification_sha256','freeze_sha256'],exclusion_reason='Measured runtime/UTC and dependent exact-output hashes vary; fixed science compared in full. Delivery verifier checks current-output SHA256s separately.',total_seconds=time.perf_counter()-start)
 (HERE/'replay-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
