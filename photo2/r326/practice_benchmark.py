"""Repeated cached-bank lower-bend practice, plus exact same-bank R325 control."""
import json,time,tempfile,shutil
from pathlib import Path
from PIL import Image,ImageOps
from photo2.r326.runner import run
from photo2.r326.verify import clean
from photo2.r325.graph import infer_graph
from photo2.r325.tracker import preprocess
from photo2.r323.tracker import save
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r326/results'
def science(g):
    z=clean(g);z.pop('timings_seconds',None)
    return z

def main():
    results=[];first=None;dirs=[]
    for i in range(2):
        out=Path(tempfile.mkdtemp(prefix='r326-practice-'));g=run(out,practice=True,cached=ROOT/'photo2/r325/results/graph.json');dirs.append(out)
        if first is None:first=science(g)
        else:assert first==science(g)
        results.append(dict(run=i,performance=json.load(open(out/'performance.json')),summary=g['summary']))
    initial=json.load(open(dirs[0]/'iteration-0.json'));old=json.load(open(ROOT/'photo2/r325/results/graph.json'));data=preprocess(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));t=time.perf_counter();nodes,graph,_,_=infer_graph(initial['observations'],initial['windows'],initial['global_solution']['selected'],data,old['stations_px'],old['period_px']);elapsed=time.perf_counter()-t
    baseline=dict(observations=len(initial['observations']),indexed=sum(n['component'] is not None for n in nodes),links=len(graph['edges']),unresolved=len(graph['unresolved_edges']),components=len(graph['components']),cached_global_solve_seconds=initial['global_solution']['seconds'],graph_seconds=elapsed)
    if (OUT/'practice').exists():shutil.move(str(OUT/'practice'),str(ROOT/'photo2/r326/development/practice-before-cache'))
    shutil.copytree(dirs[0],OUT/'practice')
    save(OUT/'practice-benchmark.json',dict(R325_same_bank=baseline,R326_runs=results,scientific_outputs_exact=True,policy='146 original observations, windows65–93; cached R325 native measurements and candidates. New context measurements and fits are fresh. No cold-detector speedup or independent photographic accuracy claim.'))
    print('R325 SAME BANK',baseline);print('R326 TOTALS',[r['performance']['total_including_serialization'] for r in results])
if __name__=='__main__':main()
