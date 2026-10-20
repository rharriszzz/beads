"""Fresh bounded producer run, decoded science and rendered output equality."""
from common import *
import subprocess
import tempfile
import time


def main():
    fresh=Path(tempfile.mkdtemp(prefix='beads-r344-'));env=dict(os.environ,R344_RUN_ROOT=str(fresh),OPENBLAS_NUM_THREADS='1',MPLCONFIGDIR='/tmp/beads-r344-mpl');start=time.perf_counter();times={}
    for stage in ['freeze','analyze','graph_paper','present','verify','verify_graph_paper','draw_graph_paper','report']:
        tick=time.perf_counter();r=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/f'photo2/r344/{stage}.py')],cwd=ROOT,env=env,capture_output=True,text=True);(fresh/(stage+'.log')).write_text(r.stdout+r.stderr)
        assert r.returncode==0,(stage,r.stdout,r.stderr);times[stage]=time.perf_counter()-tick
    science=['graph.json.gz','corrections.json','input-seal.json','freeze.json','pattern208.json','training-agreement.json','evaluation.json','heldout-predictions.json.gz','verification.json','review/panels.json','presentation-input-seal.json','graph-paper-layout.json','graph-paper-verification.json','correction-effects.json']
    for name in science:assert read(OUT/name)==read(fresh/name),name
    exact=['patterns.png','patterns.svg','geography.png','strict-sequence.txt','provisional-sequence.txt','strict-pattern.csv','provisional-pattern.csv','review/index.html','review/data.js','review/viewer.js','review/style.css','review/paper.js','graph-paper.png','graph-paper.svg','graph-paper.pdf','graph-paper-numbered.png','graph-paper-numbered.svg','graph-paper-numbered.pdf']+['review/'+r['filename'] for r in read(OUT/'review/panels.json')]
    for name in exact:assert (OUT/name).read_bytes()==(fresh/name).read_bytes(),name
    assert (ROOT/'photo2/R344_REPORT.md').read_bytes()==(fresh/'REPORT.generated.md').read_bytes()
    save(OUT/'replay-verification.json',dict(passed=True,science_products=len(science),exact_artifacts=len(exact)+1,fresh_path=str(fresh),stages=times,seconds=time.perf_counter()-start,limits='Byte/decoded replay and arithmetic checks do not independently certify the original photo labels, physical bead identity or winding.'))
    print('PASS fresh R344 replay',len(science),len(exact)+1,time.perf_counter()-start)


if __name__=='__main__':
    main()
