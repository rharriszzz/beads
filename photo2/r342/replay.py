"""Fresh bounded replay; comparisons do not constitute a second photographic review."""
from common import *
import subprocess,tempfile,time

def canonical(v):
 if isinstance(v,dict):return {k:canonical(z) for k,z in v.items() if k!='utc' and not k.endswith('_sha256')}
 if isinstance(v,list):return [canonical(z) for z in v]
 return v

def main():
 dest=Path(tempfile.mkdtemp(prefix='beads-r342-'));env=dict(os.environ,R342_RUN_ROOT=str(dest),OPENBLAS_NUM_THREADS='1',MPLCONFIGDIR='/tmp/beads-r342-mpl');started=__import__('time').perf_counter();stages=['maker','experiment','native_panels','hue_diagnostic','coverage','candidate_checks','consistency','native_review','excluded_controls','freeze','pattern','review','verify'];times={}
 for stage in stages:
  tick=__import__('time').perf_counter();r=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/f'photo2/r342/{stage}.py')],cwd=ROOT,env=env,capture_output=True,text=True);(dest/f'{stage}.log').write_text(r.stdout+r.stderr);assert r.returncode==0,(stage,r.stdout,r.stderr);times[stage]=__import__('time').perf_counter()-tick
 products=['maker-graph.json.gz','maker-decisions.json','alternatives.json.gz','experiment.json','classification.json.gz','fixed-disagreements-manifest.json','remaining-colors-manifest.json','regressions-manifest.json','hue-measurements.json','hue-diagnostic.json','coverage-candidates.json','coverage-manifest.json','candidate-checks.json','consistency.json','rejected-local-patch.json.gz','native-review.json','audited-classification.json.gz','evaluation.json','excluded-maker-controls.json','graph.json.gz','corrections.json','input-seal.json','freeze.json','pattern208.json','pattern-analysis.json','review/panels.json','review/questions.json','verification.json']
 for path in products:assert canonical(read(OUT/path))==canonical(read(dest/path)),path
 images=[p.relative_to(OUT) for p in OUT.glob('*.png')]+[Path('review')/p['filename'] for p in read(OUT/'review/panels.json')]
 for path in images:assert (OUT/path).read_bytes()==(dest/path).read_bytes(),str(path)
 assert (OUT/'review/index.html').read_bytes()==(dest/'review/index.html').read_bytes()
 save(OUT/'replay-verification.json',dict(passed=True,fresh_path=str(dest),stages=times,decoded_science_products=len(products),exact_images=len(images),exact_offline_HTML=True,seconds=__import__('time').perf_counter()-started,excluded_from_json_comparison=['utc','*_sha256'],limits='Explicit native-review annotations are frozen scientific inputs, not a fresh independent inspection. New run independently validates all producer hashes and old-input preservation. Browser receipt separate.'))
 print('PASS fresh replay',len(products),len(images),__import__('time').perf_counter()-started)
if __name__=='__main__':main()
