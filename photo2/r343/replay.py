"""Fresh bounded reproduction; manual native annotations remain explicit inputs."""
from common import *
import subprocess,tempfile,time

def canonical(v):
 if isinstance(v,dict):return {k:canonical(z) for k,z in v.items() if k!='utc' and not k.endswith('_sha256')}
 if isinstance(v,list):return [canonical(z) for z in v]
 return v

def main():
 fresh=Path(tempfile.mkdtemp(prefix='beads-r343-'));env=dict(os.environ,R343_RUN_ROOT=str(fresh),OPENBLAS_NUM_THREADS='1',MPLCONFIGDIR='/tmp/beads-r343-mpl');start=time.perf_counter();times={}
 for stage in ['reference_views','hsv','empirical','associate','provenance','position29','freeze','pattern','review','verify']:
  tick=time.perf_counter();r=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/f'photo2/r343/{stage}.py')],cwd=ROOT,env=env,capture_output=True,text=True);(fresh/f'{stage}.log').write_text(r.stdout+r.stderr);assert r.returncode==0,(stage,r.stdout,r.stderr);times[stage]=time.perf_counter()-tick
 products=['reference-manifest.json','glass-regions.json','source-pixels.json.gz','sampling-comparison.json','HSV-summary.json','HSV-findings.json','association.json','authority-overlay.json','position29.json','maker-only-graph.json.gz','graph.json.gz','maker-decisions.json','C62-original-candidate.json.gz','input-seal.json','freeze.json','pattern208.json','pattern-analysis.json','verification.json','review/panels.json','review/questions.json']
 for path in products:assert canonical(read(OUT/path))==canonical(read(fresh/path)),path
 images=[p.relative_to(OUT) for p in OUT.glob('*.png')]+[Path('review')/r['filename'] for r in read(OUT/'review/panels.json')]
 for path in images:assert (OUT/path).read_bytes()==(fresh/path).read_bytes(),str(path)
 for path in ['HSV-HV.svg','pattern208.csv','review/index.html','review/data.js','review/viewer.js','review/style.css']:assert (OUT/path).read_bytes()==(fresh/path).read_bytes(),path
 save(OUT/'replay-verification.json',dict(passed=True,fresh_path=str(fresh),stages=times,science_products=len(products),exact_images=len(images),exact_vector_plot=True,exact_csv=True,exact_offline_review=True,seconds=time.perf_counter()-start,JSON_comparison_excludes=['utc','*_sha256'],limits='Scientific photographic inputs include the annotated glass cores and independent visible-body judgments. Replay is not a second independent human inspection; fresh verifier checks input seals, producer hashes, actual RGB/HSV, graph and pattern arithmetic.'))
 print('PASS fresh R343 replay',len(products),'products',len(images),'images',time.perf_counter()-start)
if __name__=='__main__':main()
